#!/usr/bin/env python
"""Backward-compatible CLI entry point."""
from __future__ import annotations

import argparse
import json
import sys

from src.config import Settings
from src.service import analyze_stock


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="A股多智能体投研助手（教学用途）")
    parser.add_argument("--stock-code", default="600519")
    parser.add_argument("--start", default="20260101")
    parser.add_argument("--end", default="20260622")
    parser.add_argument("--mode", choices=("demo", "live"), default=None)
    parser.add_argument("--json", action="store_true", help="输出完整 JSON 状态")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = analyze_stock(args.stock_code, args.start, args.end, Settings.from_env(args.mode))
    except (ValueError, RuntimeError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result["final_report"])
    if result.get("errors"):
        print("\n降级信息：" + "; ".join(result["errors"]), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

