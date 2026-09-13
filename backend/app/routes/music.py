from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models import Music, UserBehavior
from app.utils import paginate_query, get_identity

music_bp = Blueprint('music', __name__)


@music_bp.route('', methods=['GET'])
@jwt_required()
def list_music():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    genre = request.args.get('genre', '')
    keyword = request.args.get('keyword', '')

    query = Music.query
    if genre:
        query = query.filter_by(genre=genre)
    if keyword:
        query = query.filter(Music.title.like(f'%{keyword}%'))
    query = query.order_by(Music.play_count.desc())

    return jsonify({'code': 200, 'data': paginate_query(query, page, per_page)})


@music_bp.route('/<int:music_id>', methods=['GET'])
@jwt_required()
def get_music(music_id):
    identity = get_identity()
    music = Music.query.get(music_id)
    if not music:
        return jsonify({'code': 404, 'msg': '音乐不存在'}), 404

    music.play_count += 1
    behavior = UserBehavior(user_id=identity['id'], item_type='music', item_id=music_id, action_type='view', rating=1.0)
    db.session.add(behavior)
    db.session.commit()

    return jsonify({'code': 200, 'data': music.to_dict()})
