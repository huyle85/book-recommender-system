# Hệ thống Gợi ý Sách (Book Recommender System)

Đồ án nhóm xây dựng hệ thống gợi ý sách kết hợp 3 hướng tiếp cận (**Collaborative Filtering FunkSVD**, **Content-Based TF-IDF**, và **Popularity-Based — kiêm Cold Start Fallback cho người dùng mới**), phục vụ qua **FastAPI** (đọc dữ liệu từ CSV + model `.pkl`, không cần cài PostgreSQL) và giao diện web **HTML/CSS/JS**.

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
│   └── requirements.txt             # Thư viện xử lý dữ liệu, train model, vẽ biểu đồ & Jupyter
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
│   ├── index.html                   # Tự chuyển hướng sang public/index.html khi mở http://localhost:5500/
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

## 2. Cài đặt thư viện trong môi trường ảo `venv`

> Frontend chỉ dùng HTML/CSS/JS thuần nên **không cần** `npm install`. Toàn bộ thư viện Python cho **Backend** và **AI Notebooks** đều cài gọn trong `venv` (thư mục `venv/` đã nằm trong `.gitignore`).

Mở **CMD** (hoặc **PowerShell**) tại thư mục gốc của project (`book-recommender-system/`) rồi chạy:

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r backend\requirements.txt -r ai_models\requirements.txt
```
- Nếu dùng **PowerShell**, thay dòng `venv\Scripts\activate` bằng `.\venv\Scripts\Activate.ps1`.
- Nếu dùng **macOS/Linux**, dùng `source venv/bin/activate && pip install -r backend/requirements.txt -r ai_models/requirements.txt`.
- Nếu chỉ cần cài riêng một phần: dùng `pip install -r backend\requirements.txt` (chỉ chạy Backend) hoặc `pip install -r ai_models\requirements.txt` (chỉ chạy `ai_models/notebooks/`).

> **Lưu ý về `scikit-surprise`:** File `collaborative_model.pkl` dùng `surprise.SVD`, nên cả `backend/requirements.txt` và `ai_models/requirements.txt` đều đã khai báo sẵn `scikit-surprise>=1.1.4` (đã test chạy ổn với `scikit-surprise==1.1.5` trên Python 3.13.14 Windows). Nếu máy khác gặp lỗi biên dịch từ mã nguồn khi `pip install`, hãy dùng Python 3.10/3.11 hoặc cài Microsoft C++ Build Tools.

---

## 3. Chuẩn bị dữ liệu `.csv`, chạy `ai_models/notebooks/` và tạo file `.env`

Vì `.gitignore` chặn `*.csv`, `*.pkl` và `.env`, khi chạy trên máy mới bạn cần chuẩn bị sẵn các file sau ở máy (chỉ lưu cục bộ để chạy, **không commit lên Git**):

### Bước 3.1: Chuẩn bị dữ liệu CSV trong `data/processed/`
- **Nếu đã có sẵn file sạch** từ nhóm (`books_cleaned.csv`, `ratings_cleaned.csv`): copy thẳng vào thư mục `data/processed/`.
- **Nếu mới tải dataset gốc từ Kaggle** (`Books.csv`, `Users.csv`, `Ratings.csv`): đặt vào `data/raw/` rồi chạy script tiền xử lý từ thư mục gốc của project để tự sinh `data/processed/*.csv` và biểu đồ EDA trong `docs/images/`:
  ```cmd
  python ai_models\notebooks\preprocessing.py
  ```

### Bước 3.2: Chạy các notebook trong `ai_models/notebooks/` để sinh 3 file model `.pkl`
> **Quan trọng:** Các notebook dùng đường dẫn tương đối (`../../data/processed/...` và `../saved_models/...`), nên **phải `cd ai_models\notebooks`** trước khi chạy.

- **Cách A — Chạy trực tiếp bằng dòng lệnh (không cần mở giao diện):**
  ```cmd
  cd ai_models\notebooks
  python -m jupyter nbconvert --to notebook --execute --inplace popularity_based.ipynb
  python -m jupyter nbconvert --to notebook --execute --inplace content_based.ipynb
  python -m jupyter nbconvert --to notebook --execute --inplace collaborative_filtering.ipynb
  ```
  *(Tùy chọn — chạy thêm `evaluation.ipynb` **sau khi** đã có đủ 3 file `.pkl` để đánh giá và lưu biểu đồ vào `docs/images/`:)*
  ```cmd
  python -m jupyter nbconvert --to notebook --execute --inplace evaluation.ipynb
  ```
  *(Xong bước này, quay lại thư mục gốc project bằng `cd ..\..`.)*

- **Cách B — Mở giao diện Jupyter Notebook / VS Code:**
  ```cmd
  cd ai_models\notebooks
  python -m jupyter notebook
  ```
  Sau đó mở lần lượt `popularity_based.ipynb`, `content_based.ipynb`, `collaborative_filtering.ipynb` (và `evaluation.ipynb` nếu cần), chọn kernel **`venv`** rồi bấm **Run All**.

Sau khi chạy xong, thư mục `ai_models/saved_models/` sẽ có đủ 3 file:
- `popularity_model.pkl`
- `content_based_model.pkl`
- `collaborative_model.pkl`

### Bước 3.3: Tạo file cấu hình môi trường Backend
Chạy tại thư mục gốc của project để tạo `backend/.env` từ file mẫu (nếu chưa có):
```cmd
copy backend\.env.example backend\.env
```

---

## 4. Lệnh chạy thử Frontend + Backend trên máy

> **Lưu ý:** Đảm bảo đã kích hoạt `venv` (`venv\Scripts\activate`) và bắt đầu từ **thư mục gốc của project (`book-recommender-system/`)** trước khi chạy lệnh trong cả 2 terminal dưới đây.

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

### Mở trình duyệt để kiểm thử thuật toán gợi ý
- Truy cập giao diện web tại: **`http://localhost:5500/`** (hoặc **`http://localhost:5500/public/index.html`**)
  - **Test Collaborative Filtering (SVD — người dùng đã có lịch sử):** Nhập `User ID` **`166596`** → hệ thống loại bỏ sách đã đọc ($O(1)$ trên Hash Set), dùng mô hình SVD dự đoán điểm cho sách ứng viên và lấy Top 10 bằng Min-Heap (`heapq.nlargest`).
  - **Test Cold Start Fallback (người dùng mới chưa có lịch sử):** Nhập bất kỳ `User ID` mới nào (ví dụ **`9999999`**) → hệ thống phát hiện $O(1)$ và **tự động chuyển sang Popularity-Based gợi ý 10 sách phổ biến nhất** (HTTP `200`, không báo lỗi `404`).
  - **Test Content-Based (TF-IDF):** Mở trang chi tiết một cuốn sách bất kỳ để xem Top 5 sách tương đồng Cosine theo tác giả & nhà xuất bản.
  - *Lưu ý:* Request đầu tiên sau khi bật Backend sẽ mất khoảng ~10 giây để nạp 2 file CSV vào bộ nhớ đệm RAM; các request sau phản hồi rất nhanh.
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
| `GET` | `/api/recommend/{user_id}?top_k=10` | Gợi ý Top-K cho user: dùng **SVD** nếu có lịch sử, tự động **fallback sang Popularity-Based** nếu là user mới (Cold Start) |

### Chạy bộ test tự động (từ thư mục gốc của project)
```cmd
cd backend
python -m pytest -v
```
