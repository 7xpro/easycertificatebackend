from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from controllers.user import get_user_profile


user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
	response, status_code = get_user_profile(get_jwt_identity())
	return jsonify(response), status_code
