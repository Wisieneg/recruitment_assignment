from flask import Blueprint

bp = Blueprint("errors", __name__)


@bp.app_errorhandler(400)
def handle400(e):
    return {
            "error": {
                "message": e.description,
                "type": "Bad Request",
                "code": str(e.code),
                }
            }, 400


@bp.app_errorhandler(403)
def handle403(e):
    return {
            "error": {
                "message": e.description,
                "type": "Forbidden",
                "code": str(e.code),
                }
            }, 403


@bp.app_errorhandler(404)
def handle404(e):
    print(type(e))
    return {
            "error": {
                "message": e.description,
                "type": "Not found",
                "code": str(e.code),
                }
            }, 404


@bp.app_errorhandler(500)
def handle500(e):
    return {
            "error": {
                "message": e.description,
                "type": "Internal Server Error",
                "code": str(e.code),
                }
            }, 500
