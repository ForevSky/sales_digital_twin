from unittest.mock import MagicMock

import pytest
from openai import APIConnectionError

from sales_digital_twin.core.exceptions import LLMInvokeError
from sales_digital_twin.infrastructure.llm.retry import with_llm_retry


def test_retries_retryable_errors_before_raising() -> None:
    calls: list[int] = []

    @with_llm_retry(max_attempts=3)
    def flaky() -> str:
        calls.append(1)
        if len(calls) < 3:
            raise APIConnectionError(request=MagicMock())
        return "ok"

    assert flaky() == "ok"
    assert len(calls) == 3


def test_raises_llm_invoke_error_after_retries_exhausted() -> None:
    @with_llm_retry(max_attempts=2)
    def always_fail() -> str:
        raise APIConnectionError(request=MagicMock())

    with pytest.raises(LLMInvokeError, match="已重试 2 次"):
        always_fail()
