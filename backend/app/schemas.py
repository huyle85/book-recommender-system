"""
Định nghĩa cấu trúc dữ liệu Đầu ra (JSON Response) rõ ràng bằng Pydantic.
Các tên trường khớp trực tiếp với hàm ChuanHoaSach() bên Frontend (api.js).
"""

from pydantic import BaseModel, Field


class BookOut(BaseModel):
    """Thông tin chuẩn của một cuốn sách trả về cho Frontend."""

    book_id: str = Field(..., examples=["0439425220"], description="Mã ISBN của sách")
    title: str = Field(..., examples=["Harry Potter"], description="Tên sách")
    author: str = Field(default="", examples=["J. K. Rowling"], description="Tác giả")
    year: int | str = Field(default="", examples=[2001], description="Năm xuất bản")
    publisher: str = Field(default="", examples=["Scholastic"], description="Nhà xuất bản")
    image_url: str = Field(default="", description="Link ảnh bìa sách")
    rating_mean: float | None = Field(default=None, description="Điểm đánh giá trung bình (1-10)")
    rating_count: int | None = Field(default=None, description="Số lượt đánh giá")
    score: float | None = Field(
        default=None,
        description="Điểm gợi ý (điểm dự đoán rating, điểm phổ biến hoặc độ tương đồng)",
    )


class PopularBooksResponse(BaseModel):
    """Đầu ra cho GET /api/popular"""

    recommend_type: str = "Popularity (Cold Start)"
    popular_books: list[BookOut]


class BookSearchResponse(BaseModel):
    """Đầu ra cho GET /api/books/search"""

    books: list[BookOut]


class SimilarBooksResponse(BaseModel):
    """Đầu ra cho GET /api/books/{book_id}/similar"""

    target_book_id: str
    similar_books: list[BookOut]


class UserRecommendationsResponse(BaseModel):
    """Đầu ra cho GET /api/recommend/{user_id}"""

    user_id: int
    recommendations: list[BookOut]
