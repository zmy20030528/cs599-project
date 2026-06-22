"""Build the final Chinese PDF with TOC and outline bookmarks, without GUI tools."""
from __future__ import annotations

import io
import re
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "CS599_大作业报告.md"
OUTPUT = ROOT / "docs" / "CS599_大作业报告.pdf"
FONT_PATH = Path(r"C:\Windows\Fonts\msyh.ttc")
BOLD_PATH = Path(r"C:\Windows\Fonts\msyhbd.ttc")
FONT = FontProperties(fname=str(FONT_PATH))
BOLD = FontProperties(fname=str(BOLD_PATH if BOLD_PATH.exists() else FONT_PATH))


def clean_inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.replace("**", "").replace("__", "")
    return re.sub(r"\[([^]]+)]\([^)]+\)", r"\1", text)


def wrap_text(text: str, limit: float = 48) -> list[str]:
    lines, current, width = [], "", 0.0
    for char in text:
        if char == "\n":
            lines.append(current); current, width = "", 0.0; continue
        weight = 0.55 if ord(char) < 128 else 1.0
        if width + weight > limit and current:
            lines.append(current); current, width = "", 0.0
        current += char; width += weight
    if current or not lines:
        lines.append(current)
    return lines


class Renderer:
    def __init__(self, pdf: PdfPages, known_toc=None):
        self.pdf, self.known_toc = pdf, known_toc
        self.fig = None; self.y = 0.0; self.page = 0
        self.headings: list[tuple[int, str, int]] = []

    def new_page(self):
        if self.fig is not None:
            self._footer(); self.pdf.savefig(self.fig, bbox_inches=None); plt.close(self.fig)
        self.page += 1
        self.fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
        self.y = 0.93

    def _footer(self):
        if self.page > 1:
            self.fig.text(.5, .025, f"— {self.page} —", ha="center", fontsize=9, color="#64748b", fontproperties=FONT)

    def ensure(self, height):
        if self.fig is None or self.y - height < .07:
            self.new_page()

    def text(self, text, size=10.5, color="#1f2937", indent=0, leading=1.55, bold=False, align="left"):
        prop = BOLD if bold else FONT
        limit = 48 - indent * 2
        for line in wrap_text(clean_inline(text), limit):
            h = size * leading / 842
            self.ensure(h)
            x = .09 + indent * .025 if align == "left" else .5
            self.fig.text(x, self.y, line, ha=align, va="top", fontsize=size, color=color, fontproperties=prop)
            self.y -= h
        self.y -= .006

    def heading(self, level, title):
        title = re.sub(r"\s*\{[^}]+\}\s*$", "", title).strip()
        if level == 1:
            if self.fig is not None and self.y < .90:
                self.new_page()
            elif self.fig is None:
                self.new_page()
        self.ensure(.08)
        sizes = {1: 20, 2: 15, 3: 12.5}
        self.fig.text(.09, self.y, title, fontsize=sizes.get(level, 11), color="#17365d", fontproperties=BOLD, va="top")
        self.headings.append((level, title, self.page))
        self.y -= {1: .065, 2: .048, 3: .04}.get(level, .035)

    def image(self, relative, caption):
        path = SOURCE.parent / relative
        if path.suffix.lower() != ".png" or not path.exists():
            self.text(f"[{caption}]", color="#64748b", align="center"); return
        with Image.open(path) as im:
            ratio = im.height / im.width
        height = min(.62, .72 * 8.27 / 11.69 * ratio)
        self.ensure(height + .055)
        ax = self.fig.add_axes([.14, self.y - height, .72, height])
        ax.imshow(Image.open(path)); ax.axis("off")
        self.y -= height + .018
        self.text(caption, size=9, color="#475569", align="center", leading=1.25)

    def table(self, rows):
        cols = max(len(r) for r in rows)
        rows = [r + [""] * (cols - len(r)) for r in rows]
        height = min(.42, .045 * len(rows) + .025)
        self.ensure(height + .02)
        ax = self.fig.add_axes([.09, self.y - height, .82, height]); ax.axis("off")
        table = ax.table(cellText=rows, cellLoc="center", loc="center", bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False); table.set_fontsize(8.5)
        for (r, _), cell in table.get_celld().items():
            cell.get_text().set_fontproperties(BOLD if r == 0 else FONT)
            cell.set_facecolor("#dbeafe" if r == 0 else ("#f8fafc" if r % 2 else "white"))
            cell.set_edgecolor("#94a3b8")
        self.y -= height + .025

    def toc(self):
        entries = self.known_toc or []
        for level, title, page in entries:
            if title in {"封面", "目录"} or level > 3: continue
            indent = (level - 1) * 4
            dots = "." * max(4, 48 - indent - len(title))
            self.text(" " * indent + f"{title} {dots} {page}", size=10.5 if level == 1 else 9.5,
                      bold=(level == 1), leading=1.3)

    def finish(self):
        if self.fig is not None:
            self._footer(); self.pdf.savefig(self.fig); plt.close(self.fig); self.fig = None


def render(target, known_toc=None):
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    with PdfPages(target, metadata={"Title": "StockMind CS599 大作业报告", "Author": "张铭洋", "Subject": "CS599"}) as pdf:
        r = Renderer(pdf, known_toc)
        i, paragraph, in_code = 0, [], False

        def flush():
            nonlocal paragraph
            if paragraph:
                r.text("".join(x.strip() for x in paragraph)); paragraph = []

        while i < len(lines):
            line = lines[i]
            if line.startswith("```"):
                flush(); in_code = not in_code; i += 1; continue
            if in_code:
                r.text(line or " ", size=8.5, color="#334155", indent=1, leading=1.25); i += 1; continue
            heading = re.match(r"^(#{1,3})\s+(.+)$", line)
            image = re.match(r"^!\[([^]]*)]\(([^)]+)\)(?:\{[^}]+\})?$", line)
            if heading:
                flush(); r.heading(len(heading.group(1)), heading.group(2)); i += 1; continue
            if image:
                flush(); r.image(image.group(2), image.group(1)); i += 1; continue
            if line.strip() == "[[TOC]]":
                flush(); r.toc(); i += 1; continue
            if line.strip() == "\\newpage":
                flush(); r.new_page(); i += 1; continue
            if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|"):
                flush(); rows = []
                while i < len(lines) and lines[i].startswith("|"):
                    cells = [clean_inline(x.strip()) for x in lines[i].strip().strip("|").split("|")]
                    if not all(re.fullmatch(r":?-+:?", x.replace(" ", "")) for x in cells): rows.append(cells)
                    i += 1
                r.table(rows); continue
            if line.startswith(">"):
                flush(); r.text(line.lstrip("> "), color="#7c2d12", indent=1); i += 1; continue
            if re.match(r"^[-*]\s+", line):
                flush(); r.text("• " + re.sub(r"^[-*]\s+", "", line), indent=1); i += 1; continue
            if not line.strip():
                flush(); i += 1; continue
            paragraph.append(line); i += 1
        flush(); r.finish()
        return r.headings


def add_outlines(path: Path, headings):
    data = path.read_bytes()
    start = int(re.search(rb"startxref\s+(\d+)", data[-2048:]).group(1))
    trailer = data[start:]
    size = int(re.search(rb"/Size\s+(\d+)", trailer).group(1))
    pages = [int(x) for x in re.findall(rb"(\d+) 0 obj\s*<<[^>]*?/Type\s*/Page(?!s)", data, re.S)]
    entries = [(l, t, p) for l, t, p in headings if l == 1 and t not in {"封面", "目录"}]
    if not pages or not entries: return
    outline_root = size
    item_ids = list(range(size + 1, size + 1 + len(entries)))
    objects = {}
    objects[1] = f"<< /Type /Catalog /Pages 2 0 R /Outlines {outline_root} 0 R /PageMode /UseOutlines >>".encode()
    objects[outline_root] = f"<< /Type /Outlines /First {item_ids[0]} 0 R /Last {item_ids[-1]} 0 R /Count {len(item_ids)} >>".encode()
    for idx, ((_, title, page), oid) in enumerate(zip(entries, item_ids)):
        title_hex = (b"\xfe\xff" + title.encode("utf-16-be")).hex().upper()
        prev = f" /Prev {item_ids[idx-1]} 0 R" if idx else ""
        nxt = f" /Next {item_ids[idx+1]} 0 R" if idx + 1 < len(item_ids) else ""
        page_obj = pages[min(max(page - 1, 0), len(pages) - 1)]
        objects[oid] = f"<< /Title <{title_hex}> /Parent {outline_root} 0 R /Dest [{page_obj} 0 R /Fit]{prev}{nxt} >>".encode()
    append = bytearray(b"\n")
    offsets = {}
    for oid in sorted(objects):
        offsets[oid] = len(data) + len(append)
        append += f"{oid} 0 obj\n".encode() + objects[oid] + b"\nendobj\n"
    xref_pos = len(data) + len(append)
    append += b"xref\n"
    for oid in sorted(objects):
        append += f"{oid} 1\n{offsets[oid]:010d} 00000 n \n".encode()
    new_size = max(objects) + 1
    append += f"trailer\n<< /Size {new_size} /Root 1 0 R /Prev {start} >>\nstartxref\n{xref_pos}\n%%EOF\n".encode()
    path.write_bytes(data + append)


if __name__ == "__main__":
    scratch = io.BytesIO()
    first = render(scratch)
    headings = render(OUTPUT, first)
    add_outlines(OUTPUT, headings)
    print(f"Generated: {OUTPUT} ({OUTPUT.stat().st_size} bytes)")
