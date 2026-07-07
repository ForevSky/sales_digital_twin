"""合同顾问 Agent（FR-05）：识别价格/条款/交付周期等变更需求。"""

from sales_digital_twin.agents.base import BaseAgent
from sales_digital_twin.models.extraction import ExtractionResult
from sales_digital_twin.models.suggestions import ContractSuggestion


class ContractAdvisorAgent(BaseAgent[ContractSuggestion]):
    prompt_name = "contract_advisor"
    output_model = ContractSuggestion

    def advise(self, text: str, extracted: ExtractionResult) -> ContractSuggestion:
        return self.run(
            text=text,
            extracted=extracted.model_dump_json(ensure_ascii=False),
        )
