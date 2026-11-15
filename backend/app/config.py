"""
Đọc cấu hình đường dẫn và cổng chạy server từ file backend/.env.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Thư mục backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Nạp các biến môi trường trong file .env
load_dotenv(BACKEND_DIR / ".env")


def _resolve_path(raw_path: str) -> Path:
    """Chuyển đường dẫn tương đối thành đường dẫn tuyệt đối."""
    path = Path(raw_path)
    if not path.is_absolute():
        path = (BACKEND_DIR / path).resolve()
    return path


PORT: int = int(os.getenv("PORT", "8000"))
DATA_DIR: Path = _resolve_path(os.getenv("DATA_DIR", "../data/processed"))
MODEL_DIR: Path = _resolve_path(os.getenv("MODEL_DIR", "../ai_models/saved_models"))
