from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader

from backend.app.core.config import settings
from backend.app.db.database import get_connection
from backend.app.models.chat import ChatAnswerResponse, ChatUploadResponse

try:
    import faiss  # type: ignore
    import numpy as np
    from sentence_transformers import SentenceTransformer

    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False


class ChatService:
    def __init__(self) -> None:
        self._model = None
        self._vector_dir = Path(settings.vector_dir)
        self._vector_dir.mkdir(parents=True, exist_ok=True)

    def upload_pdf(self, symbol: str, filename: str, file_bytes: bytes) -> ChatUploadResponse:
        base_symbol = symbol.strip().upper().replace(".NS", "")
        text = self._extract_pdf_text(file_bytes)
        chunks = self._chunk_text(text)
        self._index_chunks(base_symbol, chunks)

        with get_connection() as connection:
            connection.execute(
                "INSERT INTO chat_documents (symbol, filename, chunk_count) VALUES (?, ?, ?)",
                (base_symbol, filename, len(chunks)),
            )
            connection.commit()

        return ChatUploadResponse(
            symbol=base_symbol,
            filename=filename,
            chunks_indexed=len(chunks),
            message="Document indexed. You can now ask questions in the AI Company Chat page.",
        )

    def ask(self, symbol: str, question: str) -> ChatAnswerResponse:
        base_symbol = symbol.strip().upper().replace(".NS", "")
        chunks, sources = self._retrieve(base_symbol, question)
        context = "\n\n".join(chunks[:5])

        answer, used_ai = self._generate_answer(base_symbol, question, context)
        if not chunks:
            answer = (
                f"No indexed documents found for {base_symbol}. "
                "Upload an annual report PDF first on the AI Company Chat page."
            )

        return ChatAnswerResponse(
            symbol=base_symbol,
            question=question,
            answer=answer,
            sources=sources[:3],
            used_ai=used_ai,
        )

    def _extract_pdf_text(self, file_bytes: bytes) -> str:
        from io import BytesIO

        reader = PdfReader(BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)

    def _chunk_text(self, text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
        cleaned = re.sub(r"\s+", " ", text).strip()
        if not cleaned:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(cleaned):
            end = start + chunk_size
            chunks.append(cleaned[start:end])
            start = end - overlap
        return chunks

    def _index_chunks(self, symbol: str, chunks: list[str]) -> None:
        payload = {"chunks": chunks}
        text_path = self._vector_dir / f"{symbol}_chunks.json"
        text_path.write_text(json.dumps(payload), encoding="utf-8")

        if not EMBEDDINGS_AVAILABLE or not chunks:
            return

        model = self._get_model()
        vectors = model.encode(chunks, convert_to_numpy=True)
        index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(np.array(vectors, dtype="float32"))
        faiss.write_index(index, str(self._vector_dir / f"{symbol}.faiss"))

    def _retrieve(self, symbol: str, question: str) -> tuple[list[str], list[str]]:
        text_path = self._vector_dir / f"{symbol}_chunks.json"
        if not text_path.exists():
            return [], []

        chunks = json.loads(text_path.read_text(encoding="utf-8")).get("chunks", [])
        if not chunks:
            return [], []

        if EMBEDDINGS_AVAILABLE and (self._vector_dir / f"{symbol}.faiss").exists():
            model = self._get_model()
            index = faiss.read_index(str(self._vector_dir / f"{symbol}.faiss"))
            query = model.encode([question], convert_to_numpy=True)
            _, indices = index.search(np.array(query, dtype="float32"), k=min(5, len(chunks)))
            selected = [chunks[i] for i in indices[0] if i >= 0]
            sources = [chunk[:160] + "..." for chunk in selected]
            return selected, sources

        question_words = set(question.lower().split())
        scored = sorted(chunks, key=lambda c: len(question_words & set(c.lower().split())), reverse=True)
        selected = scored[:5]
        sources = [chunk[:160] + "..." for chunk in selected]
        return selected, sources

    def _generate_answer(self, symbol: str, question: str, context: str) -> tuple[str, bool]:
        if settings.gemini_api_key and context:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.gemini_api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = (
                    f"You are a beginner-friendly Indian stock analyst. Answer using ONLY the context.\n"
                    f"Company: {symbol}\nQuestion: {question}\nContext:\n{context}\n"
                    "If context is insufficient, say so clearly."
                )
                response = model.generate_content(prompt)
                return response.text.strip(), True
            except Exception:
                pass

        if not context:
            return "Upload a company PDF report to enable document Q&A.", False

        return (
            f"Based on the uploaded report for {symbol}: {context[:700]}...\n\n"
            f"Question recap: {question}\n"
            "(Keyword/RAG mode — add GEMINI_API_KEY in .env for richer AI answers.)"
        ), False

    def _get_model(self):
        if self._model is None:
            self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        return self._model
