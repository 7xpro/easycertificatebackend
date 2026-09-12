import bcrypt

from database.db import db
from flask_jwt_extended import create_access_token

from models.user import User


def register_user(username, email, password):
	if not username or not email or not password:
		return {"message": "Username, email, and password are required"}, 400

	if User.query.filter_by(email=email).first():
		return {"message": "Email already exists"}, 400

	hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
	user = User(username=username, email=email, password=hashed_password)

	db.session.add(user)
	db.session.commit()

	return {"message": "User registered successfully"}, 201


def login_user(email, password):
	if not email or not password:
		return {"message": "Email and password are required"}, 400

	user = User.query.filter_by(email=email).first()
	if not user or not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
		return {"message": "Invalid email or password"}, 401

	token = create_access_token(identity=str(user.id))
	return {"token": token, "userid": user.id}, 200
