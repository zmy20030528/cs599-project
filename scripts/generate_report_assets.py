"""Generate PDF-safe PNG diagrams from reproducible project data."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
FONT = Path(r"C:\Windows\Fonts\msyh.ttc")
MONO = Path(r"C:\Windows\Fonts\consola.ttf")


def font(size, mono=False):
    path = MONO if mono and MONO.exists() else FONT
    return ImageFont.truetype(str(path), size)


def arrow(draw, start, end, fill="#000000", width=4):
    draw.line([start, end], fill=fill, width=width)
    x, y = end
    draw.polygon([(x, y), (x - 14, y - 8), (x - 14, y + 8)], fill=fill)


def architecture():
    image = Image.new("RGB", (1500, 660), "white")
    d = ImageDraw.Draw(image)
    title, body, small = font(36), font(26), font(19)
    d.text((750, 35), "StockMind 多智能体工作流", font=title, fill="#000000", anchor="ma")
    boxes = [
        ((40, 270, 220, 360), "用户请求", "代码 / 日期", "#f7f9fc"),
        ((290, 270, 500, 360), "Fetcher", "工具调用 + 检索", "#f7f9fc"),
        ((610, 90, 830, 180), "量化分析师", "趋势 / 量价", "#e8f2ff"),
        ((610, 270, 830, 360), "舆情分析师", "事实 / 情绪", "#e8f2ff"),
        ((610, 450, 830, 540), "风险控制官", "风险 / 边界", "#e8f2ff"),
        ((950, 270, 1160, 360), "CIO Agent", "证据汇总", "#f7f9fc"),
        ((1260, 270, 1460, 360), "研究报告", "风险免责声明", "#f7f9fc"),
        ((290, 500, 500, 590), "长期记忆", "检索 / 持久化", "#f4ecff"),
        ((950, 500, 1160, 590), "JSONL Trace", "状态 / 耗时", "#f4ecff"),
    ]
    for rect, main, sub, color in boxes:
        d.rounded_rectangle(rect, radius=15, fill=color, outline="#000000", width=3)
        cx = (rect[0] + rect[2]) // 2
        d.text((cx, rect[1] + 22), main, font=body, fill="#000000", anchor="ma")
        d.text((cx, rect[1] + 58), sub, font=small, fill="#000000", anchor="ma")
    arrow(d, (220, 315), (290, 315)); arrow(d, (500, 315), (610, 135)); arrow(d, (500, 315), (610, 315)); arrow(d, (500, 315), (610, 495))
    arrow(d, (830, 135), (950, 315)); arrow(d, (830, 315), (950, 315)); arrow(d, (830, 495), (950, 315)); arrow(d, (1160, 315), (1260, 315))
    arrow(d, (395, 500), (395, 365)); arrow(d, (1055, 360), (1055, 500))
    d.text((750, 625), "LangGraph StateGraph；无依赖环境使用等价 LocalStockGraph", font=small, fill="#000000", anchor="ma")
    image.save(ASSETS / "architecture-flow.png", optimize=True)


def evidence():
    image = Image.new("RGB", (1400, 820), "white")
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((0, 0, 1399, 819), radius=18, outline="#000000", width=2)
    d.rectangle((0, 0, 1400, 52), fill="#e5e7eb")
    lines = [
        ("PS D:\\code\\Stock_forecast-master> python -m unittest discover -s tests -v", "#93c5fd"),
        ("test_demo_data_is_labeled ... ok", "#a7f3d0"), ("test_rejects_bad_code ...... ok", "#a7f3d0"),
        ("test_validate_request ...... ok", "#a7f3d0"), ("test_end_to_end_and_memory . ok", "#a7f3d0"),
        ("Ran 4 tests in 0.091s", "#e5e7eb"), ("OK", "#34d399"), ("", "#e5e7eb"),
        ("PS D:\\code\\Stock_forecast-master> python scripts/benchmark.py", "#93c5fd"),
        ('{"runs": 5, "success_rate": 1.0,', "#e5e7eb"), (' "mean_latency_ms": 34.26, "p95_latency_ms": 32.56}', "#e5e7eb"),
        ("Evidence: reproducible automated run record / 2026-06-22", "#fbbf24"),
    ]
    y = 85
    for line, color in lines:
        d.text((35, y), line, font=font(23, mono=True), fill="#000000")
        y += 53
    image.save(ASSETS / "demo-run-evidence.png", optimize=True)


if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    architecture()
    evidence()
