import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
VECTOR_DIR = DATA_DIR / "vector_indexes"


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "NiveshakAI")
    backend_host: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    database_path: str = os.getenv("DATABASE_PATH", str(DATA_DIR / "app.db"))
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    vector_dir: str = os.getenv("VECTOR_DIR", str(VECTOR_DIR))


settings = Settings()

DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR.mkdir(parents=True, exist_ok=True)
