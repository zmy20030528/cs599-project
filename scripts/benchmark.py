"""Small reproducible workflow benchmark; run from repository root."""
import json
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import Settings
from src.service import analyze_stock


def main(runs: int = 5) -> None:
    latencies = []
    passed = 0
    for _ in range(runs):
        start = time.perf_counter()
        result = analyze_stock("600519", "20260101", "20260622", Settings.from_env("demo"), prefer_langgraph=False)
        latencies.append((time.perf_counter() - start) * 1000)
        passed += int("不构成投资建议" in result["final_report"] and not result["errors"])
    print(json.dumps({"runs": runs, "success_rate": passed / runs, "mean_latency_ms": round(statistics.mean(latencies), 2),
                      "p95_latency_ms": round(sorted(latencies)[max(0, int(runs * .95) - 1)], 2)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
