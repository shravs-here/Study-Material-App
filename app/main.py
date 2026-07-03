from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import upload, generate

app = FastAPI(title="Study Desk API", version="1.0.0")

origins = [o.strip() for o in settings.allowed_origins.split(",")] if settings.allowed_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(generate.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
