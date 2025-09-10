import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

# ✅ Load environment variables
load_dotenv()

# ---------- CSS (Dark + Light Mode) ----------
landing_css = """
<style>
/* Theme-aware text */
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 10px;
    color: var(--text-color);
}
.hero-sub {
    text-align: center;
    font-size: 1.2rem;
    margin-bottom: 40px;
    color: var(--secondary-text-color);
}

/* Features section */
.features{
  display:grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap:16px;
  margin:22px 0 10px;
  align-items: stretch;
}
.feature-card{
  padding:18px;
  background: transparent !important;
  border-radius: var(--radius, 16px);
  color: var(--text, #0e1525);
  box-shadow: var(--shadow-1, 0 8px 28px rgba(0,0,0,.12));
  border: 1px solid rgba(255,255,255, var(--border-alpha, .18));
}
.feature-card h3{ margin:0 0 6px; }
.feature-card p{ margin:0; color: var(--text-muted, #54607a); }

/* Optional tighter spacing on very small screens */
@media (max-width: 480px){
  .features{ gap:12px; }
  .feature-card{ padding:14px; }
}
.feature-card:hover {
    transform: translateY(-6px);
    box-shadow: 0px 6px 14px rgba(0,0,0,0.15);
}

/* Steps */
.steps {
    margin: 50px auto;
    max-width: 700px;
}
.step {
    background: var(--step-bg);
    padding: 16px;
    border-radius: 10px;
    margin-bottom: 12px;
    border-left: 5px solid #4f46e5;
    color: var(--text-color);
}

/* Auto-adjust colors */
@media (prefers-color-scheme: light) {
    :root {
        --text-color: #111;
        --secondary-text-color: #555;
        --card-bg: #ffffff;
        --step-bg: #f9fafb;
    }
}
@media (prefers-color-scheme: dark) {
    :root {
        --text-color: #f1f5f9;
        --secondary-text-color: #cbd5e1;
        --card-bg: #1e293b;
        --step-bg: #334155;
    }
}
</style>
"""

chat_css = """
<style>
.chat-message {
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.user {
    background-color: var(--user-bg);
    text-align: right;
    color: var(--text-color);
}
.bot {
    background-color: var(--bot-bg);
    text-align: left;
    color: var(--text-color);
}

@media (prefers-color-scheme: light) {
    :root {
        --user-bg: #e0f2fe;
        --bot-bg: #f3f4f6;
        --text-color: #111;
    }
}
@media (prefers-color-scheme: dark) {
    :root {
        --user-bg: #1e40af;
        --bot-bg: #374151;
        --text-color: #f1f5f9;
    }
}
</style>
"""

# ---------- Pages ----------
def landing_page():
    st.markdown(landing_css, unsafe_allow_html=True)

    st.markdown("<h1 class='hero-title'>📚 My PDF Buddy</h1>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title'>Chat with Your PDFs</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>Upload PDFs and get instant AI-powered answers from them.</p>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class='features'>
          <div class='feature-card glass'>
            <h3>⚡ Quick Upload</h3>
            <p>Upload one or multiple PDFs instantly.</p>
         </div>
         <div class='feature-card glass'>
           <h3>🤖 Smart AI</h3>
           <p>Ask questions and receive context-aware answers.</p>
         </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='steps'>
            <div class='step'>1️⃣ Upload your PDF documents</div>
            <div class='step'>2️⃣ Ask any question related to them</div>
            <div class='step'>3️⃣ Get instant, accurate answers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Single click -> navigate and rerun immediately
    if st.button("🚀 Start Chatting"):
        st.session_state.page = "chat"
        st.experimental_set_query_params(page="chat")
        st.experimental_rerun()

def chat_page():
    st.markdown(chat_css, unsafe_allow_html=True)

    # Back to landing button (top-left)
    back_col, _ = st.columns([1, 7])
    with back_col:
        if st.button("← Back to Home"):
            st.session_state.page = "landing"
            st.experimental_set_query_params(page="landing")
            st.experimental_rerun()

    st.markdown("<h1 style='text-align: center;'>💬 Chat with Your PDFs</h1>", unsafe_allow_html=True)

    with st.sidebar:
        st.header("📂 Upload PDFs")
        pdf_docs = st.file_uploader("Upload your PDFs", accept_multiple_files=True)

        if st.button("Process"):
            if pdf_docs:
                text = ""
                for pdf in pdf_docs:
                    pdf_reader = PdfReader(pdf)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)
                chunks = text_splitter.split_text(text)
                embeddings = OpenAIEmbeddings()
                vectorstore = FAISS.from_texts(chunks, embeddings)
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                llm = ChatOpenAI()
                st.session_state.conversation = ConversationalRetrievalChain.from_llm(
                    llm=llm, retriever=vectorstore.as_retriever(), memory=memory
                )
                st.session_state.chat_history = []  # ✅ reset chat history
                st.success("✅ PDFs processed! Start chatting now.")

    # ✅ Input: Enter = Send, and input clears after submit
if "conversation" in st.session_state:
    with st.form("qa_form", clear_on_submit=True):
        col_inp, col_btn = st.columns([6, 1])
        with col_inp:
            user_question = st.text_input(
                "Ask a question about your PDFs:",
                key="user_input",
                label_visibility="collapsed",
                placeholder="e.g., Summarize section 2.1 from the contract…",
            )
        with col_btn:
            submitted = st.form_submit_button("Send", use_container_width=True)

    if submitted and user_question.strip():
        with st.spinner("Thinking…"):
            response = st.session_state.conversation({"question": user_question})
        st.session_state.chat_history.append(("user", user_question))
        st.session_state.chat_history.append(("bot", response.get("answer", "")))


        # ✅ Show chat history
        if "chat_history" in st.session_state:
            for role, msg in st.session_state.chat_history:
                if role == "user":
                    st.markdown(f"<div class='chat-message user'>{msg}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='chat-message bot'>{msg}</div>", unsafe_allow_html=True)

# ---------- Main ----------
def main():
    st.set_page_config(page_title="MyPDFBuddy-Chat with PDFs", page_icon="📚", layout="wide")

    # --- Sync page state with URL query param ---
    if "page" not in st.session_state:
        st.session_state.page = "landing"

    # If URL has ?page=..., honor it (no reload needed)
    qp = st.experimental_get_query_params()
    if "page" in qp:
        desired = qp["page"][0]
        if desired in ("landing", "chat") and desired != st.session_state.page:
            st.session_state.page = desired

    # Always reflect current state back to URL
    st.experimental_set_query_params(page=st.session_state.page)

    if st.session_state.page == "landing":
        landing_page()
    elif st.session_state.page == "chat":
        chat_page()

    # Hide default menu + footer (unchanged)
    st.markdown("""
       <style>
       /* Remove Streamlit's top-right menu (hamburger/kebab) */
       #MainMenu {display: none;}
       header [data-testid="stToolbar"] {display: none;}
       /* Hide "Made with Streamlit" footer */
       footer {display:none !important;}
       /* (Older builds) */
       [data-testid="stFooter"] {display:none !important;}
       </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
