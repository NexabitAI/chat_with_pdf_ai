import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from textwrap import dedent

# ✅ Load environment variables
load_dotenv()

# =========================
# THEME & GLOBAL STYLES
# =========================
THEMES = ["Glassy Light", "Soft Dark", "High Contrast"]

def theme_css(current: str) -> str:
    """Return CSS variables + glassmorphism styling for the selected theme.
    NOTE: no leading whitespace before <style> — avoids Markdown code block rendering.
    """
    base = dedent("""\
    <style>
    :root {
      --radius: 16px;
      --radius-sm: 12px;
      --shadow-1: 0 8px 28px rgba(0,0,0,.12);
      --shadow-2: 0 12px 40px rgba(0,0,0,.18);
      --border-alpha: 0.18;
      --blur: 14px;
      --accent: 82 91% 56%;
      --accent-rgb: 99,102,241; /* indigo-500 */
      --success-rgb: 16,185,129; /* emerald-500 */
    }

    /* App background & animated sheen */
    [data-testid="stAppViewContainer"] {
      position: relative;
      padding-top: 12px;
      transition: background 300ms ease;
      background-attachment: fixed !important;
    }

    /* Decorative floating blurs */
    [data-testid="stAppViewContainer"]::before,
    [data-testid="stAppViewContainer"]::after {
      content: "";
      position: fixed;
      width: 480px; height: 480px;
      filter: blur(90px);
      opacity: .35;
      z-index: -1;
      border-radius: 50%;
      animation: floaty 18s ease-in-out infinite alternate;
      pointer-events: none;
    }
    [data-testid="stAppViewContainer"]::before { top: -120px; left: -120px; background: radial-gradient(60% 60% at 50% 50%, rgba(var(--accent-rgb), .35), transparent 70%); }
    [data-testid="stAppViewContainer"]::after  { bottom: -160px; right: -120px; background: radial-gradient(60% 60% at 50% 50%, rgba(16,185,129,.35), transparent 70%); animation-delay: 2s; }

    @keyframes floaty { from { transform: translateY(-12px)} to { transform: translateY(12px)} }

    @media (prefers-reduced-motion: reduce) {
      [data-testid="stAppViewContainer"]::before,
      [data-testid="stAppViewContainer"]::after { animation: none; }
    }

    /* Utility */
    .glass {
      backdrop-filter: blur(var(--blur));
      -webkit-backdrop-filter: blur(var(--blur));
      border: 1px solid rgba(255,255,255,var(--border-alpha));
      box-shadow: var(--shadow-1);
      border-radius: var(--radius);
    }

    .btn-primary {
      display: inline-flex; align-items: center; gap: .5rem;
      padding: .8rem 1rem;
      border-radius: 999px;
      font-weight: 600;
      border: 1px solid rgba(255,255,255,.18);
      box-shadow: var(--shadow-1);
      transition: transform .12s ease, box-shadow .2s ease, background .2s ease, color .2s ease;
      text-decoration: none;
      cursor: pointer;
      user-select: none;
    }
    .btn-primary:hover { transform: translateY(-1px); box-shadow: var(--shadow-2); }
    .tag {
      display: inline-block; padding: .25rem .6rem; border-radius: 999px; font-size: .75rem; opacity: .9;
      border: 1px dashed rgba(255,255,255,.25);
    }

    .hero-title {
      font-size: clamp(2.2rem, 4.5vw, 3.2rem);
      font-weight: 800;
      text-align: center;
      margin: 6px 0 10px;
      letter-spacing: -.02em;
      color: var(--text);
      text-shadow: 0 1px 0 rgba(0,0,0,.06);
    }
    .hero-sub {
      text-align: center;
      font-size: clamp(1rem, 1.8vw, 1.15rem);
      margin-bottom: 28px;
      color: var(--text-muted);
    }

    .features {
      display: grid; grid-template-columns: repeat(3, minmax(0,1fr));
      gap: 16px; margin: 22px 0 10px;
    }
    @media (max-width: 980px) { .features { grid-template-columns: 1fr; } }

    .feature-card {
      padding: 18px 18px;
      color: var(--text);
      background: var(--glass-bg);
    }
    .feature-card h3 { margin: 0 0 6px; }
    .feature-card p { margin: 0; color: var(--text-muted); }

    .steps { margin: 26px auto; max-width: 800px; display: grid; gap: 10px; }
    .step {
      padding: 12px 14px;
      border-left: 4px solid hsl(var(--accent));
      background: var(--step-bg);
      color: var(--text);
      border-radius: var(--radius-sm);
    }

    /* Chat bubbles */
    .chat-message { padding: 12px 14px; border-radius: 14px; margin: 8px 0; max-width: 920px; box-shadow: var(--shadow-1)}
    .user { margin-left: auto; background: var(--user-bg); color: var(--text); border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(var(--blur)) }
    .bot  { margin-right: auto; background: var(--bot-bg);  color: var(--text); border: 1px solid rgba(255,255,255,.14); backdrop-filter: blur(var(--blur)) }

    /* Inputs alignment */
    .input-row { display: flex; gap: 8px; align-items: stretch; }
    .input-row > div:first-child { flex: 1 }
    .muted { color: var(--text-muted); font-size: .9rem }

    /* Tighten default Streamlit spacing a touch */
    section.main > div { padding-top: 0 !important; }
    </style>
    """)

    if current == "Glassy Light":
        theme_vars = dedent("""\
        <style>
        :root {
          --text: #0e1525;
          --text-muted: #54607a;
          --bg: #f5f9ff;
          --glass-bg: linear-gradient(180deg, rgba(255,255,255,.66), rgba(255,255,255,.42));
          --step-bg: rgba(255,255,255,.65);
          --user-bg: linear-gradient(180deg, rgba(224,242,254,.85), rgba(219,234,254,.7));
          --bot-bg:  linear-gradient(180deg, rgba(248,250,252,.8), rgba(241,245,249,.6));
        }
        [data-testid="stAppViewContainer"] {
          background:
            radial-gradient(1200px 600px at -10% -20%, #ffffff 0%, transparent 60%),
            radial-gradient(1000px 600px at 110% 120%, #eaf2ff 0%, transparent 58%),
            linear-gradient(180deg, #eef3ff 0%, #f8fbff 100%);
        }
        .btn-primary { background: rgba(99,102,241,.14); color: #2a2f45; }
        .btn-primary:hover { background: rgba(99,102,241,.22); }
        .tag { background: rgba(255,255,255,.65); color: #2a2f45; }
        </style>
        """)
    elif current == "Soft Dark":
        theme_vars = dedent("""\
        <style>
        :root {
          --text: #eaf2ff;
          --text-muted: #aab4cf;
          --bg: #0b1220;
          --glass-bg: linear-gradient(180deg, rgba(13,20,34,.66), rgba(13,20,34,.42));
          --step-bg: rgba(20,28,46,.66);
          --user-bg: linear-gradient(180deg, rgba(30,64,175,.52), rgba(29,78,216,.38));
          --bot-bg:  linear-gradient(180deg, rgba(31,41,55,.55), rgba(55,65,81,.35));
        }
        [data-testid="stAppViewContainer"] {
          background:
            radial-gradient(1200px 600px at -10% -20%, #0f1729 0%, transparent 60%),
            radial-gradient(1000px 600px at 110% 120%, #0a1120 0%, transparent 58%),
            linear-gradient(180deg, #0a0f1a 0%, #0b1220 100%);
        }
        .btn-primary { background: rgba(99,102,241,.16); color: #eaf2ff; }
        .btn-primary:hover { background: rgba(99,102,241,.26); }
        .tag { background: rgba(255,255,255,.08); color: #eaf2ff; }
        </style>
        """)
    else:  # High Contrast
        theme_vars = dedent("""\
        <style>
        :root {
          --text: #0a0a0a;
          --text-muted: #1a1a1a;
          --bg: #ffffff;
          --glass-bg: rgba(255,255,255, .92);
          --step-bg: rgba(0,0,0,.06);
          --user-bg: #ffe08a;
          --bot-bg:  #e5e7eb;
          --border-alpha: .35;
        }
        [data-testid="stAppViewContainer"] {
          background: #ffffff;
        }
        .chat-message, .feature-card, .step { outline: 2px solid #111; }
        .btn-primary { background: #111; color: #fff; outline: 2px solid #111; }
        .btn-primary:hover { background: #000; }
        .tag { background: #111; color: #fff; }
        </style>
        """)
    return base + theme_vars

# =========================
# HEADER (Brand + Theme)
# =========================
def header():
    c1, _, c3 = st.columns([1.2, 2, 1.5])  # removed vertical_alignment (not supported on older Streamlit)
    with c1:
        st.markdown(
            dedent("""\
            <div class="glass" style="display:flex;align-items:center;gap:.6rem;padding:.55rem .8rem;background:var(--glass-bg);">
              <div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg, rgba(var(--accent-rgb),.9), rgba(16,185,129,.9));box-shadow:0 6px 18px rgba(0,0,0,.25)"></div>
              <div>
                <div style="font-weight:800;letter-spacing:.2px;color:var(--text)">pdfbuddy</div>
                <div class="muted" style="font-size:.75rem">Chat • Extract • Summarize</div>
              </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
    with c3:
        if "theme" not in st.session_state:
            st.session_state.theme = THEMES[0]
        st.session_state.theme = st.radio(
            "Theme",
            THEMES,
            index=THEMES.index(st.session_state.theme),
            horizontal=True,
            label_visibility="collapsed",
        )
    st.markdown(theme_css(st.session_state.theme), unsafe_allow_html=True)

# =========================
# LANDING PAGE
# =========================
def landing_page():
    st.markdown("<h1 class='hero-title'>📚 Chat with Your PDFs</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>Upload PDFs and get instant, AI-powered answers with a glassy, modern UI.</p>", unsafe_allow_html=True)

    st.markdown(
        dedent("""\
        <div class='features'>
            <div class='feature-card glass'>
                <h3>⚡ Quick Upload</h3>
                <p>Drag & drop one or many PDFs. We’ll handle the rest.</p>
            </div>
            <div class='feature-card glass'>
                <h3>🤖 Smart Retrieval</h3>
                <p>Context-aware answers citing your documents.</p>
            </div>
            <div class='feature-card glass'>
                <h3>🌓 Themes & Contrast</h3>
                <p>Glassy Light, Soft Dark, and High Contrast with motion-safe animations.</p>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )

    st.markdown(
        dedent("""\
        <div class='steps'>
            <div class='step glass'>1️⃣ Upload your PDF documents</div>
            <div class='step glass'>2️⃣ Ask any question about them</div>
            <div class='step glass'>3️⃣ Get instant, accurate answers</div>
        </div>
        """),
        unsafe_allow_html=True,
    )

    st.write("")
    cta = st.columns([1, 1, 1])[1]
    with cta:
        if st.button("🚀 Start Chatting", use_container_width=True):
            st.session_state.page = "chat"

# =========================
# CHAT PAGE
# =========================
def chat_page():
    st.markdown("<h1 class='hero-title' style='font-size:2rem;margin-bottom:10px;'>💬 Chat with Your PDFs</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-sub' style='margin-bottom:10px;'>Upload → Process → Ask anything. Your chat stays in memory.</p>", unsafe_allow_html=True)

    # Sidebar: Upload & Process
    with st.sidebar:
        st.markdown("### 📂 Upload PDFs")
        pdf_docs = st.file_uploader("Drop files here", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
        st.caption("Tip: you can upload multiple PDFs at once.")
        process = st.button("⚙️ Process", use_container_width=True)
        if process:
            if pdf_docs:
                with st.spinner("Indexing your PDFs…"):
                    text = ""
                    for pdf in pdf_docs:
                        pdf_reader = PdfReader(pdf)
                        for page in pdf_reader.pages:
                            text += (page.extract_text() or "") + "\n"

                    text_splitter = CharacterTextSplitter(
                        separator="\n",
                        chunk_size=1000,
                        chunk_overlap=200,
                        length_function=len,
                    )
                    chunks = text_splitter.split_text(text)

                    embeddings = OpenAIEmbeddings()
                    vectorstore = FAISS.from_texts(chunks, embeddings)

                    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                    llm = ChatOpenAI()
                    st.session_state.conversation = ConversationalRetrievalChain.from_llm(
                        llm=llm, retriever=vectorstore.as_retriever(), memory=memory
                    )
                    st.session_state.chat_history = []  # reset chat history
                st.success("✅ PDFs processed! You can start chatting now.")
            else:
                st.warning("Please upload at least one PDF.")

    # Main chat area
    if "conversation" in st.session_state:
        st.write("")
        col_inp, col_btn = st.columns([6, 1])
        with col_inp:
            user_question = st.text_input(
                "Ask a question about your PDFs:",
                key="user_input",
                label_visibility="collapsed",
                placeholder="e.g., Summarize section 2.1 from the contract…",
            )
        with col_btn:
            # Some older Streamlit versions may not support type="primary"; remove if it errors.
            send_clicked = st.button("Send", use_container_width=True)
        if send_clicked and user_question:
            with st.spinner("Thinking…"):
                response = st.session_state.conversation({"question": user_question})
            st.session_state.chat_history.append(("user", user_question))
            st.session_state.chat_history.append(("bot", response.get("answer", "")))

        st.write("")
        if st.session_state.get("chat_history"):
            for role, msg in st.session_state.chat_history:
                css_class = "user" if role == "user" else "bot"
                st.markdown(f"<div class='chat-message {css_class}'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='muted'>No messages yet. Ask your first question above.</div>", unsafe_allow_html=True)
    else:
        st.info("Upload and process PDFs from the left sidebar to start chatting.")

# =========================
# MAIN
# =========================
def main():
    st.set_page_config(page_title="pdfbuddy — Chat with PDFs", page_icon="📚", layout="wide")
    header()
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    if st.session_state.page == "landing":
        landing_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()
