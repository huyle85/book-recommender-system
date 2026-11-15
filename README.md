# Hệ thống Gợi ý Sách (Book Recommender System)

Đồ án nhóm xây dựng hệ thống gợi ý sách kết hợp 3 hướng tiếp cận (**Popularity-Based**, **Content-Based TF-IDF**, và **Collaborative Filtering SVD**), phục vụ qua **FastAPI** (đọc dữ liệu từ CSV + model `.pkl`, không cần cài PostgreSQL) và giao diện web **HTML/CSS/JS**.

---

## 1. Cấu trúc thư mục project

```text
book-recommender-system/
│
├── data/                            # [Người 1] Dữ liệu gốc & dữ liệu đã làm sạch (không push Git)
│   ├── raw/                         # Dữ liệu gốc nguyên bản tải từ Kaggle
│   └── processed/                   # books_cleaned.csv, ratings_cleaned.csv, users_cleaned.csv
│
├── ai_models/                       # [Người 2, 3, 4 - AI & Evaluate]
│   ├── notebooks/                   # preprocessing.py, popularity_based.ipynb, content_based.ipynb,
│   │                                # collaborative_filtering.ipynb, evaluation.ipynb
│   ├── saved_models/                # Nơi xuất 3 file .pkl sau khi chạy notebook (không push Git)
│   └── requirements.txt
│
├── backend/                         # [Người 5 - Backend API (FastAPI + CSV + .pkl)]
│   ├── app/
│   │   ├── main.py                  # Khởi tạo server FastAPI + CORS + route GET /
│   │   ├── config.py                # Đọc cấu hình từ file .env
│   │   ├── schemas.py               # Định nghĩa Input / Output JSON bằng Pydantic
│   │   ├── api/
│   │   │   └── routes.py            # 5 API endpoint khớp với Frontend
│   │   ├── services/
│   │   │   └── recommend_service.py # Đọc 3 file .pkl và sinh kết quả gợi ý
│   │   └── database/
│   │       └── csv_loader.py        # Đọc books_cleaned.csv và ratings_cleaned.csv vào RAM
│   ├── tests/
│   │   └── test_api.py              # Kiểm thử tự động bằng pytest
│   ├── .env                         # Biến môi trường cục bộ (không push Git)
│   ├── .env.example                 # File mẫu cấu hình PORT, DATA_DIR, MODEL_DIR
│   └── requirements.txt             # Danh sách thư viện Python cho Backend
│
├── frontend/                        # [Người 6 - Frontend UI (HTML/CSS/JS thuần)]
│   ├── public/
│   │   └── index.html               # Trang web chính
│   ├── src/
│   │   └── services/
│   │       └── api.js               # Gọi API Backend tại http://localhost:8000/api
│   └── package.json
│
├── docs/                            # [Không gian chung] Tài liệu & hình ảnh
├── .gitignore                       # Chặn đẩy *.csv, *.pkl, .env, venv/ lên Git
└── README.md                        # Hướng dẫn cài đặt và chạy project
```

---

## 2. Cài đặt thư viện (`requirements.txt`)

> Frontend chỉ dùng HTML/CSS/JS thuần nên **không cần** `npm install`. Bạn chỉ cần cài thư viện Python cho Backend.

### Cách 1: Cài bằng môi trường ảo `venv` (khuyên dùng)
Mở **CMD** (hoặc **PowerShell**) tại thư mục gốc của project (`book-recommender-system/`) rồi chạy:

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt
```
*(Nếu dùng **PowerShell** thì thay dòng `venv\Scripts\activate` bằng `.\venv\Scripts\Activate.ps1`; nếu dùng **macOS/Linux** thì dùng `source venv/bin/activate && pip install -r backend/requirements.txt`.)*

### Cách 2: Cài trực tiếp vào Python hiện tại của máy
Mở terminal tại thư mục gốc của project rồi chạy:
```cmd
cd backend
pip install -r requirements.txt
```

**Lưu ý khi cài thư viện trên Windows:**
- **Nếu dùng Python từ Microsoft Store:** Khi chạy `pip install`, nếu thấy dòng `Defaulting to user installation because normal site-packages is not writeable`, các file `.exe` (như `uvicorn`, `pytest`) sẽ được cài vào thư mục `...\LocalCache\local-packages\Python313\Scripts` chưa có sẵn trong `PATH`. Do đó khi chạy lệnh ở các bước sau, hãy **luôn thêm `python -m` ở đầu** (`python -m uvicorn ...`, `python -m pytest ...`) để tránh lỗi `'uvicorn' is not recognized`.
- **Về `scikit-surprise`:** File `collaborative_model.pkl` dùng `surprise.SVD`, nên `backend/requirements.txt` đã khai báo sẵn `scikit-surprise>=1.1.4` (đã test chạy ổn với `scikit-surprise==1.1.5` trên Python 3.13.14 Windows). Nếu máy khác gặp lỗi biên dịch từ mã nguồn khi `pip install`, hãy dùng Python 3.10/3.11 hoặc cài Microsoft C++ Build Tools.

---

## 3. Chuẩn bị dữ liệu `.csv`, model `.pkl` và file `.env`

Vì `.gitignore` chặn `*.csv`, `*.pkl` và `.env`, khi chạy trên máy mới bạn cần chuẩn bị sẵn các file sau ở máy (chỉ lưu cục bộ để chạy, **không commit lên Git**):

1. **Dữ liệu đã làm sạch** — đặt vào `data/processed/`:
   - `books_cleaned.csv`
   - `ratings_cleaned.csv`
2. **3 file model đã train** — đặt vào `ai_models/saved_models/`:
   - `popularity_model.pkl`
   - `content_based_model.pkl`
   - `collaborative_model.pkl`
   *(Nếu thư mục `ai_models/saved_models/` chưa có 3 file trên, hãy mở và chạy lần lượt 3 notebook trong `ai_models/notebooks/`: `popularity_based.ipynb`, `content_based.ipynb`, `collaborative_filtering.ipynb`.)*
3. **File cấu hình môi trường Backend** — chạy tại thư mục gốc của project để tạo `backend/.env` từ file mẫu (nếu chưa có):
   ```cmd
   copy backend\.env.example backend\.env
   ```

---

## 4. Lệnh chạy thử Frontend + Backend trên máy

> **Lưu ý tránh lỗi `'uvicorn' is not recognized...` trên Windows:** Luôn chạy bằng `python -m uvicorn ...` (hoặc kích hoạt `venv` trước). Cả 2 terminal bên dưới đều bắt đầu từ **thư mục gốc của project (`book-recommender-system/`)**.

### Mở Terminal 1 chạy Backend (Swagger docs ở `http://localhost:8000/docs`)
```cmd
cd backend
python -m uvicorn app.main:app --reload
```

### Mở Terminal 2 chạy Frontend
```cmd
cd frontend
python -m http.server 5500
```

### Mở trình duyệt để sử dụng
- Truy cập giao diện web tại: **`http://localhost:5500/public/index.html`**
  - Để thử gợi ý cá nhân hóa trên giao diện, bạn có thể nhập một `User ID` hợp lệ như **`166596`**.
  - *Lưu ý:* Request đầu tiên sau khi bật Backend sẽ mất vài giây đến ~15 giây để nạp 2 file CSV vào bộ nhớ đệm RAM; các request sau phản hồi rất nhanh.
- Xem và test trực tiếp API qua Swagger UI tại: **`http://localhost:8000/docs`**

---

## 5. Danh sách API Backend & Chạy kiểm thử (`pytest`)

### Các API chính
| Phương thức | Endpoint | Mô tả |
| :--- | :--- | :--- |
| `GET` | `/` | Kiểm tra trạng thái hoạt động của Backend |
| `GET` | `/api/popular?top_k=10` | Lấy danh sách sách phổ biến (Popularity-Based) |
| `GET` | `/api/books/search?q=...&limit=40` | Tìm kiếm sách theo tên hoặc tác giả từ CSV |
| `GET` | `/api/books/{book_id}` | Xem chi tiết thông tin một cuốn sách theo ISBN |
| `GET` | `/api/books/{book_id}/similar?top_k=5` | Gợi ý sách tương tự (Content-Based TF-IDF) |
| `GET` | `/api/recommend/{user_id}?top_k=10` | Gợi ý cá nhân hóa theo người dùng (SVD) |

### Chạy bộ test tự động (từ thư mục gốc của project)
```cmd
cd backend
python -m pytest -v
```
