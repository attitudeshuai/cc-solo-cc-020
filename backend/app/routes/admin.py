from flask import Blueprint, request, jsonify
from app import db, logger
from app.models import User, News, Music, OperationLog
from app.utils import admin_required, log_operation, validate_required, paginate_query, get_identity

admin_bp = Blueprint('admin', __name__)


# ---- User Management ----
@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    query = User.query.order_by(User.created_at.desc())
    return jsonify({'code': 200, 'data': paginate_query(query, page, per_page)})


@admin_bp.route('/users/<int:uid>', methods=['PUT'])
@admin_required
def update_user(uid):
    identity = get_identity()
    user = User.query.get(uid)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    data = request.get_json(silent=True) or {}
    if data.get('nickname'):
        user.nickname = data['nickname']
    if data.get('role') and data['role'] in ('admin', 'user'):
        user.role = data['role']
    db.session.commit()
    log_operation(identity['id'], 'user', 'update', f'编辑用户 {user.username}')
    return jsonify({'code': 200, 'msg': '更新成功', 'data': user.to_dict()})


@admin_bp.route('/users/<int:uid>', methods=['DELETE'])
@admin_required
def delete_user(uid):
    identity = get_identity()
    user = User.query.get(uid)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    # 保护 admin 用户：检查用户名和角色
    if user.username == 'admin' or user.role == 'admin':
        return jsonify({'code': 403, 'msg': '管理员账户不能被删除'}), 403
    db.session.delete(user)
    db.session.commit()
    log_operation(identity['id'], 'user', 'delete', f'删除用户 {user.username}')
    return jsonify({'code': 200, 'msg': '删除成功'})


# ---- News Management ----
@admin_bp.route('/news', methods=['POST'])
@admin_required
def create_news():
    identity = get_identity()
    data = request.get_json(silent=True) or {}
    ok, msg = validate_required(data, ['title', 'content', 'category'])
    if not ok:
        return jsonify({'code': 400, 'msg': msg}), 400
    news = News(title=data['title'], content=data['content'], category=data['category'],
                source=data.get('source', ''), image_url=data.get('image_url', ''))
    db.session.add(news)
    db.session.commit()
    log_operation(identity['id'], 'news', 'create', f'新增新闻: {news.title}')
    return jsonify({'code': 200, 'msg': '创建成功', 'data': news.to_dict()})


@admin_bp.route('/news/<int:nid>', methods=['PUT'])
@admin_required
def update_news(nid):
    identity = get_identity()
    news = News.query.get(nid)
    if not news:
        return jsonify({'code': 404, 'msg': '新闻不存在'}), 404
    data = request.get_json(silent=True) or {}
    for field in ['title', 'content', 'category', 'source', 'image_url']:
        if field in data:
            setattr(news, field, data[field])
    db.session.commit()
    log_operation(identity['id'], 'news', 'update', f'编辑新闻: {news.title}')
    return jsonify({'code': 200, 'msg': '更新成功', 'data': news.to_dict()})


@admin_bp.route('/news/<int:nid>', methods=['DELETE'])
@admin_required
def delete_news(nid):
    identity = get_identity()
    news = News.query.get(nid)
    if not news:
        return jsonify({'code': 404, 'msg': '新闻不存在'}), 404
    db.session.delete(news)
    db.session.commit()
    log_operation(identity['id'], 'news', 'delete', f'删除新闻: {news.title}')
    return jsonify({'code': 200, 'msg': '删除成功'})


# ---- Music Management ----
@admin_bp.route('/music', methods=['POST'])
@admin_required
def create_music():
    identity = get_identity()
    data = request.get_json(silent=True) or {}
    ok, msg = validate_required(data, ['title', 'artist', 'genre'])
    if not ok:
        return jsonify({'code': 400, 'msg': msg}), 400
    music = Music(title=data['title'], artist=data['artist'], genre=data['genre'],
                  album=data.get('album', ''), duration=data.get('duration', 0),
                  cover_url=data.get('cover_url', ''))
    db.session.add(music)
    db.session.commit()
    log_operation(identity['id'], 'music', 'create', f'新增音乐: {music.title}')
    return jsonify({'code': 200, 'msg': '创建成功', 'data': music.to_dict()})


@admin_bp.route('/music/<int:mid>', methods=['PUT'])
@admin_required
def update_music(mid):
    identity = get_identity()
    music = Music.query.get(mid)
    if not music:
        return jsonify({'code': 404, 'msg': '音乐不存在'}), 404
    data = request.get_json(silent=True) or {}
    for field in ['title', 'artist', 'album', 'genre', 'duration', 'cover_url']:
        if field in data:
            setattr(music, field, data[field])
    db.session.commit()
    log_operation(identity['id'], 'music', 'update', f'编辑音乐: {music.title}')
    return jsonify({'code': 200, 'msg': '更新成功', 'data': music.to_dict()})


@admin_bp.route('/music/<int:mid>', methods=['DELETE'])
@admin_required
def delete_music(mid):
    identity = get_identity()
    music = Music.query.get(mid)
    if not music:
        return jsonify({'code': 404, 'msg': '音乐不存在'}), 404
    db.session.delete(music)
    db.session.commit()
    log_operation(identity['id'], 'music', 'delete', f'删除音乐: {music.title}')
    return jsonify({'code': 200, 'msg': '删除成功'})


# ---- Operation Logs ----
@admin_bp.route('/logs', methods=['GET'])
@admin_required
def list_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    query = OperationLog.query.order_by(OperationLog.created_at.desc())
    return jsonify({'code': 200, 'data': paginate_query(query, page, per_page)})


# ---- 数据采集 ----
@admin_bp.route('/collect', methods=['POST'])
@admin_required
def trigger_collection():
    """手动触发数据采集"""
    from flask import current_app
    from app.collector import run_collection
    identity = get_identity()
    try:
        result = run_collection(current_app._get_current_object())
        log_operation(identity['id'], 'collector', 'collect', f'手动触发数据采集')
        return jsonify({'code': 200, 'msg': '数据采集完成', 'data': result})
    except Exception as e:
        logger.error(f"手动采集失败: {e}")
        return jsonify({'code': 500, 'msg': f'采集失败: {str(e)}'}), 500


@admin_bp.route('/collect/status', methods=['GET'])
@admin_required
def collection_status():
    """获取数据采集状态"""
    from config import Config
    from app.models import News, Music
    return jsonify({'code': 200, 'data': {
        'rss_sources': [{'name': s['name'], 'category': s['category']} for s in Config.RSS_SOURCES],
        'collect_interval_hours': Config.COLLECT_INTERVAL / 3600,
        'news_count': News.query.count(),
        'music_count': Music.query.count(),
    }})
