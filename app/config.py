import os
from dotenv import load_dotenv

# Loads variables from a .env file in the current working directory, if present.
# In production (Render, etc.) you'll typically set these in the platform's
# environment variable settings instead, and this call is a harmless no-op.
load_dotenv()


def _required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Add it to your .env file (see .env.example) or your deployment "
            f"platform's environment variable settings."
        )
    return value
openai_api_key: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
pinecone_api_key:pcsk_6yvd3a_NS8iPyFAgMDN47no7SNQ4xFqimHUaHUhU9RzuFBpmMFYU2bAbZg361gq9ewrJHo

class Settings:
    def __init__(self) -> None:
        self.openai_api_key: str = _required("OPENAI_API_KEY")
        self.pinecone_api_key: str = _required("PINECONE_API_KEY")

        self.pinecone_index_name: str = os.environ.get("PINECONE_INDEX_NAME", "study-desk")
        self.pinecone_cloud: str = os.environ.get("PINECONE_CLOUD", "aws")
        self.pinecone_region: str = os.environ.get("PINECONE_REGION", "us-east-1")

        self.embedding_model: str = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
        self.embedding_dimension: int = int(os.environ.get("EMBEDDING_DIMENSION", "1536"))
        self.chat_model: str = os.environ.get("CHAT_MODEL", "gpt-4o-mini")

        self.allowed_origins: str = os.environ.get("ALLOWED_ORIGINS", "*")
        self.max_upload_chars: int = int(os.environ.get("MAX_UPLOAD_CHARS", "200000"))


settings = Settings()
