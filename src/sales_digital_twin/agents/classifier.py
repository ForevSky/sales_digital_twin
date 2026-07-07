"""场景分类 Agent：仅在规则引擎无法高置信判定时调用（边界样本）。"""

from sales_digital_twin.agents.base import BaseAgent
from sales_digital_twin.models.enums import SceneType
from sales_digital_twin.models.extraction import ClassificationResult

# ClassifierAgent 场景分类 Agent
class ClassifierAgent(BaseAgent[ClassificationResult]):
    prompt_name = "classifier"
    output_model = ClassificationResult

    def classify(self, text: str) -> SceneType:
        """LLM 语义复核，输出 sales / non_sales。"""
        result = self.run(text=text)
        return result.to_scene_type()
