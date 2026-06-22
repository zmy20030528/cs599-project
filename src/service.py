"""Application service used by CLI, tests, and future web adapters."""
from __future__ import annotations

import uuid

from .agents import StockAgents
from .config import Settings
from .graph import build_stock_graph
from .llm import create_model
from .observability import JsonlTracer
from .rag import StockRAGMemory
from .state import StockState
from .tools import DemoStockTools, LiveStockTools, validate_request


def analyze_stock(stock_code: str, start: str, end: str, settings: Settings, prefer_langgraph: bool = True) -> StockState:
    validate_request(stock_code, start, end)
    tools = DemoStockTools() if settings.mode == "demo" else LiveStockTools(settings)
    agents = StockAgents(create_model(settings), tools, StockRAGMemory(settings.memory_path), JsonlTracer(settings.trace_path))
    graph = build_stock_graph(agents, prefer_langgraph=prefer_langgraph)
    initial: StockState = {
        "request_id": uuid.uuid4().hex, "stock_code": stock_code,
        "kline_start_date": start, "kline_end_date": end, "errors": [], "trace": [],
    }
    return graph.invoke(initial, {"configurable": {"thread_id": initial["request_id"]}})
