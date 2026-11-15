"""
File khởi chạy chính của Backend FastAPI.

Cách chạy server (từ thư mục backend/):
    python -m uvicorn app.main:app --reload

Mở trình duyệt xem tài liệu API tự động tại:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import PORT

app = FastAPI(
    title="Book Recommender System API",
    description="Backend FastAPI đơn giản kết nối mô hình AI (.pkl) + dữ liệu CSV với Frontend.",
    version="1.0.0",
)

# Bật CORS để Frontend (chạy ở cổng 5500 hoặc cổng khác) gọi được API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["Health Check"], summary="Kiểm tra server đang hoạt động")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "Book Recommender Backend is running!",
        "docs_url": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
