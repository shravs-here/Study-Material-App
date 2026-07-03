from fastapi import APIRouter, HTTPException

from app.models import GenerateRequest, GenerateKind
from app.services.generation import generate as run_generation
from app.services.vectorstore import delete_session

router = APIRouter(tags=["generate"])


@router.post("/generate/{kind}")
async def generate_content(kind: GenerateKind, payload: GenerateRequest):
    try:
        result = run_generation(kind, payload.session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Generation failed: {e}")
    return result


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    delete_session(session_id)
    return {"deleted": session_id}
