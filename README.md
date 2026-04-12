# 🤖 AI Blog Generation System

A full-stack blog generation system using **LangGraph + LangChain + HuggingFace + Streamlit**.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set API Keys
```bash
cp .env.example .env
# Edit .env and add your keys
```

### 3. Get HuggingFace Token (Free)
- Go to https://huggingface.co/settings/tokens
- Click "New token" → select READ → copy token
- Paste in `.env` as `HF_API_TOKEN=hf_xxxx`

### 4. Run the App
```bash
streamlit run frontend.py
```

Open http://localhost:8501 in your browser.

---

## 📁 Project Structure

```
ai_blog_generator/
├── backend.py          # LangGraph pipeline (LLM + Image generation)
├── frontend.py         # Streamlit UI
├── requirements.txt    # Python dependencies
├── .env.example        # API key template → copy to .env
├── README.md           # This file
└── output/             # Generated blogs and images (auto-created)
    ├── blog.md         # Latest generated blog
    ├── blog.pdf        # Latest PDF export
    ├── images/         # AI-generated or placeholder images
    └── past_blogs/     # Archive of all generated blogs
```

---

## 🧠 Architecture

```
User Input (Topic + Tone + Language)
        ↓
   Router Node     → decides: closed_book / hybrid / open_book
        ↓
  Research Node    → Tavily live search OR mock research
        ↓
 Orchestrator Node → Generates 6-section blog plan (JSON via LLM)
        ↓
  Worker Nodes     → Each section written by LLM independently
        ↓
  Reducer Node     → Merges all sections into final Markdown
        ↓
  Image Node       → HuggingFace SDXL generates topic-specific images
        ↓
   Save Node       → Saves blog.md + archives + metadata
```

---

## 🔑 API Keys

| Key | Required? | Where to get |
|-----|-----------|--------------|
| `HF_API_TOKEN` | ✅ For real content | huggingface.co/settings/tokens |
| `TAVILY_API_KEY` | ❌ Optional | tavily.com (live research) |

**Without any key:** System runs in mock mode — produces structured but template-based content.  
**With HF token only:** Real LLM content (Mistral-7B) + Real AI images (Stable Diffusion XL).  
**With both keys:** Full power — live web research + real LLM + real AI images.

---

## ⏱️ Expected Time (With HF Token, Free Tier)

| Step | Time |
|------|------|
| Blog plan generation | 15–30 sec |
| Each section (6 sections) | 10–20 sec each |
| Each image (4 images) | 30–90 sec each |
| **Total** | **~7–12 minutes** |

> First request may take longer if models are cold-starting on HuggingFace.

---

## ✨ Features

- 🔀 Smart routing (closed/hybrid/open book mode)
- 🗺️ Structured 6-section blog plan
- ✍️ LLM-written sections (Mistral-7B)
- 🖼️ Topic-aware AI images (Stable Diffusion XL) with Pillow fallback
- 📄 PDF export
- 🌐 Multi-language support
- 🎨 Tone selection (Technical / Beginner / Balanced)
- 📚 Past blog history with reload
- 📋 Execution logs tab

---

## 🛠️ Troubleshooting

**"Model is loading" error:** HuggingFace cold-starts models. Wait 30s and retry — backend handles this automatically.

**Images are placeholders despite HF token:** SDXL may be unavailable on free tier. Backend auto-falls back to `stable-diffusion-v1-5`, then Pillow placeholder.

**Streamlit not found:** Run `pip install streamlit` separately.

**PyTorch warning:** Can be ignored — we use HuggingFace Inference API (cloud), not local PyTorch.
