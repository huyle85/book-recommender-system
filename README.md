book-recommender-system/
│
├── data/ # [Không gian của Người 1]
│ ├── raw/ # Dữ liệu gốc nguyên bản tải từ Kaggle
│ └── processed/ # File .csv đã làm sạch để train model
│
├── ai_models/ # [Không gian của Người 2, 3, 4 - AI & Evaluate]
│ ├── notebooks/ # Chứa các file .ipynb (EDA, Train SVD, Train TFIDF)
│ ├── saved_models/ # Nơi xuất các file mô hình đã train (VD:
svd_model.pkl)
│ └── requirements.txt # Các thư viện AI: pandas, scikit-learn, surprise...
│
├── backend/ # [Không gian của Người 5 - Backend API]
│ ├── app/
│ │ ├── main.py # File gốc khởi tạo server FastAPI
│ │ ├── api/ # Chứa các file router định tuyến (endpoints)
│ │ ├── services/ # Logic đọc file .pkl từ thư mục ai_models và dự đoán
│ │ └── database/ # Logic kết nối PostgreSQL (truy xuất thông tin sách)
│ ├── .env # Lưu biến môi trường (Database URL, Port)
│ └── requirements.txt # Các thư viện Backend: fastapi, uvicorn, psycopg2...
│
├── frontend/ # [Không gian của Người 6 - Frontend UI]
│ ├── public/ # Chứa index.html, favicon
│ ├── src/
│ │ ├── components/ # Các mảnh UI dùng chung (BookCard, SearchBar)
│ │ ├── pages/ # Các trang chính (Home, BookDetail)
│ │ └── services/ # File cấu hình axios/fetch để gọi API Backend
│ └── package.json # Quản lý thư viện React/Node.js
│
├── docs/ # [Không gian chung - Báo cáo & Tài liệu]
│ ├── Bao_Cao_Nhom.docx # File báo cáo Word
│ └── images/ # Lưu biểu đồ EDA, ảnh test model, screenshot web
│
├── .gitignore # Khai báo chặn các file không được đẩy lên Git
└── README.md # File hướng dẫn các bước cài đặt và chạy project
