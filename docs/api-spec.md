# API Spec

## CLI

```text
python langchain_merrary.py [--stock-code CODE] [--start YYYYMMDD]
                            [--end YYYYMMDD] [--mode demo|live] [--json]
```

成功退出码 `0`；输入/配置错误退出码 `2`。`--json` 输出完整 `StockState`，默认仅输出最终报告。

## Python API

```python
analyze_stock(stock_code: str, start: str, end: str,
              settings: Settings, prefer_langgraph: bool = True) -> StockState
```

关键输出字段：`stock_base_info`、`market_data`、`news`、`memory_context`、三个专家报告、`final_report`、`errors`。

## Tool contracts

| Tool | Input | Output / error |
|---|---|---|
| `validate_request` | code, start, end | `None` / `ValueError` |
| `get_stock_base_info` | code | name, sector, source |
| `get_market_data` | code, dates | OHLC-like snapshot, source |
| `search_news` | code, name | normalized news list |
| `memory.retrieve` | code, query, k | ranked context string |

未来 MCP 映射建议：将前三个数据工具公开为 `tools/list`/`tools/call`，以 JSON Schema 描述输入；记忆保留在服务内部，避免跨租户泄漏。

