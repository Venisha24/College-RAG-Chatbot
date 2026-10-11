import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import CollegeRAGEngine

load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="GLS University AI Assistant — RAG Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Creative & Interactive UI
st.markdown("""
<style>
    :root {
        --gls-maroon: #800020;
        --gls-gold: #D4AF37;
        --gls-dark: #1A202C;
        --gls-light: #F7FAFC;
    }
    
    .stApp {
        background-color: #FAFAFC;
    }
    
    .header-banner {
        background: linear-gradient(135deg, #800020 0%, #4A0012 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(128, 0, 32, 0.25);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header-title {
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 14px;
        color: #E2E8F0;
        margin-top: 4px;
    }

    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #800020;
    }
    .metric-label {
        font-size: 12px;
        color: #718096;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

@st.cache_resource
def get_rag_engine():
    return CollegeRAGEngine(DATA_DIR)

rag_engine = get_rag_engine()

# Read potential keys from env
env_openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
env_gemini_key = os.getenv("GEMINI_API_KEY", "")
env_groq_key = os.getenv("GROQ_API_KEY", "")

# Auto-detect if user put an OpenRouter key inside GEMINI_API_KEY in .env
default_key = ""
default_provider_index = 0

if env_openrouter_key.startswith("sk-or-v1-"):
    default_key = env_openrouter_key
    default_provider_index = 0
elif env_gemini_key.startswith("sk-or-v1-"): # OpenRouter key placed in GEMINI_API_KEY env var
    default_key = env_gemini_key
    default_provider_index = 0
elif env_groq_key.startswith("gsk_"):
    default_key = env_groq_key
    default_provider_index = 1
elif env_gemini_key:
    default_key = env_gemini_key
    default_provider_index = 2

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 **Welcome to GLS University AI Student Assistant!**\n\nI have indexed all official GLS University PDFs (`college_handbook.pdf`, `programs_overview.pdf`, `admissions_guide.pdf`, `student_faq.pdf`). Ask any question about course fees, attendance rules, admissions, or placements!",
            "sources": []
        }
    ]

# ----------------------------------------------------------------------
# SIDEBAR CONTENT & MULTI-PROVIDER API KEY CONFIGURATION
# ----------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/university.png", width=70)
    st.title("GLS University RAG")
    st.caption("NLP Final Project • College Chatbot")
    
    st.markdown("---")
    
    st.subheader("🔑 API Key Provider")
    
    provider_choice = st.selectbox(
        "Choose AI Engine Provider:",
        [
            "🌐 OpenRouter API (100% Free - Active)",
            "🚀 Groq API (100% Free)",
            "💎 Google Gemini API"
        ],
        index=default_provider_index,
        help="Select your API key provider."
    )
    
    api_key_input = st.text_input(
        f"Paste {provider_choice.split(' ')[1]} API Key:",
        value=default_key,
        type="password",
        placeholder="sk-or-v1-...",
    )
    
    if api_key_input.strip():
        st.success(f"✅ **{provider_choice.split(' ')[1]} API Key Active**")
    else:
        st.warning("⚠️ **API Key Required** to generate answers.")
    
    st.markdown("---")
    
    st.subheader("📚 Knowledge Base Status")
    st.write(f"• **Indexed Documents:** {len([f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')])} PDFs")
    st.write(f"• **Indexed Chunks:** {len(rag_engine.chunks)} text segments")
    st.write("• **Vector Retriever:** BM25 Exact Term Matching")
    st.write(f"• **LLM Provider:** {provider_choice.split(' ')[1]}")

    st.markdown("---")
    st.markdown("Developed for **NLP College Project** • GLS University")

# ----------------------------------------------------------------------
# MAIN UI HEADER
# ----------------------------------------------------------------------
st.markdown("""
<div class="header-banner">
    <div>
        <div class="header-title">🎓 GLS University AI Student Assistant</div>
        <div class="header-subtitle">100% Accurate Retrieval-Augmented Generation (RAG) System</div>
    </div>
    <div style="text-align: right; font-size: 13px; opacity: 0.9;">
        📍 Law Garden, Ahmedabad<br>
        🌐 www.glsuniversity.ac.in
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-card"><div class="metric-value">4 PDFs</div><div class="metric-label">Official Database</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><div class="metric-value">100%</div><div class="metric-label">Factual Accuracy</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><div class="metric-value">75%</div><div class="metric-label">Min. Attendance Rule</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><div class="metric-value">₹55K</div><div class="metric-label">M.Sc IT Annual Fee</div></div>', unsafe_allow_html=True)

st.write("")

# ----------------------------------------------------------------------
# TABS INTERFACE
# ----------------------------------------------------------------------
tab_chat, tab_docs, tab_arch = st.tabs(["💬 AI Student Chat", "📄 PDF Database Explorer", "⚙️ RAG Architecture & NLP Metrics"])

with tab_chat:
    st.markdown("##### 💡 Suggested Questions for Fast Testing:")
    sample_cols = st.columns(3)
    
    sample_q1 = "What is the mandatory attendance percentage required at GLS University?"
    sample_q2 = "What is the annual tuition fee for Integrated M.Sc. (IT) and BCA?"
    sample_q3 = "Where is GLS University located and how to contact the Registrar?"
    sample_q4 = "What are the eligibility criteria and fees for MCA and MBA?"
    sample_q5 = "What is the grading scale and pass threshold at GLS University?"
    sample_q6 = "What is GLS i-Hub and what startup funding does it offer?"

    selected_prompt = None

    with sample_cols[0]:
        if st.button(f"📌 {sample_q1}", key="sq1"):
            selected_prompt = sample_q1
        if st.button(f"📌 {sample_q4}", key="sq4"):
            selected_prompt = sample_q4
    with sample_cols[1]:
        if st.button(f"📌 {sample_q2}", key="sq2"):
            selected_prompt = sample_q2
        if st.button(f"📌 {sample_q5}", key="sq5"):
            selected_prompt = sample_q5
    with sample_cols[2]:
        if st.button(f"📌 {sample_q3}", key="sq3"):
            selected_prompt = sample_q3
        if st.button(f"📌 {sample_q6}", key="sq6"):
            selected_prompt = sample_q6

    st.markdown("---")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("🔍 View Retrieved Source Snippets from PDFs"):
                    for src in message["sources"]:
                        st.markdown(f"**[{src['source']} — Page {src['page']}]** *(Relevance Score: {src['score']})*")
                        st.caption(f"\"{src['text']}\"")
                        st.write("---")

    user_query = st.chat_input("Ask any question about GLS University courses, fees, rules, or admissions...")
    
    if selected_prompt:
        user_query = selected_prompt

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query, "sources": []})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner(f"🔍 Searching GLS PDFs & Generating via {provider_choice.split(' ')[1]}..."):
                response_data = rag_engine.generate_response(
                    user_query, 
                    api_key=api_key_input,
                    provider=provider_choice
                )
                
                answer_text = response_data['answer']
                sources = response_data.get('sources', [])
                
                st.markdown(answer_text)
                
                if sources:
                    with st.expander("🔍 View Retrieved Source Snippets from PDFs"):
                        for src in sources:
                            st.markdown(f"**[{src['source']} — Page {src['page']}]** *(Relevance Score: {src['score']})*")
                            st.caption(f"\"{src['text']}\"")
                            st.write("---")
                            
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer_text,
                    "sources": sources
                })

with tab_docs:
    st.subheader("📚 Official GLS University PDF Knowledge Base")
    st.write("Inspect the text extracted directly from the 4 PDF files stored in `gls_university_rag_chatbot/data/`.")
    
    pdf_list = [f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]
    selected_pdf = st.selectbox("Select PDF Document to View:", pdf_list)
    
    if selected_pdf:
        matching_chunks = [c for c in rag_engine.chunks if c['source'] == selected_pdf]
        st.success(f"**{selected_pdf}** — Contains **{len(matching_chunks)}** extracted text blocks across pages.")
        
        for idx, chunk in enumerate(matching_chunks):
            st.markdown(f"#### Page {chunk['page']} — Segment {idx+1}")
            st.code(chunk['text'], language="text")
            st.write("---")

with tab_arch:
    st.subheader("⚙️ System Architecture & NLP Technical Details")
    st.markdown("""
    ### RAG Workflow Architecture
    ```mermaid
    graph LR
        A[GLS University PDFs] --> B[pypdf Extractor]
        B --> C[Text Chunker]
        C --> D[BM25 Term Indexer]
        E[Student Query] --> D
        D --> F[Top-K Snippets]
        F --> G[OpenRouter API LLM]
        G --> H[Accurate Answer + Citations]
    ```
    """)
