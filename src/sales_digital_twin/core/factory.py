"""Pipeline 工厂：组装各 Agent 与领域服务，支持测试时注入 Mock Settings。"""

from sales_digital_twin.agents.classifier import ClassifierAgent
from sales_digital_twin.agents.contract_advisor import ContractAdvisorAgent
from sales_digital_twin.agents.crm_advisor import CRMAdvisorAgent
from sales_digital_twin.agents.extractor import ExtractorAgent
from sales_digital_twin.core.pipeline import SalesDigitalTwinPipeline
from sales_digital_twin.infrastructure.config import Settings
from sales_digital_twin.infrastructure.llm.client import create_llm
from sales_digital_twin.infrastructure.prompts.loader import PromptLoader
from sales_digital_twin.services.formatter import FormatterService
from sales_digital_twin.services.rule_engine import RuleEngine


def create_pipeline(settings: Settings | None = None) -> SalesDigitalTwinPipeline:
    """创建完整 Pipeline 实例；各 Agent 共享同一 LLM 与 PromptLoader。"""
    settings = settings or Settings()

    llm = create_llm(settings)
    prompt_loader = PromptLoader()

    return SalesDigitalTwinPipeline(
        classifier=ClassifierAgent(llm, prompt_loader, max_retries=settings.llm_max_retries),
        extractor=ExtractorAgent(llm, prompt_loader, max_retries=settings.llm_max_retries),
        crm_advisor=CRMAdvisorAgent(llm, prompt_loader, max_retries=settings.llm_max_retries),
        contract_advisor=ContractAdvisorAgent(
            llm, prompt_loader, max_retries=settings.llm_max_retries
        ),
        formatter=FormatterService(),
        rule_engine=RuleEngine(),
        settings=settings,
    )
