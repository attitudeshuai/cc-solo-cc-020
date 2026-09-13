import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db, logger
from app.models import User
from app.utils import validate_required, log_operation

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    ok, msg = validate_required(data, ['username', 'password'])
    if not ok:
        return jsonify({'code': 400, 'msg': msg}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400

    user = User(username=data['username'], nickname=data.get('nickname', data['username']), role='user')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    logger.info(f"User registered: {user.username}")
    return jsonify({'code': 200, 'msg': '注册成功', 'data': user.to_dict()})


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    ok, msg = validate_required(data, ['username', 'password'])
    if not ok:
        return jsonify({'code': 400, 'msg': msg}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401

    token = create_access_token(identity=json.dumps({'id': user.id, 'username': user.username, 'role': user.role}))
    log_operation(user.id, 'auth', 'login', f'{user.username} 登录系统')
    return jsonify({'code': 200, 'msg': '登录成功', 'data': {'token': token, 'user': user.to_dict()}})


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    from app.utils import get_identity
    identity = get_identity()
    user = User.query.get(identity['id'])
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    return jsonify({'code': 200, 'data': user.to_dict()})
