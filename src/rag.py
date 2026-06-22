"""Dependency-free persistent retrieval memory.

The JSONL backend makes the demo reproducible. Its interface can later be
replaced by Chroma/pgvector without changing the agents.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]", text.lower()))


class StockRAGMemory:
    def __init__(self, path: str | Path = "data/memory.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def store(self, record: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def retrieve(self, stock_code: str, query: str, k: int = 3) -> str:
        if not self.path.exists():
            return ""
        query_tokens = _tokens(f"{stock_code} {query}")
        ranked: list[tuple[float, dict[str, Any]]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("stock_code") != stock_code:
                continue
            content = str(item.get("final_report", ""))
            tokens = _tokens(content)
            score = len(tokens & query_tokens) / max(1, len(query_tokens))
            ranked.append((score, item))
        ranked.sort(key=lambda pair: (pair[0], pair[1].get("created_at", "")), reverse=True)
        return "\n\n".join(
            f"[{item.get('created_at', 'unknown')}] {item.get('final_report', '')[:1200]}"
            for _, item in ranked[:k]
        )

    # Compatibility with the original project API.
    def get_stock_history_summary(self, stock_code: str) -> str:
        return self.retrieve(stock_code, "历史 风险 趋势 投资", k=3)

