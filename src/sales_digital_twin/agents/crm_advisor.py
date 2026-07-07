"""CRM 顾问 Agent（FR-03）：推断字段变更建议，仅输出建议不写入真实 CRM。"""

from sales_digital_twin.agents.base import BaseAgent
from sales_digital_twin.models.extraction import ExtractionResult
from sales_digital_twin.models.suggestions import CRMSuggestion

# CRMAdvisorAgent CRM 顾问 Agent
class CRMAdvisorAgent(BaseAgent[CRMSuggestion]):
    prompt_name = "crm_advisor"
    output_model = CRMSuggestion

    def advise(self, text: str, extracted: ExtractionResult) -> CRMSuggestion:
        # 将已提取结构作为上下文传入，减少重复推理、提高字段推断一致性
        return self.run(
            text=text,
            extracted=extracted.model_dump_json(ensure_ascii=False),
        )
