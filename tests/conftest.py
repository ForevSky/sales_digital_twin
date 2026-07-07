import pytest

from sales_digital_twin.services.rule_engine import RuleEngine

from tests.data import CHITCHAT_TEXT, SALES_TEXT


@pytest.fixture
def rule_engine() -> RuleEngine:
    return RuleEngine()
