"""
Kiểm thử tự động cho 5 API Backend dùng dữ liệu tạm trong pytest tmp_path.
Không ghi bất kỳ file nào vào thư mục data/ hay ai_models/ của nhóm.

Chạy lệnh (từ thư mục backend/):
    python -m pytest -v
"""

from pathlib import Path
from types import SimpleNamespace

import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sklearn.feature_extraction.text import TfidfVectorizer

from app.database import csv_loader
from app.main import app
from app.services import recommend_service


class DummyTrainset:
    """Giả lập trainset của surprise chứa tập User-ID đã học trong Train."""

    def __init__(self, known_users: set[int]) -> None:
        self._known_users = known_users

    def to_inner_uid(self, user_id: int) -> int:
        if user_id not in self._known_users:
            raise ValueError(f"User {user_id} is not part of the trainset.")
        return user_id


class DummySVDModel:
    """Giả lập đối tượng SVD của thư viện surprise có .trainset và .predict(uid, iid)."""

    def __init__(self, train_users: set[int]) -> None:
        self.trainset = DummyTrainset(train_users)

    def predict(self, user_id: int, isbn: str) -> SimpleNamespace:
        scores = {
            "0439425220": 9.5,
            "0394800389": 8.8,
            "052165615X": 7.9,
            "0155061224": 6.5,
        }
        return SimpleNamespace(est=scores.get(isbn, 5.0))


@pytest.fixture(autouse=True)
def setup_temp_data_and_models(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Tạo file CSV và .pkl mẫu trong thư mục tạm để test độc lập."""
    data_dir = tmp_path / "processed"
    model_dir = tmp_path / "saved_models"
    data_dir.mkdir()
    model_dir.mkdir()

    # 1. Tạo books_cleaned.csv giả lập cấu trúc Book-Crossing (có ISBN bắt đầu bằng số 0 và chữ X)
    books_df = pd.DataFrame(
        [
            {
                "ISBN": "0439425220",
                "Book-Title": "Harry Potter and the Chamber of Secrets",
                "Book-Author": "J. K. Rowling",
                "Year-Of-Publication": "1999",
                "Publisher": "Scholastic",
                "Image-URL-M": "https://example.com/hp2.jpg",
            },
            {
                "ISBN": "0439139597",
                "Book-Title": "Harry Potter and the Goblet of Fire",
                "Book-Author": "J. K. Rowling",
                "Year-Of-Publication": "2000",
                "Publisher": "Scholastic",
                "Image-URL-M": "https://example.com/hp4.jpg",
            },
            {
                "ISBN": "0394800389",
                "Book-Title": "Fox in Socks",
                "Book-Author": "Dr. Seuss",
                "Year-Of-Publication": "1965",
                "Publisher": "Random House",
                "Image-URL-M": "https://example.com/fox.jpg",
            },
            {
                "ISBN": "052165615X",
                "Book-Title": "Clean Code Guide",
                "Book-Author": "Robert Martin",
                "Year-Of-Publication": "2008",
                "Publisher": "Prentice Hall",
                "Image-URL-M": "https://example.com/cc.jpg",
            },
        ]
    )
    books_df.to_csv(data_dir / "books_cleaned.csv", index=False)

    # 2. Tạo ratings_cleaned.csv mẫu (User 166596 đã đọc 0439139597, chưa đọc 3 cuốn còn lại)
    ratings_df = pd.DataFrame(
        [
            {"User-ID": 166596, "ISBN": "0439139597", "Book-Rating": 9.0},
            {"User-ID": 100001, "ISBN": "0439425220", "Book-Rating": 9.5},
            {"User-ID": 100001, "ISBN": "0394800389", "Book-Rating": 8.5},
            {"User-ID": 100002, "ISBN": "052165615X", "Book-Rating": 8.0},
        ]
    )
    ratings_df.to_csv(data_dir / "ratings_cleaned.csv", index=False)

    # 3. Tạo popularity_model.pkl đúng cấu trúc notebook TV3
    pop_df = pd.DataFrame(
        [
            {
                "ISBN": "0439425220",
                "Book-Title": "Harry Potter and the Chamber of Secrets",
                "Book-Author": "J. K. Rowling",
                "rating_count": 20,
                "rating_mean": 9.5,
            },
            {
                "ISBN": "0394800389",
                "Book-Title": "Fox in Socks",
                "Book-Author": "Dr. Seuss",
                "rating_count": 15,
                "rating_mean": 8.5,
            },
        ]
    )
    joblib.dump(
        {"popular_books_df": pop_df, "id_col": "ISBN", "title_col": "Book-Title"},
        model_dir / "popularity_model.pkl",
    )

    # 4. Tạo content_based_model.pkl đúng cấu trúc notebook TV3
    features = books_df["Book-Author"] + " " + books_df["Publisher"]
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(features)
    indices = pd.Series(books_df.index, index=books_df["ISBN"]).drop_duplicates()
    joblib.dump(
        {
            "tfidf_vectorizer": tfidf,
            "tfidf_matrix": tfidf_matrix,
            "df_books": books_df[["ISBN", "Book-Title", "Book-Author"]],
            "indices": indices,
            "id_col": "ISBN",
            "title_col": "Book-Title",
        },
        model_dir / "content_based_model.pkl",
    )

    # Trỏ đường dẫn CSV & Model sang thư mục tạm và xóa cache cũ
    monkeypatch.setattr(csv_loader, "DATA_DIR", data_dir)
    monkeypatch.setattr(recommend_service, "MODEL_DIR", model_dir)
    csv_loader.clear_csv_cache()
    recommend_service.clear_model_cache()
    # Chỉ 166596 và 100001 nằm trong tập Train SVD; 100002 giả lập user chỉ thuộc Validation/Test
    recommend_service._model_cache["collaborative_model.pkl"] = DummySVDModel({166596, 100001})


client = TestClient(app)


def test_health_check() -> None:
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_popular_books() -> None:
    res = client.get("/api/popular", params={"top_k": 10})
    assert res.status_code == 200
    body = res.json()
    assert len(body["popular_books"]) == 2
    first = body["popular_books"][0]
    assert first["book_id"] == "0439425220"  # Giữ nguyên số 0 ở đầu ISBN
    assert first["image_url"] == "https://example.com/hp2.jpg"
    assert first["score"] == 9.5


def test_search_books() -> None:
    res = client.get("/api/books/search", params={"q": "harry"})
    assert res.status_code == 200
    books = res.json()["books"]
    assert len(books) == 2
    assert all("Harry Potter" in b["title"] for b in books)


def test_book_detail_and_404() -> None:
    res_ok = client.get("/api/books/052165615X")
    assert res_ok.status_code == 200
    assert res_ok.json()["title"] == "Clean Code Guide"
    assert res_ok.json()["rating_mean"] == 8.0

    res_missing = client.get("/api/books/9999999999")
    assert res_missing.status_code == 404


def test_similar_books() -> None:
    res = client.get("/api/books/0439425220/similar", params={"top_k": 2})
    assert res.status_code == 200
    body = res.json()
    assert body["target_book_id"] == "0439425220"
    assert len(body["similar_books"]) == 2
    # Sách cùng tác giả J. K. Rowling và NXB Scholastic phải đứng đầu
    assert body["similar_books"][0]["book_id"] == "0439139597"
    assert body["similar_books"][0]["score"] > 0


def test_recommend_known_user_and_cold_start_fallback() -> None:
    # 1. User đã có lịch sử -> chạy Collaborative Filtering (SVD)
    res_ok = client.get("/api/recommend/166596", params={"top_k": 3})
    assert res_ok.status_code == 200
    body = res_ok.json()
    assert body["user_id"] == 166596
    assert body["is_cold_start"] is False
    assert body["recommend_type"] == "Collaborative Filtering (SVD)"
    recs = body["recommendations"]
    assert len(recs) == 3
    # Không gợi ý lại sách 0439139597 mà user 166596 đã đọc
    assert all(item["book_id"] != "0439139597" for item in recs)
    assert recs[0]["book_id"] == "0439425220"
    assert recs[0]["score"] == 9.5

    # 2. User có trong CSV (Validation/Test) nhưng KHÔNG nằm trong trainset SVD -> Popularity Fallback
    res_val_only = client.get("/api/recommend/100002", params={"top_k": 10})
    assert res_val_only.status_code == 200
    val_body = res_val_only.json()
    assert val_body["user_id"] == 100002
    assert val_body["is_cold_start"] is True
    assert val_body["recommend_type"] == "Popularity-Based (Cold Start Fallback)"

    # 3. User mới chưa có lịch sử (Cold Start) -> tự động chuyển sang Popularity-Based (200 OK)
    res_cold_start = client.get("/api/recommend/999999999", params={"top_k": 10})
    assert res_cold_start.status_code == 200
    cold_body = res_cold_start.json()
    assert cold_body["user_id"] == 999999999
    assert cold_body["is_cold_start"] is True
    assert cold_body["recommend_type"] == "Popularity-Based (Cold Start Fallback)"
    cold_recs = cold_body["recommendations"]
    assert len(cold_recs) == 2
    assert cold_recs[0]["book_id"] == "0439425220"
    assert cold_recs[0]["score"] == 9.5


def test_missing_model_returns_503(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    recommend_service.clear_model_cache()
    monkeypatch.setattr(recommend_service, "MODEL_DIR", tmp_path / "empty_models")
    res = client.get("/api/popular")
    assert res.status_code == 503
    assert "popularity_model.pkl" in res.json()["detail"]
