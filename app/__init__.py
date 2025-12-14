from flask import Flask
from app.config import DevelopmentConfig
from app.extensions import init_extensions
from app.routes.users import users_bp
from app.routes.auth import auth_bp
from app.models.users import User
from app.models.articles import Article
from app.models.comments import Comment

BASE_ROUTE = '/api/v1/blog'

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    init_extensions(app)

    app.register_blueprint(users_bp, url_prefix=f'{BASE_ROUTE}/users')
    app.register_blueprint(auth_bp, url_prefix=f'{BASE_ROUTE}/auth')

    return app