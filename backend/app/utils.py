import json
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app import db, logger
from app.models import OperationLog


def get_identity():
    """解析 JWT identity（JSON 字符串 -> dict）"""
    raw = get_jwt_identity()
    if isinstance(raw, str):
        return json.loads(raw)
    return raw


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_identity()
        if identity.get('role') != 'admin':
            return jsonify({'code': 403, 'msg': '需要管理员权限'}), 403
        return fn(*args, **kwargs)
    return wrapper


def log_operation(user_id, module, action, detail=''):
    try:
        ip = request.remote_addr or ''
        log = OperationLog(user_id=user_id, module=module, action=action, detail=detail, ip=ip)
        db.session.add(log)
        db.session.commit()
        logger.info(f"[OP] user={user_id} module={module} action={action} detail={detail}")
    except Exception as e:
        logger.error(f"Failed to log operation: {e}")


def validate_required(data, fields):
    missing = [f for f in fields if not data.get(f)]
    if missing:
        return False, f"缺少必填字段: {', '.join(missing)}"
    return True, ''


def paginate_query(query, page=1, per_page=10):
    page = max(1, page)
    per_page = min(max(1, per_page), 100)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'list': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    }
