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
    load_books,
)

# Bộ nhớ đệm (cache) lưu mô hình và Top ứng viên Trainset sau lần nạp đầu tiên
_model_cache: dict[str, object] = {}
_svd_candidate_cache: dict[int, list[str]] = {}


def clear_model_cache() -> None:
    """Xóa cache mô hình trong RAM."""
    _model_cache.clear()
    _svd_candidate_cache.clear()


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
    """Kiểm tra O(1) xem user_id có nằm trong _raw2inner_id_users của svd_model.trainset không."""
    trainset = getattr(svd_model, "trainset", None)
    if trainset is None:
        return False

    uid = int(user_id)
    raw_to_inner = getattr(trainset, "_raw2inner_id_users", None)
    if isinstance(raw_to_inner, dict):
        return uid in raw_to_inner

    if hasattr(trainset, "to_inner_uid"):
        try:
            trainset.to_inner_uid(uid)
            return True
        except ValueError:
            return False
    return False


def _get_svd_seen_isbns(svd_model: object, user_id: int) -> set[str]:
    """Lấy tập ISBN mà user_id đã chấm trong tập Train của svd_model."""
    trainset = getattr(svd_model, "trainset", None)
    if trainset is None or not hasattr(trainset, "to_inner_uid") or not hasattr(trainset, "to_raw_iid"):
        return set()
    try:
        inner_uid = trainset.to_inner_uid(int(user_id))
    except ValueError:
        return set()

    user_ratings = getattr(trainset, "ur", None)
    if not user_ratings or inner_uid not in user_ratings:
        return set()
    return {str(trainset.to_raw_iid(inner_iid)) for inner_iid, _ in user_ratings[inner_uid]}


def _get_svd_top_candidate_isbns(svd_model: object, limit: int = 3000) -> list[str]:
    """Lấy Top-N sách phổ biến nhất hoàn toàn từ trainset.ir theo (-count, -mean, isbn) khớp evaluation.ipynb."""
    cache_key = id(svd_model)
    cached = _svd_candidate_cache.get(cache_key)
    if cached is not None:
        return cached[:limit]

    trainset = getattr(svd_model, "trainset", None)
    item_ratings = getattr(trainset, "ir", None) if trainset is not None else None
    if not item_ratings or not hasattr(trainset, "to_raw_iid"):
        return get_top_candidate_isbns(limit=limit)

    def _candidate_sort_key(entry: tuple[object, list]) -> tuple[int, float, str]:
        inner_iid, ratings = entry
        isbn = str(trainset.to_raw_iid(inner_iid))
        count = len(ratings)
        mean_rating = sum(float(rating) for _, rating in ratings) / count if count else 0.0
        return (-count, -mean_rating, isbn)

    ranked_isbns = [
        str(trainset.to_raw_iid(inner_iid))
        for inner_iid, _ in sorted(item_ratings.items(), key=_candidate_sort_key)
    ]
    _svd_candidate_cache[cache_key] = ranked_isbns
    return ranked_isbns[:limit]


def get_user_recommendations(user_id: int, top_k: int = 10) -> dict:
    """
    Gợi ý Top-K sách cho user_id theo chiến lược Hybrid nhất quán với ranh giới Train:
    - Kiểm tra trực tiếp bảng băm _raw2inner_id_users trong svd_model.trainset trước (O(1)):
      nếu user chưa có nhân tố ẩn (user mới hoặc chỉ ở Validation/Test), fallback sang Popularity-Based.
    - Nếu user thuộc svd_model.trainset: chỉ dùng lịch sử Train (trainset.ur) và tập ứng viên
      Train-only (trainset.ir) để chấm điểm bằng FunkSVD và chọn Top-K bằng Min-Heap (O(N log K)),
      tách bạch hoàn toàn khỏi dữ liệu Validation/Test trong ratings_cleaned.csv.
    """
    svd_model = _load_model("collaborative_model.pkl")
    if not _is_user_in_svd_trainset(svd_model, user_id):
        return {
            "recommend_type": "Popularity-Based (Cold Start Fallback)",
            "is_cold_start": True,
            "message": (
                f"User-ID {user_id} không thuộc tập huấn luyện Train của FunkSVD (Cold Start). "
                f"Hệ thống tự động fallback sang Popularity-Based Top-{top_k} sách phổ biến nhất."
            ),
            "recommendations": get_popular_books(top_k=top_k),
        }

    load_books()

    seen_books = _get_svd_seen_isbns(svd_model, user_id)

    # Chọn ứng viên phổ biến hoàn toàn trong Trainset (trainset.ir) và loại sách đã đọc theo O(1)
    candidate_isbns = _get_svd_top_candidate_isbns(svd_model, limit=3000)
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
