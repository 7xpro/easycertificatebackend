from flask import Blueprint, jsonify, request

from controllers.auth import login_user, register_user


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    response, status_code = register_user(
        data.get("username"),
        data.get("email"),
        data.get("password"),
    )
    return jsonify(response), status_code


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    response, status_code = login_user(data.get("email"), data.get("password"))
    return jsonify(response), status_code