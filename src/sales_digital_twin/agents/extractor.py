"""信息提取 Agent（FR-01）：从通话文本抽取客户、摘要、需求、下一步行动。"""

from sales_digital_twin.agents.base import BaseAgent
from sales_digital_twin.models.extraction import ExtractionResult

# ExtractorAgent 信息提取 Agent
class ExtractorAgent(BaseAgent[ExtractionResult]):
    prompt_name = "extractor"
    output_model = ExtractionResult

    def extract(self, text: str) -> ExtractionResult:
        return self.run(text=text)
