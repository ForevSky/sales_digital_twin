"""规则引擎：分类第一层，高置信场景跳过 LLM 以节省成本与延迟。"""

from pydantic import BaseModel

from sales_digital_twin.core.constants import (
    MIN_SALES_TEXT_LENGTH,
    SALES_KEYWORD_HIT_THRESHOLD,
    SALES_KEYWORDS,
    STRONG_SALES_KEYWORDS,
    STRONG_SALES_MIN_TEXT_LENGTH,
)
from sales_digital_twin.models.enums import SceneType


class RuleResult(BaseModel):
    """规则预筛结果；is_confident=False 表示需 LLM 复核。"""

    scene: SceneType | None = None
    is_confident: bool = False

# RuleEngine 规则引擎
class RuleEngine:
    def pre_classify(self, text: str) -> RuleResult:
        normalized = text.lower()
        text_len = len(text.strip())
        # 计算命中关键词数量
        hits = sum(1 for keyword in SALES_KEYWORDS if keyword.lower() in normalized)
        # 计算强关键词命中数量
        strong_hits = sum(
            1 for keyword in STRONG_SALES_KEYWORDS if keyword.lower() in normalized
        )
        # 如果强关键词命中数量大于等于2，并且文本长度大于等于强关键词最小长度，则返回销售场景
        if strong_hits >= 2 and text_len >= STRONG_SALES_MIN_TEXT_LENGTH:
            return RuleResult(scene=SceneType.SALES, is_confident=True)
        # 如果命中关键词数量大于等于阈值，并且文本长度大于等于最小长度，则返回销售场景
        if hits >= SALES_KEYWORD_HIT_THRESHOLD and text_len >= MIN_SALES_TEXT_LENGTH:
            return RuleResult(scene=SceneType.SALES, is_confident=True)

        # 如果命中关键词数量为0，则返回非销售场景
        if hits == 0:
            return RuleResult(scene=SceneType.NON_SALES, is_confident=True)

        return RuleResult(is_confident=False)
