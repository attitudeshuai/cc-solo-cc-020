from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import redis
import logging

db = SQLAlchemy()
jwt = JWTManager()
redis_client = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('recommend')


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    CORS(app, supports_credentials=True)
    db.init_app(app)
    jwt.init_app(app)

    global redis_client
    try:
        redis_client = redis.from_url(app.config.get('REDIS_URL', 'redis://redis:6379/0'))
        redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}, running without cache")
        redis_client = None

    from app.routes.auth import auth_bp
    from app.routes.news import news_bp
    from app.routes.music import music_bp
    from app.routes.recommend import recommend_bp
    from app.routes.admin import admin_bp
    from app.routes.analytics import analytics_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(news_bp, url_prefix='/api/news')
    app.register_blueprint(music_bp, url_prefix='/api/music')
    app.register_blueprint(recommend_bp, url_prefix='/api/recommend')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(analytics_bp, url_prefix='/api/admin/analytics')

    from app.errors import register_error_handlers
    register_error_handlers(app)

    with app.app_context():
        db.create_all()
        from app.seed import seed_data
        seed_data()

    # 启动推荐引擎缓存刷新线程
    from app.engine import engine
    engine.start_cache_refresh_thread(app)

    # 启动数据采集定时线程
    from app.collector import start_scheduled_collector
    start_scheduled_collector(app)

    return app
