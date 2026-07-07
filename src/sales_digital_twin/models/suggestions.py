"""CRM 与合同建议 Schema 及文本渲染。"""

from pydantic import BaseModel, Field


class CRMFieldUpdate(BaseModel):
    field: str
    old_value: str = "未知"
    new_value: str


class CRMSuggestion(BaseModel):
    updates: list[CRMFieldUpdate] = Field(default_factory=list)

    def render(self) -> str:
        """渲染为 PRD 规定的【CRM 更新建议】块。"""
        if not self.updates:
            return "【CRM 更新建议】\n暂无明确变更建议"
        lines = ["【CRM 更新建议】"]
        lines.extend(f"- {item.field}：{item.old_value} → {item.new_value}" for item in self.updates)
        return "\n".join(lines)


class ContractSuggestion(BaseModel):
    has_change: bool = False
    suggestion: str = "暂无合同变更需求，待方案确认后再议。"

    def render(self) -> str:
        """渲染为 PRD 规定的【商业合同变更建议】块。"""
        return f"【商业合同变更建议】\n{self.suggestion}"
