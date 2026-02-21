# ui.py — Bright mode, AskYourPDF-style layout (fully fixed)

import streamlit as st
import os
from books import books, genres
from gutenberg_search import search_gutenberg

# ── Cover colour palette (cycles through books) ─────────────────────────────
COVER_COLORS = [
    "linear-gradient(135deg,#2d6a4f,#40916c)",
    "linear-gradient(135deg,#7b2d8b,#a855c8)",
    "linear-gradient(135deg,#c8622a,#e07b3a)",
    "linear-gradient(135deg,#1a1a2e,#16213e)",
    "linear-gradient(135deg,#b5432a,#d45f3c)",
    "linear-gradient(135deg,#2c5f8a,#3a7abd)",
    "linear-gradient(135deg,#4a4a6a,#6b6b9a)",
    "linear-gradient(135deg,#5a3e2b,#7a5c3f)",
    "linear-gradient(135deg,#1d4e89,#2176ae)",
    "linear-gradient(135deg,#6b2737,#a33b4f)",
]

def _bg(i: int) -> str:
    return COVER_COLORS[i % len(COVER_COLORS)]

def _book_idx(book: dict) -> int:
    title = (book or {}).get("title", "")
    for i, b in enumerate(books):
        if b.get("title") == title:
            return i
    return 0


# ─── CSS LOADER ──────────────────────────────────────────────────────────────

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

def sidebar_ui(get_pdf_text, get_text_chunks, get_vector_store):
    with st.sidebar:

        # Logo
        st.markdown("""
        <div style="padding:20px 20px 14px;border-bottom:1px solid rgba(26,26,46,0.08);margin-bottom:4px;">
            <div style="display:flex;align-items:center;gap:10px;">
                <div style="width:34px;height:34px;background:#1a1a2e;border-radius:9px;
                            display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0;">📚</div>
                <div>
                    <div style="font-family:'Lora',serif;font-weight:700;font-size:15px;color:#1a1a2e;letter-spacing:-0.01em;">BookChat</div>
                    <div style="font-size:10px;color:#9d9aaa;font-weight:500;">AI Literature Assistant</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        page = st.session_state.get("page", "library")

        # Nav buttons
        for key, icon, label in [
            ("library", "📖", "Books Library"),
            ("search",  "🔍", "Search Gutenberg"),
            ("upload",  "📄", "Upload PDF"),
        ]:
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.rerun()

        st.markdown("---")

        # Now Reading
        ab = st.session_state.get("active_book")
        if ab:
            bg    = _bg(_book_idx(ab))
            title = ab.get("title","")
            auth  = ab.get("author","")
            st.markdown(f"""
            <div style="background:#f7f5f0;border:1px solid rgba(26,26,46,0.08);
                        border-radius:12px;padding:12px 14px;margin-bottom:10px;">
                <div style="font-size:10px;color:#9d9aaa;font-weight:700;letter-spacing:0.08em;
                            text-transform:uppercase;margin-bottom:6px;">Now Reading</div>
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="width:30px;height:42px;border-radius:4px;background:{bg};flex-shrink:0;"></div>
                    <div>
                        <div style="font-size:13px;font-weight:700;color:#1a1a2e;font-family:'Lora',serif;line-height:1.3;">
                            {title[:24]}{'…' if len(title)>24 else ''}</div>
                        <div style="font-size:11px;color:#6b6880;margin-top:2px;">{auth}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("💬 Open Reader", use_container_width=True, key="sb_open_reader"):
                st.session_state.page = "reader"
                st.rerun()

        # Upload section
        if page == "upload":
            st.markdown("**📂 Upload PDF**")
            pdf_docs = st.file_uploader("Drop PDFs", type=["pdf"],
                                         accept_multiple_files=True,
                                         label_visibility="collapsed")
            if pdf_docs:
                for pdf in pdf_docs:
                    kb = round(pdf.size/1024, 1)
                    st.markdown(f"""
                    <div class="sidebar-stat">
                        <div class="icon">📄</div>
                        <div><div class="label">File</div>
                        <div class="value">{pdf.name[:16]}{"…" if len(pdf.name)>16 else ""}</div></div>
                        <div style="margin-left:auto;font-size:11px;color:#9d9aaa;">{kb} KB</div>
                    </div>""", unsafe_allow_html=True)

            if st.button("⚡ Process PDF", use_container_width=True, key="proc_pdf"):
                if not pdf_docs:
                    st.warning("Upload at least one PDF first.")
                else:
                    with st.spinner("Processing…"):
                        try:
                            raw    = get_pdf_text(pdf_docs)
                            chunks = get_text_chunks(raw)
                            get_vector_store(chunks)
                            st.session_state.active_book = {
                                "title": pdf_docs[0].name,
                                "author": "Your Document",
                                "emoji": "📄", "genre": "Document", "url": None,
                            }
                            st.session_state.chat_history = []
                            st.session_state.page = "reader"
                            st.success("✅ Done!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {e}")

        st.markdown("---")

        if st.session_state.get("chat_history"):
            if st.button("🗑️ Clear Chat", use_container_width=True, key="clr_chat"):
                st.session_state.chat_history = []
                st.rerun()

        if os.path.exists("faiss_index"):
            if st.button("🔄 Reset Index", use_container_width=True, key="rst_idx"):
                import shutil
                shutil.rmtree("faiss_index", ignore_errors=True)
                st.session_state.active_book  = None
                st.session_state.chat_history = []
                st.session_state.page = "library"
                st.rerun()

        st.markdown("""
        <div style="padding:14px 4px 4px;text-align:center;">
            <div style="font-size:10px;color:#9d9aaa;line-height:2;">
                Powered by <b style="color:#c8622a;">Gemini</b> · <b style="color:#c8622a;">LangChain</b><br>
                Books from <b style="color:#c8622a;">Project Gutenberg</b>
            </div>
        </div>""", unsafe_allow_html=True)


# ─── LIBRARY PAGE ─────────────────────────────────────────────────────────────

def library_page(load_book_function):
    # ── Top search + filter bar ──
    st.markdown("""
    <div style="padding:28px 0 16px;">
        <div style="font-family:'Lora',serif;font-size:26px;font-weight:700;
                    color:#1a1a2e;letter-spacing:-0.02em;margin-bottom:4px;">Books</div>
        <div style="font-size:13px;color:#6b6880;">
            Engage in interactive conversations with popular books</div>
    </div>""", unsafe_allow_html=True)

    # Search bar + tab buttons in the same row
    src_col, tab_col = st.columns([2, 1])
    with src_col:
        search_q = st.text_input("Search library", placeholder="🔍  Search...",
                                  label_visibility="collapsed", key="lib_search")
    with tab_col:
        view_mode = st.radio("View", ["Books", "Authors", "Genre"],
                              horizontal=True, label_visibility="collapsed",
                              key="lib_view")

    st.markdown("<hr style='margin:8px 0 20px;border-color:rgba(26,26,46,0.08);'>", unsafe_allow_html=True)

    # Apply filters
    filtered = books

    if search_q:
        q = search_q.lower()
        filtered = [b for b in filtered if
                    q in b["title"].lower() or q in b["author"].lower()]

    if view_mode == "Authors":
        authors = sorted(set(b["author"] for b in filtered))
        sel = st.selectbox("Author", authors, label_visibility="collapsed", key="auth_sel")
        filtered = [b for b in filtered if b["author"] == sel]

    elif view_mode == "Genre":
        sel = st.selectbox("Genre", genres, label_visibility="collapsed", key="genre_sel")
        filtered = [b for b in filtered if b["genre"] == sel]

    if not filtered:
        st.markdown('<p style="color:#9d9aaa;font-size:14px;padding:20px 0;">No books found.</p>',
                    unsafe_allow_html=True)
        return

    _render_askyourpdf_grid(filtered, load_book_function)


def _render_askyourpdf_grid(book_list: list, load_book_function):
    """
    Two-column grid exactly like AskYourPDF:
    [book cover thumbnail] [title + author + Chat button]
    """
    left_col, right_col = st.columns(2, gap="large")

    for i, book in enumerate(book_list):
        with (left_col if i % 2 == 0 else right_col):
            _render_askyourpdf_card(book, i, load_book_function)


def _render_askyourpdf_card(book: dict, idx: int, load_book_function):
    """
    Exact AskYourPDF card layout:
    ┌──────────┬────────────────────────────────┐
    │  Cover   │  Title (large)                 │
    │  thumb   │  Author · Year                 │
    │          │  [💬 Chat with this Book]       │
    └──────────┴────────────────────────────────┘
    """
    bg        = _bg(idx)
    is_active = (st.session_state.get("active_book") or {}).get("title") == book["title"]
    emoji     = book.get("emoji", "📖")
    title     = book["title"]
    author    = book.get("author", "")
    year      = book.get("year", "")
    desc      = book.get("description", "")

    # Cover: mini Gutenberg-style colourful thumbnail
    cover_html = f"""
    <div style="width:90px;height:120px;border-radius:6px;flex-shrink:0;
                background:{bg};display:flex;flex-direction:column;
                align-items:center;justify-content:flex-end;
                box-shadow:2px 4px 12px rgba(0,0,0,0.18);overflow:hidden;position:relative;">
        <!-- geometric pattern like Gutenberg covers -->
        <div style="position:absolute;inset:0;opacity:0.25;">
            <div style="width:60px;height:60px;border:8px solid rgba(255,255,255,0.6);
                        border-radius:50%;position:absolute;top:-10px;left:-10px;"></div>
            <div style="width:40px;height:40px;background:rgba(255,255,255,0.3);
                        transform:rotate(45deg);position:absolute;top:20px;right:-10px;"></div>
            <div style="width:70px;height:4px;background:rgba(255,255,255,0.5);
                        position:absolute;bottom:28px;left:0;"></div>
        </div>
        <!-- title on cover bottom -->
        <div style="position:relative;z-index:1;padding:6px 6px 4px;width:100%;
                    background:rgba(0,0,0,0.22);">
            <div style="font-size:8px;font-weight:700;color:rgba(255,255,255,0.9);
                        line-height:1.2;text-align:center;font-family:'Lora',serif;">
                {title[:22]}{'…' if len(title)>22 else ''}
            </div>
            <div style="font-size:7px;color:rgba(255,255,255,0.65);text-align:center;margin-top:1px;">
                {author.split(',')[0][:18]}
            </div>
        </div>
    </div>"""

    # Right side info
    border_c = "rgba(200,98,42,0.3)" if is_active else "rgba(26,26,46,0.07)"
    bg_card  = "rgba(200,98,42,0.02)" if is_active else "#ffffff"

    st.markdown(f"""
    <div style="display:flex;align-items:flex-start;gap:18px;
                background:{bg_card};border:1px solid {border_c};
                border-radius:14px;padding:18px;margin-bottom:6px;
                box-shadow:0 1px 4px rgba(26,26,46,0.05);">
        {cover_html}
        <div style="flex:1;min-width:0;padding-top:4px;">
            <div style="font-family:'Lora',serif;font-size:17px;font-weight:700;
                        color:#1a1a2e;line-height:1.25;margin-bottom:5px;">
                {title}</div>
            <div style="font-size:13px;color:#6b6880;margin-bottom:14px;">
                {author} · {year}</div>
            <div style="font-size:12px;color:#9d9aaa;line-height:1.45;margin-bottom:4px;">
                {desc[:90]}{'…' if len(desc)>90 else ''}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Button below (full width, matching AskYourPDF black button style)
    key   = f"card_{idx}_{title.replace(' ','_')[:18]}"
    label = "✅ Open Reader →" if is_active else "💬 Chat with this Book"

    if st.button(label, key=key, use_container_width=True):
        if is_active:
            st.session_state.page = "reader"
            st.rerun()
        else:
            with st.spinner(f"📥 Loading {title}…"):
                try:
                    load_book_function(book["url"])
                    st.session_state.active_book  = book
                    st.session_state.chat_history = []
                    st.session_state.page = "reader"
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# ─── SEARCH PAGE ─────────────────────────────────────────────────────────────

def search_page(load_book_function):
    st.markdown("""
    <div style="padding:28px 0 16px;">
        <div style="font-family:'Lora',serif;font-size:26px;font-weight:700;
                    color:#1a1a2e;letter-spacing:-0.02em;margin-bottom:4px;">
            Search Gutenberg</div>
        <div style="font-size:13px;color:#6b6880;">
            Search 70,000+ free public domain books and load any instantly</div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([5, 1])
    with c1:
        q = st.text_input("Query", placeholder="Search by title, author, or topic…",
                           label_visibility="collapsed", key="gut_q")
    with c2:
        go = st.button("Search", use_container_width=True, key="gut_go")

    if q and go:
        with st.spinner("Searching Project Gutenberg…"):
            results = search_gutenberg(q, max_results=6)

        if not results:
            st.markdown(
                '<div style="padding:32px;color:#9d9aaa;font-size:14px;text-align:center;">'
                'No results. Try a different search.</div>', unsafe_allow_html=True)
            return

        st.markdown(f'<p style="font-size:12px;color:#9d9aaa;margin:8px 0 16px;">'
                    f'{len(results)} results</p>', unsafe_allow_html=True)
        _render_askyourpdf_grid(results, load_book_function)


# ─── SPLIT-SCREEN READER ─────────────────────────────────────────────────────

def reader_page(ask_question_fn):
    book    = st.session_state.get("active_book") or {}
    history = st.session_state.get("chat_history", [])

    # Guard: no book
    if not book:
        st.markdown("""
        <div style="text-align:center;padding:80px 24px;">
            <div style="font-size:48px;margin-bottom:16px;">📖</div>
            <div style="font-size:16px;color:#6b6880;margin-bottom:6px;">No book loaded yet.</div>
            <div style="font-size:13px;color:#9d9aaa;">
                Go to Books Library and click "Chat with this Book".</div>
        </div>""", unsafe_allow_html=True)
        if st.button("← Back to Library", key="no_book_back"):
            st.session_state.page = "library"
            st.rerun()
        return

    # Guard: index missing
    if not os.path.exists("faiss_index"):
        st.warning("⚠️ Book index was cleared. Please reload the book from the library.")
        if st.button("← Back to Library", key="no_idx_back"):
            st.session_state.page = "library"
            st.rerun()
        return

    title  = book.get("title", "")
    author = book.get("author", "")
    emoji  = book.get("emoji", "📖")
    idx    = _book_idx(book)
    bg     = _bg(idx)

    # ── Fire suggested question stored from last rerun ──
    if "_fire_q" in st.session_state:
        q = st.session_state["_fire_q"]
        del st.session_state["_fire_q"]
        with st.spinner("Thinking…"):
            ans = ask_question_fn(q)
        # history is saved inside ask_question_fn; just rerun to render
        st.rerun()

    # ════════════════════════════════
    # SPLIT: chat LEFT  |  viewer RIGHT
    # ════════════════════════════════
    left_col, right_col = st.columns([1, 1], gap="medium")

    # ━━━━━━━━━━━━━━ LEFT: CHAT ━━━━━━━━━━━━━━
    with left_col:

        # Panel header
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid rgba(26,26,46,0.08);
                    border-radius:14px 14px 0 0;padding:14px 18px;
                    display:flex;align-items:center;gap:12px;">
            <div style="width:36px;height:36px;border-radius:8px;background:{bg};
                        display:flex;align-items:center;justify-content:center;
                        font-size:18px;flex-shrink:0;">{emoji}</div>
            <div style="flex:1;min-width:0;">
                <div style="font-family:'Lora',serif;font-size:14px;font-weight:700;
                            color:#1a1a2e;line-height:1.2;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                    {title[:44]}{'…' if len(title)>44 else ''}</div>
                <div style="font-size:11px;color:#9d9aaa;">{author}</div>
            </div>
            <div style="flex-shrink:0;">
                <div style="background:rgba(34,139,75,0.1);border:1px solid rgba(34,139,75,0.25);
                            border-radius:99px;padding:3px 10px;font-size:10px;font-weight:700;
                            color:#228b4b;letter-spacing:0.04em;white-space:nowrap;">● LOADED</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Suggested questions (only before first message)
        if not history:
            suggestions = [
                f"What is the main purpose of {title}?",
                "Who are the main characters?",
                "What are the major themes?",
                "Summarize the opening chapter.",
                "When and where is this story set?",
            ]
            st.markdown(f"""
            <div style="background:#faf9f7;border:1px solid rgba(26,26,46,0.06);
                        border-top:none;padding:14px 16px 8px;">
                <div style="font-size:12px;font-weight:600;color:#4a4a6a;margin-bottom:10px;">
                    5 questions you could ask based on this context</div>
            </div>""", unsafe_allow_html=True)

            for num, q in enumerate(suggestions, 1):
                btn_key = f"sq_{num}_{title[:10].replace(' ','_')}"
                if st.button(f"{num}. {q}", key=btn_key, use_container_width=True):
                    st.session_state["_fire_q"] = q
                    st.rerun()

            st.markdown("""
            <div style="background:#faf9f7;border:1px solid rgba(26,26,46,0.06);
                        border-top:none;padding:10px 16px 14px;">
                <div style="font-size:12px;color:#9d9aaa;">
                    Ask me a question about the document whenever you're ready.</div>
            </div>""", unsafe_allow_html=True)

        # Full chat history
        if history:
            past = history[:-2] if len(history) >= 2 else []
            if past:
                st.markdown("""
                <div style="padding:10px 0 4px;">
                    <div style="font-size:10px;font-weight:700;color:#9d9aaa;
                                letter-spacing:0.1em;text-transform:uppercase;
                                border-top:1px solid rgba(26,26,46,0.07);
                                padding-top:10px;margin-bottom:6px;">
                        Earlier in this conversation</div>
                </div>""", unsafe_allow_html=True)
                for role, msg in past:
                    with st.chat_message("user" if role=="User" else "assistant"):
                        st.write(msg)

            # Most recent exchange
            if len(history) >= 2:
                with st.chat_message("user"):
                    st.write(history[-2][1])
                with st.chat_message("assistant"):
                    st.write(history[-1][1])

        # Chat input
        question = st.chat_input("Ask a question or Use @ to mention a document…")
        if question and question.strip():
            with st.chat_message("user"):
                st.write(question)
            with st.spinner("Thinking…"):
                ans = ask_question_fn(question)
            with st.chat_message("assistant"):
                st.write(ans)
            st.rerun()

    # ━━━━━━━━━━━━━━ RIGHT: BOOK VIEWER ━━━━━━━━━━━━━━
    with right_col:
        _render_book_viewer(book, bg, title, author, emoji)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("← Back to Library", key="back_reader", use_container_width=True):
            st.session_state.page = "library"
            st.rerun()


def _generate_pdf_bytes(book_text: str, title: str, author: str) -> bytes:
    """Typeset the full book into a downloadable PDF using reportlab."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.colors import HexColor
    import re as _re

    TEXT_COLOR  = HexColor("#1a1810")
    MUTED_COLOR = HexColor("#8a8070")
    RULE_COLOR  = HexColor("#d4c9b0")
    PW, PH = A4
    ML = MR = 2.6 * cm
    MT = MB = 2.8 * cm

    body_s = ParagraphStyle("B", fontName="Times-Roman", fontSize=11.5,
                             leading=21, alignment=TA_JUSTIFY,
                             textColor=TEXT_COLOR, firstLineIndent=20)
    chap_s = ParagraphStyle("C", fontName="Times-Bold", fontSize=16,
                             leading=26, alignment=TA_CENTER,
                             textColor=TEXT_COLOR, spaceBefore=20, spaceAfter=8)

    def _esc(t):
        return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

    def _is_heading(s):
        s = s.strip()
        if _re.match(r"^(CHAPTER|Chapter|PART|Part|BOOK|Book|SECTION|Section)\s+[IVXLC\d]", s):
            return True
        if s.isupper() and 2 <= len(s.split()) <= 6 and len(s) > 3:
            return True
        return False

    def _on_page(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(RULE_COLOR); canvas.setLineWidth(0.5)
        canvas.line(ML, PH-MT+8, PW-MR, PH-MT+8)
        canvas.setFont("Times-Italic", 8); canvas.setFillColor(MUTED_COLOR)
        canvas.drawString(ML, PH-MT+12, author[:40])
        canvas.drawRightString(PW-MR, PH-MT+12, title[:40])
        canvas.line(ML, MB-8, PW-MR, MB-8)
        canvas.setFont("Times-Roman", 8)
        canvas.drawCentredString(PW/2, MB-16, str(doc.page))
        canvas.restoreState()

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=ML, rightMargin=MR,
                             topMargin=MT+0.3*cm, bottomMargin=MB+0.3*cm)
    story = []
    for para in _re.split(r"\n{2,}", book_text):
        lines = [l.strip() for l in para.split("\n") if l.strip()]
        if not lines:
            story.append(Spacer(1, 8)); continue
        first = lines[0]
        if _is_heading(first):
            story.append(Spacer(1, 14))
            story.append(HRFlowable(width="60%", thickness=0.5,
                                     color=RULE_COLOR, spaceAfter=8))
            story.append(Paragraph(_esc(first), chap_s))
            story.append(HRFlowable(width="60%", thickness=0.5,
                                     color=RULE_COLOR, spaceBefore=4, spaceAfter=14))
            for l in lines[1:]:
                if l: story.append(Paragraph(_esc(l), body_s))
        else:
            combined = " ".join(lines)
            if combined:
                story.append(Paragraph(_esc(combined), body_s))
                story.append(Spacer(1, 4))
    if not story:
        story.append(Paragraph("No content.", body_s))
    doc.build(story, onFirstPage=_on_page, onLaterPages=_on_page)
    return buf.getvalue()


def _render_book_viewer(book: dict, bg: str, title: str, author: str, emoji: str):
    """Right panel: continuous scrolling book reader — all pages stacked vertically."""
    import re as _re
    import base64
    from io import BytesIO

    url = book.get("url", "")

    # ── State key for which batch (section) we're in ─────────────────────────
    batch_key = f"book_batch_{title[:20].replace(' ','_')}"
    if batch_key not in st.session_state:
        st.session_state[batch_key] = 0

    # ── Load book text from disk ─────────────────────────────────────────────
    book_text = None
    try:
        from book_loader import get_book_text_by_url, get_book_text
        if url:
            book_text = get_book_text_by_url(url, max_chars=None)
        if not book_text and url:
            ids = _re.findall(r"\d+", url)
            if ids:
                book_text = get_book_text(ids[0])
    except Exception:
        pass

    CHARS_PER_BATCH = 40_000

    # ── Toolbar ──────────────────────────────────────────────────────────────
    batch_idx     = st.session_state[batch_key]
    total_batches = max(1, (len(book_text) + CHARS_PER_BATCH - 1) // CHARS_PER_BATCH) if book_text else 1
    pct           = int(100 * batch_idx / max(1, total_batches - 1)) if total_batches > 1 else 0

    st.markdown(f"""
    <div style="background:#f0ede6;border:1px solid rgba(26,26,46,0.10);
                border-radius:14px 14px 0 0;padding:10px 20px;
                display:flex;align-items:center;justify-content:space-between;gap:12px;">
        <div style="font-size:12px;color:#6b6880;font-weight:600;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:55%;">
            📖&nbsp; {title[:50]}</div>
        <div style="flex:1;height:4px;background:#ddd8ce;border-radius:99px;min-width:40px;">
            <div style="height:4px;width:{pct}%;background:#c8622a;
                        border-radius:99px;transition:width 0.4s;"></div>
        </div>
        <div style="font-size:11px;color:#9d9aaa;white-space:nowrap;flex-shrink:0;">
            §&thinsp;{batch_idx + 1}&thinsp;/&thinsp;{total_batches}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Download bar (shown whenever book text is available) ─────────────────
    if book_text:
        safe_title = title.replace(" ", "_").replace("/", "-")[:40]
        word_count = len(book_text.split())

        dl_txt_col, dl_pdf_col, dl_info_col = st.columns([1, 1, 2])

        with dl_txt_col:
            st.download_button(
                label="📥 Download TXT",
                data=book_text.encode("utf-8"),
                file_name=f"{safe_title}.txt",
                mime="text/plain",
                use_container_width=True,
                key=f"dl_txt_{safe_title}",
                help="Download the plain-text version of this book",
            )

        with dl_pdf_col:
            # Build and cache the PDF so reruns don't re-generate it
            pdf_cache_key = f"_pdf_bytes_{safe_title}"
            if pdf_cache_key not in st.session_state:
                with st.spinner("Building PDF…"):
                    try:
                        st.session_state[pdf_cache_key] = _generate_pdf_bytes(
                            book_text, title, author
                        )
                    except Exception:
                        st.session_state[pdf_cache_key] = None

            pdf_bytes = st.session_state.get(pdf_cache_key)
            if pdf_bytes:
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"{safe_title}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"dl_pdf_{safe_title}",
                    help="Download a typeset PDF of this book",
                )
            else:
                st.button("📥 PDF unavailable", disabled=True,
                          use_container_width=True,
                          key=f"dl_pdf_err_{safe_title}")

        with dl_info_col:
            st.markdown(
                f"<div style='padding:8px 4px;font-size:11px;color:#9d9aaa;'>"
                f"<b style='color:#6b6880;'>~{word_count:,}</b> words &nbsp;·&nbsp; "
                f"<b style='color:#6b6880;'>~{word_count // 200}</b> min read"
                f"</div>",
                unsafe_allow_html=True,
            )
        # ── Render all pages for current batch ───────────────────────────────
        with st.spinner("📄 Rendering pages…"):
            try:
                from book_renderer import get_book_page_images
                images, total_batches = get_book_page_images(
                    book_text, title, author,
                    batch_index=batch_idx,
                    chars_per_batch=CHARS_PER_BATCH,
                    dpi=120,
                )
            except Exception as e:
                st.error(f"Page render error: {e}")
                return

        # ── Render pages via components.html (st.markdown strips base64 src) ──
        import streamlit.components.v1 as components

        pages_html = ""
        for img in images:
            buf = BytesIO()
            img.save(buf, format="PNG", optimize=True)
            b64 = base64.b64encode(buf.getvalue()).decode()
            pages_html += (
                "<div style='margin:0 auto 18px auto;max-width:100%;"
                "box-shadow:0 4px 20px rgba(0,0,0,0.22),-2px 0 6px rgba(0,0,0,0.06);"
                "border-radius:2px;overflow:hidden;border:1px solid #ccc5b0;background:#faf8f3;'>"
                f"<img src='data:image/png;base64,{b64}' style='width:100%;display:block;'/></div>"
            )

        # components.html renders in an iframe — base64 images work correctly here
        scrollable = (
            "<!DOCTYPE html><html><body style='margin:0;padding:0;background:#d6d0c4;'>"
            "<div style='background:#d6d0c4;padding:16px 10px 10px;height:660px;"
            "overflow-y:scroll;overflow-x:hidden;scroll-behavior:smooth;box-sizing:border-box;'>"
            + pages_html +
            "</div></body></html>"
        )
        components.html(scrollable, height=680, scrolling=False)

        # ── Section navigation bar ────────────────────────────────────────────
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        nav_l, nav_c, nav_r = st.columns([1, 2, 1])

        with nav_l:
            if batch_idx > 0:
                if st.button("← Earlier", key=f"batch_prev_{batch_idx}",
                             use_container_width=True):
                    st.session_state[batch_key] -= 1
                    st.rerun()

        with nav_c:
            total_pages_approx = len(images)
            st.markdown(f"""
            <div style="text-align:center;padding:5px 0;font-size:12px;color:#6b6880;">
                <b style="color:#1a1a2e;">{total_pages_approx} pages</b>
                &nbsp;·&nbsp; Section {batch_idx + 1} of {total_batches}
                &nbsp;·&nbsp; ~{int(100*(batch_idx*CHARS_PER_BATCH)/max(1,len(book_text)))}% read
            </div>""", unsafe_allow_html=True)

        with nav_r:
            if batch_idx < total_batches - 1:
                if st.button("Later →", key=f"batch_next_{batch_idx}",
                             use_container_width=True):
                    st.session_state[batch_key] += 1
                    st.rerun()

    else:
        # ── Fallback cover view ───────────────────────────────────────────────
        year  = book.get("year", "")
        genre = book.get("genre", "")
        desc  = book.get("description", "")

        cover_html = f"""
        <div style="width:140px;height:190px;border-radius:8px;margin:0 auto 20px;
                    background:{bg};display:flex;flex-direction:column;
                    align-items:center;justify-content:flex-end;
                    box-shadow:5px 8px 28px rgba(0,0,0,0.22);overflow:hidden;position:relative;">
            <div style="position:absolute;inset:0;">
                <div style="width:90px;height:90px;border:12px solid rgba(255,255,255,0.18);
                            border-radius:50%;position:absolute;top:-20px;left:-15px;"></div>
                <div style="width:65px;height:65px;background:rgba(255,255,255,0.1);
                            transform:rotate(45deg);position:absolute;top:30px;right:-15px;"></div>
            </div>
            <div style="position:relative;z-index:1;padding:8px;width:100%;background:rgba(0,0,0,0.25);">
                <div style="font-size:9px;font-weight:700;color:rgba(255,255,255,0.92);
                            text-align:center;font-family:'Lora',serif;">{title[:24]}</div>
                <div style="font-size:8px;color:rgba(255,255,255,0.6);text-align:center;">
                    {author.split(',')[0][:20]}</div>
            </div>
        </div>"""

        st.markdown(f"""
        <div style="background:#e8e4dc;border:1px solid rgba(26,26,46,0.08);
                    border-top:none;border-radius:0 0 14px 14px;
                    padding:32px 28px;text-align:center;">
            {cover_html}
            <div style="font-family:'Lora',serif;font-size:18px;font-weight:700;
                        color:#1a1a2e;margin-bottom:4px;">{title}</div>
            <div style="font-size:13px;color:#6b6880;margin-bottom:14px;">{author} · {year}</div>
            <div style="display:inline-block;background:#f7f5f0;border:1px solid rgba(26,26,46,0.12);
                        border-radius:99px;padding:3px 12px;font-size:10px;font-weight:700;
                        color:#6b6880;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:16px;">
                {genre}</div>
            <div style="background:#fff;border:1px solid rgba(26,26,46,0.08);border-radius:12px;
                        padding:14px 18px;text-align:left;">
                <div style="font-size:11px;font-weight:700;color:#9d9aaa;text-transform:uppercase;
                            letter-spacing:0.08em;margin-bottom:6px;">About this book</div>
                <div style="font-size:13px;color:#4a4a6a;line-height:1.6;">{desc}</div>
            </div>
            <div style="margin-top:14px;font-size:12px;color:#c8622a;">
                ⏳ Book pages will appear once indexing completes.</div>
        </div>
        """, unsafe_allow_html=True)


# ─── COMPAT STUBS ────────────────────────────────────────────────────────────

def header_ui():
    pass

def show_chat_history():
    pass

def books_ui(fn):
    library_page(fn)

def search_books_ui(fn):
    search_page(fn)