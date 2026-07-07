"""
Agent 基类：封装 Prompt 加载、JSON 解析与双层重试策略（兼容 DeepSeek）。
"""

import logging
from abc import ABC
from json import JSONDecodeError
from typing import Any, Generic, TypeVar

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

from sales_digital_twin.core.exceptions import AgentOutputError, LLMInvokeError
from sales_digital_twin.infrastructure.llm.json_parser import parse_llm_json
from sales_digital_twin.infrastructure.llm.retry import with_llm_retry
from sales_digital_twin.infrastructure.prompts.loader import PromptLoader
from sales_digital_twin.infrastructure.tracing import get_trace_id

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def _extract_text_content(
    response: AIMessage | BaseMessage | str | dict[str, Any],
) -> str:
    """从 LangChain 响应中提取纯文本，兼容 str / AIMessage / 多模态 content 列表。"""
    if isinstance(response, str):
        return response

    # LangChain 消息体或 dict 形式的 content
    if isinstance(response, BaseMessage):
        content = response.content
    elif isinstance(response, dict):
        content = response.get("content", response)
    else:
        content = response

    if isinstance(content, str):
        return content

    # 部分模型返回 content 块列表，仅拼接 type=text 的片段
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts)

    return str(content)


class BaseAgent(ABC, Generic[T]):
    """Agent 基类；子类通过类属性绑定 Prompt 与输出 Schema。"""

    prompt_name: str  # 对应 infrastructure/prompts/{name}.txt
    output_model: type[T]  # LLM JSON 校验目标

    def __init__(
        self,
        llm: ChatOpenAI,
        prompt_loader: PromptLoader,
        max_retries: int = 2,
    ) -> None:
        self._llm = llm
        self._prompt_loader = prompt_loader
        self._max_retries = max_retries  # 传给 with_llm_retry，仅用于网络/API 异常
        self._prompt = self._prompt_loader.load(self.prompt_name)
        # DeepSeek 兼容 OpenAI JSON 模式，减少 Markdown 包裹导致的解析失败
        self._json_llm = llm.bind(response_format={"type": "json_object"})

    def run(self, **variables: str) -> T:
        """执行 LLM 调用并返回 Pydantic 模型。

        variables 的键须与 Prompt 占位符一致（如 text、extracted）。
        解析/校验失败时重新 invoke，最多共 2 次；网络错误由 _invoke_llm 内重试。
        """
        last_error: Exception | None = None
        parse_attempts = 2

        for attempt in range(1, parse_attempts + 1):
            try:
                return self._invoke_llm(dict(variables))
            except (ValidationError, JSONDecodeError, ValueError, TypeError) as exc:
                # 输出格式问题：允许再调一次 LLM，不消耗网络层重试配额
                last_error = exc
                logger.warning(
                    "trace_id=%s %s 输出解析失败 (attempt %d/%d): %s",
                    get_trace_id(),
                    self.__class__.__name__,
                    attempt,
                    parse_attempts,
                    exc,
                )
            except LLMInvokeError:
                # 网络层已耗尽重试，直接上抛，不再做解析层重试
                raise

        raise AgentOutputError(self.__class__.__name__, last_error or "未知错误")

    def _invoke_llm(self, variables: dict[str, str]) -> T:
        """单次 LLM 调用：Prompt | LLM → 文本 → JSON → Pydantic。"""

        @with_llm_retry(max_attempts=self._max_retries)
        def _call() -> T:
            chain = self._prompt | self._json_llm
            response = chain.invoke(variables)
            raw_text = _extract_text_content(response)
            # parse_llm_json 仍保留，兼容偶发的 ```json 代码块包裹
            data = parse_llm_json(raw_text)
            if not isinstance(data, dict):
                raise ValueError(f"期望 JSON 对象，实际为: {type(data).__name__}")
            return self.output_model.model_validate(data)

        return _call()
