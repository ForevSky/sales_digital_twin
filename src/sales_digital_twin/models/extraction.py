"""提取与分类相关的 Pydantic Schema（Agent 结构化输出）。"""

from pydantic import BaseModel, Field, field_validator


class NextAction(BaseModel):
    """下一步行动三要素：负责人、任务、截止时间。"""

    person: str = "待确认"
    task: str = "待确认"
    deadline: str = "待确认"


class ExtractionResult(BaseModel):
    """ExtractorAgent 输出；缺失字段默认「待确认」以保证 Pipeline 不中断。"""

    customer_name: str = "待确认"
    summary: str = "待确认"
    pain_points: list[str] = Field(default_factory=list)
    next_action: NextAction = Field(default_factory=NextAction)

    @field_validator("summary")
    @classmethod
    def summary_not_empty(cls, value: str) -> str:
        return value.strip() or "待确认"

    @field_validator("customer_name")
    @classmethod
    def customer_name_not_empty(cls, value: str) -> str:
        return value.strip() or "待确认"

# ClassificationResult 分类结果
class ClassificationResult(BaseModel):
    """ClassifierAgent 输出；scene 支持中英文别名。"""

    scene: str
    reason: str = ""

    def to_scene_type(self) -> "SceneType":
        from sales_digital_twin.models.enums import SceneType

        normalized = self.scene.strip().lower()
        if normalized in ("sales", "销售", "销售场景"):
            return SceneType.SALES
        return SceneType.NON_SALES
