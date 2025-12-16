import os

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import cloudinary

db = SQLAlchemy()
jwt = JWTManager()
ma = Marshmallow()
migrate = Migrate()

def init_cloudinary():
    cloudinary.config(cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'), api_key=os.getenv('CLOUDINARY_API_KEY'),api_secret=os.getenv('CLOUDINARY_API_SECRET'), secure=True)

def init_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    ma.init_app(app)
    init_cloudinary()
