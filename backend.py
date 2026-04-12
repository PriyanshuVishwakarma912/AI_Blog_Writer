"""
AI-Powered Blog Generation Backend
Uses LangGraph for orchestration, LangChain + HuggingFace for LLM.
"""

import os
import re
import json
import time
import logging
import requests
from pathlib import Path
from typing import TypedDict, List, Optional, Annotated
from datetime import datetime

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import io

# LangChain imports
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

# LangGraph imports
from langgraph.graph import StateGraph, END

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))
IMAGES_DIR = OUTPUT_DIR / "images"
PAST_BLOGS_DIR = OUTPUT_DIR / "past_blogs"

OUTPUT_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
PAST_BLOGS_DIR.mkdir(exist_ok=True)

# HuggingFace model – using a reliable Inference API model
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# ─────────────────────────────────────────────
# STATE DEFINITION
# ─────────────────────────────────────────────
class BlogState(TypedDict):
    topic: str
    tone: str                        # technical | beginner | balanced
    language: str                    # en | hi | es etc.
    mode: str                        # closed_book | hybrid | open_book
    research_data: Optional[str]
    blog_plan: Optional[List[dict]]
    sections: Optional[List[dict]]   # [{title, content}]
    final_markdown: Optional[str]
    image_paths: Optional[List[str]]
    logs: List[str]
    error: Optional[str]
    status: str


# ─────────────────────────────────────────────
# LLM FACTORY
# ─────────────────────────────────────────────
def get_llm(max_new_tokens: int = 800):
    """Returns a HuggingFace LLM via Inference API, with fallback."""
    if HF_API_TOKEN:
        try:
            llm = HuggingFaceEndpoint(
                repo_id=HF_MODEL,
                huggingfacehub_api_token=HF_API_TOKEN,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                task="text-generation",
            )
            logger.info(f"LLM loaded: {HF_MODEL}")
            return llm
        except Exception as e:
            logger.warning(f"HuggingFace LLM init failed: {e}")
    logger.warning("No HF_API_TOKEN found – using mock LLM")
    return None


def llm_generate(prompt: str, max_tokens: int = 800) -> str:
    """
    Call Groq API for fast, free LLM generation.
    Falls back to mock if no key available.
    """
    groq_key = os.getenv("GROQ_API_KEY", "")
    
    if not groq_key:
        logger.warning("No GROQ_API_KEY found – using mock")
        return mock_generate(prompt)

    try:
        from groq import Groq
        client = Groq(api_key=groq_key)
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional blog writer. Write detailed, informative, well-structured content."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        
        result = response.choices[0].message.content.strip()
        logger.info(f"Groq LLM success: {len(result)} chars")
        return result
        
    except Exception as e:
        logger.warning(f"Groq API failed: {e}, using mock")
        return mock_generate(prompt)


def mock_generate(prompt: str) -> str:
    """Intelligent mock generation based on prompt keywords."""
    prompt_lower = prompt.lower()

    if "blog plan" in prompt_lower or "outline" in prompt_lower or "json" in prompt_lower:
        # Extract topic from prompt
        topic_match = re.search(r'topic[:\s]+["\']?([^"\'\n]+)', prompt_lower)
        topic = topic_match.group(1).strip() if topic_match else "Technology"
        return json.dumps([
            {"title": f"Introduction to {topic}", "goal": "Hook the reader and set context", "bullets": ["What is it?", "Why it matters", "Who should read this"], "word_count": 200},
            {"title": f"Core Concepts of {topic}", "goal": "Build foundational understanding", "bullets": ["Key principles", "How it works", "Real-world analogy"], "word_count": 300},
            {"title": f"Getting Started with {topic}", "goal": "Practical first steps", "bullets": ["Prerequisites", "Setup guide", "First example"], "word_count": 350},
            {"title": f"Advanced {topic} Techniques", "goal": "Go deeper for experienced readers", "bullets": ["Best practices", "Common patterns", "Optimization tips"], "word_count": 400},
            {"title": f"Real-World Use Cases of {topic}", "goal": "Show practical applications", "bullets": ["Industry examples", "Case studies", "Lessons learned"], "word_count": 300},
            {"title": f"Common Challenges and Solutions", "goal": "Address pain points", "bullets": ["Typical mistakes", "Debugging tips", "Community resources"], "word_count": 250},
            {"title": "Conclusion and Next Steps", "goal": "Wrap up and inspire action", "bullets": ["Key takeaways", "Further reading", "Call to action"], "word_count": 150},
        ])
    else:
        # Extract section title from worker prompt – look for "Section title:"
        title_match = re.search(r'section title[:\s]+([^\n]+)', prompt_lower)
        if title_match:
            title = title_match.group(1).strip().title()
        else:
            # Fallback: extract topic
            topic_match = re.search(r'about[:\s"]+([^"\n]+)', prompt_lower)
            title = topic_match.group(1).strip().title()[:60] if topic_match else "This Topic"

        # Extract bullets from prompt
        bullets_in_prompt = re.findall(r'[-•]\s+(.+)', prompt)
        bullets_text = ""
        if bullets_in_prompt:
            bullets_text = "\n".join([f"- **{b.strip()}**: A critical aspect that practitioners must understand" for b in bullets_in_prompt[:4]])

        return f"""This section provides an in-depth look at **{title}**.

Whether you're just starting out or looking to deepen your understanding, this section covers everything you need to know.

### Core Fundamentals

{bullets_text if bullets_text else "- **Key Concept 1**: Understanding the foundations is essential for success\\n- **Key Concept 2**: Practical application reinforces theoretical knowledge\\n- **Key Concept 3**: Community and resources accelerate your learning journey"}

### Practical Insights

When approaching {title.lower()}, the most important thing is to start small and build incrementally. 
Real-world experience teaches lessons that no textbook can fully capture.

The best practitioners combine:
1. **Theoretical understanding** – knowing the *why* behind every decision
2. **Hands-on experimentation** – breaking things and learning from failures
3. **Peer collaboration** – sharing knowledge amplifies everyone's growth

### Key Takeaways

Mastering {title.lower()} is a journey, not a destination. Each step forward builds confidence and capability.
Stay curious, keep experimenting, and leverage the vast ecosystem of tools and communities available today.
"""



# ─────────────────────────────────────────────
# RESEARCH UTILITIES
# ─────────────────────────────────────────────
def fetch_research_tavily(topic: str) -> str:
    """Fetch research via Tavily Search API."""
    if not TAVILY_API_KEY:
        return ""
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": topic,
            "search_depth": "basic",
            "max_results": 5,
            "include_answer": True,
        }
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            answer = data.get("answer", "")
            snippets = "\n".join([f"- {r.get('title', '')}: {r.get('content', '')[:300]}" for r in results])
            return f"Summary: {answer}\n\nSources:\n{snippets}"
    except Exception as e:
        logger.warning(f"Tavily fetch failed: {e}")
    return ""


def mock_research(topic: str) -> str:
    """Mock research data when no API key available."""
    return f"""Key facts about {topic}:
- {topic} has gained significant traction in recent years across multiple industries
- Experts predict continued growth and adoption through 2025 and beyond
- Primary use cases include automation, efficiency improvement, and innovation
- Common challenges: learning curve, integration complexity, tooling maturity
- Leading organizations have reported 30-50% productivity gains after adoption
- The open-source community has contributed substantial tooling and documentation
- Best practices emphasize iterative adoption and continuous learning"""


# ─────────────────────────────────────────────
# IMAGE GENERATION
# ─────────────────────────────────────────────

# HuggingFace image model – Stable Diffusion XL (free Inference API)
HF_IMAGE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

# Fallback lighter model if SDXL is unavailable
HF_IMAGE_MODEL_FALLBACK = "runwayml/stable-diffusion-v1-5"


def build_image_prompt(section_title: str, topic: str) -> str:
    """
    Convert a section title + blog topic into a rich Stable Diffusion prompt.
    Produces topic-relevant, professional illustration prompts.
    """
    title_lower = section_title.lower()
    topic_lower = topic.lower()

    # Domain detection → style guidance
    style_map = {
        ("docker", "container", "kubernetes", "k8s", "devops", "ci/cd", "pipeline"):
            "digital art of containers and servers, blue tech aesthetic, isometric 3D illustration",
        ("machine learning", "ai", "neural", "deep learning", "transformer", "llm", "gpt"):
            "abstract neural network visualization, glowing nodes and connections, dark background, purple and cyan",
        ("python", "programming", "code", "software", "developer", "api"):
            "clean code editor with syntax highlighting, developer workspace, dark mode, tech illustration",
        ("cloud", "aws", "azure", "gcp", "serverless", "infrastructure"):
            "cloud computing infrastructure, server racks, network connections, blue and white, professional 3D render",
        ("blockchain", "crypto", "web3", "decentralized"):
            "blockchain network visualization, interconnected blocks, gold and blue, futuristic digital art",
        ("data", "database", "sql", "analytics", "big data"):
            "data visualization dashboard, flowing data streams, charts and graphs, dark tech aesthetic",
        ("security", "cybersecurity", "hacking", "encryption"):
            "cybersecurity concept art, shield and lock icons, matrix green on dark background, digital protection",
        ("web", "frontend", "react", "html", "css", "javascript"):
            "modern web interface design, browser with clean UI, colorful components, flat design illustration",
        ("linux", "terminal", "bash", "shell", "unix"):
            "terminal screen with green text, command line interface, dark background, hacker aesthetic",
        ("networking", "tcp", "http", "dns", "protocol"):
            "network topology diagram, routers and connections, clean technical illustration, blue tones",
    }

    chosen_style = "professional technology concept art, clean illustration, vibrant colors, 4k quality"
    for keywords, style in style_map.items():
        if any(kw in title_lower or kw in topic_lower for kw in keywords):
            chosen_style = style
            break

    # Section-type modifiers
    if any(w in title_lower for w in ["introduction", "overview", "what is"]):
        modifier = "wide establishing shot, concept overview, informative"
    elif any(w in title_lower for w in ["getting started", "setup", "install"]):
        modifier = "step by step process, workflow diagram, beginner friendly"
    elif any(w in title_lower for w in ["advanced", "deep dive", "techniques"]):
        modifier = "complex detailed diagram, expert level, intricate details"
    elif any(w in title_lower for w in ["use case", "real world", "example"]):
        modifier = "real world application, industry setting, professional environment"
    elif any(w in title_lower for w in ["challenge", "problem", "solution"]):
        modifier = "problem solving concept, debugging, fixing issues"
    elif any(w in title_lower for w in ["conclusion", "summary", "next steps"]):
        modifier = "success and achievement, forward looking, bright future"
    else:
        modifier = "detailed technical illustration"

    prompt = (
        f"{chosen_style}, {modifier}, "
        f"related to {topic[:40]}, "
        "no text, no watermark, high quality, professional blog illustration, "
        "wide format 16:9, sharp details"
    )

    logger.info(f"Image prompt for '{section_title}': {prompt[:100]}...")
    return prompt


def generate_hf_image(prompt: str, index: int) -> bytes | None:
    """
    Generate image using Pollinations.ai — completely free, no API key needed.
    Falls back to None if fails.
    """
    try:
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=432&nologo=true&seed={index * 42}"
        
        logger.info(f"Fetching image from Pollinations.ai...")
        resp = requests.get(url, timeout=90)
        
        if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
            logger.info(f"✅ Pollinations image received: {len(resp.content)} bytes")
            return resp.content
        else:
            logger.warning(f"Pollinations returned {resp.status_code}")
            return None
            
    except Exception as e:
        logger.warning(f"Pollinations image failed: {e}")
        return None


def generate_pillow_fallback(label: str, index: int, topic: str) -> Path:
    """
    Generate a styled placeholder image using Pillow.
    Used as fallback when HuggingFace image API fails.
    """
    width, height = 800, 432

    schemes = [
        ((15, 23, 42), (99, 102, 241), (224, 231, 255)),
        ((5, 46, 22), (34, 197, 94), (220, 252, 231)),
        ((45, 20, 3), (234, 88, 12), (255, 237, 213)),
        ((20, 14, 40), (168, 85, 247), (243, 232, 255)),
        ((7, 36, 55), (6, 182, 212), (207, 250, 254)),
    ]
    bg, accent, text_color = schemes[index % len(schemes)]

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    for x in range(0, width + height, 30):
        draw.line([(x, 0), (x - height, height)], fill=(*accent, 20), width=1)

    draw.rectangle([0, height - 8, width, height], fill=accent)
    draw.rectangle([0, 0, width, 8], fill=accent)
    draw.rectangle([0, 0, 6, height], fill=accent)

    for cx, cy in [(20, 20), (width - 20, 20), (20, height - 20), (width - 20, height - 20)]:
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=accent)

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_idx  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    except Exception:
        font_large = ImageFont.load_default()
        font_small = font_large
        font_idx   = font_large

    draw.text((width - 110, height // 2 - 45), f"#{index + 1}", fill=(*accent, 40), font=font_idx)
    label_short = label[:50] + "..." if len(label) > 50 else label
    draw.text((50, height // 2 - 45), label_short, fill=text_color, font=font_large)
    topic_short = topic[:60] + "..." if len(topic) > 60 else topic
    draw.text((50, height // 2 + 10), f"Topic: {topic_short}", fill=(*text_color, 180), font=font_small)
    draw.text((50, height // 2 + 45), f"[ AI Image Placeholder #{index + 1} ]", fill=accent, font=font_small)

    out_path = IMAGES_DIR / f"image_{index + 1}.png"
    img.save(out_path, "PNG")
    return out_path


def generate_image(label: str, index: int, topic: str) -> Path:
    """
    Main image generation function.
    1. Try HuggingFace Stable Diffusion (topic-aware prompt)
    2. Fallback to Pillow styled placeholder
    Always returns a valid image Path.
    """
    out_path = IMAGES_DIR / f"image_{index + 1}.png"

    if HF_API_TOKEN:
        logger.info(f"🎨 Generating AI image {index+1} via HuggingFace SDXL...")
        prompt = build_image_prompt(label, topic)
        image_bytes = generate_hf_image(prompt, index)

        if image_bytes:
            try:
                # Validate and save
                img = Image.open(io.BytesIO(image_bytes))
                img = img.convert("RGB")
                # Resize to standard 16:9 blog format
                img = img.resize((800, 432), Image.LANCZOS)
                img.save(out_path, "PNG", quality=95)
                logger.info(f"✅ AI image saved: {out_path}")
                return out_path
            except Exception as e:
                logger.warning(f"Image save failed: {e}, using Pillow fallback")
        else:
            logger.warning(f"HF image generation failed for image {index+1}, using Pillow fallback")
    else:
        logger.info("No HF_API_TOKEN – using Pillow placeholder")

    # Fallback
    return generate_pillow_fallback(label, index, topic)


# ─────────────────────────────────────────────
# LANGGRAPH NODES
# ─────────────────────────────────────────────

def router_node(state: BlogState) -> BlogState:
    """Decide research mode based on topic complexity."""
    logs = state.get("logs", [])
    topic = state["topic"]
    logs.append(f"🔀 Router: Analyzing topic '{topic}'")

    # Simple heuristic: specific/technical topics need research
    technical_keywords = ["how to", "tutorial", "guide", "vs", "comparison", "2024", "2025", "latest", "new"]
    needs_research = any(kw in topic.lower() for kw in technical_keywords)

    if TAVILY_API_KEY and needs_research:
        mode = "open_book"
        logs.append("📡 Mode: open_book (live research via Tavily)")
    elif needs_research:
        mode = "hybrid"
        logs.append("📚 Mode: hybrid (mock research, no Tavily key)")
    else:
        mode = "closed_book"
        logs.append("🧠 Mode: closed_book (LLM knowledge only)")

    return {**state, "mode": mode, "logs": logs, "status": "routing_done"}


def research_node(state: BlogState) -> BlogState:
    """Fetch research data based on mode."""
    logs = state.get("logs", [])
    mode = state["mode"]
    topic = state["topic"]

    logs.append(f"🔍 Research Node: mode={mode}")

    if mode == "closed_book":
        research_data = ""
        logs.append("⏭️ Skipping research (closed_book mode)")
    elif mode == "open_book":
        logs.append("🌐 Fetching live data from Tavily...")
        research_data = fetch_research_tavily(topic)
        if research_data:
            logs.append(f"✅ Research fetched: {len(research_data)} chars")
        else:
            research_data = mock_research(topic)
            logs.append("⚠️ Tavily failed, using mock research")
    else:  # hybrid
        research_data = mock_research(topic)
        logs.append("📝 Using structured mock research data")

    return {**state, "research_data": research_data, "logs": logs, "status": "research_done"}


def orchestrator_node(state: BlogState) -> BlogState:
    """Generate a structured blog plan with 5-7 sections."""
    logs = state.get("logs", [])
    topic = state["topic"]
    tone = state.get("tone", "balanced")
    language = state.get("language", "en")
    research = state.get("research_data", "")
    logs.append("🗺️ Orchestrator: Generating blog plan...")

    tone_instruction = {
        "technical": "Use precise technical language, code snippets where relevant, assume intermediate knowledge.",
        "beginner": "Use simple language, analogies, avoid jargon, explain every term.",
        "balanced": "Mix accessible explanations with technical depth. Appeal to curious learners.",
    }.get(tone, "balanced")

    lang_instruction = f" Write the blog in {language} language." if language != "en" else ""

    research_section = f"\n\nResearch Context:\n{research}" if research else ""

    prompt = f"""You are a professional blog architect. Create a detailed blog plan for the topic: "{topic}".

Tone: {tone_instruction}{lang_instruction}{research_section}

Generate a JSON array of exactly 6 sections. Each section must have:
- "title": section heading (string)
- "goal": what this section achieves (string)  
- "bullets": list of 3-4 key points to cover (array of strings)
- "word_count": target word count (number, between 150-400)

Return ONLY the JSON array, no other text, no markdown backticks.
"""

    raw = llm_generate(prompt, max_tokens=1000)
    logs.append(f"📋 Raw plan received ({len(raw)} chars)")

    # Parse JSON robustly
    blog_plan = None
    try:
        # Strip any markdown fences
        cleaned = re.sub(r"```(?:json)?", "", raw).strip()
        # Find JSON array
        match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if match:
            blog_plan = json.loads(match.group())
    except Exception as e:
        logger.warning(f"Plan JSON parse failed: {e}")

    # Fallback plan
    if not blog_plan or not isinstance(blog_plan, list):
        logs.append("⚠️ Using fallback blog plan")
        blog_plan = json.loads(mock_generate(f"blog plan json topic: {topic}"))

    logs.append(f"✅ Blog plan ready: {len(blog_plan)} sections")
    for i, s in enumerate(blog_plan):
        logs.append(f"   Section {i+1}: {s.get('title', 'Untitled')}")

    return {**state, "blog_plan": blog_plan, "logs": logs, "status": "plan_ready"}


def worker_node(state: BlogState) -> BlogState:
    """Generate content for each section in the blog plan."""
    logs = state.get("logs", [])
    topic = state["topic"]
    tone = state.get("tone", "balanced")
    language = state.get("language", "en")
    blog_plan = state.get("blog_plan", [])
    research = state.get("research_data", "")
    sections = []

    tone_instruction = {
        "technical": "Be precise, use technical terms, include specifics.",
        "beginner": "Keep it simple, use analogies, be encouraging.",
        "balanced": "Balance depth with accessibility.",
    }.get(tone, "balanced")

    lang_instruction = f"Write in {language} language. " if language != "en" else ""

    research_context = f"\n\nBackground research:\n{research[:500]}" if research else ""

    for i, section in enumerate(blog_plan):
        title = section.get("title", f"Section {i+1}")
        goal = section.get("goal", "")
        bullets = section.get("bullets", [])
        word_count = section.get("word_count", 250)

        logs.append(f"✍️ Worker {i+1}: Writing '{title}'...")

        bullets_str = "\n".join([f"- {b}" for b in bullets])
        prompt = f"""You are writing a section of a blog post about: "{topic}"

Section title: {title}
Section goal: {goal}
Key points to cover:
{bullets_str}

{lang_instruction}Tone: {tone_instruction}
Target length: ~{word_count} words.{research_context}

Write the full section content in Markdown format. 
Start directly with the section content (do NOT repeat the title - it will be added separately).
Use subheadings (###), bullet points, and bold text where appropriate.
Make it engaging, informative, and well-structured.
"""

        content = llm_generate(prompt, max_tokens=600)

        # Clean up – remove any title repetition at start
        lines = content.strip().split("\n")
        if lines and (lines[0].startswith("#") or lines[0].strip().lower() == title.lower()):
            content = "\n".join(lines[1:]).strip()

        sections.append({"title": title, "content": content, "index": i})
        logs.append(f"   ✅ Section {i+1} written ({len(content.split())} words approx)")

    return {**state, "sections": sections, "logs": logs, "status": "sections_written"}


def reducer_node(state: BlogState) -> BlogState:
    """Merge all sections into final Markdown with image placeholders."""
    logs = state.get("logs", [])
    topic = state["topic"]
    tone = state.get("tone", "balanced")
    sections = state.get("sections", [])
    logs.append("🔗 Reducer: Merging sections into final Markdown...")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    tone_badge = {"technical": "🔬 Technical", "beginner": "🌱 Beginner-Friendly", "balanced": "⚖️ Balanced"}.get(tone, "")

    # Build markdown
    parts = []
    parts.append(f"# {topic}\n")
    parts.append(f"> **Generated by AI Blog System** | {timestamp} | {tone_badge}\n")
    parts.append("---\n")

    # Table of contents
    parts.append("## 📋 Table of Contents\n")
    for i, section in enumerate(sections):
        anchor = section['title'].lower().replace(' ', '-').replace(',', '').replace("'", "")
        parts.append(f"{i+1}. [{section['title']}](#{anchor})")
    parts.append("\n---\n")

    # Sections with image placeholders
    image_count = 0
    for i, section in enumerate(sections):
        parts.append(f"\n## {section['title']}\n")

        # Insert image placeholder every 2 sections
        if i % 2 == 0:
            parts.append(f"\n[[IMAGE_{image_count + 1}: {section['title']}]]\n")
            image_count += 1

        parts.append(section["content"])
        parts.append("\n")

    parts.append("\n---\n")
    parts.append(f"\n*This blog was automatically generated by the AI Blog Generation System on {timestamp}.*\n")

    final_markdown = "\n".join(parts)
    logs.append(f"✅ Final Markdown assembled: {len(final_markdown)} chars")

    return {**state, "final_markdown": final_markdown, "logs": logs, "status": "markdown_ready"}


def image_node(state: BlogState) -> BlogState:
    """Generate topic-relevant AI images via HuggingFace SDXL (with Pillow fallback)."""
    logs = state.get("logs", [])
    topic = state["topic"]
    final_markdown = state.get("final_markdown", "")

    using_ai = bool(HF_API_TOKEN)
    logs.append(f"🖼️ Image Node: {'HuggingFace SDXL' if using_ai else 'Pillow placeholder'} mode")

    pattern = r'\[\[IMAGE_(\d+): ([^\]]+)\]\]'
    matches = re.findall(pattern, final_markdown)

    image_paths = []
    updated_markdown = final_markdown

    for idx_str, label in matches:
        idx = int(idx_str) - 1
        if using_ai:
            logs.append(f"   🤖 AI generating image {idx+1}: '{label[:40]}...' (may take 30-90s)")
        else:
            logs.append(f"   🎨 Creating placeholder image {idx+1}: '{label[:40]}'")

        try:
            img_path = generate_image(label, idx, topic)
            image_paths.append(str(img_path))
            source = "AI-generated" if using_ai else "placeholder"
            logs.append(f"   ✅ Image {idx+1} saved ({source}): {img_path.name}")
        except Exception as e:
            logger.error(f"Image {idx+1} completely failed: {e}")
            # Emergency fallback
            img_path = generate_pillow_fallback(label, idx, topic)
            image_paths.append(str(img_path))
            logs.append(f"   ⚠️ Image {idx+1} used emergency fallback: {img_path.name}")

        placeholder = f"[[IMAGE_{idx_str}: {label}]]"
        img_md = f"![{label}](images/image_{idx_str}.png)\n*Figure {idx_str}: {label}*"
        updated_markdown = updated_markdown.replace(placeholder, img_md)

    logs.append(f"✅ {len(image_paths)} images ready")
    return {**state, "final_markdown": updated_markdown, "image_paths": image_paths, "logs": logs, "status": "images_done"}


def save_node(state: BlogState) -> BlogState:
    """Save the final blog markdown and metadata."""
    logs = state.get("logs", [])
    topic = state["topic"]
    final_markdown = state.get("final_markdown", "")
    logs.append("💾 Save Node: Writing output files...")

    # Sanitize topic for filename
    safe_topic = re.sub(r'[^\w\s-]', '', topic)[:50].strip().replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_topic}_{timestamp}.md"

    # Save to output dir
    blog_path = OUTPUT_DIR / "blog.md"
    blog_path.write_text(final_markdown, encoding="utf-8")

    # Also save to past_blogs with timestamp
    past_path = PAST_BLOGS_DIR / filename
    past_path.write_text(final_markdown, encoding="utf-8")

    # Save metadata
    meta = {
        "topic": topic,
        "tone": state.get("tone"),
        "language": state.get("language"),
        "mode": state.get("mode"),
        "timestamp": timestamp,
        "filename": filename,
        "sections": len(state.get("blog_plan", [])),
        "images": len(state.get("image_paths", [])),
    }
    meta_path = PAST_BLOGS_DIR / filename.replace(".md", ".json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    logs.append(f"✅ Blog saved: {blog_path}")
    logs.append(f"✅ Archive saved: {past_path}")
    logs.append(f"🎉 Generation complete!")

    return {**state, "logs": logs, "status": "complete"}


# ─────────────────────────────────────────────
# BUILD LANGGRAPH
# ─────────────────────────────────────────────
def build_graph():
    graph = StateGraph(BlogState)

    graph.add_node("router", router_node)
    graph.add_node("research", research_node)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("worker", worker_node)
    graph.add_node("reducer", reducer_node)
    graph.add_node("image_processor", image_node)
    graph.add_node("save", save_node)

    graph.set_entry_point("router")
    graph.add_edge("router", "research")
    graph.add_edge("research", "orchestrator")
    graph.add_edge("orchestrator", "worker")
    graph.add_edge("worker", "reducer")
    graph.add_edge("reducer", "image_processor")
    graph.add_edge("image_processor", "save")
    graph.add_edge("save", END)

    return graph.compile()


# ─────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────
def generate_blog(topic: str, tone: str = "balanced", language: str = "en") -> dict:
    """
    Main entry point. Returns dict with keys:
    - markdown, image_paths, logs, status, error
    """
    logger.info(f"Starting blog generation: '{topic}' | tone={tone} | lang={language}")

    initial_state: BlogState = {
        "topic": topic,
        "tone": tone,
        "language": language,
        "mode": "closed_book",
        "research_data": None,
        "blog_plan": None,
        "sections": None,
        "final_markdown": None,
        "image_paths": [],
        "logs": [f"🚀 Starting blog generation for: '{topic}'"],
        "error": None,
        "status": "starting",
    }

    try:
        app = build_graph()
        final_state = app.invoke(initial_state)
        return {
            "markdown": final_state.get("final_markdown", ""),
            "image_paths": final_state.get("image_paths", []),
            "logs": final_state.get("logs", []),
            "status": final_state.get("status", "unknown"),
            "blog_plan": final_state.get("blog_plan", []),
            "error": None,
        }
    except Exception as e:
        logger.error(f"Graph execution failed: {e}", exc_info=True)
        return {
            "markdown": "",
            "image_paths": [],
            "logs": [f"❌ Fatal error: {str(e)}"],
            "status": "error",
            "blog_plan": [],
            "error": str(e),
        }


def get_past_blogs() -> list:
    """Return list of previously generated blogs with metadata."""
    blogs = []
    for meta_file in sorted(PAST_BLOGS_DIR.glob("*.json"), reverse=True):
        try:
            meta = json.loads(meta_file.read_text())
            md_file = PAST_BLOGS_DIR / meta["filename"]
            meta["exists"] = md_file.exists()
            meta["path"] = str(md_file)
            blogs.append(meta)
        except Exception:
            pass
    return blogs


def export_pdf(markdown_text: str, output_path: str = None) -> str:
    """Export blog to PDF using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib import colors

    if not output_path:
        output_path = str(OUTPUT_DIR / "blog.pdf")

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=inch, rightMargin=inch,
                            topMargin=inch, bottomMargin=inch)

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=22, spaceAfter=12,
                         textColor=colors.HexColor("#1e3a5f"))
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=16, spaceAfter=8,
                         textColor=colors.HexColor("#2563eb"))
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=11, leading=16, spaceAfter=6)

    story = []
    for line in markdown_text.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
        elif line.startswith("# "):
            story.append(Paragraph(line[2:], h1))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563eb")))
        elif line.startswith("## "):
            story.append(Spacer(1, 12))
            story.append(Paragraph(line[3:], h2))
        elif line.startswith("### "):
            story.append(Paragraph(f"<b>{line[4:]}</b>", body))
        elif line.startswith("- ") or line.startswith("* "):
            story.append(Paragraph(f"• {line[2:]}", body))
        elif line.startswith("**") and line.endswith("**"):
            story.append(Paragraph(f"<b>{line[2:-2]}</b>", body))
        elif line.startswith("!["):
            continue  # Skip image markdown in PDF
        elif line.startswith(">"):
            quote_style = ParagraphStyle("Quote", parent=body, leftIndent=20,
                                          textColor=colors.HexColor("#6b7280"), fontSize=10)
            story.append(Paragraph(line[1:].strip(), quote_style))
        elif line.startswith("---"):
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
        else:
            # Clean markdown bold/italic for PDF
            cleaned = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
            cleaned = re.sub(r'\*(.+?)\*', r'<i>\1</i>', cleaned)
            if cleaned:
                story.append(Paragraph(cleaned, body))

    doc.build(story)
    logger.info(f"PDF exported: {output_path}")
    return output_path


if __name__ == "__main__":
    result = generate_blog("Docker and Kubernetes for Beginners", tone="beginner")
    print("\n=== LOGS ===")
    for log in result["logs"]:
        print(log)
    print(f"\n=== STATUS: {result['status']} ===")
    if result["markdown"]:
        print("\n=== PREVIEW (first 500 chars) ===")
        print(result["markdown"][:500])
