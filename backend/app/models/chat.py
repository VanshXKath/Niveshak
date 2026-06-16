from pydantic import BaseModel


class ChatUploadResponse(BaseModel):
    symbol: str
    filename: str
    chunks_indexed: int
    message: str


class ChatQuestionRequest(BaseModel):
    symbol: str
    question: str


class ChatAnswerResponse(BaseModel):
    symbol: str
    question: str
    answer: str
    sources: list[str]
    used_ai: bool
