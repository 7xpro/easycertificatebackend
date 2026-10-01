from flask import Flask 
from flask_cors import CORS
from config import DevelopmentConfig
from database.db import db
from models.user import User
from sqlalchemy import text
from flask_jwt_extended import JWTManager
from routes.auth import auth_bp
from routes.user import user_bp
from routes.uploads import routes_bp
from datetime import timedelta





app =Flask(__name__)
app.config.from_object(DevelopmentConfig)
CORS(app)
db.init_app(app)
jwt = JWTManager(app)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(routes_bp, url_prefix='/upload')
with app.app_context():
    try:
        db.session.execute(text("SELECT 1"))
        print("✅ Connected to MySQL successfully")
        db.create_all();
    except Exception as e:
        print("❌ Connection failed")
        print(e)

@app.route('/')
def hello():
    return "server is running"



    


if __name__ == '__main__':
    app.run(
    host="0.0.0.0",
    port=5000,
    debug=True
)