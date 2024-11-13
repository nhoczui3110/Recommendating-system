import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class Recommender:
    def __init__(self, user_item_matrix=None, k=2):
        self.k = k
        if user_item_matrix is not None:
            self.fit(user_item_matrix)

    def fit(self, user_item_matrix):
        self.set_data(user_item_matrix)

    def set_data(self, user_item_matrix):
        self.user_item_matrix = user_item_matrix
        self._calculate_metrics()

    def _calculate_metrics(self):
        print("Updated User-item matrix: ")
        print(self.user_item_matrix)

        # Calculate item means by ignoring zero ratings
        self.item_mean = self.user_item_matrix.replace(0, np.nan).mean(axis=0)
        print("\nItem means (excluding 0 ratings):")
        print(self.item_mean)

        # Normalize the user-item matrix by subtracting item mean
        self.user_item_matrix_normalized = self.user_item_matrix.sub(self.item_mean, axis=1)

        for item in self.user_item_matrix.columns:
            self.user_item_matrix_normalized.loc[:, item][self.user_item_matrix[item] == 0] = 0

        print("\nNormalized User-Item Matrix:")
        print(self.user_item_matrix_normalized)

        # Calculate item similarity matrix using cosine similarity
        self.item_similarity = cosine_similarity(self.user_item_matrix_normalized.T)
        self.item_similarity_df = pd.DataFrame(self.item_similarity, index=self.user_item_matrix.columns, columns=self.user_item_matrix.columns)
        print("\nItem Similarity Matrix:")
        print(self.item_similarity_df)
    def predict_rating(self, user, item):
    # Lấy danh sách các sản phẩm mà người dùng đã đánh giá
        rated_items = self.user_item_matrix_normalized.loc[user][self.user_item_matrix.loc[user] > 0].index
        if len(rated_items) == 0:
            return 0  # Nếu người dùng chưa đánh giá bất kỳ sản phẩm nào, dự đoán là 0

    # Tính độ tương đồng giữa sản phẩm đang xét và các sản phẩm đã được đánh giá
        similarities = self.item_similarity_df[item][rated_items]
        top_k_items = similarities.nlargest(self.k).index
    
    # Tính tổng trọng số dựa trên ma trận chuẩn hóa
        weighted_sum = np.dot(similarities[top_k_items], self.user_item_matrix_normalized.loc[user, top_k_items])
        similarity_sum = np.abs(similarities[top_k_items].sum())
    
    # Dự đoán điểm cho sản phẩm, cộng lại điểm trung bình của sản phẩm để chuyển về thang đo gốc
        predicted_rating = self.item_mean[item] + weighted_sum / (similarity_sum + 1e-8)  # Tránh chia cho 0
        return predicted_rating


    def get_recommendations(self, user, top_n=10):
    # Lấy danh sách các sản phẩm mà người dùng chưa đánh giá
        if user not in self.user_item_matrix.index:
            print(f"Error: User '{user}' không tồn tại trong dữ liệu.")
            return {"error": f"User '{user}' không tồn tại trong dữ liệu."}
        unrated_items = self.user_item_matrix.loc[user][self.user_item_matrix.loc[user] == 0].index
    
    # Khởi tạo Series để lưu rating dự đoán cho các sản phẩm chưa đánh giá
        predicted_ratings = pd.Series(dtype='float64')
    # Tính rating dự đoán cho mỗi sản phẩm chưa đánh giá
        for item in unrated_items:
            predicted_rating = self.predict_rating(user, item)
            if predicted_rating > 0:  # Chỉ lưu rating dự đoán lớn hơn 0
                predicted_ratings[item] = predicted_rating   
        top_recommendations = predicted_ratings.sort_values(ascending=False).head(top_n)
        recommendations_list = [{"item_id": item, "predicted_rating": rating} for item, rating in top_recommendations.items()]
        print("Predicted ratings for unrated items:")
        print(recommendations_list)
    
    # Sắp xếp và trả về top_n sản phẩm có rating dự đoán cao nhất
        return recommendations_list
    def get_similar_products(self, product_id, top_n=5):
    # Kiểm tra sản phẩm tồn tại trong ma trận độ tương đồng
        if product_id not in self.item_similarity_df.index:
            print("Product ID không có trong ma trận độ tương đồng.")
            return []
    
    # Lấy danh sách độ tương đồng của các sản phẩm với product_id
        similar_scores = self.item_similarity_df[product_id]
    
    # Sắp xếp theo thứ tự giảm dần và lấy top N sản phẩm tương tự (ngoại trừ chính sản phẩm đó)
        similar_products = similar_scores.sort_values(ascending=False).drop(product_id)
        similar_products = similar_products[similar_products > 0].head(top_n)
    
        print(f"Top {top_n} sản phẩm tương tự với {product_id}:")
        print(similar_products)
    
    # Chuyển kết quả thành một mảng các từ điển
        similar_products_list = [{"productId": idx, "similarity": sim} for idx, sim in similar_products.items()]
    
        return similar_products_list