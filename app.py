import hashlib
import os
from typing import Optional

from dotenv import load_dotenv
from flask import Flask, request, send_file
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()
UPLOAD_FOLDER = "store"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(150), nullable=False)
    files = db.relationship("File", backref="files")

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def __repr__(self):
        return f"{self.id}: {self.username}"


class File(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer(), primary_key=True)
    file_name = db.Column(db.String(128), nullable=False)
    owner_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)

    def __init__(self, file_name, owner_id):
        self.file_name = file_name
        self.owner_id = owner_id

    def __repr__(self):
        return f"{self.id}: {self.file_name}"


@auth.verify_password
def verify_password(username: str, password: str) -> Optional[str]:
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return username
    return None


def sha512_hasher(file_data: bytes) -> str:
    hasher = hashlib.sha512()
    hasher.update(file_data)
    return hasher.hexdigest()


@app.route("/upload", methods=["POST"])
@auth.login_required
def upload_file():
    if "file" not in request.files:
        return "Field 'file' shouldn't be null", 400

    file = request.files["file"]
    if file.filename == "":
        return "File doesn't selected", 400

    file_data = file.read()
    file_name = sha512_hasher(file_data)
    file_path = os.path.join(BASE_DIR, UPLOAD_FOLDER, file_name[0:2])
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    elif os.path.exists(os.path.join(file_path, file_name)):
        return "File with such name already exists", 400

    file.save(os.path.join(os.path.join(file_path, file_name)))
    user = User.query.filter_by(username=auth.username()).first()
    db.session.add(File(file_name=file_name, owner_id=user.id))
    db.session.commit()
    return file_name, 201


@app.route("/download", methods=["GET"])
def download_file():
    file_name = request.args.get("file_name", " ")
    file_path = os.path.join(BASE_DIR, UPLOAD_FOLDER, file_name[0:2], file_name)
    if os.path.exists(file_path):
        return send_file(file_path), 200
    return "File isn't found", 404


@app.route("/delete", methods=["DELETE"])
@auth.login_required
def delete_file():
    file_name = request.args.get("file_name", " ")
    file = File.query.filter_by(file_name=file_name).first_or_404()
    file_path = os.path.join(BASE_DIR, UPLOAD_FOLDER, file_name[0:2], file_name)
    user = User.query.filter_by(username=auth.username()).first()
    if file.owner_id == user.id and os.path.exists(file_path):
        os.remove(file_path)
        if not os.listdir(os.path.join(BASE_DIR, UPLOAD_FOLDER, file_name[0:2])):
            os.rmdir(os.path.join(BASE_DIR, UPLOAD_FOLDER, file_name[0:2]))
        db.session.delete(file)
        db.session.commit()
        return "File is successfully deleted", 204
    return "Permission denied", 403


if __name__ == "__main__":
    app.run(debug=os.getenv("DEBUG"))
