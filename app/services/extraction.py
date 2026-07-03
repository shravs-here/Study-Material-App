import io
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader


async def extract_text(file: UploadFile) -> str:
    """Extract plain text from an uploaded .txt or .pdf file."""
    name = (file.filename or "").lower()
    raw = await file.read()

    if name.endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(raw))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read PDF: {e}")
        pages = []
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                continue
        text = "\n\n".join(pages)
    elif name.endswith(".txt"):
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1", errors="ignore")
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a .txt or .pdf file.",
        )

    text = text.strip()
    if len(text) < 40:
        raise HTTPException(
            status_code=400,
            detail="Couldn't find enough readable text in that file (it may be a scanned/image-only PDF).",
        )
    return text
