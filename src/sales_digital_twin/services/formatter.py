"""格式化服务（FR-02）：将 ExtractionResult 渲染为 PRD 规定的固定四行文本。"""

from sales_digital_twin.models.extraction import ExtractionResult


class FormatterService:
    def format(self, data: ExtractionResult) -> str:
        """输出字段顺序与标点格式不可变更，供销售直接复制到 CRM。"""
        needs = "、".join(data.pain_points) if data.pain_points else "待确认"
        action = data.next_action
        return "\n".join(
            [
                f"客户名称：{data.customer_name}",
                f"沟通摘要：{data.summary}",
                f"客户需求：{needs}",
                (
                    f"下一步行动：负责人{action.person}，"
                    f"任务{action.task}，截止{action.deadline}"
                ),
            ]
        )
