from unittest.mock import MagicMock

import pytest

from sales_digital_twin.agents.classifier import ClassifierAgent
from sales_digital_twin.agents.contract_advisor import ContractAdvisorAgent
from sales_digital_twin.agents.crm_advisor import CRMAdvisorAgent
from sales_digital_twin.agents.extractor import ExtractorAgent
from sales_digital_twin.core.constants import NON_SALES_MESSAGE
from sales_digital_twin.core.exceptions import EmptyInputError
from sales_digital_twin.core.pipeline import SalesDigitalTwinPipeline
from sales_digital_twin.infrastructure.config import Settings
from sales_digital_twin.models.input import ProcessRequest
from sales_digital_twin.services.formatter import FormatterService
from sales_digital_twin.services.rule_engine import RuleEngine

from tests.data import CHITCHAT_TEXT


@pytest.fixture
def pipeline_with_mocks() -> SalesDigitalTwinPipeline:
    classifier = MagicMock(spec=ClassifierAgent)
    extractor = MagicMock(spec=ExtractorAgent)
    crm_advisor = MagicMock(spec=CRMAdvisorAgent)
    contract_advisor = MagicMock(spec=ContractAdvisorAgent)

    return SalesDigitalTwinPipeline(
        classifier=classifier,
        extractor=extractor,
        crm_advisor=crm_advisor,
        contract_advisor=contract_advisor,
        formatter=FormatterService(),
        rule_engine=RuleEngine(),
        settings=Settings(),
    )


def test_non_sales_fallback_without_llm(pipeline_with_mocks: SalesDigitalTwinPipeline) -> None:
    result = pipeline_with_mocks.process(ProcessRequest(text=CHITCHAT_TEXT))
    assert result.is_fallback is True
    assert result.render() == NON_SALES_MESSAGE
    pipeline_with_mocks._extractor.extract.assert_not_called()


def test_empty_input_raises(pipeline_with_mocks: SalesDigitalTwinPipeline) -> None:
    with pytest.raises(EmptyInputError):
        pipeline_with_mocks.process(ProcessRequest(text="   "))
