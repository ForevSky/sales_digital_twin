from sales_digital_twin.models.extraction import ExtractionResult, NextAction
from sales_digital_twin.services.formatter import FormatterService


def test_format_output_structure() -> None:
    formatter = FormatterService()
    data = ExtractionResult(
        customer_name="上海华讯科技（王总）",
        summary="介绍 SalesMind 平台，获得初步兴趣。",
        pain_points=["CRM 系统老旧", "数据分散"],
        next_action=NextAction(
            person="张三",
            task="发送详细方案报价",
            deadline="2026-07-14 14:00",
        ),
    )
    output = formatter.format(data)
    lines = output.split("\n")
    assert len(lines) == 4
    assert lines[0].startswith("客户名称：")
    assert lines[1].startswith("沟通摘要：")
    assert lines[2].startswith("客户需求：")
    assert lines[3].startswith("下一步行动：")
    assert "张三" in lines[3]
    assert "2026-07-14" in lines[3]
