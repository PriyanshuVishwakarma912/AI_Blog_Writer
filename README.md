# 🤖 AI Blog Writer

> A powerful full-stack AI-powered blog generation system that leverages LangGraph, LangChain, HuggingFace, and Streamlit to automatically create high-quality, multi-section blog posts with AI-generated images.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF69B4.svg)](https://streamlit.io/)
[![LangChain](https://img.shields.io/badge/LangChain-Framework-000000.svg)](https://www.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [API Keys & Setup](#api-keys--setup)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 📖 Overview

**AI Blog Writer** is an intelligent blog generation system that transforms simple topic inputs into comprehensive, well-structured blog posts. It employs advanced techniques including:

- **Smart Router Logic**: Automatically selects optimal research modes (closed-book, hybrid, or open-book)
- **LangGraph Pipeline**: Orchestrates multi-step LLM workflows with parallel processing
- **Dynamic Content Generation**: Creates 6-section blog outlines with independent LLM-generated sections
- **AI Image Generation**: Produces topic-relevant images using Stable Diffusion XL
- **Multi-language Support**: Generates content in multiple languages
- **Professional Output**: Exports to Markdown and PDF formats with metadata tracking

Perfect for bloggers, content creators, digital marketers, and developers who need to scale their content production.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔀 **Smart Routing** | Automatically determines research mode based on topic complexity |
| 📋 **Structured Planning** | Generates comprehensive 6-section blog outlines via LLM |
| ✍️ **AI Content Writing** | Creates original, coherent sections using Mistral-7B LLM |
| 🖼️ **Image Generation** | Produces topic-aware images with Stable Diffusion XL + fallback |
| 📚 **Blog History** | Archives and manages all previously generated blogs |
| 📄 **PDF Export** | Professional PDF document generation |
| 🌐 **Multi-language** | Support for multiple languages and tones |
| 🎨 **Tone Selection** | Technical, Beginner, or Balanced writing styles |
| 📊 **Execution Logs** | Detailed logs for debugging and monitoring |
| ⚡ **Free Tier Compatible** | Runs on HuggingFace's free Inference API tier |

---

## 🏗️ Architecture

The system uses a sophisticated **LangGraph state machine** to orchestrate the blog generation pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input                               │
│         (Topic, Tone, Language, Research Mode)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   Router Node          │
        │ (Decides research mode)│
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   Research Node        │
        │ (Tavily API / Mock)    │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Orchestrator Node     │
        │ (Generates blog plan)  │
        └────────────┬───────────┘
                     │
       ┌─────────────┴──────────────┐
       │    Parallel Processing     │
       ▼                            ▼
    Worker 1-6 Nodes          Reducer Node
    (Section Writers)         (Merge Sections)
       │                            │
       └──────────────┬─────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │   Image Node         │
            │ (HuggingFace SDXL)   │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   Save Node          │
            │ (Output & Archive)   │
            └──────────────────────┘
```

---

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **pip**: Package manager (comes with Python)
- **Internet Connection**: For API calls and model downloading
- **System Resources**: 
  - Minimum RAM: 2GB
  - Disk Space: 2GB (for model caching)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/PriyanshuVishwakarma912/AI_Blog_Writer.git
cd AI_Blog_Writer
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your actual API keys
# See Configuration section below
```

### 5. Run the Application

```bash
streamlit run frontend.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file in the project root with the following variables:

```env
# Required: HuggingFace API Token (Free)
HF_API_TOKEN=hf_your_token_here

# Optional: Tavily API Key for live web research
TAVILY_API_KEY=tvly_your_key_here

# Optional: Other configuration
LOG_LEVEL=INFO
DEBUG_MODE=False
```

### Getting API Keys

#### 🤗 HuggingFace Token (FREE - Required)

1. Visit [HuggingFace Settings](https://huggingface.co/settings/tokens)
2. Click **"New token"**
3. Select **"Read"** permission
4. Copy the generated token
5. Paste in `.env`: `HF_API_TOKEN=hf_xxxx`

**Benefits**: Real LLM content (Mistral-7B) + AI-generated images (Stable Diffusion XL)

#### 🔍 Tavily API Key (Optional)

1. Visit [Tavily AI](https://tavily.com)
2. Sign up for free account
3. Get your API key from dashboard
4. Paste in `.env`: `TAVILY_API_KEY=tvly_xxxx`

**Benefits**: Live web research for current information and trending topics

#### Running Without API Keys

The system gracefully handles missing keys:
- **No keys**: Template-based, structured content
- **HF token only**: Real LLM + real images
- **Both keys**: Full power with live research

---

## 📁 Project Structure

```
AI_Blog_Writer/
├── backend.py                 # LangGraph pipeline orchestration
├── frontend.py                # Streamlit web interface
├── requirements.txt           # Python dependencies
├── .env.example              # API key configuration template
├── .gitignore                # Git ignore rules
├── README.md                 # This file
│
└── output/                   # Generated content (auto-created)
    ├── blog.md              # Latest generated blog
    ├── blog.pdf             # Latest PDF export
    ├── blog_metadata.json   # Blog metadata and statistics
    ├── images/              # AI-generated images
    │   ├── image_1.png
    │   ├── image_2.png
    │   └── ...
    └── past_blogs/          # Archive of all generated blogs
        ├── blog_20260428_123045.md
        ├── blog_20260427_095030.md
        └── ...
```

---

## 📖 Usage Guide

### Generating Your First Blog

1. **Open the Application**
   - Navigate to `http://localhost:8501`
   - The Streamlit interface loads with all controls visible

2. **Enter Blog Details**
   - **Topic**: What you want the blog about (e.g., "Machine Learning in Healthcare")
   - **Tone**: Choose from:
     - 🔬 **Technical**: Deep, technical language for experts
     - 👨‍🎓 **Beginner**: Simple, accessible language for newcomers
     - ⚖️ **Balanced**: Mix of detail and accessibility
   - **Language**: Select output language

3. **Advanced Options** (Optional)
   - **Research Mode**: 
     - Closed-book: No external research (faster)
     - Hybrid: Mix of knowledge and research
     - Open-book: Live web research (requires Tavily key)
   - **Custom Instructions**: Add specific requirements or focus areas

4. **Generate Blog**
   - Click "Generate Blog" button
   - Monitor progress in real-time
   - Watch execution logs for detailed process information

5. **Review & Export**
   - Read the generated blog in the Preview tab
   - View execution logs and statistics
   - Download as Markdown or PDF
   - Access previous blogs from History tab

### Workflow Example

```
Topic: "How to Learn Python Programming"
Tone: Beginner
Language: English
↓
Blog Plan Generated:
1. Introduction to Python
2. Setting Up Your Environment
3. Basic Syntax and Data Types
4. Control Flow and Functions
5. Working with Libraries
6. Next Steps and Resources
↓
6 Sections Written in Parallel (~2 min)
↓
4 Topic-Relevant Images Generated (~4 min)
↓
Complete Blog Ready!
```

---

## ⏱️ Performance & Timing

Estimated execution times on HuggingFace **Free Tier**:

| Component | Time | Notes |
|-----------|------|-------|
| Blog plan generation | 15–30 sec | LLM generates 6-section outline |
| Each section (×6) | 10–20 sec | Parallel processing |
| Each image (×4) | 30–90 sec | Model initialization on first run |
| **Total** | **~7–12 min** | First run may be slower |

**Optimization Tips**:
- Batch multiple blog generations to leverage warm models
- Use closed-book mode for faster generation without research
- Images are optional - disable if speed is critical

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### ❌ "Model is loading" Error

**Cause**: HuggingFace cold-starting models on free tier
**Solution**: 
- Wait 30 seconds and retry
- Backend automatically handles retries
- Models warm up after first use

#### ❌ Images are Placeholders

**Cause**: SDXL unavailable on free tier or API limits
**Solution**:
1. Verify `HF_API_TOKEN` is valid
2. Backend auto-falls back to `stable-diffusion-v1-5`
3. If still failing, Pillow generates placeholder PNG
4. Upgrade to HuggingFace Pro for priority access

#### ❌ "Module not found" Errors

**Cause**: Dependencies not installed
**Solution**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### ❌ Streamlit not starting

**Cause**: Streamlit not installed
**Solution**:
```bash
pip install streamlit --upgrade
```

#### ❌ .env file not being read

**Cause**: File location or naming issues
**Solution**:
1. Ensure file is named exactly `.env` (not `.env.txt`)
2. Place in project root directory (same as `frontend.py`)
3. Restart the application after creating/editing

#### ⚠️ PyTorch/CUDA Warnings

**Cause**: System configuration messages
**Solution**: These can be safely ignored - app uses HuggingFace API (cloud), not local GPU

---

## 🤝 Contributing

We welcome contributions! Here's how to help:

### Steps to Contribute

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit**: `git commit -m 'Add amazing feature'`
5. **Push**: `git push origin feature/amazing-feature`
6. **Open a Pull Request** with detailed description

### Areas for Contribution

- 🐛 Bug fixes and improvements
- ✨ New features and enhancements
- 📚 Documentation improvements
- 🧪 Additional test coverage
- 🎨 UI/UX improvements

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Priyanshu Vishwakarma**
- GitHub: [@PriyanshuVishwakarma912](https://github.com/PriyanshuVishwakarma912)
- Repository: [AI_Blog_Writer](https://github.com/PriyanshuVishwakarma912/AI_Blog_Writer)

---

## 🙋 Support & Questions

- 📖 Check the [Troubleshooting](#troubleshooting) section
- 🐛 Open an [Issue](https://github.com/PriyanshuVishwakarma912/AI_Blog_Writer/issues) for bugs
- 💡 Use [Discussions](https://github.com/PriyanshuVishwakarma912/AI_Blog_Writer/discussions) for questions

---

## 🎉 Acknowledgments

Built with:
- [LangChain](https://www.langchain.com/) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - State machine orchestration
- [Streamlit](https://streamlit.io/) - Web interface
- [HuggingFace](https://huggingface.co/) - Model APIs
- [Tavily AI](https://tavily.com/) - Web research API

---

## 📊 Project Stats

- **Language**: Python 100%
- **Created**: April 2026
- **Status**: Active & Maintained
- **Last Updated**: April 28, 2026

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/PriyanshuVishwakarma912">Priyanshu Vishwakarma</a>
  <br>
  <a href="https://github.com/PriyanshuVishwakarma912/AI_Blog_Writer">⭐ Star this repository</a> if you find it useful!
</p>
