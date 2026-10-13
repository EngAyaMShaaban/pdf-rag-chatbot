# 📄 PDF RAG Chatbot — Chat with your PDFs using Gemini, LangChain & Chroma

A small Retrieval-Augmented Generation (RAG) app built with **Streamlit**.
Upload one or more PDFs, build a knowledge base from them, and chat with the documents.
Answers are grounded only in the PDF content, and every answer shows the source file and page it came from.

## Features

- Upload multiple PDFs from the sidebar
- Text extraction page by page with `pypdf` (file name and page number kept as metadata)
- Chunking with `RecursiveCharacterTextSplitter` (800 characters, 100 overlap)
- Embeddings with Google `gemini-embedding-001`, stored in an in-memory **Chroma** vector store
- Top-3 similarity search for every question
- Answers from **Gemini 3.5 Flash**, restricted to the retrieved context
- Conversation memory: earlier messages are passed to the model as chat history
- Sources (file + page) shown under each answer
- "Clear conversation" button

## How it works

```
PDFs ──► pypdf (text per page) ──► text splitter (chunks)
                                          │
                                          ▼
                           Gemini embeddings ──► Chroma vector store
                                                        │
Question ──► similarity search (k=3) ◄──────────────────┘
                 │
                 ▼
   prompt = context + chat history + question ──► Gemini 3.5 Flash ──► answer + sources
```

## Project structure

| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI: sidebar (API key, upload, build), chat window |
| `rag.py` | RAG pipeline: read PDFs, split, embed, store, retrieve, answer |
| `memory.py` | Chat history kept in `st.session_state` |
| `prompts.py` | The prompt template sent to Gemini |
| `requirements.txt` | Python dependencies |

## Getting started

### 1. Prerequisites

- Python 3.10 or newer
- A Google Gemini API key — get one free from [Google AI Studio](https://aistudio.google.com/apikey)

### 2. Clone and install

```bash
git clone https://github.com/EngAyaMShaaban/pdf-rag-chatbot.git
cd pdf-rag-chatbot

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### 4. Use it

1. Paste your Gemini API key in the sidebar.
2. Upload one or more PDF files.
3. Click **Build knowledge base** and wait for "Knowledge base is ready".
4. Ask questions in the chat box.

> Your API key is typed into the app at runtime and is never saved to disk or to the repository.

## Configuration

These values live in `rag.py` and can be changed:

| Setting | Default | Where |
|---------|---------|-------|
| Chunk size / overlap | `800` / `100` | `build_vector_store` |
| Embedding model | `models/gemini-embedding-001` | `build_vector_store` |
| Retrieved chunks (k) | `3` | `answer_question` |
| Chat model | `gemini-3.5-flash` | `answer_question` |
| Temperature | `0.7` | `answer_question` |

The prompt itself is in `prompts.py`.

## Limitations

- The vector store is in memory — it is rebuilt every time you click **Build knowledge base** and is lost when the app restarts.
- Scanned PDFs (images without a text layer) produce no text, because there is no OCR.
- The whole chat history is sent with every question, so very long conversations make prompts larger.

## Tech stack

[Streamlit](https://streamlit.io) · [LangChain](https://python.langchain.com) · [Chroma](https://www.trychroma.com) · [Google Gemini](https://ai.google.dev) · [pypdf](https://pypdf.readthedocs.io)
