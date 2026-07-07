"""销售数字分身核心编排层。

流程：分类 →（非销售短路 | 提取 → 格式化 + CRM/合同建议）→ 聚合输出。
CLI 与测试均通过 SalesDigitalTwinPipeline.process() 进入，保证调用链路唯一。
"""

import logging
import uuid

from sales_digital_twin.agents.classifier import ClassifierAgent
from sales_digital_twin.agents.contract_advisor import ContractAdvisorAgent
from sales_digital_twin.agents.crm_advisor import CRMAdvisorAgent
from sales_digital_twin.agents.extractor import ExtractorAgent
from sales_digital_twin.core.constants import NON_SALES_MESSAGE
from sales_digital_twin.core.exceptions import EmptyInputError
from sales_digital_twin.infrastructure.config import Settings
from sales_digital_twin.models.enums import SceneType
from sales_digital_twin.models.input import ProcessRequest
from sales_digital_twin.models.output import PipelineResult
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
        text = request.text.strip()

        if not text:
            raise EmptyInputError("输入文本不能为空")

        logger.info("pipeline.start trace_id=%s text_len=%d", trace_id, len(text))

        # Step 1: 场景分类（规则优先，边界样本才调 LLM）
        scene = self._classify(text, trace_id)
        logger.info("classify.result trace_id=%s scene=%s", trace_id, scene)

        # Step 2: 非销售场景短路，跳过全部 LLM 提取/建议（FR-04）
        if scene is SceneType.NON_SALES:
            result = PipelineResult.fallback(NON_SALES_MESSAGE)
            logger.info("pipeline.done trace_id=%s is_fallback=True", trace_id)
            return result

        # 进入 LLM 链路前校验 API Key，避免无密钥时仍发起请求
        self._settings.validate_api_key()

        # Step 3: 信息提取 → 固定四行格式化 → CRM/合同并行建议
        extracted = self._extractor.extract(text)
        formatted = self._formatter.format(extracted)
        crm = self._crm_advisor.advise(text, extracted)
        contract = self._contract_advisor.advise(text, extracted)

        # Step 4: 聚合为 PipelineResult，由 render() 输出最终文本
        result = PipelineResult.success(formatted=formatted, crm=crm, contract=contract)
        logger.info("pipeline.done trace_id=%s is_fallback=False", trace_id)
        return result

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

        # 边界样本（关键词命中 1-2 个）：交给 ClassifierAgent 做语义判定
        logger.info("classify.llm trace_id=%s reason=boundary_case", trace_id)
        self._settings.validate_api_key()
        return self._classifier.classify(text)
