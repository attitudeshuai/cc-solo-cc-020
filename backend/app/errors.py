from flask import jsonify
from app import logger


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        logger.warning(f"400 Bad Request: {e}")
        return jsonify({'code': 400, 'msg': str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'code': 401, 'msg': '未授权，请先登录'}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'code': 403, 'msg': '权限不足'}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'code': 404, 'msg': '资源不存在'}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({'code': 405, 'msg': '请求方法不允许'}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"500 Internal Error: {e}")
        return jsonify({'code': 500, 'msg': '服务器内部错误'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled Exception: {e}", exc_info=True)
        return jsonify({'code': 500, 'msg': f'服务器错误: {str(e)}'}), 500
