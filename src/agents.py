"""Agent nodes with dependency injection and graceful error isolation."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from .llm import ChatModel
from .observability import JsonlTracer
from .rag import StockRAGMemory
from .state import StockState
from .tools import DemoStockTools


class StockAgents:
    def __init__(self, model: ChatModel, tools: DemoStockTools, memory: StockRAGMemory, tracer: JsonlTracer) -> None:
        self.model, self.tools, self.memory, self.tracer = model, tools, memory, tracer

    def _safe_llm(self, state: StockState, node: str, system: str, user: str) -> str:
        try:
            with self.tracer.span(state["request_id"], node):
                return self.model.invoke(system, user)
        except Exception as exc:
            state.setdefault("errors", []).append(f"{node}: {exc}")
            return f"【{node}降级结果】模型暂不可用，请人工复核。错误类型：{type(exc).__name__}。"

    def fetcher(self, state: StockState) -> dict:
        with self.tracer.span(state["request_id"], "fetcher"):
            code = state["stock_code"]
            base = self.tools.get_stock_base_info(code)
            return {
                "stock_base_info": base,
                "market_data": self.tools.get_market_data(code, state["kline_start_date"], state["kline_end_date"]),
                "news": self.tools.search_news(code, base["name"]),
                "memory_context": self.memory.get_stock_history_summary(code),
            }

    def quant(self, state: StockState) -> dict:
        prompt = f"行情={state['market_data']}\n历史={state.get('memory_context') or '无'}"
        return {"quant_report": self._safe_llm(state, "quant_agent", "你是：量化分析师。分析趋势、量价与证据边界。", prompt)}

    def risk(self, state: StockState) -> dict:
        prompt = f"标的={state['stock_base_info']}\n行情={state['market_data']}"
        return {"risk_report": self._safe_llm(state, "risk_agent", "你是：风险控制官。给出风险、止损原则与数据局限。", prompt)}

    def news(self, state: StockState) -> dict:
        prompt = f"新闻={state.get('news', [])}"
        return {"news_report": self._safe_llm(state, "news_agent", "你是：舆情分析师。区分事实、观点与模拟数据。", prompt)}

    def cio(self, state: StockState) -> dict:
        evidence = (
            f"量化：{state.get('quant_report')}\n风险：{state.get('risk_report')}\n"
            f"舆情：{state.get('news_report')}\n基础信息：{state.get('stock_base_info')}"
        )
        instruction = (
            "你是：CIO。综合多智能体证据，输出包含摘要、证据、风险、观察清单的中文报告。"
            "不得承诺收益，必须写明不构成投资建议。"
        )
        return {"final_report": self._safe_llm(state, "cio_agent", instruction, evidence)}

    def store(self, state: StockState) -> dict:
        with self.tracer.span(state["request_id"], "memory_store"):
            self.memory.store({
                "request_id": state["request_id"], "stock_code": state["stock_code"],
                "created_at": datetime.now(timezone.utc).isoformat(), "final_report": state["final_report"],
            })
        return {}


Node = Callable[[StockState], dict]

