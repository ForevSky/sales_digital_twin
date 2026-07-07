"""销售数字分身核心编排层。

流程：分类 →（非销售短路 | 提取 → 格式化 + CRM/合同建议）→ 聚合输出。
CLI 与测试均通过 SalesDigitalTwinPipeline.process() 进入，保证调用链路唯一。
"""

import logging
import uuid
from concurrent.futures import ThreadPoolExecutor

from sales_digital_twin.agents.classifier import ClassifierAgent
from sales_digital_twin.agents.contract_advisor import ContractAdvisorAgent
from sales_digital_twin.agents.crm_advisor import CRMAdvisorAgent
from sales_digital_twin.agents.extractor import ExtractorAgent
from sales_digital_twin.core.constants import CONTRACT_KEYWORDS, NON_SALES_MESSAGE
from sales_digital_twin.core.exceptions import EmptyInputError
from sales_digital_twin.infrastructure.config import Settings
from sales_digital_twin.infrastructure.tracing import set_trace_id
from sales_digital_twin.models.enums import SceneType
from sales_digital_twin.models.extraction import ExtractionResult
from sales_digital_twin.models.input import ProcessRequest
from sales_digital_twin.models.output import PipelineResult
from sales_digital_twin.models.suggestions import ContractSuggestion, CRMSuggestion
from sales_digital_twin.services.formatter import FormatterService
from sales_digital_twin.services.rule_engine import RuleEngine

logger = logging.getLogger(__name__)


class SalesDigitalTwinPipeline:
    """唯一业务入口：CLI 与测试均通过此类调用。"""

    def __init__(
        self,
        classifier: ClassifierAgent,
        extractor: ExtractorAgent,
        crm_advisor: CRMAdvisorAgent,
        contract_advisor: ContractAdvisorAgent,
        formatter: FormatterService,
        rule_engine: RuleEngine,
        settings: Settings,
    ) -> None:
        self._classifier = classifier
        self._extractor = extractor
        self._crm_advisor = crm_advisor
        self._contract_advisor = contract_advisor
        self._formatter = formatter
        self._rule_engine = rule_engine
        self._settings = settings

    def process(self, request: ProcessRequest) -> PipelineResult:
        """处理单次通话文本，返回结构化结果或兜底文案。"""
        trace_id = uuid.uuid4().hex[:8]
        set_trace_id(trace_id)
        text = request.text.strip()
        if not text:
            raise EmptyInputError("输入文本不能为空")

        logger.info("pipeline.start trace_id=%s text_len=%d", trace_id, len(text))

        scene = self._classify(text, trace_id)
        logger.info("classify.result trace_id=%s scene=%s", trace_id, scene)
        # 如果场景为非销售场景，则返回兜底文案
        if scene is SceneType.NON_SALES:
            result = PipelineResult.fallback(NON_SALES_MESSAGE)
            logger.info("pipeline.done trace_id=%s is_fallback=True", trace_id)
            return result

        self._settings.validate_api_key()
        # 提取
        extracted = self._extractor.extract(text)
        # 格式化
        formatted = self._formatter.format(extracted)
        # 建议
        crm, contract = self._advise(text, extracted, trace_id)

        result = PipelineResult.success(formatted=formatted, crm=crm, contract=contract)
        logger.info("pipeline.done trace_id=%s is_fallback=False", trace_id)
        return result

    # 建议
    def _advise(
        self, text: str, extracted: ExtractionResult, trace_id: str
    ) -> tuple[CRMSuggestion, ContractSuggestion]:
        # 如果不需要合同建议，则返回 CRM 建议和空合同建议
        if not self._needs_contract_advice(text):
            logger.info(
                "pipeline.skip_contract trace_id=%s reason=no_contract_keywords",
                trace_id,
            )
            return self._crm_advisor.advise(text, extracted), ContractSuggestion()

        # 多线程处理 CRM 和合同建议
        with ThreadPoolExecutor(max_workers=2) as executor:
            # 提交 CRM 建议任务
            crm_future = executor.submit(self._crm_advisor.advise, text, extracted)
            # 提交合同建议任务
            contract_future = executor.submit(self._contract_advisor.advise, text, extracted)
            return crm_future.result(), contract_future.result()

    @staticmethod
    def _needs_contract_advice(text: str) -> bool:
        normalized = text.lower()
        return any(keyword.lower() in normalized for keyword in CONTRACT_KEYWORDS)

    def _classify(self, text: str, trace_id: str) -> SceneType:
        """双层分类：规则高置信直接返回，1-2 个关键词命中时 LLM 复核。"""
        rule_result = self._rule_engine.pre_classify(text)
        if rule_result.is_confident and rule_result.scene is not None:
            logger.info(
                "classify.rule trace_id=%s scene=%s confident=True",
                trace_id,
                rule_result.scene,
            )
            return rule_result.scene

        logger.info("classify.llm trace_id=%s reason=boundary_case", trace_id)
        self._settings.validate_api_key()
        return self._classifier.classify(text)
