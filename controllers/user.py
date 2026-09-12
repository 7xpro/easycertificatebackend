from database.db import db
from models.user import User


def get_user_profile(user_id):
	user = db.session.get(User, int(user_id))
	if not user:
		return {"message": "User not found"}, 404

	return {"username": user.username, "email": user.email, "userid": user.id}, 200
