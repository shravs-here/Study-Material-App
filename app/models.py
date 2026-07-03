from typing import List, Literal
from pydantic import BaseModel


class UploadResponse(BaseModel):
    session_id: str
    filename: str
    chunk_count: int
    char_count: int
    preview: str


class GenerateRequest(BaseModel):
    session_id: str


class Concept(BaseModel):
    term: str
    explanation: str


class ConceptsResponse(BaseModel):
    concepts: List[Concept]


class Question(BaseModel):
    question: str
    options: List[str]
    correctIndex: int
    explanation: str


class QuestionsResponse(BaseModel):
    questions: List[Question]


class Flashcard(BaseModel):
    front: str
    back: str


class FlashcardsResponse(BaseModel):
    flashcards: List[Flashcard]


class StudyDay(BaseModel):
    day: int
    title: str
    minutes: int
    tasks: List[str]


class StudyPlanResponse(BaseModel):
    days: List[StudyDay]


GenerateKind = Literal["concepts", "questions", "flashcards", "plan"]
