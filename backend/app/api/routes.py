"""
Định nghĩa 5 API Endpoint chính khớp 100% với Frontend (frontend/src/services/api.js):
1. GET /api/popular
2. GET /api/books/search
3. GET /api/books/{book_id}
4. GET /api/books/{book_id}/similar
5. GET /api/recommend/{user_id}
"""

from fastapi import APIRouter, HTTPException, Query

from app.database.csv_loader import get_book_detail_dict, search_books_in_csv
from app.schemas import (
    BookOut,
    BookSearchResponse,
    PopularBooksResponse,
    SimilarBooksResponse,
    UserRecommendationsResponse,
)
from app.services.recommend_service import (
    get_popular_books,
    get_similar_books,
    get_user_recommendations,
)

router = APIRouter(prefix="/api", tags=["Book Recommender API"])


def _handle_missing_resource(exc: Exception) -> HTTPException:
    """Chuyển lỗi thiếu file CSV/.pkl hoặc thiếu thư viện thành mã HTTP 503 dễ hiểu."""
    return HTTPException(status_code=503, detail=str(exc))


@router.get(
    "/popular",
    response_model=PopularBooksResponse,
    summary="Lấy danh sách sách phổ biến nhất (Popularity-Based)",
)
def read_popular_books(
    top_k: int = Query(default=10, ge=1, le=200, description="Số lượng sách muốn lấy"),
) -> PopularBooksResponse:
    """Trả về Top-K sách được đánh giá cao và nhiều lượt bình chọn nhất."""
    try:
        items = get_popular_books(top_k=top_k)
    except (FileNotFoundError, RuntimeError) as exc:
        raise _handle_missing_resource(exc) from exc

    return PopularBooksResponse(popular_books=[BookOut(**item) for item in items])


@router.get(
    "/books/search",
    response_model=BookSearchResponse,
    summary="Tìm kiếm sách theo tên hoặc tác giả",
)
def search_books(
    q: str = Query(..., min_length=1, description="Từ khóa tên sách hoặc tên tác giả"),
    limit: int = Query(default=40, ge=1, le=100, description="Số kết quả tối đa"),
) -> BookSearchResponse:
    """Tìm sách trong books_cleaned.csv cho thanh tìm kiếm Frontend."""
    try:
        items = search_books_in_csv(keyword=q, limit=limit)
    except FileNotFoundError as exc:
        raise _handle_missing_resource(exc) from exc

    return BookSearchResponse(books=[BookOut(**item) for item in items])


@router.get(
    "/books/{book_id}",
    response_model=BookOut,
    summary="Xem chi tiết một cuốn sách theo mã ISBN",
)
def read_book_detail(book_id: str) -> BookOut:
    """Trả về thông tin chi tiết của một cuốn sách."""
    try:
        book = get_book_detail_dict(book_id)
    except FileNotFoundError as exc:
        raise _handle_missing_resource(exc) from exc

    if book is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy sách có mã '{book_id}'")
    return BookOut(**book)


@router.get(
    "/books/{book_id}/similar",
    response_model=SimilarBooksResponse,
    summary="Gợi ý các sách tương tự (Content-Based)",
)
def read_similar_books(
    book_id: str,
    top_k: int = Query(default=5, ge=1, le=50, description="Số sách tương tự cần lấy"),
) -> SimilarBooksResponse:
    """Dùng content_based_model.pkl để tìm các sách giống cuốn đang xem."""
    try:
        if get_book_detail_dict(book_id) is None:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sách có mã '{book_id}'")
        items = get_similar_books(book_id=book_id, top_k=top_k)
    except (FileNotFoundError, RuntimeError) as exc:
        raise _handle_missing_resource(exc) from exc

    return SimilarBooksResponse(
        target_book_id=book_id,
        similar_books=[BookOut(**item) for item in items],
    )


@router.get(
    "/recommend/{user_id}",
    response_model=UserRecommendationsResponse,
    summary="Gợi ý sách riêng cho người dùng (Collaborative Filtering)",
)
def read_user_recommendations(
    user_id: int,
    top_k: int = Query(default=10, ge=1, le=50, description="Số sách gợi ý tối đa"),
) -> UserRecommendationsResponse:
    """Dùng collaborative_model.pkl (SVD) dự đoán các cuốn sách user sẽ thích nhất."""
    try:
        items = get_user_recommendations(user_id=user_id, top_k=top_k)
    except (FileNotFoundError, RuntimeError) as exc:
        raise _handle_missing_resource(exc) from exc

    if items is None:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy User-ID {user_id} trong dữ liệu đánh giá.",
        )

    return UserRecommendationsResponse(
        user_id=user_id,
        recommendations=[BookOut(**item) for item in items],
    )
