"""
Đọc dữ liệu sách và thống kê hiển thị từ thư mục data/processed/*.csv phục vụ lớp giao diện Demo.
Lưu ý tách biệt dữ liệu: các luồng gợi ý SVD, Popularity Fallback và đánh giá đều tuân thủ
ranh giới tập Train bên trong *.pkl (không dùng dữ liệu Validation/Test trong CSV để phân nhánh).
"""

import pandas as pd

from app.config import DATA_DIR

# Cache dữ liệu trong RAM sau lần đọc đầu tiên
_books_df: pd.DataFrame | None = None
_books_by_id: dict[str, dict] | None = None
_ratings_stats: dict[str, tuple[float, int]] | None = None
_user_seen_books: dict[int, set[str]] | None = None
_top_candidate_isbns: list[str] | None = None


def clear_csv_cache() -> None:
    """Xóa cache dữ liệu CSV (dùng khi kiểm thử hoặc thay file CSV mới)."""
    global _books_df, _books_by_id, _ratings_stats, _user_seen_books, _top_candidate_isbns
    _books_df = None
    _books_by_id = None
    _ratings_stats = None
    _user_seen_books = None
    _top_candidate_isbns = None


def _clean_year(value: object) -> int | str:
    """Chuẩn hóa năm xuất bản (bỏ qua giá trị 0, NaN hoặc chữ lỗi)."""
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if not text or text == "0":
        return ""
    try:
        year_num = int(float(text))
        return "" if year_num == 0 else year_num
    except ValueError:
        return text


def _pick_column(df: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    """Tìm tên cột đầu tiên tồn tại trong DataFrame."""
    for name in candidates:
        if name in df.columns:
            return name
    return None


def load_books() -> tuple[pd.DataFrame, dict[str, dict]]:
    """
    Đọc file books_cleaned.csv và chuẩn hóa về các cột chung:
    book_id, title, author, year, publisher, image_url.
    """
    global _books_df, _books_by_id
    if _books_df is not None and _books_by_id is not None:
        return _books_df, _books_by_id

    books_path = DATA_DIR / "books_cleaned.csv"
    if not books_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file dữ liệu '{books_path}'. "
            "Hãy chép file books_cleaned.csv từ Thành viên 1 vào thư mục data/processed/."
        )

    raw_df = pd.read_csv(
        books_path,
        low_memory=False,
        dtype={"ISBN": str, "book_id": str, "Year-Of-Publication": str, "year": str},
    )
    id_col = _pick_column(raw_df, ("book_id", "ISBN")) or raw_df.columns[0]
    title_col = _pick_column(raw_df, ("title", "Book-Title")) or raw_df.columns[1]
    author_col = _pick_column(raw_df, ("author", "Book-Author"))
    year_col = _pick_column(raw_df, ("year", "Year-Of-Publication"))
    pub_col = _pick_column(raw_df, ("publisher", "Publisher"))
    img_col = _pick_column(raw_df, ("image_url", "Image-URL-M", "Image-URL-L", "Image-URL-S"))

    clean_df = pd.DataFrame()
    clean_df["book_id"] = raw_df[id_col].astype(str).str.strip()
    clean_df["title"] = raw_df[title_col].fillna("Chưa có tên sách").astype(str)
    clean_df["author"] = raw_df[author_col].fillna("").astype(str) if author_col else ""
    clean_df["year"] = raw_df[year_col].apply(_clean_year) if year_col else ""
    clean_df["publisher"] = raw_df[pub_col].fillna("").astype(str) if pub_col else ""
    clean_df["image_url"] = raw_df[img_col].fillna("").astype(str) if img_col else ""

    # Tạo từ điển tra cứu nhanh theo book_id (O(1))
    clean_df = clean_df.drop_duplicates(subset=["book_id"]).reset_index(drop=True)
    books_dict = {
        row["book_id"]: {
            "book_id": row["book_id"],
            "title": row["title"],
            "author": row["author"],
            "year": row["year"],
            "publisher": row["publisher"],
            "image_url": row["image_url"],
        }
        for row in clean_df.to_dict(orient="records")
    }

    _books_df = clean_df
    _books_by_id = books_dict
    return _books_df, _books_by_id


def _load_ratings_summary(required: bool = False) -> None:
    """
    Đọc file ratings_cleaned.csv (nếu có) để tính sẵn:
    - Điểm trung bình và số lượt đánh giá của từng sách
    - Danh sách sách mỗi user đã đánh giá
    - Danh sách sách được đánh giá nhiều nhất (làm ứng viên cho SVD)
    """
    global _ratings_stats, _user_seen_books, _top_candidate_isbns
    if _ratings_stats is not None:
        return

    ratings_path = DATA_DIR / "ratings_cleaned.csv"
    if not ratings_path.exists():
        if required:
            raise FileNotFoundError(
                f"Không tìm thấy file dữ liệu '{ratings_path}'. "
                "Hãy chép file ratings_cleaned.csv từ Thành viên 1 vào thư mục data/processed/."
            )
        _ratings_stats = {}
        _user_seen_books = {}
        _top_candidate_isbns = []
        return

    df = pd.read_csv(
        ratings_path,
        low_memory=False,
        dtype={"ISBN": str, "book_id": str},
    )
    uid_col = _pick_column(df, ("user_id", "User-ID")) or df.columns[0]
    bid_col = _pick_column(df, ("book_id", "ISBN")) or df.columns[1]
    rate_col = _pick_column(df, ("rating", "Book-Rating")) or df.columns[2]

    df[uid_col] = pd.to_numeric(df[uid_col], errors="coerce")
    df[rate_col] = pd.to_numeric(df[rate_col], errors="coerce")
    df = df.dropna(subset=[uid_col, bid_col, rate_col])
    df[uid_col] = df[uid_col].astype(int)
    df[bid_col] = df[bid_col].astype(str).str.strip()

    # 1. Thống kê theo sách
    grouped = (
        df.groupby(bid_col)[rate_col]
        .agg(rating_mean="mean", rating_count="count")
        .sort_values(by=["rating_count", "rating_mean"], ascending=[False, False])
    )
    _ratings_stats = {
        str(bid): (round(float(row["rating_mean"]), 2), int(row["rating_count"]))
        for bid, row in grouped.iterrows()
    }
    _top_candidate_isbns = [str(bid) for bid in grouped.index]

    # 2. Lịch sử sách đã đánh giá của từng user
    _user_seen_books = {
        int(uid): set(group[bid_col].astype(str))
        for uid, group in df.groupby(uid_col)
    }


def get_book_detail_dict(book_id: str) -> dict | None:
    """Lấy thông tin đầy đủ của một cuốn sách kèm điểm đánh giá trung bình."""
    _, books_by_id = load_books()
    book = books_by_id.get(str(book_id).strip())
    if book is None:
        return None

    _load_ratings_summary(required=False)
    stats = _ratings_stats.get(book["book_id"])
    return {
        **book,
        "rating_mean": stats[0] if stats else None,
        "rating_count": stats[1] if stats else None,
    }


def search_books_in_csv(keyword: str, limit: int = 40) -> list[dict]:
    """Tìm kiếm sách theo tên sách hoặc tên tác giả (không phân biệt hoa thường)."""
    books_df, _ = load_books()
    q = keyword.strip()
    if not q:
        return []

    mask_title = books_df["title"].str.contains(q, case=False, na=False, regex=False)
    mask_author = books_df["author"].str.contains(q, case=False, na=False, regex=False)
    matched = books_df[mask_title | mask_author].head(limit)

    _load_ratings_summary(required=False)
    results: list[dict] = []
    for row in matched.to_dict(orient="records"):
        stats = _ratings_stats.get(row["book_id"])
        results.append(
            {
                **row,
                "rating_mean": stats[0] if stats else None,
                "rating_count": stats[1] if stats else None,
                "score": stats[0] if stats else None,
            }
        )
    return results


def get_user_seen_books(user_id: int) -> set[str] | None:
    """
    Tra cứu lịch sử sách user_id đã đánh giá trong ratings_cleaned.csv theo O(1).
    Chỉ dùng để loại bỏ sách đã đọc; việc phân nhánh Cold Start do
    recommend_service.py kiểm tra trực tiếp trên _raw2inner_id_users của svd_model.
    """
    _load_ratings_summary(required=True)
    return _user_seen_books.get(int(user_id))


def get_top_candidate_isbns(limit: int = 3000) -> list[str]:
    """Lấy tối đa `limit` mã sách có nhiều lượt đánh giá nhất để mô hình SVD chấm điểm nhanh."""
    _load_ratings_summary(required=True)
    return _top_candidate_isbns[:limit]
