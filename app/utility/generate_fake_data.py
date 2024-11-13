import random
from faker import Faker
from dotenv import load_dotenv
from pymongo import MongoClient
import os
from bson.objectid import ObjectId
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')

# Kết nối đến MongoDB
client = MongoClient(MONGODB_URI)
db = client['e-commerce-website']  

fake = Faker()


categories = [
    ObjectId('670658cc89ae22296ece1528'),
    ObjectId('670658d789ae22296ece152c'),
    ObjectId('67250edc22e5200c529b7402')
]
def generate_fake_users(num_users=300):
    users = []


    product_ids = [product['_id'] for product in db['products'].find()]

   
    for _ in range(num_users):
        user_ratings = []
        num_ratings = random.randint(1, min(5, len(product_ids)))  

        # Chọn ngẫu nhiên sản phẩm để đánh giá
        rated_products_indices = random.sample(range(len(product_ids)), num_ratings)

        for index in rated_products_indices:
            rating = {
                "product": product_ids[index], 
                "isRated": True,
                "rating": random.randint(1, 5),
                "comment": fake.sentence()
            }
            user_ratings.append(rating)

        user = {
            "lastName": fake.last_name(),
            "firstName": fake.first_name(),
            "email": fake.email(),
            "password": '$2b$10$7Yhs3fRnB0YanHxb8U/qaOjm.Jvnn5EUgy0Zb/r/V.2l/ATWhEhAe',
            "ratings": user_ratings,  
            "birthday": fake.date_of_birth(minimum_age=18, maximum_age=65).isoformat(),
            "address": []
        }
        users.append(user)


    db['users'].insert_many(users)

    print(f"Đã thêm {len(users)} người dùng.")
if __name__ == "__main__":
    generate_fake_users() 