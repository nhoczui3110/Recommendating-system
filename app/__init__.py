import threading
import schedule
import time
from flask import Flask

from .utility.database import connect_to_db, fetch_data_from_mongodb
from .utility.recommender import Recommender

# Hàm cập nhật recommendation
def update_recommendations(app):
    with app.app_context():  # Đảm bảo truy cập các biến trong ngữ cảnh Flask
        db = app.config['db']
        user_item_matrix = fetch_data_from_mongodb(db)
        recommender = Recommender(user_item_matrix)
        app.config['recommender'] = recommender  # Cập nhật recommender trong cấu hình Flask
        print("Updated recommendations")

# Khởi chạy schedule trong luồng riêng
def run_schedule(app):
    while True:
        schedule.run_pending()
        time.sleep(1)  # Thời gian chờ giữa các lần kiểm tra

def create_app():
    app = Flask(__name__)

    # Kết nối cơ sở dữ liệu và tạo recommender khi ứng dụng Flask khởi động
    db = connect_to_db()
    user_item_matrix = fetch_data_from_mongodb(db)
    recommender = Recommender(user_item_matrix)
    
    # Lưu vào cấu hình ứng dụng
    app.config['db'] = db
    app.config['recommender'] = recommender

    # Thiết lập lịch trình cập nhật recommender mỗi 24 giờ
    schedule.every(24).hours.do(update_recommendations, app)

    # Khởi động luồng chạy schedule
    schedule_thread = threading.Thread(target=run_schedule, args=(app,))
    schedule_thread.daemon = True
    schedule_thread.start()

    # Import và đăng ký các route
    with app.app_context():
        from .routes import api
        app.register_blueprint(api)

    return app
