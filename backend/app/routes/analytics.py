from flask import Blueprint, jsonify, request
from app import db
from app.models import User, News, Music, UserBehavior, RecommendationLog
from app.engine import engine
from app.utils import admin_required
from sqlalchemy import func

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/overview', methods=['GET'])
@admin_required
def overview():
    data = {
        'user_count': User.query.count(),
        'news_count': News.query.count(),
        'music_count': Music.query.count(),
        'behavior_count': UserBehavior.query.count(),
        'recommendation_count': RecommendationLog.query.count()
    }
    return jsonify({'code': 200, 'data': data})


@analytics_bp.route('/behavior', methods=['GET'])
@admin_required
def behavior_analysis():
    item_type = request.args.get('item_type', 'news')

    # 行为类型分布
    action_dist = db.session.query(
        UserBehavior.action_type, func.count(UserBehavior.id)
    ).filter_by(item_type=item_type).group_by(UserBehavior.action_type).all()

    # 每日行为趋势 (最近30天)
    daily_trend = db.session.query(
        func.date(UserBehavior.created_at).label('date'),
        func.count(UserBehavior.id).label('count')
    ).filter_by(item_type=item_type).group_by(
        func.date(UserBehavior.created_at)
    ).order_by(func.date(UserBehavior.created_at).desc()).limit(30).all()

    # 分类热度
    if item_type == 'news':
        category_heat = db.session.query(
            News.category, func.count(UserBehavior.id)
        ).join(UserBehavior, (UserBehavior.item_id == News.id) & (UserBehavior.item_type == 'news')
        ).group_by(News.category).all()
    else:
        category_heat = db.session.query(
            Music.genre, func.count(UserBehavior.id)
        ).join(UserBehavior, (UserBehavior.item_id == Music.id) & (UserBehavior.item_type == 'music')
        ).group_by(Music.genre).all()

    # 评分分布
    rating_dist = engine.get_rating_distribution(item_type)

    return jsonify({'code': 200, 'data': {
        'action_distribution': [{'type': a[0], 'count': a[1]} for a in action_dist],
        'daily_trend': [{'date': str(d[0]), 'count': d[1]} for d in reversed(list(daily_trend))],
        'category_heat': [{'category': c[0], 'count': c[1]} for c in category_heat],
        'rating_distribution': rating_dist
    }})


@analytics_bp.route('/recommendation', methods=['GET'])
@admin_required
def recommendation_analysis():
    # 推荐算法分布
    algo_dist = db.session.query(
        RecommendationLog.algorithm, func.count(RecommendationLog.id)
    ).group_by(RecommendationLog.algorithm).all()

    # 推荐评分分布
    score_ranges = [
        ('0-1', 0, 1), ('1-2', 1, 2), ('2-3', 2, 3), ('3-4', 3, 4), ('4-5', 4, 5)
    ]
    score_dist = []
    for label, low, high in score_ranges:
        count = RecommendationLog.query.filter(
            RecommendationLog.score >= low, RecommendationLog.score < high
        ).count()
        score_dist.append({'range': label, 'count': count})

    # 每日推荐量
    daily_rec = db.session.query(
        func.date(RecommendationLog.created_at).label('date'),
        func.count(RecommendationLog.id).label('count')
    ).group_by(func.date(RecommendationLog.created_at)
    ).order_by(func.date(RecommendationLog.created_at).desc()).limit(30).all()

    return jsonify({'code': 200, 'data': {
        'algorithm_distribution': [{'algorithm': a[0], 'count': a[1]} for a in algo_dist],
        'score_distribution': score_dist,
        'daily_recommendations': [{'date': str(d[0]), 'count': d[1]} for d in reversed(list(daily_rec))]
    }})


@analytics_bp.route('/similarity', methods=['GET'])
@admin_required
def similarity_matrix():
    item_type = request.args.get('item_type', 'news')
    data = engine.get_similarity_matrix_data(item_type)
    if data is None:
        return jsonify({'code': 200, 'data': {'user_ids': [], 'matrix': [], 'size': 0}})
    return jsonify({'code': 200, 'data': data})


@analytics_bp.route('/algorithm', methods=['GET'])
@admin_required
def algorithm_explanation():
    return jsonify({'code': 200, 'data': engine.get_algorithm_explanation()})
