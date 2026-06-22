"""LangGraph topology plus a dependency-free fallback executor."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from .agents import StockAgents
from .state import StockState


class LocalStockGraph:
    """Same DAG semantics as the LangGraph version, usable offline."""
    def __init__(self, agents: StockAgents) -> None:
        self.agents = agents

    def invoke(self, initial_state: StockState, config: dict | None = None) -> StockState:
        state: StockState = dict(initial_state)
        state.update(self.agents.fetcher(state))
        # Expert agents are independent; execute in parallel before CIO aggregation.
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(node, state) for node in (self.agents.quant, self.agents.risk, self.agents.news)]
            for future in futures:
                state.update(future.result())
        state.update(self.agents.cio(state))
        self.agents.store(state)
        return state


def build_stock_graph(agents: StockAgents, checkpointer: Any = None, prefer_langgraph: bool = True):
    """Build the production LangGraph DAG, falling back for minimal environments."""
    if not prefer_langgraph:
        return LocalStockGraph(agents)
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError:
        return LocalStockGraph(agents)

    builder = StateGraph(StockState)
    for name, node in {
        "fetcher": agents.fetcher, "quant_agent": agents.quant, "risk_agent": agents.risk,
        "news_agent": agents.news, "cio_agent": agents.cio, "memory_store": agents.store,
    }.items():
        builder.add_node(name, node)
    builder.add_edge(START, "fetcher")
    for expert in ("quant_agent", "risk_agent", "news_agent"):
        builder.add_edge("fetcher", expert)
    # A list-valued source is an explicit fan-in barrier: CIO runs once after all experts.
    builder.add_edge(["quant_agent", "risk_agent", "news_agent"], "cio_agent")
    builder.add_edge("cio_agent", "memory_store")
    builder.add_edge("memory_store", END)
    return builder.compile(checkpointer=checkpointer)
