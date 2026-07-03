# Study Desk API

A FastAPI backend for the Study Desk app. Upload notes or a textbook chapter,
and it uses **OpenAI** for embeddings + generation and **Pinecone** as the
vector store, so each generation step (concepts, questions, flashcards, study
plan) pulls the most relevant passages via retrieval (RAG) instead of always
stuffing the whole document into the prompt.

## How it works

1. `POST /api/upload` (or `/api/upload-text` for pasted text) — extracts text
   from a `.txt`/`.pdf` file, splits it into ~700-token chunks, embeds each
   chunk with `text-embedding-3-small`, and stores them in a Pinecone
   namespace unique to that upload (`session_id`).
2. `POST /api/generate/{kind}` where `kind` is one of `concepts`, `questions`,
   `flashcards`, `plan` — embeds a task-specific retrieval query (e.g. "key
   terms and definitions"), fetches the top matching chunks for that
   `session_id` from Pinecone, and asks an OpenAI chat model to generate
   structured JSON from just that context.
3. `DELETE /api/session/{session_id}` — deletes that session's vectors from
   Pinecone once you're done with it.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your OPENAI_API_KEY and PINECONE_API_KEY
```

Run it:

```bash
uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000`, with interactive docs at
`http://localhost:8000/docs`.

The Pinecone index is created automatically on first run (serverless, cosine
similarity, matching the embedding model's dimension) if it doesn't already
exist.

## Example usage

```bash
# Upload a file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@chapter3.pdf"
# -> {"session_id": "...", "chunk_count": 12, ...}

# Or upload pasted text
curl -X POST http://localhost:8000/api/upload-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Photosynthesis is the process by which..."}'

# Generate flashcards for that session
curl -X POST http://localhost:8000/api/generate/flashcards \
  -H "Content-Type: application/json" \
  -d '{"session_id": "PASTE_SESSION_ID_HERE"}'

# kind can also be: concepts | questions | plan

# Clean up when done
curl -X DELETE http://localhost:8000/api/session/PASTE_SESSION_ID_HERE
```

## Project layout

```
app/
  main.py                 FastAPI app, CORS, router registration
  config.py                Settings loaded from environment / .env
  models.py                 Pydantic request/response schemas
  services/
    extraction.py            Pulls text out of .txt / .pdf uploads
    chunking.py               Token-aware chunking (tiktoken)
    embeddings.py             OpenAI embeddings, batched
    vectorstore.py            Pinecone index create / upsert / query / delete
    generation.py             Retrieval + OpenAI chat generation per task
  routers/
    upload.py                 /api/upload, /api/upload-text
    generate.py                /api/generate/{kind}, /api/session/{id}
requirements.txt
.env.example
```

## Notes for production use

This is a working starting point, not a hardened production service. Before
shipping it for real users, you'll likely want to add:

- **Auth** on the endpoints (API key, JWT, or your app's session auth).
- **Rate limiting**, since each generation call costs OpenAI tokens.
- **Persistent session metadata** (right now the only record of a session is
  its Pinecone namespace — consider a small database table mapping
  `session_id` → user, filename, upload time, so you can list/expire old
  uploads).
- **A scheduled cleanup job** to delete old Pinecone namespaces that were
  never explicitly deleted.
- Tightening `ALLOWED_ORIGINS` in `.env` to your actual frontend's origin
  instead of `*`.

## Connecting a frontend

Any frontend can talk to this by calling `/api/upload` (or `/api/upload-text`)
to get a `session_id`, then calling `/api/generate/{kind}` for each of
`concepts`, `questions`, `flashcards`, and `plan` with that `session_id`. If
you're using the Study Desk HTML artifact built earlier, swap its direct
`fetch()` calls to `api.anthropic.com` for calls to this backend's endpoints
instead.
