from sales_digital_twin.models.enums import SceneType
from sales_digital_twin.services.rule_engine import RuleEngine

from tests.data import CHITCHAT_TEXT, SALES_TEXT


def test_sales_text_classified_as_sales(rule_engine: RuleEngine) -> None:
    result = rule_engine.pre_classify(SALES_TEXT)
    assert result.is_confident is True
    assert result.scene is SceneType.SALES


def test_chitchat_classified_as_non_sales(rule_engine: RuleEngine) -> None:
    result = rule_engine.pre_classify(CHITCHAT_TEXT)
    assert result.is_confident is True
    assert result.scene is SceneType.NON_SALES


def test_short_keyword_rich_text_not_confident(rule_engine: RuleEngine) -> None:
    result = rule_engine.pre_classify("聊了合同、价格、客户")
    assert result.is_confident is False
    assert result.scene is None