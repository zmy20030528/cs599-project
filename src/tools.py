"""Function-calling style stock tools with reproducible demo fixtures."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import urllib.parse
import urllib.request

from .config import Settings


def validate_request(stock_code: str, start: str, end: str) -> None:
    if not (stock_code.isdigit() and len(stock_code) == 6):
        raise ValueError("股票代码必须是 6 位数字")
    for value in (start, end):
        datetime.strptime(value, "%Y%m%d")
    if start > end:
        raise ValueError("结束日期不能早于开始日期")


@dataclass
class DemoStockTools:
    """Offline tool implementation; values are visibly labeled simulated."""
    def get_stock_base_info(self, stock_code: str) -> dict:
        names = {"600519": ("贵州茅台", "食品饮料"), "000858": ("五粮液", "食品饮料"), "300750": ("宁德时代", "新能源")}
        name, sector = names.get(stock_code, (f"演示股票{stock_code}", "未知行业"))
        return {"code": stock_code, "name": name, "sector": sector, "data_source": "demo_fixture"}

    def get_market_data(self, stock_code: str, start: str, end: str) -> dict:
        seed = int(hashlib.sha256(stock_code.encode()).hexdigest()[:6], 16)
        close = round(20 + seed % 9000 / 10, 2)
        return {"close": close, "high": round(close * 1.025, 2), "low": round(close * 0.978, 2),
                "change_pct": 1.2, "volume_ratio": 1.15, "period": f"{start}-{end}", "data_source": "demo_fixture"}

    def search_news(self, stock_code: str, stock_name: str) -> list[dict[str, str]]:
        return [
            {"title": f"{stock_name}经营情况演示材料", "content": "公司经营保持稳定；此条为离线演示数据。", "source": "demo_fixture"},
            {"title": "行业风险提示", "content": "需求与政策变化可能带来估值波动；此条为离线演示数据。", "source": "demo_fixture"},
        ]


class LiveStockTools(DemoStockTools):
    """Real-time quote/news adapter; degrades to labeled fixtures on source failure."""
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @staticmethod
    def _prefix(code: str) -> str:
        return "sh" if code.startswith(("6", "9")) else "bj" if code.startswith(("4", "8")) else "sz"

    def _quote(self, code: str) -> list[str]:
        request = urllib.request.Request(
            f"https://hq.sinajs.cn/list={self._prefix(code)}{code}",
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn/"},
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            text = response.read().decode("gb18030", errors="replace")
        if '"' not in text:
            raise RuntimeError("行情源返回格式异常")
        fields = text.split('"', 2)[1].split(",")
        if len(fields) < 10 or not fields[0]:
            raise RuntimeError("未找到股票行情")
        return fields

    def get_stock_base_info(self, stock_code: str) -> dict:
        try:
            fields = self._quote(stock_code)
            return {"code": stock_code, "name": fields[0], "sector": "待补充", "data_source": "sina_realtime"}
        except Exception as exc:
            result = super().get_stock_base_info(stock_code)
            result.update(data_source="demo_fallback", source_error=type(exc).__name__)
            return result

    def get_market_data(self, stock_code: str, start: str, end: str) -> dict:
        try:
            fields = self._quote(stock_code)
            current, previous = float(fields[3]), float(fields[2])
            return {"open": float(fields[1]), "close": current, "high": float(fields[4]), "low": float(fields[5]),
                    "change_pct": round((current - previous) / previous * 100, 2) if previous else 0,
                    "volume": fields[8], "period": f"realtime; requested={start}-{end}", "data_source": "sina_realtime"}
        except Exception as exc:
            result = super().get_market_data(stock_code, start, end)
            result.update(data_source="demo_fallback", source_error=type(exc).__name__)
            return result

    def search_news(self, stock_code: str, stock_name: str) -> list[dict[str, str]]:
        if not self.settings.tavily_api_key:
            return [{"title": "未配置新闻检索", "content": "设置 TAVILY_API_KEY 后启用实时新闻。", "source": "system"}]
        payload = json.dumps({"api_key": self.settings.tavily_api_key, "query": f"{stock_name} {stock_code} 最新公告 新闻",
                              "topic": "news", "max_results": 5}).encode("utf-8")
        request = urllib.request.Request("https://api.tavily.com/search", data=payload,
                                         headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                result = json.loads(response.read().decode("utf-8"))
            return [{"title": item.get("title", ""), "content": item.get("content", ""),
                     "url": item.get("url", ""), "source": "tavily"} for item in result.get("results", [])]
        except Exception as exc:
            return [{"title": "新闻检索降级", "content": f"实时新闻不可用：{type(exc).__name__}", "source": "system"}]
