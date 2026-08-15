# 🦜🔗 Cipher

Chat with your PDFs using a hosted LLM. Upload a document, and ask questions about it in plain English — answers are generated via [Groq](https://groq.com/)'s fast inference API, grounded in your document through local retrieval.

**Live demo:**

## ✨ Features

- 📄 **Upload a PDF** and ask natural-language questions about its contents
- 🔍 **Retrieval-augmented generation (RAG)** — answers are grounded in the actual document via similarity search, with the matching passages shown alongside each response
- ⚡ **Powered by Groq** (e.g. `llama-3.1-8b-instant`) for fast LLM responses — requires a free [Groq API key](https://console.groq.com/keys)
- 🧠 **Local embeddings** — document chunks are embedded on your machine via HuggingFace `sentence-transformers`, so only your questions (not the raw document content) are sent to Groq
- 💬 **Persistent chat interface** with history, avatars, and a "thinking..." spinner while the model responds
- 🟢 **Live connection status** — the sidebar checks your Groq API key and shows a green/red status pill, so a missing or invalid key shows a plain-English message instead of a raw traceback
- ⚙️ **Configurable at runtime** — set your Groq API key and model name directly from the sidebar, no code changes needed

## 🛠️ Tech stack

- [Streamlit](https://streamlit.io/) — UI
- [LangChain](https://www.langchain.com/) (`langchain`, `langchain-community`, `langchain-groq`) — RAG orchestration (`RetrievalQA`)
- [Groq](https://groq.com/) (via `langchain-groq`'s `ChatGroq`) — hosted LLM inference
- [Chroma](https://www.trychroma.com/) — vector store
- [HuggingFace `sentence-transformers`](https://www.sbert.net/) (`all-MiniLM-L6-v2`) — local embeddings
- `PyPDFLoader` (via `langchain-community`) — PDF parsing
- `python-dotenv` — local environment variable loading
- `Pillow` — optional sidebar logo rendering

## 🚀 Running locally

```
git clone https://github.com/vartikas773-ops/Cipher.git
cd Cipher
pip install -r requirements.txt

streamlit run app.py
```

## 📌 Notes

- Uploaded PDFs are written to a temporary directory during processing and are not persisted between sessions.
- Document chunks are embedded locally and never leave your machine — only your questions are sent to Groq for answer generation.
- Better to set `GROQ_API_KEY` as an environment variable / Streamlit secret than paste it into the sidebar in a shared deployment.

## 📄 License

MIT
