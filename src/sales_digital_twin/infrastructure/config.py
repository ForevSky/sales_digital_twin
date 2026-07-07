"""应用配置：从 .env 加载 DeepSeek API 与 LLM 运行参数。"""

from pydantic_settings import BaseSettings, SettingsConfigDict

from sales_digital_twin.core.paths import project_root


def _env_files() -> tuple[str, ...]:
    """优先加载项目根目录 .env，兼容从任意子目录启动。"""
    root_env = project_root() / ".env"
    return (str(root_env), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_files(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    deepseek_api_key: str = ""
    deepseek_api_base: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    llm_temperature: float = 0.1
    llm_max_retries: int = 2
    llm_timeout_seconds: int = 60
    log_level: str = "INFO"

    def validate_api_key(self) -> None:
        """在首次 LLM 调用前校验，非销售短路场景可不触发。"""
        if not self.deepseek_api_key or self.deepseek_api_key.startswith("sk-your"):
            from sales_digital_twin.core.exceptions import ConfigurationError

            raise ConfigurationError(
                "未配置有效的 DEEPSEEK_API_KEY，请在项目根目录 .env 中填入密钥"
            )
