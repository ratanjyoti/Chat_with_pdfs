# htmlTemplates.py

css = ""  # Loaded via styles.css

# ─── BOT / USER TEMPLATES (kept for compatibility) ──
bot_template = """
<div style="display:flex;gap:12px;align-items:flex-start;padding:12px 20px;">
    <div style="width:32px;height:32px;flex-shrink:0;background:#c8622a;
                border-radius:8px;display:flex;align-items:center;
                justify-content:center;font-size:15px;">📖</div>
    <div style="flex:1;background:#f7f5f0;border:1px solid rgba(26,26,46,0.08);
                border-radius:14px;padding:12px 16px;font-size:14px;
                line-height:1.6;color:#1a1a2e;font-family:'DM Sans',sans-serif;">
        {{MSG}}
    </div>
</div>
"""

user_template = """
<div style="display:flex;gap:12px;align-items:flex-start;padding:12px 20px;flex-direction:row-reverse;">
    <div style="width:32px;height:32px;flex-shrink:0;background:#1a1a2e;
                border-radius:8px;display:flex;align-items:center;
                justify-content:center;font-size:15px;">👤</div>
    <div style="flex:1;background:#1a1a2e;border-radius:14px;padding:12px 16px;
                font-size:14px;line-height:1.6;color:white;
                font-family:'DM Sans',sans-serif;">
        {{MSG}}
    </div>
</div>
"""

# ─── WELCOME CARD (bright mode) ──────────────────────
welcome_card = """
<div style="
    background: #ffffff;
    border: 1px solid rgba(26,26,46,0.08);
    border-radius: 20px;
    padding: 40px 36px;
    text-align: center;
    margin: 24px 0;
    box-shadow: 0 4px 12px rgba(26,26,46,0.05);
">
    <div style="font-size:56px;margin-bottom:16px;">📚</div>
    <h3 style="font-family:'Lora',serif;font-weight:700;color:#1a1a2e;margin:0 0 8px;
               font-size:22px;letter-spacing:-0.02em;">
        Chat with Great Literature
    </h3>
    <p style="color:#6b6880;font-size:14px;margin:0 0 28px;line-height:1.7;max-width:420px;margin-left:auto;margin-right:auto;">
        Choose a classic from our library below, search 70,000+ Gutenberg books,
        or upload your own PDF — then ask anything.
    </p>
    <div style="display:flex;gap:14px;justify-content:center;flex-wrap:wrap;">
        <div style="background:#f7f5f0;border:1px solid rgba(26,26,46,0.08);
                    border-radius:14px;padding:18px 22px;min-width:130px;text-align:center;">
            <div style="font-size:26px;margin-bottom:8px;">📖</div>
            <div style="font-weight:700;color:#1a1a2e;font-size:13px;margin-bottom:3px;">Pick a Book</div>
            <div style="font-size:12px;color:#9d9aaa;">from our library</div>
        </div>
        <div style="background:#f7f5f0;border:1px solid rgba(26,26,46,0.08);
                    border-radius:14px;padding:18px 22px;min-width:130px;text-align:center;">
            <div style="font-size:26px;margin-bottom:8px;">🔍</div>
            <div style="font-weight:700;color:#1a1a2e;font-size:13px;margin-bottom:3px;">Search Gutenberg</div>
            <div style="font-size:12px;color:#9d9aaa;">70,000+ free books</div>
        </div>
        <div style="background:#f7f5f0;border:1px solid rgba(26,26,46,0.08);
                    border-radius:14px;padding:18px 22px;min-width:130px;text-align:center;">
            <div style="font-size:26px;margin-bottom:8px;">📄</div>
            <div style="font-weight:700;color:#1a1a2e;font-size:13px;margin-bottom:3px;">Upload PDF</div>
            <div style="font-size:12px;color:#9d9aaa;">your own document</div>
        </div>
    </div>
</div>
"""