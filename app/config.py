import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Base Config Object"""
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'info3180')
    UPLOAD_FOLDER = os.environ.get(os.path.dirname(basedir), 'uploads')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # This is just here to suppress a warning from SQLAlchemy as it will soon be removed)