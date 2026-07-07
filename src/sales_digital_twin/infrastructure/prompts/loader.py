"""Prompt 模板加载器：从 prompts/*.txt 读取外置提示词。"""

from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

from sales_digital_twin.core.exceptions import ConfigurationError


class PromptLoader:
    def __init__(self, prompts_dir: Path | None = None) -> None:
        # 默认指向 infrastructure/prompts/ 目录
        self._prompts_dir = prompts_dir or Path(__file__).resolve().parent

    def load(self, name: str) -> ChatPromptTemplate:
        """加载 {name}.txt 为 system 消息模板，支持 {text} 等占位符。"""
        path = self._prompts_dir / f"{name}.txt"
        if not path.exists():
            raise ConfigurationError(f"Prompt 文件不存在: {path}")
        content = path.read_text(encoding="utf-8").strip()
        return ChatPromptTemplate.from_messages([("system", content)])
