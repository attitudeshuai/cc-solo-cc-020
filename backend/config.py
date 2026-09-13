import os
import json


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'rec-system-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:root123@db:3306/recommend_db?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-2024')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24h
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

    # ---- 推荐引擎配置 ----
    # 用户行为评分权重（可通过环境变量 ACTION_SCORES 覆盖，JSON 格式）
    ACTION_SCORES = json.loads(os.getenv('ACTION_SCORES', '{}')) or {
        'view': 1.0,
        'like': 3.0,
        'rate': 5.0,
        'collect': 4.0,
    }
    # 缓存刷新间隔（秒）
    CACHE_REFRESH_INTERVAL = int(os.getenv('CACHE_REFRESH_INTERVAL', '300'))

    # ---- 数据采集配置 ----
    # RSS 新闻源（可通过环境变量 RSS_SOURCES 覆盖，JSON 格式）
    RSS_SOURCES = json.loads(os.getenv('RSS_SOURCES', '[]')) or [
        {'name': '人民网-科技', 'url': 'http://www.people.com.cn/rss/keji.xml', 'category': '科技'},
        {'name': '人民网-财经', 'url': 'http://www.people.com.cn/rss/caijing.xml', 'category': '财经'},
        {'name': '人民网-体育', 'url': 'http://www.people.com.cn/rss/tiyu.xml', 'category': '体育'},
    ]
    # 音乐采集搜索关键词（可通过环境变量 MUSIC_SEARCH_QUERIES 覆盖，JSON 格式）
    MUSIC_SEARCH_QUERIES = json.loads(os.getenv('MUSIC_SEARCH_QUERIES', '[]')) or [
        ['pop', '周杰伦'], ['pop', 'Taylor Swift'], ['rock', 'Queen'],
        ['jazz', 'Miles Davis'], ['classical', 'Mozart'], ['electronic', 'Daft Punk'],
        ['hiphop', 'Eminem'], ['pop', '林俊杰'], ['rock', 'Coldplay'],
    ]
    # 采集间隔（秒），默认 6 小时
    COLLECT_INTERVAL = int(os.getenv('COLLECT_INTERVAL', str(6 * 3600)))
    # HTTP 请求超时（秒）
    COLLECT_REQUEST_TIMEOUT = int(os.getenv('COLLECT_REQUEST_TIMEOUT', '10'))
