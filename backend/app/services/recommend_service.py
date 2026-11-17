"""
Tầng Service: Nạp 3 file mô hình .pkl từ thư mục ai_models/saved_models/
và kết hợp với thông tin sách từ CSV để trả kết quả cho Frontend.

3 file mô hình do Thành viên 2 và 3 xuất ra:
- popularity_model.pkl    : Sách phổ biến nhất
- content_based_model.pkl : Sách tương tự theo TF-IDF (tác giả, NXB/thể loại)
- collaborative_model.pkl : Mô hình SVD (scikit-surprise) gợi ý theo User-ID
"""

import heapq

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel

from app.config import MODEL_DIR
from app.database.csv_loader import (
    get_book_detail_dict,
    get_top_candidate_isbns,
    get_user_seen_books,
    load_books,
)

# Bộ nhớ đệm (cache) lưu mô hình sau lần nạp đầu tiên
_model_cache: dict[str, object] = {}


def clear_model_cache() -> None:
    """Xóa cache mô hình trong RAM."""
    _model_cache.clear()


def _load_model(filename: str) -> object:
    """Đọc file .pkl bằng joblib và thông báo lỗi rõ ràng nếu thiếu file hoặc thiếu thư viện."""
    if filename in _model_cache:
        return _model_cache[filename]

    model_path = MODEL_DIR / filename
    if not model_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file mô hình '{model_path}'. "
            "Hãy chép các file .pkl đã train vào thư mục ai_models/saved_models/."
        )

    try:
        model_obj = joblib.load(model_path)
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f"Không nạp được '{filename}' do thiếu thư viện '{exc.name}'. "
            "Nếu đây là mô hình Surprise SVD, hãy cài scikit-surprise (khuyên dùng Python 3.10/3.11)."
        ) from exc

    _model_cache[filename] = model_obj
    return model_obj


def _build_book_response(
    book_id: str,
    score: float | None = None,
    fallback_title: str = "",
    fallback_author: str = "",
    rating_mean: float | None = None,
    rating_count: int | None = None,
) -> dict:
    """
    Ghép đầy đủ thông tin sách từ books_cleaned.csv (có ảnh bìa, năm, NXB).
    Nếu sách chưa có trong books_cleaned.csv thì dùng thông tin dự phòng từ .pkl.
    """
    detail = get_book_detail_dict(book_id)
    if detail is not None:
        return {
            **detail,
            "rating_mean": detail["rating_mean"] if detail["rating_mean"] is not None else rating_mean,
            "rating_count": detail["rating_count"] if detail["rating_count"] is not None else rating_count,
            "score": score,
        }

    return {
        "book_id": book_id,
        "title": fallback_title or "Chưa có tên sách",
        "author": fallback_author,
        "year": "",
        "publisher": "",
        "image_url": "",
        "rating_mean": rating_mean,
        "rating_count": rating_count,
        "score": score,
    }


def _safe_str(value: object) -> str:
    """Chuyển giá trị sang chuỗi an toàn, tránh biến NaN thành chữ 'nan'."""
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def get_popular_books(top_k: int = 10) -> list[dict]:
    """Đọc popularity_model.pkl và trả về Top-K sách phổ biến nhất."""
    model_data = _load_model("popularity_model.pkl")
    popular_df: pd.DataFrame = model_data["popular_books_df"]
    id_col: str = model_data.get("id_col", "ISBN")
    title_col: str = model_data.get("title_col", "Book-Title")

    # Đảm bảo books_cleaned.csv sẵn sàng để gắn thêm ảnh bìa, năm, NXB
    load_books()

    results: list[dict] = []
    for _, row in popular_df.head(top_k).iterrows():
        book_id = _safe_str(row[id_col])
        mean_val = round(float(row["rating_mean"]), 2)
        count_val = int(row["rating_count"])
        author_val = _safe_str(row.get("Book-Author", row.get("author", "")))

        results.append(
            _build_book_response(
                book_id=book_id,
                score=mean_val,
                fallback_title=_safe_str(row[title_col]),
                fallback_author=author_val,
                rating_mean=mean_val,
                rating_count=count_val,
            )
        )
    return results


def get_similar_books(book_id: str, top_k: int = 5) -> list[dict]:
    """Đọc content_based_model.pkl và tìm Top-K sách giống book_id nhất."""
    model_data = _load_model("content_based_model.pkl")
    tfidf_matrix = model_data["tfidf_matrix"]
    indices = model_data["indices"]
    df_books: pd.DataFrame = model_data["df_books"]
    id_col: str = model_data.get("id_col", "ISBN")
    title_col: str = model_data.get("title_col", "Book-Title")

    if book_id not in indices:
        return []

    idx = indices[book_id]
    if isinstance(idx, pd.Series):
        idx = int(idx.iloc[0])
    else:
        idx = int(idx)

    # Tính độ tương đồng Cosine giữa sách đang xem và toàn bộ sách
    cosine_sim = linear_kernel(tfidf_matrix[idx], tfidf_matrix).flatten()
    sorted_indices = np.argsort(cosine_sim)[::-1]

    load_books()
    similar_books: list[dict] = []
    seen_ids = {book_id}

    for i in sorted_indices:
        if int(i) == idx:
            continue
        row = df_books.iloc[int(i)]
        rec_id = _safe_str(row[id_col])
        if rec_id in seen_ids:
            continue
        seen_ids.add(rec_id)

        sim_score = round(float(cosine_sim[int(i)]), 2)
        author_val = _safe_str(row.get("Book-Author", row.get("author", "")))
        similar_books.append(
            _build_book_response(
                book_id=rec_id,
                score=sim_score,
                fallback_title=_safe_str(row[title_col]),
                fallback_author=author_val,
            )
        )
        if len(similar_books) >= top_k:
            break

    return similar_books


def _is_user_in_svd_trainset(svd_model: object, user_id: int) -> bool:
    """Kiểm tra O(1) xem user_id có thực sự nằm trong trainset của mô hình SVD hay không."""
    trainset = getattr(svd_model, "trainset", None)
    if trainset is None or not hasattr(trainset, "to_inner_uid"):
        return False
    try:
        trainset.to_inner_uid(user_id)
        return True
    except ValueError:
        return False


def get_user_recommendations(user_id: int, top_k: int = 10) -> dict:
    """
    Gợi ý Top-K sách cho user_id theo chiến lược Hybrid nhất quán với mô hình đã huấn luyện:
    - Nếu user chưa có lịch sử hoặc chưa nằm trong trainset của FunkSVD (Cold Start):
      tự động fallback sang Popularity-Based để gợi ý Top-K sách phổ biến nhất.
    - Nếu user đã có nhân tố ẩn p_u trong trainset của FunkSVD: lọc sách đã đọc qua
      Hash Set O(1), chấm điểm các sách ứng viên và chọn Top-K bằng Min-Heap (O(N log K)).
    """
    seen_books = get_user_seen_books(user_id)
    if seen_books is None:
        return {
            "recommend_type": "Popularity-Based (Cold Start Fallback)",
            "is_cold_start": True,
            "message": (
                f"User-ID {user_id} chưa có lịch sử đánh giá (Cold Start). "
                f"Hệ thống tự động chuyển sang Popularity-Based gợi ý {top_k} sách phổ biến nhất."
            ),
            "recommendations": get_popular_books(top_k=top_k),
        }

    svd_model = _load_model("collaborative_model.pkl")
    if not _is_user_in_svd_trainset(svd_model, user_id):
        return {
            "recommend_type": "Popularity-Based (Cold Start Fallback)",
            "is_cold_start": True,
            "message": (
                f"User-ID {user_id} chưa nằm trong tập huấn luyện (Train) của mô hình FunkSVD "
                f"(Cold Start ở mức mô hình). Hệ thống tự động fallback sang Popularity-Based Top-{top_k}."
            ),
            "recommendations": get_popular_books(top_k=top_k),
        }

    load_books()

    # Chọn các sách có nhiều đánh giá nhất làm ứng viên và loại sách đã đọc theo O(1)
    candidate_isbns = get_top_candidate_isbns(limit=3000)
    unseen_isbns = [isbn for isbn in candidate_isbns if isbn not in seen_books]
    if not unseen_isbns:
        return {
            "recommend_type": "Popularity-Based (Cold Start Fallback)",
            "is_cold_start": True,
            "message": (
                f"Không còn sách ứng viên mới cho User-ID {user_id}. "
                f"Hệ thống chuyển sang Popularity-Based gợi ý {top_k} sách phổ biến nhất."
            ),
            "recommendations": get_popular_books(top_k=top_k),
        }

    predictions: list[tuple[str, float]] = []
    for isbn in unseen_isbns:
        est_score = float(svd_model.predict(user_id, isbn).est)
        predictions.append((isbn, est_score))

    # Tối ưu Min-Heap O(N log K) thay vì sắp xếp toàn bộ mảng O(N log N)
    top_predictions = heapq.nlargest(top_k, predictions, key=lambda item: item[1])

    recommendations = [
        _build_book_response(book_id=isbn, score=round(est_score, 2))
        for isbn, est_score in top_predictions
    ]
    return {
        "recommend_type": "Collaborative Filtering (SVD)",
        "is_cold_start": False,
        "message": (
            f"Gợi ý cá nhân hóa cho User-ID {user_id} bằng Collaborative Filtering (FunkSVD) "
            "sau khi loại bỏ các sách đã đánh giá."
        ),
        "recommendations": recommendations,
    }
