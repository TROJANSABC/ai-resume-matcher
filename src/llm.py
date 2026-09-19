"""LLM 调用封装：预留模型切换接口，支持任意 OpenAI 兼容后端。

通过环境变量配置，方便在 OpenAI / DeepSeek / 本地模型之间切换：
    OPENAI_API_KEY   必填
    OPENAI_BASE_URL  可选，默认 https://api.openai.com/v1
    LLM_MODEL        可选，默认 gpt-4o-mini
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover
    pass


class LLMConfigError(RuntimeError):
    """LLM 配置缺失或不可用时抛出。"""


def get_client_config() -> Dict[str, str]:
    """读取当前 LLM 配置。"""
    return {
        "api_key": os.getenv("OPENAI_API_KEY", "").strip(),
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip(),
        "model": os.getenv("LLM_MODEL", "gpt-4o-mini").strip(),
    }


def is_configured() -> bool:
    """是否已完成最小可用的 LLM 配置。"""
    return bool(get_client_config()["api_key"])


def _client():
    cfg = get_client_config()
    if not cfg["api_key"]:
        raise LLMConfigError(
            "未检测到 OPENAI_API_KEY，请在 .env 中配置，或在侧边栏填入 API Key。"
        )
    try:
        from openai import OpenAI
    except Exception as e:  # pragma: no cover
        raise LLMConfigError(f"未安装 openai 依赖：{e}") from e
    return OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])


def chat(
    messages: List[Dict[str, str]],
    *,
    temperature: float = 0.3,
    model: Optional[str] = None,
    response_format_json: bool = False,
) -> str:
    """一次对话调用，返回文本内容。

    Args:
        messages: OpenAI 风格消息列表。
        temperature: 采样温度。
        model: 覆盖默认模型。
        response_format_json: 是否要求返回 JSON。
    """
    cfg = get_client_config()
    kwargs: Dict[str, Any] = {
        "model": model or cfg["model"],
        "messages": messages,
        "temperature": temperature,
    }
    if response_format_json:
        kwargs["response_format"] = {"type": "json_object"}
    resp = _client().chat.completions.create(**kwargs)
    return (resp.choices[0].message.content or "").strip()


def chat_json(messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """对话调用并解析 JSON；解析失败时尽力从文本中提取 JSON 片段。"""
    kwargs.setdefault("temperature", 0.2)
    text = chat(messages, response_format_json=True, **kwargs)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 兜底：截取第一个 { 到最后一个 }
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise LLMConfigError(f"模型返回无法解析为 JSON：{text[:500]}")
