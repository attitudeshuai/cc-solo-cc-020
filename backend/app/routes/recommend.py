from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import UserBehavior
from app.engine import engine
from app.utils import validate_required, get_identity

recommend_bp = Blueprint('recommend', __name__)


@recommend_bp.route('/news', methods=['GET'])
@jwt_required()
def recommend_news():
    identity = get_identity()
    top_n = request.args.get('top_n', 10, type=int)
    results = engine.recommend_for_user(identity['id'], 'news', top_n)
    return jsonify({'code': 200, 'data': results})


@recommend_bp.route('/music', methods=['GET'])
@jwt_required()
def recommend_music():
    identity = get_identity()
    top_n = request.args.get('top_n', 10, type=int)
    results = engine.recommend_for_user(identity['id'], 'music', top_n)
    return jsonify({'code': 200, 'data': results})


@recommend_bp.route('/algorithm', methods=['GET'])
@jwt_required()
def algorithm_info():
    return jsonify({'code': 200, 'data': engine.get_algorithm_explanation()})


@recommend_bp.route('/behavior', methods=['GET'])
@jwt_required()
def get_behaviors():
    """获取用户的行为记录（点赞、评分）"""
    identity = get_identity()
    item_type = request.args.get('item_type')  # news 或 music，可选
    
    query = UserBehavior.query.filter_by(user_id=identity['id'])
    if item_type:
        query = query.filter_by(item_type=item_type)
    
    behaviors = query.all()
    result = {'likes': {}, 'ratings': {}}
    
    for b in behaviors:
        key = f"{b.item_type}_{b.item_id}"
        if b.action_type == 'like':
            result['likes'][key] = True
        elif b.action_type == 'rate' and b.rating > 0:
            result['ratings'][key] = b.rating
    
    return jsonify({'code': 200, 'data': result})


@recommend_bp.route('/behavior', methods=['POST'])
@jwt_required()
def record_behavior():
    identity = get_identity()
    data = request.get_json(silent=True) or {}
    ok, msg = validate_required(data, ['item_type', 'item_id', 'action_type'])
    if not ok:
        return jsonify({'code': 400, 'msg': msg}), 400

    if data['item_type'] not in ('news', 'music'):
        return jsonify({'code': 400, 'msg': 'item_type 必须为 news 或 music'}), 400
    if data['action_type'] not in ('view', 'like', 'rate', 'collect'):
        return jsonify({'code': 400, 'msg': 'action_type 无效'}), 400

    behavior = UserBehavior(
        user_id=identity['id'], item_type=data['item_type'],
        item_id=data['item_id'], action_type=data['action_type'],
        rating=data.get('rating', 0.0)
    )
    db.session.add(behavior)
    db.session.commit()
    return jsonify({'code': 200, 'msg': '行为记录成功'})


@recommend_bp.route('/my-behaviors', methods=['GET'])
@jwt_required()
def get_my_behaviors():
    """获取当前用户的行为记录（点赞、评分）"""
    identity = get_identity()
    item_type = request.args.get('item_type', '')
    
    query = UserBehavior.query.filter_by(user_id=identity['id'])
    if item_type:
        query = query.filter_by(item_type=item_type)
    
    behaviors = query.filter(UserBehavior.action_type.in_(['like', 'rate'])).all()
    
    result = {'likes': [], 'ratings': {}}
    for b in behaviors:
        key = f"{b.item_type}_{b.item_id}"
        if b.action_type == 'like':
            result['likes'].append({'item_type': b.item_type, 'item_id': b.item_id})
        elif b.action_type == 'rate' and b.rating > 0:
            result['ratings'][key] = b.rating
    
    return jsonify({'code': 200, 'data': result})


@recommend_bp.route('/my-stats', methods=['GET'])
@jwt_required()
def get_my_stats():
    """获取当前用户的兴趣统计数据"""
    from sqlalchemy import func
    from app.models import News, Music
    
    identity = get_identity()
    user_id = identity['id']
    
    # 统计用户行为
    behaviors = UserBehavior.query.filter_by(user_id=user_id).all()
    
    # 分类统计
    news_categories = {}
    music_genres = {}
    action_counts = {'view': 0, 'like': 0, 'rate': 0}
    total_ratings = []
    
    for b in behaviors:
        action_counts[b.action_type] = action_counts.get(b.action_type, 0) + 1
        if b.action_type == 'rate' and b.rating > 0:
            total_ratings.append(b.rating)
        
        if b.item_type == 'news' and b.action_type in ('like', 'rate'):
            news = News.query.get(b.item_id)
            if news:
                news_categories[news.category] = news_categories.get(news.category, 0) + 1
        elif b.item_type == 'music' and b.action_type in ('like', 'rate'):
            music = Music.query.get(b.item_id)
            if music:
                music_genres[music.genre] = music_genres.get(music.genre, 0) + 1
    
    # 构建雷达图数据
    all_categories = ['科技', '财经', '体育', '娱乐', '教育', '健康']
    all_genres = ['pop', 'rock', 'jazz', 'classical', 'electronic', 'hiphop']
    
    radar_news = [{'name': c, 'value': news_categories.get(c, 0)} for c in all_categories]
    radar_music = [{'name': g, 'value': music_genres.get(g, 0)} for g in all_genres]
    
    return jsonify({
        'code': 200,
        'data': {
            'behavior_summary': {
                'total_views': action_counts.get('view', 0),
                'total_likes': action_counts.get('like', 0),
                'total_ratings': len(total_ratings),
                'avg_rating': round(sum(total_ratings) / len(total_ratings), 1) if total_ratings else 0
            },
            'news_interests': radar_news,
            'music_interests': radar_music,
            'top_news_category': max(news_categories, key=news_categories.get) if news_categories else None,
            'top_music_genre': max(music_genres, key=music_genres.get) if music_genres else None
        }
    })


@recommend_bp.route('/behavior', methods=['DELETE'])
@jwt_required()
def delete_behavior():
    """删除用户行为记录（取消点赞）"""
    identity = get_identity()
    item_type = request.args.get('item_type')
    item_id = request.args.get('item_id', type=int)
    action_type = request.args.get('action_type', 'like')
    
    if not item_type or not item_id:
        return jsonify({'code': 400, 'msg': '缺少参数'}), 400
    
    UserBehavior.query.filter_by(
        user_id=identity['id'], item_type=item_type,
        item_id=item_id, action_type=action_type
    ).delete()
    db.session.commit()
    return jsonify({'code': 200, 'msg': '已取消'})


@recommend_bp.route('/my-profile', methods=['GET'])
@jwt_required()
def get_my_profile():
    """获取用户兴趣画像数据"""
    from app.models import News, Music
    identity = get_identity()
    
    # 获取用户所有行为
    behaviors = UserBehavior.query.filter_by(user_id=identity['id']).all()
    
    # 统计各类别兴趣
    news_categories = {}
    music_genres = {}
    action_stats = {'view': 0, 'like': 0, 'rate': 0}
    total_rating = 0
    rating_count = 0
    
    for b in behaviors:
        action_stats[b.action_type] = action_stats.get(b.action_type, 0) + 1
        if b.action_type == 'rate' and b.rating > 0:
            total_rating += b.rating
            rating_count += 1
        
        if b.item_type == 'news':
            news = News.query.get(b.item_id)
            if news:
                cat = news.category or '其他'
                news_categories[cat] = news_categories.get(cat, 0) + (2 if b.action_type == 'like' else 1)
        elif b.item_type == 'music':
            music = Music.query.get(b.item_id)
            if music:
                genre = music.genre or '其他'
                music_genres[genre] = music_genres.get(genre, 0) + (2 if b.action_type == 'like' else 1)
    
    # 转换为雷达图数据
    def to_radar(data, max_items=6):
        sorted_items = sorted(data.items(), key=lambda x: -x[1])[:max_items]
        if not sorted_items:
            return {'labels': [], 'values': []}
        max_val = max(v for _, v in sorted_items) or 1
        return {
            'labels': [k for k, _ in sorted_items],
            'values': [round(v / max_val * 100) for _, v in sorted_items]
        }
    
    return jsonify({
        'code': 200,
        'data': {
            'news_radar': to_radar(news_categories),
            'music_radar': to_radar(music_genres),
            'stats': {
                'total_actions': sum(action_stats.values()),
                'likes': action_stats.get('like', 0),
                'views': action_stats.get('view', 0),
                'ratings': rating_count,
                'avg_rating': round(total_rating / rating_count, 1) if rating_count > 0 else 0
            }
        }
    })
