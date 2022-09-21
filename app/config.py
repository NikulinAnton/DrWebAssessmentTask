import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    DEBUG = os.getenv("DEBUG")
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
