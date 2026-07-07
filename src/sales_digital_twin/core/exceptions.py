"""项目异常体系：CLI 统一捕获 SalesDigitalTwinError 及其子类。"""


class SalesDigitalTwinError(Exception):
    """项目根异常。"""


class EmptyInputError(SalesDigitalTwinError):
    """输入文本为空。"""


class AgentOutputError(SalesDigitalTwinError):
    """LLM 输出无法解析为预期 Schema。"""

    def __init__(self, agent_name: str, detail: str | Exception) -> None:
        self.agent_name = agent_name
        super().__init__(f"[{agent_name}] 输出解析失败: {detail}")


class LLMInvokeError(SalesDigitalTwinError):
    """LLM API 调用失败（重试耗尽）。"""


class ConfigurationError(SalesDigitalTwinError):
    """配置缺失或非法。"""
