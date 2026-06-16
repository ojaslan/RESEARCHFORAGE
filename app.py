import streamlit as st
import pdfplumber
from groq import Groq
import json
import io
import time
from datetime import datetime

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Paper Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────────
# PREMIUM STYLING
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    min-height: 100vh;
}

.block-container {
    padding: 2.5rem 3rem !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* NAVIGATION BAR */
/* ════════════════════════════════════════════════════════════════════════════ */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.2rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    margin-bottom: 3rem;
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffffff;
}

.logo-icon {
    font-size: 1.8rem;
}

.nav-badge {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* HERO SECTION */
/* ════════════════════════════════════════════════════════════════════════════ */
.hero-section {
    text-align: center;
    margin-bottom: 3.5rem;
}

.hero-title {
    font-size: 3.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.8rem;
    letter-spacing: -0.02em;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.hero-description {
    font-size: 0.95rem;
    color: #cbd5e1;
    max-width: 600px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* INPUT SECTION */
/* ════════════════════════════════════════════════════════════════════════════ */
.input-container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.input-card {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 16px;
    padding: 1.8rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.input-card:hover {
    border-color: rgba(59, 130, 246, 0.4);
    background: rgba(30, 41, 59, 0.95);
    box-shadow: 0 0 30px rgba(59, 130, 246, 0.1);
}

.input-label {
    font-size: 0.85rem;
    font-weight: 700;
    color: #cbd5e1;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

.input-label-icon {
    font-size: 1.2rem;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* FILE UPLOADER */
/* ════════════════════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: transparent !important;
}

[data-testid="stFileUploader"] > div {
    border: 2px dashed rgba(59, 130, 246, 0.5) !important;
    border-radius: 12px !important;
    padding: 2rem !important;
    background: rgba(59, 130, 246, 0.05) !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"] > div:hover {
    border-color: #3b82f6 !important;
    background: rgba(59, 130, 246, 0.1) !important;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* TEXT INPUT */
/* ════════════════════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input {
    background: rgba(15, 23, 42, 0.5) !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    padding: 0.8rem 1rem !important;
    font-size: 0.9rem !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input::placeholder {
    color: #64748b !important;
}

.stTextInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.3) !important;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* BUTTONS */
/* ════════════════════════════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
    transform: translateY(-2px);
}

.stButton > button:active {
    transform: translateY(0);
}

.stDownloadButton > button {
    background: rgba(59, 130, 246, 0.2) !important;
    color: #3b82f6 !important;
    border: 1px solid #3b82f6 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.3s ease !important;
}

.stDownloadButton > button:hover {
    background: rgba(59, 130, 246, 0.3) !important;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* PROGRESS BAR */
/* ════════════════════════════════════════════════════════════════════════════ */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* SECTION TITLES */
/* ════════════════════════════════════════════════════════════════════════════ */
.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    margin: 2.5rem 0 1.5rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 1rem;
    border-bottom: 2px solid rgba(59, 130, 246, 0.3);
}

.section-icon {
    font-size: 1.8rem;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* PAPER INFO CARD */
/* ════════════════════════════════════════════════════════════════════════════ */
.paper-card {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(30, 41, 59, 0.8) 100%);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(10px);
}

.paper-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 1rem;
    line-height: 1.4;
}

.paper-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-bottom: 1.2rem;
    font-size: 0.9rem;
}

.meta-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #cbd5e1;
}

.meta-icon {
    font-size: 1.1rem;
    color: #3b82f6;
}

.keywords-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
}

.keyword-tag {
    background: rgba(59, 130, 246, 0.2);
    color: #60a5fa;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid rgba(96, 165, 250, 0.3);
    transition: all 0.3s ease;
}

.keyword-tag:hover {
    background: rgba(59, 130, 246, 0.3);
    border-color: #60a5fa;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* METRICS */
/* ════════════════════════════════════════════════════════════════════════════ */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.metric-card:hover {
    border-color: rgba(59, 130, 246, 0.4);
    background: rgba(30, 41, 59, 0.95);
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(59, 130, 246, 0.15);
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}

.metric-label {
    font-size: 0.75rem;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.05em;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* INSIGHT CARDS */
/* ════════════════════════════════════════════════════════════════════════════ */
.insight-card {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 14px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.insight-card:hover {
    border-color: rgba(59, 130, 246, 0.3);
    box-shadow: 0 12px 30px rgba(59, 130, 246, 0.1);
    transform: translateY(-2px);
}

.insight-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1rem;
}

.insight-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #60a5fa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.insight-icon {
    font-size: 1.3rem;
}

.insight-content {
    color: #cbd5e1;
    font-size: 0.95rem;
    line-height: 1.7;
}

.insight-content strong {
    color: #ffffff;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* GRID LAYOUT FOR INSIGHTS */
/* ════════════════════════════════════════════════════════════════════════════ */
.insights-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* STEP INDICATOR */
/* ════════════════════════════════════════════════════════════════════════════ */
.step-indicator {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 12px;
    animation: slideIn 0.3s ease;
}

.step-number {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    font-weight: 700;
    flex-shrink: 0;
    font-size: 0.9rem;
}

.step-text {
    color: #cbd5e1;
    font-size: 0.9rem;
    font-weight: 500;
}

.step-text strong {
    color: #60a5fa;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* MESSAGES */
/* ════════════════════════════════════════════════════════════════════════════ */
.stWarning {
    background: rgba(202, 138, 4, 0.1) !important;
    border: 1px solid rgba(202, 138, 4, 0.3) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}

.stError {
    background: rgba(220, 38, 38, 0.1) !important;
    border: 1px solid rgba(220, 38, 38, 0.3) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}

.stSuccess {
    background: rgba(34, 197, 94, 0.1) !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* EXPANDER */
/* ════════════════════════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: rgba(30, 41, 59, 0.8) !important;
    border: 1px solid rgba(148, 163, 184, 0.2) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}

.streamlit-expanderHeader:hover {
    background: rgba(30, 41, 59, 0.95) !important;
    border-color: rgba(59, 130, 246, 0.3) !important;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* EMPTY STATE */
/* ════════════════════════════════════════════════════════════════════════════ */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: rgba(30, 41, 59, 0.5);
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    margin: 2rem 0;
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
    opacity: 0.7;
}

.empty-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.5rem;
}

.empty-text {
    font-size: 0.95rem;
    color: #94a3b8;
    margin-bottom: 2rem;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* FEATURE CARDS */
/* ════════════════════════════════════════════════════════════════════════════ */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.2rem;
    margin-top: 2rem;
}

.feature-card {
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.feature-card:hover {
    border-color: rgba(59, 130, 246, 0.4);
    background: rgba(30, 41, 59, 0.95);
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(59, 130, 246, 0.1);
}

.feature-icon {
    font-size: 2rem;
    margin-bottom: 0.8rem;
}

.feature-name {
    font-weight: 600;
    color: #cbd5e1;
    font-size: 0.9rem;
    margin-bottom: 0.3rem;
}

.feature-desc {
    font-size: 0.75rem;
    color: #64748b;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* FOOTER INFO */
/* ════════════════════════════════════════════════════════════════════════════ */
.info-box {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 12px;
    padding: 1rem;
    color: #cbd5e1;
    font-size: 0.85rem;
    margin-top: 1.5rem;
}

.info-box strong {
    color: #60a5fa;
}

/* ════════════════════════════════════════════════════════════════════════════ */
/* RESPONSIVE */
/* ════════════════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .input-container {
        grid-template-columns: 1fr;
    }
    
    .hero-title {
        font-size: 2.2rem;
    }
    
    .metrics-grid {
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    }
    
    .section-title {
        font-size: 1.2rem;
    }
}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(30, 41, 59, 0.5);
}

::-webkit-scrollbar-thumb {
    background: rgba(59, 130, 246, 0.4);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(59, 130, 246, 0.6);
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def extract_pdf_text(file) -> str:
    """Extract text from PDF file."""
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file.read())) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"❌ Error extracting PDF: {str(e)}")
        return ""

def call_groq_agent(client: Groq, system_prompt: str, user_prompt: str) -> str:
    """Call Groq API."""
    try:
        response = client.messages.create(
            model="mixtral-8x7b-32768",
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        st.error(f"❌ Groq API Error: {str(e)}")
        return ""

def run_agent_pipeline(paper_text: str, api_key: str):
    """Run 7-step analysis pipeline."""
    
    client = Groq(api_key=api_key)
    truncated = paper_text[:12000]
    
    results = {}
    steps = [
        ("metadata",      "📋 Extracting metadata"),
        ("summary",       "📝 Summarizing contribution"),
        ("methodology",   "🔬 Analyzing methodology"),
        ("findings",      "💡 Extracting key findings"),
        ("limitations",   "⚠️ Identifying limitations"),
        ("future_work",   "🚀 Extracting future work"),
        ("critical",      "🧠 Generating critical review"),
    ]
    
    progress_bar = st.progress(0)
    status_container = st.container()
    
    for i, (key, label) in enumerate(steps):
        with status_container:
            st.markdown(f"""
            <div class='step-indicator'>
                <div class='step-number'>{i+1}</div>
                <div class='step-text'>
                    <strong>Step {i+1}/7</strong> — {label}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if key == "metadata":
            result = call_groq_agent(
                client,
                "You are a research paper analyst. Extract metadata and return ONLY valid JSON with keys: title, authors (list), year, domain, keywords (list of 5). No extra text.",
                f"Extract from this paper:\n\n{truncated[:3000]}"
            )
            try:
                clean = result.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                results[key] = json.loads(clean)
            except:
                results[key] = {"title": "Unknown", "authors": [], "year": "—", "domain": "—", "keywords": []}
        
        elif key == "summary":
            result = call_groq_agent(
                client,
                "You are a research paper analyst. Write a clear 3-4 sentence summary of the paper's core contribution and problem it solves. Be concise and precise.",
                f"Paper text:\n\n{truncated[:6000]}"
            )
            results[key] = result
        
        elif key == "methodology":
            result = call_groq_agent(
                client,
                "You are a research paper analyst. Extract the methodology used. List the main steps, techniques, datasets, and models used. Use bullet points. Be specific.",
                f"Paper text:\n\n{truncated}"
            )
            results[key] = result
        
        elif key == "findings":
            result = call_groq_agent(
                client,
                "You are a research paper analyst. List the key findings and results of this paper. Include numbers/metrics if mentioned. Use bullet points. Be specific and factual.",
                f"Paper text:\n\n{truncated}"
            )
            results[key] = result
        
        elif key == "limitations":
            result = call_groq_agent(
                client,
                "You are a research paper analyst. Identify and explain the main limitations of this paper. What are the weaknesses, gaps, or constraints? Use bullet points.",
                f"Paper text:\n\n{truncated}"
            )
            results[key] = result
        
        elif key == "future_work":
            result = call_groq_agent(
                client,
                "You are a research paper analyst. Extract future research directions mentioned or implied by this paper. What should be built or studied next? Use bullet points.",
                f"Paper text:\n\n{truncated}"
            )
            results[key] = result
        
        elif key == "critical":
            result = call_groq_agent(
                client,
                "You are a senior academic reviewer. Write a brief critical review of this paper (3-5 sentences). Comment on novelty, rigor, clarity, and impact. Be balanced and honest.",
                f"Paper text:\n\n{truncated[:6000]}"
            )
            results[key] = result
        
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(0.3)
    
    progress_bar.empty()
    return results

# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────

if "results" not in st.session_state:
    st.session_state.results = None
if "paper_text" not in st.session_state:
    st.session_state.paper_text = ""
if "filename" not in st.session_state:
    st.session_state.filename = ""

# ──────────────────────────────────────────────────────────────────────────────
# NAVBAR
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='navbar'>
    <div class='logo'>
        <div class='logo-icon'>🔬</div>
        <div>Research Paper Analyzer</div>
    </div>
    <div class='nav-badge'>Powered by Groq</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# HERO SECTION
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='hero-section'>
    <div class='hero-title'>
        Intelligent Research Paper Analysis
    </div>
    <div class='hero-subtitle'>
        ⚡ Powered by Groq's Ultra-Fast AI
    </div>
    <div class='hero-description'>
        Upload any research paper and get comprehensive insights in seconds. 
        7 intelligent steps extract metadata, methodology, findings, and more.
    </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# INPUT SECTION
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div style='margin-bottom: 2rem;'>
    <h3 style='color: #ffffff; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;'>
        📥 Upload & Configure
    </h3>
</div>
""", unsafe_allow_html=True)

col_upload, col_key = st.columns([2, 1])

with col_upload:
    st.markdown("""
    <div class='input-card'>
        <div class='input-label'>
            <span class='input-label-icon'>📄</span>
            <span>Research Paper (PDF)</span>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        label_visibility="collapsed",
        help="Drag & drop or click to upload"
    )
    if uploaded_file:
        st.session_state.filename = uploaded_file.name
        st.markdown(f"<p style='color: #60a5fa; font-size: 0.85rem; margin-top: 0.5rem;'>✓ {uploaded_file.name}</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

with col_key:
    st.markdown("""
    <div class='input-card'>
        <div class='input-label'>
            <span class='input-label-icon'>🔑</span>
            <span>API Key</span>
        </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="gsk_...",
        label_visibility="collapsed",
        help="From console.groq.com"
    )
    
    st.markdown("""
    <p style='color: #64748b; font-size: 0.75rem; margin-top: 0.5rem;'>
        🔒 Never stored. Session only.
    </p>
    </div>
    """, unsafe_allow_html=True)

# Analyze button
st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
analyze_btn = st.button("🚀 Analyze Paper", use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────────
# RUN ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────

if analyze_btn:
    if not uploaded_file:
        st.warning("📄 Please upload a research paper PDF first.")
    elif not api_key:
        st.warning("🔑 Please enter your Groq API key.")
    elif not api_key.startswith("gsk_"):
        st.warning("⚠️ API key should start with 'gsk_'. Get one from console.groq.com")
    else:
        with st.spinner("Processing your paper..."):
            try:
                uploaded_file.seek(0)
                paper_text = extract_pdf_text(uploaded_file)
                
                if len(paper_text) < 200:
                    st.error("❌ Could not extract enough text. Try another PDF.")
                else:
                    st.session_state.paper_text = paper_text
                    
                    st.markdown("""
                    <h2 class='section-title'>
                        <span class='section-icon'>⚙️</span>
                        Analyzing Your Paper
                    </h2>
                    """, unsafe_allow_html=True)
                    
                    results = run_agent_pipeline(paper_text, api_key)
                    st.session_state.results = results
                    st.rerun()
            
            except Exception as e:
                if "401" in str(e) or "Unauthorized" in str(e) or "invalid" in str(e).lower():
                    st.error("❌ Invalid Groq API key. Check console.groq.com")
                elif "rate" in str(e).lower():
                    st.error("⏳ Rate limit reached. Try again in a moment.")
                else:
                    st.error(f"❌ Error: {str(e)}")

# ──────────────────────────────────────────────────────────────────────────────
# RESULTS DISPLAY
# ──────────────────────────────────────────────────────────────────────────────

if st.session_state.results:
    r = st.session_state.results
    meta = r.get("metadata", {})
    
    # PAPER INFO
    st.markdown("""
    <h2 class='section-title'>
        <span class='section-icon'>📑</span>
        Paper Information
    </h2>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='paper-card'>
        <div class='paper-title'>{meta.get('title', st.session_state.filename)}</div>
        <div class='paper-meta'>
            <div class='meta-item'>
                <span class='meta-icon'>👥</span>
                <span>{", ".join(meta.get("authors", [])) or "Authors not detected"}</span>
            </div>
            <div class='meta-item'>
                <span class='meta-icon'>📅</span>
                <span>{meta.get("year", "—")}</span>
            </div>
            <div class='meta-item'>
                <span class='meta-icon'>🏷️</span>
                <span>{meta.get("domain", "—")}</span>
            </div>
        </div>
        <div class='keywords-container'>
            {"".join(f"<span class='keyword-tag'>{k}</span>" for k in meta.get("keywords", []))}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # METRICS
    st.markdown("""
    <h2 class='section-title'>
        <span class='section-icon'>📊</span>
        Analysis Metrics
    </h2>
    """, unsafe_allow_html=True)
    
    words = len(st.session_state.paper_text.split())
    pages_est = max(1, words // 300)
    findings = r.get("findings", "").count("•") + r.get("findings", "").count("-") + 1
    lims = r.get("limitations", "").count("•") + r.get("limitations", "").count("-") + 1
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{words:,}</div>
            <div class='metric-label'>Words</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>~{pages_est}</div>
            <div class='metric-label'>Pages</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{min(findings, 9)}</div>
            <div class='metric-label'>Findings</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{min(lims, 7)}</div>
            <div class='metric-label'>Limitations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>7</div>
            <div class='metric-label'>Steps</div>
        </div>
        """, unsafe_allow_html=True)
    
    # SUMMARY
    st.markdown("""
    <h2 class='section-title'>
        <span class='section-icon'>💡</span>
        Core Contribution
    </h2>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='insight-card'>
        <div class='insight-header'>
            <span class='insight-icon'>📝</span>
            <span class='insight-title'>Summary</span>
        </div>
        <div class='insight-content'>{r.get("summary", "—")}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # CRITICAL REVIEW
    st.markdown(f"""
    <div class='insight-card' style='border-color: rgba(168, 85, 247, 0.3); background: rgba(168, 85, 247, 0.05);'>
        <div class='insight-header'>
            <span class='insight-icon'>🧠</span>
            <span class='insight-title' style='color: #d8b4fe;'>Critical Review</span>
        </div>
        <div class='insight-content'>{r.get("critical", "—")}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # DETAILED INSIGHTS
    st.markdown("""
    <h2 class='section-title'>
        <span class='section-icon'>🔍</span>
        Detailed Insights
    </h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-header'>
                <span class='insight-icon'>🔬</span>
                <span class='insight-title' style='color: #86efac;'>Methodology</span>
            </div>
            <div class='insight-content' style='white-space: pre-wrap;'>{r.get("methodology", "—")}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-header'>
                <span class='insight-icon'>📈</span>
                <span class='insight-title' style='color: #fbbf24;'>Key Findings</span>
            </div>
            <div class='insight-content' style='white-space: pre-wrap;'>{r.get("findings", "—")}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='insight-card'>
            <div class='insight-header'>
                <span class='insight-icon'>⚠️</span>
                <span class='insight-title' style='color: #f87171;'>Limitations</span>
            </div>
            <div class='insight-content' style='white-space: pre-wrap;'>{r.get("limitations", "—")}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # FUTURE WORK
    st.markdown("""
    <h2 class='section-title'>
        <span class='section-icon'>🚀</span>
        Future Directions
    </h2>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='insight-card' style='border-color: rgba(34, 197, 94, 0.3); background: rgba(34, 197, 94, 0.05);'>
        <div class='insight-header'>
            <span class='insight-icon'>🎯</span>
            <span class='insight-title' style='color: #86efac;'>Future Work</span>
        </div>
        <div class='insight-content' style='white-space: pre-wrap;'>{r.get("future_work", "—")}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # EXPORT
    st.markdown("""
    <h2 class='section-title'>
        <span class='section-icon'>⬇️</span>
        Export Results
    </h2>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    report = f"""RESEARCH INSIGHT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Tool: Research Paper Analyzer (Powered by Groq)
{'='*70}

PAPER INFORMATION
{'='*70}
Title: {meta.get('title', '—')}
Authors: {", ".join(meta.get('authors', [])) or '—'}
Year: {meta.get('year', '—')}
Domain: {meta.get('domain', '—')}
Keywords: {", ".join(meta.get('keywords', [])) or '—'}

{'='*70}
SUMMARY
{'='*70}
{r.get('summary', '—')}

{'='*70}
METHODOLOGY
{'='*70}
{r.get('methodology', '—')}

{'='*70}
KEY FINDINGS
{'='*70}
{r.get('findings', '—')}

{'='*70}
LIMITATIONS
{'='*70}
{r.get('limitations', '—')}

{'='*70}
FUTURE WORK
{'='*70}
{r.get('future_work', '—')}

{'='*70}
CRITICAL REVIEW
{'='*70}
{r.get('critical', '—')}

{'='*70}
END OF REPORT
{'='*70}
"""
    
    with col1:
        st.download_button(
            "📄 Download Report (TXT)",
            data=report,
            file_name=f"report_{meta.get('title', 'paper')[:25].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    
    with col2:
        st.download_button(
            "📊 Download Data (JSON)",
            data=json.dumps(r, indent=2),
            file_name=f"data_{meta.get('title', 'paper')[:25].replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
        )
    
    # RAW TEXT
    with st.expander("📄 View Extracted PDF Text"):
        st.text_area(
            "Raw Text",
            value=st.session_state.paper_text[:3000] + "\n\n[... truncated ...]",
            height=250,
            label_visibility="collapsed"
        )
    
    # RESET
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Analyze Another Paper", use_container_width=True):
        st.session_state.results = None
        st.session_state.paper_text = ""
        st.session_state.filename = ""
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# EMPTY STATE
# ──────────────────────────────────────────────────────────────────────────────

if not st.session_state.results and not analyze_btn:
    st.markdown("""
    <div class='empty-state'>
        <div class='empty-icon'>📚</div>
        <div class='empty-title'>Ready to Analyze</div>
        <div class='empty-text'>
            Upload a research paper and enter your Groq API key to begin intelligent analysis
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h3 style='color: #cbd5e1; margin-top: 3rem; margin-bottom: 1.5rem; font-size: 1.1rem;'>
        ✨ What You Get
    </h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>📋</div>
            <div class='feature-name'>Smart Metadata</div>
            <div class='feature-desc'>Title, authors, year, domain, keywords</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>⚙️</div>
            <div class='feature-name'>7-Step Analysis</div>
            <div class='feature-desc'>Summary, methodology, findings, limits</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>⚡</div>
            <div class='feature-name'>Lightning Fast</div>
            <div class='feature-desc'>Results in 4-6 seconds powered by Groq</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
        <strong>🔑 Need a Groq API Key?</strong><br>
        Get a free key in 2 minutes at <strong><a href='https://console.groq.com' target='_blank'>console.groq.com</a></strong>
    </div>
    """, unsafe_allow_html=True)