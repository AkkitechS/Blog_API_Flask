import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config():
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'uploads', 'avatars')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Database
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 120
    JWT_REFRESH_TOKEN_EXPIRES = 60 * 60 * 24 * 30

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
