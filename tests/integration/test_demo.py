"""三组端到端演示 —— 需要配置有效的 DEEPSEEK_API_KEY。"""

import os
from pathlib import Path

import pytest

from sales_digital_twin.core.constants import NON_SALES_MESSAGE
from sales_digital_twin.core.factory import create_pipeline
from sales_digital_twin.models.input import ProcessRequest

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"

pytestmark = pytest.mark.skipif(
    not os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY", "").startswith("sk-your"),
    reason="未配置 DEEPSEEK_API_KEY，跳过集成测试",
)


@pytest.fixture(scope="module")
def pipeline():
    return create_pipeline()


def test_sample1_sales(pipeline) -> None:
    text = (EXAMPLES_DIR / "sample1_sales.txt").read_text(encoding="utf-8")
    result = pipeline.process(ProcessRequest(text=text))
    output = result.render()
    assert not result.is_fallback
    assert "客户名称：" in output
    assert "沟通摘要：" in output
    assert "【CRM 更新建议】" in output
    assert "【商业合同变更建议】" in output


def test_sample2_negotiation(pipeline) -> None:
    text = (EXAMPLES_DIR / "sample2_negotiation.txt").read_text(encoding="utf-8")
    result = pipeline.process(ProcessRequest(text=text))
    output = result.render()
    assert not result.is_fallback
    assert "客户名称：" in output
    assert "【CRM 更新建议】" in output


def test_sample3_chitchat(pipeline) -> None:
    text = (EXAMPLES_DIR / "sample3_chitchat.txt").read_text(encoding="utf-8")
    result = pipeline.process(ProcessRequest(text=text))
    assert result.is_fallback
    assert result.render() == NON_SALES_MESSAGE
