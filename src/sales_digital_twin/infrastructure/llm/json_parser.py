"""从 LLM 文本响应中解析 JSON（兼容 DeepSeek 等非 Schema 模式 API）。"""

import json
import re


def extract_json_text(raw: str) -> str:
    """去除 Markdown 代码块等包裹，提取 JSON 字符串。"""
    text = raw.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence_match:
        return fence_match.group(1).strip()

    # 无代码块时，尝试截取首个 { ... } 或 [ ... ]
    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]

    return text


def parse_llm_json(raw: str) -> dict | list:
    """解析 LLM 返回的 JSON 文本。"""
    text = extract_json_text(raw)
    return json.loads(text)
