"""Shared LangGraph state contract (Python 3.8+ compatible)."""
from typing import Any, Dict, List, TypedDict


class StockState(TypedDict, total=False):
    request_id: str
    stock_code: str
    kline_start_date: str
    kline_end_date: str
    stock_base_info: Dict[str, Any]
    market_data: Dict[str, Any]
    news: List[Dict[str, str]]
    memory_context: str
    quant_report: str
    risk_report: str
    news_report: str
    final_report: str
    errors: List[str]
    trace: List[Dict[str, Any]]
