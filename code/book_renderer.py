# book_renderer.py — Pure PIL book page renderer (no poppler needed)

import re
import textwrap
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple

# ── Font paths (Liberation Serif = Times New Roman equivalent, always on Ubuntu) ──
FONT_DIR = "/usr/share/fonts/truetype/liberation"
FONT_REGULAR = f"{FONT_DIR}/LiberationSerif-Regular.ttf"
FONT_BOLD    = f"{FONT_DIR}/LiberationSerif-Bold.ttf"
FONT_ITALIC  = f"{FONT_DIR}/LiberationSerif-Italic.ttf"

# ── Page dimensions (A4 at 96 dpi) ───────────────────────────────────────────
PAGE_W    = 794
PAGE_H    = 1123
MARGIN_X  = 82    # left & right margin (px)
MARGIN_T  = 88    # top margin
MARGIN_B  = 80    # bottom margin

# ── Colours ───────────────────────────────────────────────────────────────────
COL_BG      = "#faf8f3"   # warm cream
COL_TEXT    = "#1a1810"   # near-black
COL_MUTED   = "#8a8070"   # warm grey
COL_RULE    = "#d4c9b0"   # rule lines

BODY_SIZE    = 17
CHAPTER_SIZE = 24
HEADER_SIZE  = 13
LINE_H       = 30          # body line height (px)


def _load_fonts():
    try:
        body    = ImageFont.truetype(FONT_REGULAR, BODY_SIZE)
        bold    = ImageFont.truetype(FONT_BOLD,    CHAPTER_SIZE)
        italic  = ImageFont.truetype(FONT_ITALIC,  HEADER_SIZE)
        header  = ImageFont.truetype(FONT_REGULAR, HEADER_SIZE)
        return body, bold, italic, header
    except Exception:
        fb = ImageFont.load_default(size=BODY_SIZE)
        return fb, fb, fb, fb


def _is_chapter_heading(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    patterns = [
        r"^(CHAPTER|Chapter|PART|Part|BOOK|Book|SECTION|Section)\s+[IVXLC\d]",
        r"^(CHAPTER|PART|BOOK|SECTION)\s+[A-Z]",
        r"^[IVX]+\.$",
        r"^\d+\.$",
    ]
    for p in patterns:
        if re.match(p, s):
            return True
    if s.isupper() and 2 <= len(s.split()) <= 6 and len(s) > 3:
        return True
    return False


def _text_width(draw: ImageDraw.Draw, text: str, font) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _wrap_paragraph(draw: ImageDraw.Draw, text: str, font,
                    max_width: int) -> List[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    if not words:
        return []
    lines = []
    current = []
    for word in words:
        test = " ".join(current + [word])
        if _text_width(draw, test, font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _draw_justified_line(draw: ImageDraw.Draw, line: str, x: int, y: int,
                          font, max_width: int, color: str,
                          is_last: bool = False):
    """Draw a single line with full justification (except last line)."""
    words = line.split()
    if not words:
        return
    if is_last or len(words) == 1:
        draw.text((x, y), line, font=font, fill=color)
        return

    total_text_w = sum(_text_width(draw, w, font) for w in words)
    total_gap    = max_width - total_text_w
    gap          = total_gap / (len(words) - 1)
    cx = x
    for i, word in enumerate(words):
        draw.text((int(cx), y), word, font=font, fill=color)
        cx += _text_width(draw, word, font) + gap


def render_page(paragraphs: List[str], title: str, author: str,
                page_num: int) -> Image.Image:
    """
    Render a list of paragraph strings onto a single A4-like PIL image.
    Returns the image.  Remaining paragraphs that didn't fit are NOT returned
    (caller must track position).
    """
    img  = Image.new("RGB", (PAGE_W, PAGE_H), color=COL_BG)
    draw = ImageDraw.Draw(img)
    body_font, chapter_font, italic_font, header_font = _load_fonts()

    text_w = PAGE_W - 2 * MARGIN_X

    # ── Header ────────────────────────────────────────────────────────────────
    hy = MARGIN_T - 34
    draw.line([(MARGIN_X, hy + 20), (PAGE_W - MARGIN_X, hy + 20)],
              fill=COL_RULE, width=1)
    draw.text((MARGIN_X, hy), author[:38], font=italic_font, fill=COL_MUTED)
    tr = title[:38]
    tw = _text_width(draw, tr, italic_font)
    draw.text((PAGE_W - MARGIN_X - tw, hy), tr, font=italic_font, fill=COL_MUTED)

    # ── Body ──────────────────────────────────────────────────────────────────
    y = MARGIN_T

    for para in paragraphs:
        para = para.strip()
        if not para:
            y += LINE_H // 2
            continue

        if _is_chapter_heading(para):
            # Decorative rule above
            y += 18
            rule_x1 = MARGIN_X + int(text_w * 0.2)
            rule_x2 = PAGE_W - MARGIN_X - int(text_w * 0.2)
            draw.line([(rule_x1, y), (rule_x2, y)], fill=COL_RULE, width=1)
            y += 14
            # Centred bold chapter text
            cw = _text_width(draw, para, chapter_font)
            draw.text(((PAGE_W - cw) // 2, y), para, font=chapter_font, fill=COL_TEXT)
            y += 34
            draw.line([(rule_x1, y), (rule_x2, y)], fill=COL_RULE, width=1)
            y += 20
        else:
            # First-line indent
            indent = 22
            lines  = _wrap_paragraph(draw, para, body_font, text_w - indent)
            if not lines:
                continue
            for i, line in enumerate(lines):
                if y + LINE_H > PAGE_H - MARGIN_B - 20:
                    break   # page full — stop (caller handles overflow)
                x = MARGIN_X + (indent if i == 0 else 0)
                lw = text_w - (indent if i == 0 else 0)
                is_last = (i == len(lines) - 1)
                _draw_justified_line(draw, line, x, y, body_font, lw,
                                     COL_TEXT, is_last=is_last)
                y += LINE_H
            y += 8   # paragraph spacing

    # ── Footer ────────────────────────────────────────────────────────────────
    fy = PAGE_H - MARGIN_B
    draw.line([(MARGIN_X, fy - 10), (PAGE_W - MARGIN_X, fy - 10)],
              fill=COL_RULE, width=1)
    pn = str(page_num)
    pw = _text_width(draw, pn, header_font)
    draw.text(((PAGE_W - pw) // 2, fy - 4), pn, font=header_font, fill=COL_MUTED)

    return img


def _split_into_paragraphs(text: str) -> List[str]:
    """Split book text into paragraphs."""
    return [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]


def _paginate(paragraphs: List[str], font, draw: ImageDraw.Draw,
              text_w: int, page_h: int) -> List[List[str]]:
    """
    Group paragraphs into pages based on how many lines they need.
    Returns list of lists-of-paragraphs (one list per page).
    """
    usable_h   = page_h - MARGIN_T - MARGIN_B - 30
    pages      = []
    cur_page   = []
    cur_h      = 0
    tmp_img    = Image.new("RGB", (PAGE_W, PAGE_H))
    tmp_draw   = ImageDraw.Draw(tmp_img)

    for para in paragraphs:
        para = para.strip()
        if not para:
            needed = LINE_H // 2
        elif _is_chapter_heading(para):
            needed = 18 + 14 + 34 + 20 + 30   # fixed cost of a chapter head
        else:
            wrapped = _wrap_paragraph(tmp_draw, para, font, text_w - 22)
            needed  = len(wrapped) * LINE_H + 8

        if cur_h + needed > usable_h and cur_page:
            pages.append(cur_page)
            cur_page = []
            cur_h    = 0

        cur_page.append(para)
        cur_h += needed

    if cur_page:
        pages.append(cur_page)

    return pages


def get_book_page_images(book_text: str, title: str, author: str,
                         batch_index: int = 0,
                         chars_per_batch: int = 40_000,
                         dpi: int = 130) -> Tuple[List[Image.Image], int]:
    """
    Slice book_text into batches, paginate the current batch, and
    return (list_of_PIL_Images, total_batch_count).
    """
    total_chars   = len(book_text)
    total_batches = max(1, (total_chars + chars_per_batch - 1) // chars_per_batch)
    batch_index   = max(0, min(batch_index, total_batches - 1))

    start     = batch_index * chars_per_batch
    slice_txt = book_text[start: start + chars_per_batch]

    paragraphs = _split_into_paragraphs(slice_txt)

    # Load font for pagination calculation
    try:
        font = ImageFont.truetype(FONT_REGULAR, BODY_SIZE)
    except Exception:
        font = ImageFont.load_default(size=BODY_SIZE)

    pages_of_paragraphs = _paginate(paragraphs, font,
                                     ImageDraw.Draw(Image.new("RGB",(1,1))),
                                     PAGE_W - 2 * MARGIN_X, PAGE_H)

    images = []
    for page_num, page_paras in enumerate(pages_of_paragraphs, start=1):
        img = render_page(page_paras, title, author, page_num)
        images.append(img)

    if not images:
        # fallback blank page
        images = [Image.new("RGB", (PAGE_W, PAGE_H), COL_BG)]

    return images, total_batches