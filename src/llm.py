"""LLM gateway: deterministic demo model and OpenAI-compatible live API."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Protocol

from .config import Settings


class ChatModel(Protocol):
    def invoke(self, system: str, user: str) -> str: ...


class DeepSeekChatModel:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def invoke(self, system: str, user: str) -> str:
        payload = json.dumps({
            "model": self.settings.model,
            "temperature": 0.1,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        }).encode("utf-8")
        request = urllib.request.Request(
            f"{self.settings.api_base}/chat/completions",
            data=payload,
            headers={"Authorization": f"Bearer {self.settings.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.settings.timeout_seconds) as response:
                result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
        except (urllib.error.URLError, KeyError, IndexError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"LLM 调用失败: {exc}") from exc


class DemoChatModel:
    """Stable local substitute used for tests and five-minute demos."""
    def invoke(self, system: str, user: str) -> str:
        role = system.split("：", 1)[-1].split("。", 1)[0]
        return (
            f"【{role}】基于演示数据：趋势为震荡偏强，但证据完整度有限。"
            "建议观察成交量确认，不追涨；关键风险包括数据时效、市场波动和模型误判。"
            "本结论仅用于教学与研究，不构成投资建议。"
        )


def create_model(settings: Settings) -> ChatModel:
    return DemoChatModel() if settings.mode == "demo" else DeepSeekChatModel(settings)

