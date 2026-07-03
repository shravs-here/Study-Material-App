import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.models import UploadResponse
from app.services.extraction import extract_text
from app.services.chunking import chunk_text
from app.services.vectorstore import upsert_chunks

router = APIRouter(tags=["upload"])


class PastedText(BaseModel):
    text: str
    label: str = "Pasted notes"


@router.post("/upload", response_model=UploadResponse)
async def upload_notes(file: UploadFile = File(...)):
    text = await extract_text(file)

    if len(text) > settings.max_upload_chars:
        text = text[: settings.max_upload_chars]

    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text could be extracted from this file.")

    session_id = str(uuid.uuid4())
    stored = upsert_chunks(session_id, chunks)

    return UploadResponse(
        session_id=session_id,
        filename=file.filename or "pasted-text",
        chunk_count=stored,
        char_count=len(text),
        preview=text[:300],
    )


@router.post("/upload-text", response_model=UploadResponse)
async def upload_pasted_text(payload: PastedText):
    text = payload.text.strip()
    if len(text) < 40:
        raise HTTPException(status_code=400, detail="Add a bit more text first.")
    if len(text) > settings.max_upload_chars:
        text = text[: settings.max_upload_chars]

    chunks = chunk_text(text)
    session_id = str(uuid.uuid4())
    stored = upsert_chunks(session_id, chunks)

    return UploadResponse(
        session_id=session_id,
        filename=payload.label,
        chunk_count=stored,
        char_count=len(text),
        preview=text[:300],
    )
