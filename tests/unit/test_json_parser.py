import pytest

from sales_digital_twin.infrastructure.llm.json_parser import extract_json_text, parse_llm_json


def test_parse_plain_json() -> None:
    data = parse_llm_json('{"scene": "sales", "reason": "test"}')
    assert data["scene"] == "sales"


def test_parse_markdown_fence() -> None:
    raw = '```json\n{"scene": "non_sales"}\n```'
    data = parse_llm_json(raw)
    assert data["scene"] == "non_sales"


def test_extract_json_from_mixed_text() -> None:
    raw = '分析如下：\n{"has_change": false, "suggestion": "暂无"}'
    text = extract_json_text(raw)
    assert text.startswith("{")
