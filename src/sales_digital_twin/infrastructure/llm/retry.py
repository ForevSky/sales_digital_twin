"""LLM 网络层重试：仅对连接/限流/超时异常做指数退避，不对 Schema 校验失败重试。"""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from openai import APIConnectionError, APITimeoutError, RateLimitError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from sales_digital_twin.core.exceptions import LLMInvokeError

P = ParamSpec("P")
R = TypeVar("R")

# 可恢复的网络/API 异常；ValidationError 在 BaseAgent.run() 层单独处理
RETRYABLE_EXCEPTIONS = (APIConnectionError, RateLimitError, APITimeoutError)

# with_llm_retry 重试装饰器
def with_llm_retry(max_attempts: int = 2) -> Callable[[Callable[P, R]], Callable[P, R]]:
    # 装饰器
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        # 重试装饰器
        @retry(
            retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=8),
            reraise=True,
        )
        # 重试函数
        @wraps(func)
        def _retrying(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(*args, **kwargs)

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return _retrying(*args, **kwargs)
            except RETRYABLE_EXCEPTIONS as exc:
                raise LLMInvokeError(
                    f"LLM 调用失败（已重试 {max_attempts} 次）: {exc}"
                ) from exc

        return wrapper

    return decorator
