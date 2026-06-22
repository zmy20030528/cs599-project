"""Simple JSONL tracing for Agent execution and evaluation."""
from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class JsonlTracer:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def span(self, request_id: str, node: str) -> Iterator[dict[str, Any]]:
        start = time.perf_counter()
        event: dict[str, Any] = {"request_id": request_id, "node": node, "status": "ok"}
        try:
            yield event
        except Exception as exc:
            event.update(status="error", error=type(exc).__name__)
            raise
        finally:
            event["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")

