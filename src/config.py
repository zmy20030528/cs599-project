"""Runtime configuration with no import-time side effects."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: Path = Path(".env")) -> None:
    """Load a small .env file without adding a mandatory dependency."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


@dataclass(frozen=True)
class Settings:
    mode: str = "demo"
    model: str = "deepseek-chat"
    api_base: str = "https://api.deepseek.com"
    api_key: str = ""
    tavily_api_key: str = ""
    data_dir: Path = Path("data")
    timeout_seconds: int = 45

    @property
    def memory_path(self) -> Path:
        return self.data_dir / "memory.jsonl"

    @property
    def trace_path(self) -> Path:
        return self.data_dir / "traces.jsonl"

    @classmethod
    def from_env(cls, mode: str | None = None) -> "Settings":
        _load_dotenv()
        selected = (mode or os.getenv("STOCK_AGENT_MODE", "demo")).lower()
        if selected not in {"demo", "live"}:
            raise ValueError("STOCK_AGENT_MODE 必须是 demo 或 live")
        settings = cls(
            mode=selected,
            model=os.getenv("LLM_MODEL", "deepseek-chat"),
            api_base=os.getenv("LLM_API_BASE", "https://api.deepseek.com").rstrip("/"),
            api_key=os.getenv("LLM_API_KEY", ""),
            tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
            data_dir=Path(os.getenv("DATA_DIR", "data")),
            timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS", "45")),
        )
        if settings.mode == "live" and not settings.api_key:
            raise ValueError("live 模式需要环境变量 LLM_API_KEY；演示可使用 --mode demo")
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        return settings
