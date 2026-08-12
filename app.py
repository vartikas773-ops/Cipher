import os
import tempfile

import streamlit as st
from PIL import Image
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA

load_dotenv()

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
DEFAULT_MODEL = "llama-3.1-8b-instant"

st.set_page_config(
    page_title="PDF-Chat",
    page_icon="🦜",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; }
    .hero { text-align: center; padding: 2rem 1rem 1.5rem 1rem; }
    .hero h1 { font-size: 2rem; margin-bottom: 0.25rem; }
    .hero p { color: #9aa0ab; font-size: 1.05rem; }
    .source-snippet {
        background: rgba(255,255,255,0.04);
        border-left: 3px solid #63b3ed;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #c7cbd1;
    }
    .status-pill {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    .status-ok { background: rgba(72,187,120,0.15); color: #48bb78; border: 1px solid rgba(72,187,120,0.4); }
    .status-bad { background: rgba(245,101,101,0.15); color: #f56565; border: 1px solid rgba(245,101,101,0.4); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Session state
# ------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []
if "store" not in st.session_state:
    st.session_state.store = None
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = None
if "api_key" not in st.session_state:
    st.session_state.api_key = GROQ_API_KEY
if "model_name" not in st.session_state:
    st.session_state.model_name = DEFAULT_MODEL


def check_groq_connection(api_key: str) -> tuple[bool, str]:
    """Do a cheap sanity check that we have a usable API key, without
    burning a real completion call."""
    if not api_key or not api_key.strip():
        return False, "No GROQ_API_KEY configured yet."
    if not api_key.startswith("gsk_"):
        return False, "That doesn't look like a valid Groq API key (should start with 'gsk_')."
    return True, "Connected"


@st.cache_resource(show_spinner=False)
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def process_pdf(uploaded_file, api_key, model_name):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.read())

        progress = st.progress(0, text="Loading PDF...")
        loader = PyPDFLoader(temp_file_path)
        pages = loader.load_and_split()
        progress.progress(35, text=f"Embedding {len(pages)} chunks locally...")

        embeddings = get_embeddings()
        store = Chroma.from_documents(pages, embeddings, collection_name="Pdf")
        progress.progress(70, text="Connecting to Groq...")

        llm = ChatGroq(api_key=api_key, model=model_name, temperature=0.2)
        retriever = store.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
        )
        progress.progress(100, text="Ready!")
        progress.empty()

        st.session_state.store = store
        st.session_state.qa_chain = qa_chain
        st.session_state.uploaded_name = uploaded_file.name
        st.toast(f"Indexed **{uploaded_file.name}** ({len(pages)} pages)", icon="✅")


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------

with st.sidebar:
    if os.path.exists("my_logo.png"):
        st.image(Image.open("my_logo.png"))
    st.markdown("### 🦜🔗 PDF-Chat")
    st.caption("RAG via Groq (hosted LLM) + local HuggingFace embeddings")

    with st.expander("⚙️ Connection settings", expanded=False):
        raw_key = st.text_input(
            "Groq API key",
            value=st.session_state.api_key,
            type="password",
            help="Get a free key at https://console.groq.com/keys. "
                 "Better to set this as a Streamlit secret / env var (GROQ_API_KEY) "
                 "than paste it here in a shared deployment.",
        )
        st.session_state.api_key = raw_key.strip()
        st.session_state.model_name = st.text_input("Model", value=st.session_state.model_name)

    ok, detail = check_groq_connection(st.session_state.api_key)
    if ok:
        st.markdown('<span class="status-pill status-ok">🟢 Groq key set</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-pill status-bad">🔴 No Groq key</span>', unsafe_allow_html=True)
        st.caption(f"`{detail}`")
        st.caption(
            "This app can't answer questions without a Groq API key. "
            "Grab a free one at console.groq.com/keys and paste it above, "
            "or set GROQ_API_KEY as an env var / secret."
        )

    st.divider()

    uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])
    if uploaded_file is not None and uploaded_file.name != st.session_state.uploaded_name:
        if not ok:
            st.error("Can't process the PDF until a Groq API key is set — fix the connection above first.")
        else:
            process_pdf(uploaded_file, st.session_state.api_key, st.session_state.model_name)

    if st.session_state.uploaded_name:
        st.success(f"📄 {st.session_state.uploaded_name}")

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ------------------------------------------------------------------
# Main area
# ------------------------------------------------------------------

if not st.session_state.qa_chain:
    st.markdown(
        """
        <div class="hero">
            <h1>🦜🔗 PDF-Chat</h1>
            <p>Upload a PDF in the sidebar, then ask questions about it in natural language.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(f"#### 💬 Ask about *{st.session_state.uploaded_name}*")

for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🦜"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 Document similarity search"):
                for i, src in enumerate(msg["sources"], 1):
                    st.markdown(f'<div class="source-snippet"><b>Match {i}</b><br>{src}</div>', unsafe_allow_html=True)

prompt = st.chat_input(
    "Ask a question about your PDF..." if st.session_state.qa_chain else "Upload a PDF first to start chatting",
    disabled=not st.session_state.qa_chain,
)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.write(prompt)

    with st.chat_message("assistant", avatar="🦜"):
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.qa_chain.invoke({"query": prompt})
                answer = result["result"]
                search = st.session_state.store.similarity_search_with_score(prompt, k=3)
                sources = [doc.page_content[:400] + ("..." if len(doc.page_content) > 400 else "") for doc, _ in search]
            except Exception as e:
                answer = (
                    "⚠️ I couldn't reach Groq, so I can't answer right now. "
                    "Check the connection status in the sidebar — your API key may be missing, invalid, or rate-limited."
                )
                sources = []
                st.caption(f"Debug: `{e}`")

        st.write(answer)
        if sources:
            with st.expander("📚 Document similarity search"):
                for i, src in enumerate(sources, 1):
                    st.markdown(f'<div class="source-snippet"><b>Match {i}</b><br>{src}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})