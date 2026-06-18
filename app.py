import streamlit as st
import pdfplumber
from groq import Groq
import json
import io
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# ──────────────────────────────────────────────────────────────────────────────
# LOAD ENVIRONMENT VARIABLES
# ──────────────────────────────────────────────────────────────────────────────
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ Error: GROQ_API_KEY not found in .env file!")
    st.info("Please create a .env file with: GROQ_API_KEY=gsk_your_key_here")
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RESEARCHFORAGE",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────────────────────────
# STYLING
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Poppins', sans-serif !important; }
.stApp { background: #f5f7fa; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1200px !important; }

.header {
    text-align: center;
    margin-bottom: 2.5rem;
    padding: 2.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    color: white;
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.main-title { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }
.subtitle { font-size: 1rem; opacity: 0.9; }

.card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    transition: all 0.3s ease;
}

.card:hover {
    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    border-color: #667eea;
}

.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: #333;
    margin-top: 2rem;
    margin-bottom: 1rem;
    padding-bottom: 0.8rem;
    border-bottom: 3px solid #667eea;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3) !important;
}

.metadata-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 1.5rem 0;
}

.meta-item {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
}

.meta-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #667eea;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}

.meta-value {
    color: #333;
    font-weight: 600;
    font-size: 0.95rem;
}

.content-text {
    font-size: 0.95rem;
    line-height: 1.8;
    color: #444;
}

.progress-container {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin: 1rem 0;
}

@media (max-width: 768px) {
    .main-title { font-size: 1.8rem; }
    .section-header { font-size: 1.2rem; }
    .metadata-grid { grid-template-columns: 1fr; }
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
        st.error(f"❌ Error reading PDF: {str(e)}")
        return ""

def call_groq_agent(client: Groq, system_prompt: str, user_prompt: str) -> str:
    """Call Groq API with proper error handling."""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.warning(f"⚠️ API Error: {str(e)}")
        return "Information not available"

def run_analysis_pipeline(paper_text: str, api_key: str):
    """Run comprehensive analysis pipeline."""
    
    client = Groq(api_key=api_key)
    truncated = paper_text[:15000]
    
    results = {}
    
    steps = [
        ("metadata", "📋 Extracting Paper Details",
         """You are an expert research analyst. Extract the following metadata from the paper.
         Return ONLY valid JSON (no markdown, no extra text) with these exact keys:
         {
            "title": "exact paper title",
            "authors": ["author1", "author2"],
            "year": "publication year or 'Not found'",
            "domain": "research domain/field",
            "institution": "author institution or 'Not found'",
            "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
         }"""),
        
        ("problem_statement", "🎯 Understanding The Problem",
         """Explain what problem this research paper solves. Be specific and detailed:
         - What is the main problem?
         - Why is this problem important?
         - What was the gap in existing research?
         Write 2-3 clear paragraphs. Use simple language."""),
        
        ("objectives", "🎯 Research Objectives",
         """What are the specific objectives and goals of this research? List them clearly:
         - Main objective
         - Specific goals
         - What they want to achieve
         Make it clear and understandable. Use bullet points."""),
        
        ("methodology", "🔬 Research Methodology",
         """Explain HOW the researchers conducted this study. Be detailed:
         - What methods did they use?
         - What data/dataset did they use?
         - What tools, frameworks, or algorithms?
         - How many participants/samples?
         - What was the experimental setup?
         Be specific and technical but clear. Use bullet points."""),
        
        ("key_results", "📊 Key Results & Findings",
         """What are the main results and findings? Be specific with numbers:
         - What percentage/numbers did they achieve?
         - What were the main discoveries?
         - How do results compare to previous work?
         - What metrics improved?
         Include actual numbers and percentages. Use bullet points."""),
        
        ("conclusions", "💡 Conclusions & Impact",
         """What are the main conclusions? Why do these findings matter?
         - What do the findings mean?
         - What is the real-world impact?
         - What contributions does this make to the field?
         - Who benefits from this research?
         Be specific about impact. Use 2-3 paragraphs."""),
        
        ("strengths", "✅ Strengths",
         """What are the main strengths of this paper?
         - What did they do well?
         - What is innovative or novel?
         - What are the advantages of their approach?
         List specific strengths. Use bullet points."""),
        
        ("limitations", "⚠️ Limitations & Weaknesses",
         """What are the limitations and weaknesses?
         - What couldn't they test?
         - What are the constraints?
         - What could be improved?
         - Are there any flaws in the methodology?
         Be honest and specific. Use bullet points."""),
        
        ("future_work", "🚀 Future Research Directions",
         """What future research does this paper suggest?
         - What should be studied next?
         - How can this work be improved?
         - What new questions does this raise?
         - What applications could be explored?
         Be specific about next steps. Use bullet points."""),
        
        ("practical_applications", "💼 Real-World Applications",
         """What are the practical, real-world applications of this research?
         - How can this be used in practice?
         - What industries or fields benefit?
         - What products or services could use this?
         Be specific and concrete. Use bullet points."""),
    ]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, (key, label, system_msg) in enumerate(steps):
        status_text.text(f"⏳ {label}")
        
        if key == "metadata":
            result = call_groq_agent(client, system_msg, f"Extract from:\n\n{truncated[:4000]}")
            try:
                if "```json" in result:
                    result = result.split("```json")[1].split("```")[0]
                elif "```" in result:
                    result = result.split("```")[1].split("```")[0]
                results[key] = json.loads(result.strip())
            except:
                results[key] = {
                    "title": "Title Not Found",
                    "authors": ["Unknown"],
                    "year": "Not found",
                    "domain": "Research",
                    "institution": "Not found",
                    "keywords": ["research", "study", "analysis", "data", "method"]
                }
        else:
            result = call_groq_agent(client, system_msg, f"Paper content:\n\n{truncated}")
            results[key] = result
        
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(0.1)
    
    status_text.empty()
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
# HEADER
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class='header'>
    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📊</div>
    <div class='main-title'>RESEARCHFORAGE</div>
    <div class='subtitle'>Professional Research Paper Analysis & Insights</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# INPUT SECTION
# ──────────────────────────────────────────────────────────────────────────────

st.markdown("### 📤 Upload Research Paper")

uploaded_file = st.file_uploader("Select PDF file", type=["pdf"], help="Upload research paper in PDF format")

if uploaded_file:
    st.session_state.filename = uploaded_file.name
    st.success(f"✅ Loaded: {uploaded_file.name}")
    
    analyze_btn = st.button("🚀 Analyze Paper", use_container_width=True, type="primary")
    
    # ──────────────────────────────────────────────────────────────────────────────
    # RUN ANALYSIS
    # ──────────────────────────────────────────────────────────────────────────────
    
    if analyze_btn:
        with st.spinner("🔄 Analyzing paper... This may take 1-2 minutes"):
            try:
                uploaded_file.seek(0)
                paper_text = extract_pdf_text(uploaded_file)
                
                if len(paper_text) < 300:
                    st.error("❌ Could not extract enough text from PDF. Try another file.")
                else:
                    st.session_state.paper_text = paper_text
                    results = run_analysis_pipeline(paper_text, GROQ_API_KEY)
                    st.session_state.results = results
                    st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ──────────────────────────────────────────────────────────────────────────────
# RESULTS DISPLAY
# ──────────────────────────────────────────────────────────────────────────────

if st.session_state.results:
    r = st.session_state.results
    meta = r.get("metadata", {})
    
    # ════════════════════════════════════════════════════════════════════════
    # PAPER METADATA
    # ════════════════════════════════════════════════════════════════════════
    
    st.markdown(f"### 📑 Paper Details")
    
    st.markdown(f"""
    <div class='card'>
        <h3 style='color: #333; margin-bottom: 0.5rem;'>{meta.get('title', 'Unknown Title')}</h3>
        <div class='metadata-grid'>
            <div class='meta-item'>
                <div class='meta-label'>👥 Authors</div>
                <div class='meta-value'>{', '.join(meta.get('authors', ['Unknown'])) if meta.get('authors') else 'Unknown'}</div>
            </div>
            <div class='meta-item'>
                <div class='meta-label'>📅 Year</div>
                <div class='meta-value'>{meta.get('year', 'Not found')}</div>
            </div>
            <div class='meta-item'>
                <div class='meta-label'>🏛️ Institution</div>
                <div class='meta-value'>{meta.get('institution', 'Not found')}</div>
            </div>
            <div class='meta-item'>
                <div class='meta-label'>🏷️ Domain</div>
                <div class='meta-value'>{meta.get('domain', 'Research')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Keywords
    if meta.get('keywords'):
        st.markdown("**🔑 Keywords:**")
        keyword_html = " ".join([f"<span style='background: #e8eef7; color: #667eea; padding: 0.4rem 0.8rem; border-radius: 20px; margin: 0.2rem; display: inline-block; font-size: 0.85rem; font-weight: 600;'>{kw}</span>" for kw in meta.get('keywords', [])])
        st.markdown(keyword_html, unsafe_allow_html=True)
    
    # ════════════════════════════════════════════════════════════════════════
    # PROBLEM & OBJECTIVES
    # ════════════════════════════════════════════════════════════════════════
    
    st.markdown("### 🎯 Problem & Objectives")
    
    st.markdown(f"""
    <div class='card'>
        <h4 style='color: #333; margin-bottom: 1rem;'>The Problem</h4>
        <div class='content-text'>{r.get('problem_statement', 'Not available')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='card'>
        <h4 style='color: #333; margin-bottom: 1rem;'>Research Objectives</h4>
        <div class='content-text'>{r.get('objectives', 'Not available')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ════════════════════════════════════════════════════════════════════════
    # METHODOLOGY
    # ════════════════════════════════════════════════════════════════════════
    
    st.markdown("### 🔬 Research Methodology")
    
    st.markdown(f"""
    <div class='card'>
        <div class='content-text'>{r.get('methodology', 'Not available')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ════════════════════════════════════════════════════════════════════════
    # RESULTS & FINDINGS
    # ════════════════════════════════════════════════════════════════════════
    
    st.markdown("### 📊 Results & Findings")
    
    st.markdown(f"""
    <div class='card' style='border-left: 5px solid #28a745;'>
        <div class='content-text'>{r.get('key_results', 'Not available')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ════════════════════════════════════════════════════════════════════════
    # CONCLUSIONS & IMPACT
    # ════════════════════════════════════════════════════════════════════════
    
    st.markdown("### 💡 Conclusions & Impact")
    
    st.markdown(f"""
    <div class='card' style='border-left: 5px solid #667eea;'>
        <div class='content-text'>{r.get('conclusions', 'Not available')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ════════════════════════════════════════════════════════════════════════
    # STRENGTHS & WEAKNESSES
    # ════════════════════════════════════════════════════════════════════════
    
    st.markdown("### ✅ Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""<h4 style='color: #28a745; margin-bottom: 1rem;'>✅ Strengths</h4>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='card'>
            <div class='content-text'>{r.get('strengths', 'Not available')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""<h4 style='color: #dc3545; margin-bottom: 1rem;'>⚠️ Limitations</h4>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='card'>
            <div class='content-text'>{r.get('limitations', 'Not available')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ════════════════════════════════════════════════════════════════════════
    # APPLICATIONS & FUTURE WORK
    # ════════════════════════════════════════════════════════════════════════
    
    st.markdown("### 🚀 Applications & Future Work")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""<h4 style='color: #667eea; margin-bottom: 1rem;'>💼 Practical Applications</h4>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='card'>
            <div class='content-text'>{r.get('practical_applications', 'Not available')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""<h4 style='color: #764ba2; margin-bottom: 1rem;'>🔮 Future Research</h4>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='card'>
            <div class='content-text'>{r.get('future_work', 'Not available')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ════════════════════════════════════════════════════════════════════════
    # EXPORT SECTION
    # ════════════════════════════════════════════════════════════════════════
    
    st.markdown("### 📥 Export Options")
    
    # Generate exports
    def generate_text_report():
        report = f"""
{'='*80}
RESEARCH PAPER ANALYSIS REPORT
{'='*80}

PAPER INFORMATION
{'-'*80}
Title:          {meta.get('title', 'Unknown')}
Authors:        {', '.join(meta.get('authors', ['Unknown'])) if meta.get('authors') else 'Unknown'}
Year:           {meta.get('year', 'Not found')}
Domain:         {meta.get('domain', 'Research')}
Institution:    {meta.get('institution', 'Not found')}
Keywords:       {', '.join(meta.get('keywords', [])) if meta.get('keywords') else 'Not found'}

{'='*80}
PROBLEM STATEMENT
{'-'*80}
{r.get('problem_statement', 'Not available')}

{'='*80}
RESEARCH OBJECTIVES
{'-'*80}
{r.get('objectives', 'Not available')}

{'='*80}
METHODOLOGY
{'-'*80}
{r.get('methodology', 'Not available')}

{'='*80}
RESULTS & FINDINGS
{'-'*80}
{r.get('key_results', 'Not available')}

{'='*80}
CONCLUSIONS & IMPACT
{'-'*80}
{r.get('conclusions', 'Not available')}

{'='*80}
STRENGTHS
{'-'*80}
{r.get('strengths', 'Not available')}

{'='*80}
LIMITATIONS
{'-'*80}
{r.get('limitations', 'Not available')}

{'='*80}
PRACTICAL APPLICATIONS
{'-'*80}
{r.get('practical_applications', 'Not available')}

{'='*80}
FUTURE RESEARCH DIRECTIONS
{'-'*80}
{r.get('future_work', 'Not available')}

{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Tool: Paper Intelligence
{'='*80}
"""
        return report
    
    def generate_json_export():
        return json.dumps(r, indent=2)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        report_text = generate_text_report()
        st.download_button(
            "📄 Download as Text Report",
            data=report_text,
            file_name=f"analysis_{meta.get('title', 'paper')[:40].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        json_data = generate_json_export()
        st.download_button(
            "📊 Download as JSON",
            data=json_data,
            file_name=f"analysis_{meta.get('title', 'paper')[:40].replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 Analyze Another Paper", use_container_width=True):
            st.session_state.results = None
            st.session_state.paper_text = ""
            st.session_state.filename = ""
            st.rerun()

# ──────────────────────────────────────────────────────────────────────────────
# EMPTY STATE
# ──────────────────────────────────────────────────────────────────────────────

else:
    st.markdown("""
    <div style='text-align: center; padding: 3rem 2rem; background: white; 
                border-radius: 10px; border: 2px dashed #ccc; margin: 2rem 0;'>
        <div style='font-size: 3rem; margin-bottom: 1rem;'>📚</div>
        <h3>Start Analyzing Research Papers</h3>
        <p style='color: #666; margin: 1rem 0;'>
            Upload a PDF research paper and get a comprehensive analysis with:
        </p>
        <ul style='list-style: none; color: #666; margin: 1rem 0;'>
            <li>✅ Paper metadata extraction</li>
            <li>✅ Problem & objectives analysis</li>
            <li>✅ Detailed methodology review</li>
            <li>✅ Results & findings summary</li>
            <li>✅ Strengths & limitations assessment</li>
            <li>✅ Practical applications & future work</li>
            <li>✅ Multiple export formats</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎯 Features
    
    **Paper Intelligence** uses advanced AI to analyze research papers and extract:
    - **Problem Identification**: What problem does this paper solve?
    - **Methodology**: How was the research conducted?
    - **Results**: What were the key findings?
    - **Impact**: What are the real-world applications?
    - **Evaluation**: What are the strengths and limitations?
    
    ### 📋 How to Use
    
    1. Upload a research paper (PDF format)
    2. Click "Analyze Paper"
    3. Wait 1-2 minutes for analysis
    4. Download results as Text or JSON
    
    ### 👥 Perfect For
    
    - 👨‍🎓 Students reviewing papers
    - 👨‍💼 Researchers analyzing related work
    - 📊 Professionals understanding technical papers
    - 🎯 Teams evaluating research findings
    """)
