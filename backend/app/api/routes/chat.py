from fastapi import APIRouter, File, Form, UploadFile

from backend.app.models.chat import ChatAnswerResponse, ChatQuestionRequest, ChatUploadResponse
from backend.app.services.chat_service import ChatService


router = APIRouter()
service = ChatService()


@router.post("/upload", response_model=ChatUploadResponse)
async def upload_document(
    symbol: str = Form(...),
    file: UploadFile = File(...),
) -> ChatUploadResponse:
    content = await file.read()
    return service.upload_pdf(symbol=symbol, filename=file.filename or "document.pdf", file_bytes=content)


@router.post("/ask", response_model=ChatAnswerResponse)
def ask_question(request: ChatQuestionRequest) -> ChatAnswerResponse:
    return service.ask(symbol=request.symbol, question=request.question)
