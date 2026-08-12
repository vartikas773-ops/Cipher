# 🦜🔗 PDF-Chat

Chat with your PDFs using a locally-run LLM. Upload a document, and ask questions about it in plain English — answers are generated entirely by your own [Ollama](https://ollama.com/) model, with no document content sent to a third-party API.

**Live demo:** https://pdf-chat-ollama.streamlit.app/

## ✨ Features

- 📄 **Upload a PDF** and ask natural-language questions about its contents
- 🔍 **Retrieval-augmented generation (RAG)** — answers are grounded in the actual document via similarity search, with the matching passages shown alongside each response
- 🧠 **Runs on your own Ollama model** (e.g. `llama3.1`) — fully local inference, no proprietary API calls
- 💬 **Persistent chat interface** with history, avatars, and a "thinking..." spinner while the model responds
- 🟢 **Live connection status** — the sidebar pings Ollama's `/api/tags` endpoint and shows a green/red status pill, so a broken connection shows a plain-English message instead of a raw traceback
- ⚙️ **Configurable at runtime** — set your Ollama server URL and model name directly from the sidebar, no code changes needed

## 🛠️ Tech stack

- [Streamlit](https://streamlit.io/) — UI
- [LangChain](https://www.langchain.com/) (`langchain`, `langchain-community`, `langchain-ollama`) — RAG orchestration (`RetrievalQA`)
- [Ollama](https://ollama.com/) — local LLM inference
- [Chroma](https://www.trychroma.com/) — vector store
- [HuggingFace `sentence-transformers`](https://www.sbert.net/) (`all-MiniLM-L6-v2`) — embeddings
- `PyPDFLoader` (via `langchain-community`) — PDF parsing
- `httpx` — connection health checks
- `python-dotenv` — local environment variable loading
- `Pillow` — optional sidebar logo rendering

## 🚀 Running locally

```bash
git clone https://github.com/vartikas773-ops/PDFChat.git
cd PDFChat
pip install -r requirements.txt

# Make sure Ollama is installed and running with the model you want, e.g.:
ollama pull llama3.1
ollama serve

streamlit run app.py
```

By default the app looks for Ollama at `http://localhost:11434`. You can override this via the `OLLAMA_HOST` environment variable (read at startup via `.env` / `python-dotenv`), or change it live from the app's sidebar under **Connection settings**.

An optional `my_logo.png` in the project root will be shown at the top of the sidebar if present.

## ☁️ Deploying (e.g. Streamlit Community Cloud)

Streamlit Cloud doesn't run Ollama for you — it's a hosted container with no local model server. To connect a cloud-deployed instance of this app to Ollama running on your own machine:

1. Run Ollama locally:
   ```bash
   ollama serve
   ```
2. Expose it publicly via a tunnel, e.g. [ngrok](https://ngrok.com/):
   ```bash
   ngrok http 11434
   ```
3. **Important:** recent versions of Ollama reject requests where the `Host` header isn't `localhost`, which a plain tunnel triggers. Rewrite the header using an ngrok traffic policy file (`ollama.yaml`):
   ```yaml
   on_http_request:
     - actions:
         - type: add-headers
           config:
             headers:
               host: localhost
   ```
   ```bash
   ngrok http 127.0.0.1:11434 --traffic-policy-file ollama.yaml
   ```
4. Paste the resulting `https://….ngrok-free.app` URL into the app's sidebar under **Connection settings** (or set it as an `OLLAMA_HOST` secret in Streamlit Cloud's app settings).
5. Confirm the sidebar status pill turns 🟢 before uploading a PDF.

⚠️ Since Ollama runs on your machine, it — and the tunnel — need to stay running and awake for as long as anyone might use the deployed app. Free ngrok URLs also rotate on every restart, so this setup needs to be redone each time you restart either process.

## 📌 Notes

- Uploaded PDFs are written to a temporary directory during processing and are not persisted between sessions.
- No document content or questions are sent anywhere except your own Ollama instance.
- Paste the Ollama URL carefully — stray whitespace or a malformed scheme (e.g. a missing slash) copied from a terminal can cause a DNS/connection error even when the tunnel itself is healthy.

## 📄 License

MIT
