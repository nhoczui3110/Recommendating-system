# Kết nối MongoDB
import os
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')
print(DATABASE_NAME)
# Kết nối MongoDB
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
user_collection = db['users']

# Kết nối MongoDB
def connect_to_db():
    client = MongoClient(MONGODB_URI)
    db = client['e-commerce-website']
    return db


def fetch_data_from_mongodb(db):
    # Lấy tất cả sản phẩm từ collection 'products'
    product_collection = db["products"]
    products = product_collection.find({}, {'_id': 1})
    product_ids = [str(product['_id']) for product in products]

    # Lấy tất cả người dùng và đánh giá của họ từ collection 'users'
    user_collection = db["users"]
    user_ratings_data = []
    users = user_collection.find({}, {'_id': 1, 'ratings': 1})
    
    user_ids = []
    for user in users:
        user_id = str(user['_id'])
        user_ids.append(user_id)
        for rating in user.get('ratings', []):
            product_id = str(rating['product'])
            rating_value = rating.get('rating', 0)
            user_ratings_data.append([user_id, product_id, rating_value])
    
    # Chuyển đổi danh sách đánh giá thành DataFrame
    ratings_df = pd.DataFrame(user_ratings_data, columns=['user_id', 'item_id', 'rating'])

    # Tạo ma trận user-item, đảm bảo bao gồm tất cả user_id và product_id
    user_item_matrix = ratings_df.pivot_table(index='user_id', columns='item_id', values='rating', fill_value=0)

    # Bổ sung các hàng và cột còn thiếu để đảm bảo tất cả user_id và product_id đều có mặt
    user_item_matrix = user_item_matrix.reindex(index=user_ids, columns=product_ids, fill_value=0)
    
    print("User-Item Matrix:")
    print(user_item_matrix)
    
    return user_item_matrix