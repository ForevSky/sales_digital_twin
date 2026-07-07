"""请求级 trace_id，供 Pipeline 与 Agent 日志关联。"""

from contextvars import ContextVar

_trace_id: ContextVar[str] = ContextVar("trace_id", default="-")

# 设置 trace_id
def set_trace_id(trace_id: str) -> None:
    _trace_id.set(trace_id)

# 获取 trace_id
def get_trace_id() -> str:
    return _trace_id.get()
