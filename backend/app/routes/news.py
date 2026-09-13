from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import News, UserBehavior
from app.utils import paginate_query, get_identity

news_bp = Blueprint('news', __name__)


@news_bp.route('', methods=['GET'])
@jwt_required()
def list_news():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '')

    query = News.query
    if category:
        query = query.filter_by(category=category)
    if keyword:
        query = query.filter(News.title.like(f'%{keyword}%'))
    query = query.order_by(News.published_at.desc())

    return jsonify({'code': 200, 'data': paginate_query(query, page, per_page)})


@news_bp.route('/<int:news_id>', methods=['GET'])
@jwt_required()
def get_news(news_id):
    identity = get_identity()
    news = News.query.get(news_id)
    if not news:
        return jsonify({'code': 404, 'msg': '新闻不存在'}), 404

    news.view_count += 1
    behavior = UserBehavior(user_id=identity['id'], item_type='news', item_id=news_id, action_type='view', rating=1.0)
    db.session.add(behavior)
    db.session.commit()

    return jsonify({'code': 200, 'data': news.to_dict()})
