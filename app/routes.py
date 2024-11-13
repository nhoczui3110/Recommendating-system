# app/routes.py
from flask import Blueprint, jsonify, current_app

api = Blueprint('api', __name__)
  # Hoặc có thể lấy từ tham số truy vấn
recommender = current_app.config['recommender']
@api.route('/recommendations/<user_id>', methods=['GET'])
def recommendations(user_id):
    try:
        # Gọi hàm get_recommendations và xử lý kết quả
        recommended_items = recommender.get_recommendations(user_id)
        
        # Kiểm tra nếu có lỗi (như user không tồn tại)
        if isinstance(recommended_items, dict) and "error" in recommended_items:
            return jsonify([]), 200

        return jsonify(recommended_items), 200
    except Exception as e:
        # Xử lý các lỗi khác và trả về phản hồi lỗi tổng quát
        print(e)
        return jsonify([]), 200
        # return jsonify({"error": f"Lỗi khi tạo đề xuất: {str(e)}"}), 500

@api.route('/get-similar-products/<product_id>', methods=['GET'])
def getSimilarProducts(product_id):
    try:
        recommender = current_app.config['recommender']
        similar_products = recommender.get_similar_products(product_id)
        return jsonify(similar_products), 200
    except Exception as e:
        print(e)
        return jsonify([]), 200
    
