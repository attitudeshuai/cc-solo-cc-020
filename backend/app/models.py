from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(64), default='')
    role = db.Column(db.String(16), default='user')  # admin / user
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id, 'username': self.username, 'nickname': self.nickname,
            'role': self.role, 'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    content = db.Column(db.Text)
    category = db.Column(db.String(32), default='general')
    source = db.Column(db.String(128), default='')
    image_url = db.Column(db.String(512), default='')
    view_count = db.Column(db.Integer, default=0)
    published_at = db.Column(db.DateTime, default=datetime.now)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'content': self.content,
            'category': self.category, 'source': self.source, 'image_url': self.image_url,
            'view_count': self.view_count,
            'published_at': self.published_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class Music(db.Model):
    __tablename__ = 'music'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(256), nullable=False)
    artist = db.Column(db.String(128), default='')
    album = db.Column(db.String(128), default='')
    genre = db.Column(db.String(32), default='pop')
    duration = db.Column(db.Integer, default=0)
    cover_url = db.Column(db.String(512), default='')
    play_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'artist': self.artist,
            'album': self.album, 'genre': self.genre, 'duration': self.duration,
            'cover_url': self.cover_url, 'play_count': self.play_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class UserBehavior(db.Model):
    __tablename__ = 'user_behaviors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_type = db.Column(db.String(16), nullable=False)  # news / music
    item_id = db.Column(db.Integer, nullable=False)
    action_type = db.Column(db.String(16), nullable=False)  # view / like / rate
    rating = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'item_type': self.item_type,
            'item_id': self.item_id, 'action_type': self.action_type,
            'rating': self.rating, 'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class RecommendationLog(db.Model):
    __tablename__ = 'recommendation_logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_type = db.Column(db.String(16), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, default=0.0)
    algorithm = db.Column(db.String(32), default='collaborative_filtering')
    created_at = db.Column(db.DateTime, default=datetime.now)


class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module = db.Column(db.String(32), nullable=False)
    action = db.Column(db.String(32), nullable=False)
    detail = db.Column(db.String(512), default='')
    ip = db.Column(db.String(64), default='')
    created_at = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id, 'user_id': self.user_id, 'module': self.module,
            'action': self.action, 'detail': self.detail, 'ip': self.ip,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
