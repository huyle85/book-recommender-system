import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if CURRENT_DIR.name == 'notebooks':
    BASE_DIR = CURRENT_DIR.parent.parent
elif CURRENT_DIR.name in ['ai_models', 'data']:
    BASE_DIR = CURRENT_DIR.parent
else:
    BASE_DIR = CURRENT_DIR

RAW_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
IMAGES_DIR = BASE_DIR / 'docs' / 'images'

# Thiết lập giao diện biểu đồ
sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

print("--- 1. ĐANG TẢI DỮ LIỆU GỐC ---")
books = pd.read_csv(RAW_DIR / 'Books.csv', low_memory=False, encoding='utf-8', on_bad_lines='skip')
users = pd.read_csv(RAW_DIR / 'Users.csv', low_memory=False, encoding='utf-8', on_bad_lines='skip')
ratings = pd.read_csv(RAW_DIR / 'Ratings.csv', low_memory=False, encoding='utf-8', on_bad_lines='skip')

print(f"Kích thước ban đầu:")
print(f"- Books: {books.shape}")
print(f"- Users: {users.shape}")
print(f"- Ratings: {ratings.shape}")

print("\n--- 2. LÀM SẠCH DỮ LIỆU (DATA CLEANING) ---")

# 2.1. Xử lý bảng Users (Lọc độ tuổi hợp lý từ 5 đến 100 tuổi)
users_cleaned = users[(users['Age'] >= 5) & (users['Age'] <= 100)].copy()

# 2.2. Xử lý bảng Ratings cho mô hình (Đảm bảo User-ID và ISBN tồn tại)
valid_ratings = ratings[
    ratings['User-ID'].isin(users['User-ID']) & 
    ratings['ISBN'].isin(books['ISBN'])
].copy()

# Lọc bỏ các điểm rating bằng 0 (chỉ giữ lại explicit feedback từ 1 đến 10)
ratings_explicit = valid_ratings[valid_ratings['Book-Rating'] > 0].copy()

print(f"Kích thước sau khi làm sạch:")
print(f"- Users hợp lệ (có độ tuổi chuẩn): {users_cleaned.shape}")
print(f"- Ratings tường minh (>0) hợp lệ: {ratings_explicit.shape}")

print("\n--- 3. PHÂN TÍCH KHÁM PHÁ DỮ LIỆU (EDA) & VẼ BIỂU ĐỒ ---")


os.makedirs(IMAGES_DIR, exist_ok=True)

# Biểu đồ 1: Phân bố điểm số Rating (1-10)
plt.figure(figsize=(8, 5))
sns.countplot(x='Book-Rating', data=ratings_explicit, palette='Blues_r')
plt.title('Phân bố điểm số Rating (1-10)', fontsize=14, fontweight='bold')
plt.xlabel('Điểm Rating', fontsize=12)
plt.ylabel('Số lượng đánh giá', fontsize=12)
plt.savefig(IMAGES_DIR / 'eda_rating_distribution.png', bbox_inches='tight', dpi=300)
plt.close()

# Biểu đồ 2: Phân bố độ tuổi người dùng
plt.figure(figsize=(10, 5))
sns.histplot(users_cleaned['Age'], bins=30, kde=True, color='coral')
plt.title('Phân bố độ tuổi người dùng (Users Age Distribution)', fontsize=14, fontweight='bold')
plt.xlabel('Độ tuổi', fontsize=12)
plt.ylabel('Tần suất', fontsize=12)
plt.savefig(IMAGES_DIR / 'eda_users_age.png', bbox_inches='tight', dpi=300)
plt.close()

print(f"Đã vẽ và lưu biểu đồ thành công vào: {IMAGES_DIR}")

print("\n--- 4. XUẤT FILE CSV CHUẨN HÓA CHO CẢ NHÓM ---")
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Lưu các file đã xử lý vào thư mục data/processed
users_cleaned.to_csv(PROCESSED_DIR / 'users_cleaned.csv', index=False)
ratings_explicit.to_csv(PROCESSED_DIR / 'ratings_cleaned.csv', index=False)
books.to_csv(PROCESSED_DIR / 'books_cleaned.csv', index=False)

print(f"Hoàn tất! Các file sạch đã được lưu vào: {PROCESSED_DIR}")