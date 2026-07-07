"""项目级常量：兜底文案、规则预筛关键词及命中阈值。"""

# FR-04 规定的唯一兜底输出，不可附带其他内容
NON_SALES_MESSAGE = "非销售场景，跳过处理"

# 销售场景关键词库，用于 RuleEngine 第一层快速过滤（降本 + 提速）
SALES_KEYWORDS: tuple[str, ...] = (
    "价格",
    "合同",
    "报价",
    "签约",
    "合作",
    "需求",
    "方案",
    "付款",
    "交付",
    "项目",
    "订单",
    "客户",
    "商机",
    "采购",
    "CRM",
    "演示",
    "预算",
    "谈判",
)

# 命中 ≥3 个关键词 → 高置信 sales；0 个 → 高置信 non_sales；1-2 个 → LLM 复核
SALES_KEYWORD_HIT_THRESHOLD = 3

# 销售场景文本最小长度，用于 RuleEngine 第二层过滤（降本 + 提速）
MIN_SALES_TEXT_LENGTH = 50

# 强销售信号词：命中 ≥2 且文本足够长 → 高置信销售（弥补短文本未达 MIN_SALES_TEXT_LENGTH）
STRONG_SALES_KEYWORDS: tuple[str, ...] = (
    "价格",
    "合同",
    "报价",
    "签约",
    "付款",
    "谈判",
    "预算",
)
STRONG_SALES_MIN_TEXT_LENGTH = 30

# 合同相关关键词：未命中时可跳过 ContractAdvisorAgent（降本）
CONTRACT_KEYWORDS: tuple[str, ...] = (
    "价格",
    "合同",
    "报价",
    "签约",
    "付款",
    "交付",
    "条款",
    "谈判",
    "预算",
)
