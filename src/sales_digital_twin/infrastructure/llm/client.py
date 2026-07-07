"""LLM 客户端工厂：DeepSeek 通过 OpenAI 兼容接口接入 LangChain。"""

from langchain_openai import ChatOpenAI

from sales_digital_twin.infrastructure.config import Settings


def create_llm(settings: Settings) -> ChatOpenAI:
    """创建 ChatOpenAI 实例；max_retries=0 由 BaseAgent 层统一控制重试。"""
    # 允许无 Key 时创建实例（非销售短路场景不调 LLM）；实际调用前由 Pipeline 校验
    api_key = settings.deepseek_api_key or "sk-placeholder-not-used"
    return ChatOpenAI(
        model=settings.deepseek_model,
        api_key=api_key,
        base_url=settings.deepseek_api_base,
        temperature=settings.llm_temperature,
        timeout=settings.llm_timeout_seconds,
        max_retries=0,
    )
