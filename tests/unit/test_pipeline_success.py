from unittest.mock import MagicMock

from sales_digital_twin.agents.classifier import ClassifierAgent
from sales_digital_twin.agents.contract_advisor import ContractAdvisorAgent
from sales_digital_twin.agents.crm_advisor import CRMAdvisorAgent
from sales_digital_twin.agents.extractor import ExtractorAgent
from sales_digital_twin.core.pipeline import SalesDigitalTwinPipeline
from sales_digital_twin.infrastructure.config import Settings
from sales_digital_twin.models.extraction import ExtractionResult, NextAction
from sales_digital_twin.models.input import ProcessRequest
from sales_digital_twin.models.suggestions import CRMFieldUpdate, CRMSuggestion, ContractSuggestion
from sales_digital_twin.services.formatter import FormatterService
from sales_digital_twin.services.rule_engine import RuleEngine

from tests.data import SALES_TEXT


def _build_pipeline_with_mocks() -> tuple[SalesDigitalTwinPipeline, MagicMock, MagicMock, MagicMock]:
    extractor = MagicMock(spec=ExtractorAgent)
    crm_advisor = MagicMock(spec=CRMAdvisorAgent)
    contract_advisor = MagicMock(spec=ContractAdvisorAgent)

    pipeline = SalesDigitalTwinPipeline(
        classifier=MagicMock(spec=ClassifierAgent),
        extractor=extractor,
        crm_advisor=crm_advisor,
        contract_advisor=contract_advisor,
        formatter=FormatterService(),
        rule_engine=RuleEngine(),
        settings=Settings(),
    )
    return pipeline, extractor, crm_advisor, contract_advisor


def test_sales_success_path_renders_full_output() -> None:
    pipeline, extractor, crm_advisor, contract_advisor = _build_pipeline_with_mocks()

    extractor.extract.return_value = ExtractionResult(
        customer_name="深圳智创科技（李经理）",
        summary="第二轮价格谈判，客户认为报价偏高。",
        pain_points=["预算有限"],
        next_action=NextAction(
            person="张三",
            task="提交修订报价",
            deadline="2026-07-14",
        ),
    )
    crm_advisor.advise.return_value = CRMSuggestion(
        updates=[CRMFieldUpdate(field="商机金额", old_value="30万", new_value="25万")]
    )
    contract_advisor.advise.return_value = ContractSuggestion(
        has_change=True,
        suggestion="建议调整报价条款，将总价下调至25万。",
    )

    result = pipeline.process(ProcessRequest(text=SALES_TEXT))
    output = result.render()

    assert result.is_fallback is False
    assert "客户名称：深圳智创科技（李经理）" in output
    assert "【CRM 更新建议】" in output
    assert "【商业合同变更建议】" in output
    extractor.extract.assert_called_once()
    crm_advisor.advise.assert_called_once()
    contract_advisor.advise.assert_called_once()


def test_skips_contract_advisor_without_contract_keywords() -> None:
    pipeline, extractor, crm_advisor, contract_advisor = _build_pipeline_with_mocks()

    sales_text_without_contract = (
        "今天向上海华讯科技王总介绍了 SalesMind 平台，"
        "客户对一体化销售管理和自动跟进记录很感兴趣，"
        "约定下周安排在线演示并发送详细方案。"
    )
    extractor.extract.return_value = ExtractionResult(
        customer_name="上海华讯科技（王总）",
        summary="介绍 SalesMind 平台，客户有初步兴趣。",
        pain_points=["CRM 老旧", "数据分散"],
        next_action=NextAction(person="张三", task="安排演示", deadline="2026-07-14"),
    )
    crm_advisor.advise.return_value = CRMSuggestion(
        updates=[CRMFieldUpdate(field="客户状态", old_value="未知", new_value="跟进中")]
    )

    result = pipeline.process(ProcessRequest(text=sales_text_without_contract))
    output = result.render()

    assert result.is_fallback is False
    assert "【CRM 更新建议】" in output
    assert "暂无合同变更需求" in output
    crm_advisor.advise.assert_called_once()
    contract_advisor.advise.assert_not_called()
