"""
AI Blog Generation System – Streamlit Frontend
Run with: streamlit run frontend.py
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

import streamlit as st

# ─────────────────────────────────────────────
# PAGE CONFIG (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Blog Generator",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* Root variables */
:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --border: #1f2937;
    --accent: #6366f1;
    --accent2: #8b5cf6;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --success: #10b981;
    --warn: #f59e0b;
    --danger: #ef4444;
}

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}

.stApp {
    background: var(--bg);
}

/* Headers */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}

.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(99,102,241,0.15) 0%, transparent 60%);
    pointer-events: none;
}

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #818cf8, #c084fc, #fb7185);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}

.hero-sub {
    color: var(--muted);
    font-size: 1rem;
    margin-top: 0.5rem;
    font-weight: 300;
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}

.card-accent {
    border-left: 3px solid var(--accent);
}

/* Status badge */
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 500;
    font-family: 'Syne', monospace;
}
.status-complete { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid #10b981; }
.status-running  { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid #818cf8; }
.status-error    { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid #ef4444; }

/* Log entries */
.log-entry {
    font-family: 'DM Mono', 'Courier New', monospace;
    font-size: 0.82rem;
    padding: 3px 0;
    color: var(--muted);
    border-bottom: 1px solid rgba(31,41,55,0.5);
}

/* Streamlit component overrides */
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stTextArea textarea {
    background: #0d1117 !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(99,102,241,0.4) !important;
}

.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #080c16 !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: var(--muted) !important;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px;
    border: 1px solid var(--border);
    gap: 4px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
}

.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
}

/* Section plan cards */
.section-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent2);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}

.section-number {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    color: var(--accent);
    font-size: 1.2rem;
}

/* Download button */
.dl-btn {
    background: linear-gradient(135deg, #0f172a, #1e293b) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

/* Image gallery */
.img-caption {
    font-size: 0.8rem;
    color: var(--muted);
    text-align: center;
    padding: 4px 0;
}

/* Markdown preview */
.markdown-preview {
    background: #0d1117;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    max-height: 600px;
    overflow-y: auto;
}

/* History items */
.history-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.4rem 0;
    cursor: pointer;
    transition: border-color 0.2s;
}

.history-item:hover {
    border-color: var(--accent);
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# IMPORT BACKEND
# ─────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

try:
    import backend
    BACKEND_OK = True
except ImportError as e:
    st.error(f"❌ Backend import failed: {e}")
    BACKEND_OK = False


# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "result": None,
        "generating": False,
        "logs": [],
        "current_topic": "",
        "pdf_path": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0; border-bottom: 1px solid #1f2937; margin-bottom: 1rem;'>
        <div style='font-family: Syne; font-size: 1.1rem; font-weight: 800; color: #818cf8;'>⚙️ Settings</div>
    </div>
    """, unsafe_allow_html=True)

    tone = st.selectbox(
        "Blog Tone",
        ["balanced", "technical", "beginner"],
        format_func=lambda x: {"balanced": "⚖️ Balanced", "technical": "🔬 Technical", "beginner": "🌱 Beginner-Friendly"}[x],
        help="Controls vocabulary complexity and writing style"
    )

    language = st.selectbox(
        "Language",
        ["en", "hi", "es", "fr", "de", "ja", "zh"],
        format_func=lambda x: {
            "en": "🇺🇸 English", "hi": "🇮🇳 Hindi", "es": "🇪🇸 Spanish",
            "fr": "🇫🇷 French", "de": "🇩🇪 German", "ja": "🇯🇵 Japanese",
            "zh": "🇨🇳 Chinese"
        }[x],
    )

    st.markdown("---")
    st.markdown("### 🔑 API Configuration")

    hf_token = st.text_input("HuggingFace Token", type="password",
                              value=os.getenv("HF_API_TOKEN", ""),
                              help="Get from huggingface.co/settings/tokens")
    if hf_token:
        os.environ["HF_API_TOKEN"] = hf_token
        backend.HF_API_TOKEN = hf_token

    tavily_key = st.text_input("Tavily API Key (optional)", type="password",
                                value=os.getenv("TAVILY_API_KEY", ""),
                                help="For live web research. Get from tavily.com")
    if tavily_key:
        os.environ["TAVILY_API_KEY"] = tavily_key
        backend.TAVILY_API_KEY = tavily_key

    st.markdown("---")
    st.markdown("""
    <div style='font-size: 0.78rem; color: #6b7280; line-height: 1.6;'>
        <div style='color: #94a3b8; font-weight: 600; margin-bottom: 4px;'>ℹ️ Image Generation</div>
        With HF token: <span style='color: #818cf8;'>Stable Diffusion XL</span> generates real topic-specific images.<br>
        Each image takes <span style='color: #f59e0b;'>30–90 sec</span> on free tier.<br>
        Without token: styled placeholders used instantly.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    hf_status = "✅ Connected" if os.getenv("HF_API_TOKEN") else "⚠️ Not set (mock mode)"
    tv_status = "✅ Connected" if os.getenv("TAVILY_API_KEY") else "⚠️ Not set"
    st.markdown(f"""
    <div style='font-size: 0.8rem; color: #94a3b8;'>
        <div style='margin: 4px 0;'>🤗 HuggingFace: <span style='color: {"#10b981" if "✅" in hf_status else "#f59e0b"}'>{hf_status}</span></div>
        <div style='margin: 4px 0;'>🔍 Tavily: <span style='color: {"#10b981" if "✅" in tv_status else "#94a3b8"}'>{tv_status}</span></div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────

# Hero banner
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">✍️ AI Blog Generator</div>
    <div class="hero-sub">LangGraph · LangChain · HuggingFace · Streamlit — Generate complete, structured blogs in seconds</div>
</div>
""", unsafe_allow_html=True)


# ─── Input Area ───────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    topic = st.text_input(
        "📝 Blog Topic",
        placeholder="e.g. Docker and Kubernetes for Beginners, How Transformers work, CI/CD pipelines...",
        label_visibility="collapsed",
    )

with col2:
    generate_clicked = st.button("🚀 Generate", disabled=st.session_state.generating)


# ─── GENERATION ───────────────────────────────
if generate_clicked and topic.strip() and BACKEND_OK:
    st.session_state.generating = True
    st.session_state.result = None
    st.session_state.current_topic = topic
    st.session_state.pdf_path = None

    progress_bar = st.progress(0)
    status_text = st.empty()
    log_container = st.empty()

    steps = [
        (10, "🔀 Analyzing topic..."),
        (25, "🔍 Researching..."),
        (45, "🗺️ Building blog plan..."),
        (70, "✍️ Writing sections..."),
        (85, "🔗 Assembling Markdown..."),
        (95, "🖼️ Generating images..."),
        (100, "💾 Saving output..."),
    ]

    step_idx = 0

    def update_progress(pct, msg):
        progress_bar.progress(pct)
        status_text.markdown(f"""
        <div class="card card-accent" style="padding: 0.75rem 1.25rem;">
            <span class="status-badge status-running">● RUNNING</span>
            <span style="margin-left: 10px; color: #f1f5f9; font-size: 0.95rem;">{msg}</span>
        </div>
        """, unsafe_allow_html=True)

    # Animate through steps while generating
    update_progress(5, "🚀 Initializing pipeline...")
    time.sleep(0.3)

    # Run generation
    result = backend.generate_blog(topic.strip(), tone=tone, language=language)

    # Animate remaining steps
    for pct, msg in steps:
        update_progress(pct, msg)
        time.sleep(0.2)

    st.session_state.result = result
    st.session_state.logs = result.get("logs", [])
    st.session_state.generating = False

    progress_bar.empty()

    if result.get("status") == "complete":
        status_text.markdown("""
        <div class="card" style="border-left: 3px solid #10b981; padding: 0.75rem 1.25rem;">
            <span class="status-badge status-complete">✓ COMPLETE</span>
            <span style="margin-left: 10px; color: #10b981; font-size: 0.95rem;">Blog generated successfully!</span>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    else:
        status_text.markdown(f"""
        <div class="card" style="border-left: 3px solid #ef4444; padding: 0.75rem 1.25rem;">
            <span class="status-badge status-error">✗ ERROR</span>
            <span style="margin-left: 10px; color: #ef4444;">{result.get("error", "Unknown error")}</span>
        </div>
        """, unsafe_allow_html=True)

elif generate_clicked and not topic.strip():
    st.warning("⚠️ Please enter a blog topic first!")


# ─────────────────────────────────────────────
# RESULTS TABS
# ─────────────────────────────────────────────
if st.session_state.result:
    result = st.session_state.result
    markdown = result.get("markdown", "")
    image_paths = result.get("image_paths", [])
    blog_plan = result.get("blog_plan", [])
    logs = result.get("logs", [])

    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

    tab_preview, tab_plan, tab_images, tab_logs, tab_download = st.tabs([
        "📄 Preview", "🗺️ Plan", "🖼️ Images", "📋 Logs", "⬇️ Download"
    ])

    # ─── TAB: PREVIEW ─────────────────────────
    with tab_preview:
        if markdown:
            st.markdown(f"""
            <div class="card" style="padding: 0.5rem 1rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 1rem;">
                <span style="color: #94a3b8; font-size: 0.85rem;">Topic:</span>
                <span style="font-family: Syne; font-weight: 700; color: #818cf8;">{st.session_state.current_topic}</span>
                <span style="color: #94a3b8; font-size: 0.8rem; margin-left: auto;">{len(markdown.split())} words · {len(blog_plan)} sections</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(markdown)
        else:
            st.info("No markdown generated yet.")

    # ─── TAB: PLAN ────────────────────────────
    with tab_plan:
        if blog_plan:
            st.markdown("### 🗺️ Generated Blog Structure")
            for i, section in enumerate(blog_plan):
                with st.expander(f"Section {i+1}: {section.get('title', 'Untitled')}", expanded=(i == 0)):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**🎯 Goal:** {section.get('goal', '')}")
                        st.markdown("**📌 Key Points:**")
                        for bullet in section.get("bullets", []):
                            st.markdown(f"- {bullet}")
                    with col_b:
                        wc = section.get("word_count", 0)
                        st.markdown(f"""
                        <div style='text-align: center; padding: 1rem; background: #0d1117; border-radius: 8px; border: 1px solid #1f2937;'>
                            <div style='font-family: Syne; font-size: 1.8rem; font-weight: 800; color: #818cf8;'>{wc}</div>
                            <div style='font-size: 0.75rem; color: #94a3b8;'>target words</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No plan available.")

    # ─── TAB: IMAGES ──────────────────────────
    with tab_images:
        if image_paths:
            st.markdown(f"### 🖼️ Generated Images ({len(image_paths)})")
            cols = st.columns(min(len(image_paths), 2))
            for i, img_path in enumerate(image_paths):
                p = Path(img_path)
                if p.exists():
                    with cols[i % 2]:
                        st.image(str(p), use_container_width=True)
                        st.markdown(f"<div class='img-caption'>📁 {p.name}</div>", unsafe_allow_html=True)
                        with open(p, "rb") as f:
                            st.download_button(
                                f"⬇️ Download Image {i+1}",
                                f.read(),
                                file_name=p.name,
                                mime="image/png",
                                key=f"dl_img_{i}"
                            )
        else:
            st.info("No images generated.")

    # ─── TAB: LOGS ────────────────────────────
    with tab_logs:
        st.markdown("### 📋 Pipeline Execution Logs")
        log_html = "".join([
            f"<div class='log-entry'>{log}</div>"
            for log in logs
        ])
        st.markdown(f"""
        <div style='background: #0a0e1a; border: 1px solid #1f2937; border-radius: 10px; padding: 1rem; max-height: 450px; overflow-y: auto; font-family: monospace;'>
            {log_html}
        </div>
        """, unsafe_allow_html=True)

        # Copy logs
        logs_text = "\n".join(logs)
        st.download_button("📋 Export Logs", logs_text, file_name="blog_generation_logs.txt", mime="text/plain")

    # ─── TAB: DOWNLOAD ────────────────────────
    with tab_download:
        st.markdown("### ⬇️ Export Your Blog")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="card card-accent">
                <div style='font-family: Syne; font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem;'>📝 Markdown</div>
                <div style='color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;'>
                    Raw Markdown file — open in Obsidian, VS Code, Notion, etc.
                </div>
            </div>
            """, unsafe_allow_html=True)

            safe_topic = "".join(c for c in st.session_state.current_topic if c.isalnum() or c in " _-")[:30].strip()
            st.download_button(
                "⬇️ Download blog.md",
                markdown.encode("utf-8"),
                file_name=f"{safe_topic or 'blog'}.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with col2:
            st.markdown("""
            <div class="card" style="border-left: 3px solid #f59e0b;">
                <div style='font-family: Syne; font-weight: 700; font-size: 1rem; margin-bottom: 0.5rem;'>📄 PDF Export</div>
                <div style='color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;'>
                    Professional PDF — shareable, printable document.
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🔄 Generate PDF", use_container_width=True):
                with st.spinner("Creating PDF..."):
                    try:
                        pdf_path = backend.export_pdf(markdown)
                        st.session_state.pdf_path = pdf_path
                        st.success("✅ PDF created!")
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")

            if st.session_state.pdf_path and Path(st.session_state.pdf_path).exists():
                with open(st.session_state.pdf_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download PDF",
                        f.read(),
                        file_name=f"{safe_topic or 'blog'}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

        st.markdown("---")

        # Raw text preview
        with st.expander("👁️ Raw Markdown Source"):
            st.code(markdown[:3000] + ("..." if len(markdown) > 3000 else ""), language="markdown")


# ─────────────────────────────────────────────
# PAST BLOGS SECTION
# ─────────────────────────────────────────────
st.markdown("<div style='height: 2rem'></div>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("### 📚 Previously Generated Blogs")

if BACKEND_OK:
    past_blogs = backend.get_past_blogs()
    if past_blogs:
        for blog_meta in past_blogs[:10]:
            topic_label = blog_meta.get("topic", "Unknown")
            ts = blog_meta.get("timestamp", "")
            tone_label = blog_meta.get("tone", "")
            sections_n = blog_meta.get("sections", 0)
            lang = blog_meta.get("language", "en")

            try:
                dt = datetime.strptime(ts, "%Y%m%d_%H%M%S")
                date_str = dt.strftime("%b %d, %Y %H:%M")
            except Exception:
                date_str = ts

            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                <div class="history-item">
                    <div style='font-family: Syne; font-weight: 700; color: #f1f5f9;'>{topic_label}</div>
                    <div style='font-size: 0.8rem; color: #94a3b8; margin-top: 4px;'>
                        🕐 {date_str} &nbsp;·&nbsp; 
                        📑 {sections_n} sections &nbsp;·&nbsp; 
                        🎨 {tone_label} &nbsp;·&nbsp; 
                        🌐 {lang.upper()}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                blog_path = Path(blog_meta.get("path", ""))
                if blog_path.exists():
                    content = blog_path.read_text(encoding="utf-8")
                    if st.button("📂 Load", key=f"load_{ts}", use_container_width=True):
                        st.session_state.result = {
                            "markdown": content,
                            "image_paths": [],
                            "blog_plan": [],
                            "logs": [f"📂 Loaded from history: {topic_label}"],
                            "status": "complete",
                        }
                        st.session_state.current_topic = topic_label
                        st.rerun()
    else:
        st.markdown("""
        <div class="card" style="text-align: center; padding: 2rem; color: #94a3b8;">
            <div style='font-size: 2rem;'>📭</div>
            <div style='margin-top: 0.5rem;'>No past blogs yet. Generate your first one above!</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.error("Backend not available.")


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style='text-align: center; padding: 2rem 0 1rem; color: #374151; font-size: 0.8rem; margin-top: 2rem; border-top: 1px solid #1f2937;'>
    <span style='font-family: Syne; color: #4b5563;'>AI Blog Generator</span> · 
    Built with LangGraph, LangChain, HuggingFace & Streamlit
</div>
""", unsafe_allow_html=True)
