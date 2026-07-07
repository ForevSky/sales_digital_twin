"""Pipeline 输出聚合模型：统一 fallback / success 两种结果形态。"""

from pydantic import BaseModel

from sales_digital_twin.models.suggestions import ContractSuggestion, CRMSuggestion


class PipelineResult(BaseModel):
    """最终输出容器；CLI 通过 render() 获取控制台/文件字符串。"""

    is_fallback: bool = False
    fallback_message: str | None = None
    formatted_text: str | None = None
    crm: CRMSuggestion | None = None
    contract: ContractSuggestion | None = None

    def render(self) -> str:
        if self.is_fallback:
            return self.fallback_message or ""
        parts: list[str] = []
        if self.formatted_text:
            parts.append(self.formatted_text)
        if self.crm:
            parts.append(self.crm.render())
        if self.contract:
            parts.append(self.contract.render())
        return "\n\n".join(parts)

    @classmethod
    def fallback(cls, message: str) -> "PipelineResult":
        """非销售场景等短路路径使用。"""
        return cls(is_fallback=True, fallback_message=message)

    @classmethod
    def success(
        cls,
        formatted: str,
        crm: CRMSuggestion,
        contract: ContractSuggestion,
    ) -> "PipelineResult":
        """销售场景完整处理结果。"""
        return cls(
            is_fallback=False,
            formatted_text=formatted,
            crm=crm,
            contract=contract,
        )
