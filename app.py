import os

from dotenv import load_dotenv
from flask import Blueprint, Flask, Markup, Request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

load_dotenv()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


if __name__ == "__main__":
    app.run()
