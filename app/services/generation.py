import json
from openai import OpenAI

from app.config import settings
from app.services.vectorstore import query_chunks
from app.models import (
    ConceptsResponse,
    QuestionsResponse,
    FlashcardsResponse,
    StudyPlanResponse,
)

_client = OpenAI(api_key=settings.openai_api_key)

# Each task defines: a retrieval query (what to fetch from Pinecone for this task),
# a system prompt, and the pydantic model used to validate the model's JSON output.
TASKS = {
    "concepts": {
        "retrieval_query": "key terms, definitions, and important concepts in this material",
        "system": (
            "You are a study coach. Read the study material excerpts and identify the 5-6 most "
            "important concepts or terms a student must understand. Respond with ONLY valid JSON "
            "(no markdown fences, no commentary) matching exactly this schema: "
            '{"concepts":[{"term":"string","explanation":"a clear 2-3 sentence explanation in plain language"}]}'
        ),
        "model_cls": ConceptsResponse,
        "max_tokens": 1200,
    },
    "questions": {
        "retrieval_query": "important facts, definitions, and ideas worth testing understanding of",
        "system": (
            "You are a study coach writing a short quiz. Read the study material excerpts and write "
            "5 multiple-choice practice questions that test real understanding, not just recall of "
            "wording. Respond with ONLY valid JSON (no markdown fences, no commentary) matching exactly "
            'this schema: {"questions":[{"question":"string","options":["string","string","string","string"],'
            '"correctIndex":0,"explanation":"1-2 sentence explanation of why the answer is correct"}]}'
        ),
        "model_cls": QuestionsResponse,
        "max_tokens": 1400,
    },
    "flashcards": {
        "retrieval_query": "key terms, facts, and ideas worth memorizing",
        "system": (
            "You are a study coach making flashcards. Read the study material excerpts and produce "
            "8-10 flashcards covering key terms, facts, and ideas. Fronts should be short questions or "
            "terms; backs should be concise answers (1-2 sentences). Respond with ONLY valid JSON "
            '(no markdown fences, no commentary) matching exactly: {"flashcards":[{"front":"string","back":"string"}]}'
        ),
        "model_cls": FlashcardsResponse,
        "max_tokens": 1200,
    },
    "plan": {
        "retrieval_query": "overall structure, topics, and difficulty of this material",
        "system": (
            "You are a study coach building a study schedule. Read the study material excerpts and "
            "design a realistic 5-day study plan to master it, assuming about 30-45 minutes per day. "
            'Respond with ONLY valid JSON (no markdown fences, no commentary) matching exactly: '
            '{"days":[{"day":1,"title":"string","minutes":30,"tasks":["string","string"]}]}'
        ),
        "model_cls": StudyPlanResponse,
        "max_tokens": 1200,
    },
}


def generate(kind: str, session_id: str):
    task = TASKS[kind]

    # Pull the most relevant chunks for this task from Pinecone (RAG retrieval).
    chunks = query_chunks(session_id, task["retrieval_query"], top_k=8)
    if not chunks:
        raise ValueError("No study material found for this session. Upload a file first.")
    context = "\n\n---\n\n".join(chunks)

    resp = _client.chat.completions.create(
        model=settings.chat_model,
        max_tokens=task["max_tokens"],
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": task["system"]},
            {"role": "user", "content": f"STUDY MATERIAL EXCERPTS:\n\n{context}"},
        ],
    )

    raw = resp.choices[0].message.content
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}")

    # Validate shape before handing back to the client.
    validated = task["model_cls"](**data)
    return validated
