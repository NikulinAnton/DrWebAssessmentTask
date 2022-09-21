import hashlib
import os
from typing import Optional

import database
from flask import Flask, request, send_file
from flask_httpauth import HTTPBasicAuth
from models import File, User, db
from werkzeug.security import check_password_hash, generate_password_hash

UPLOAD_FOLDER = "store"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config.from_object("config.Config")
database.init_app(app)


@app.before_first_request
def create_test_user():
    test_user = User(username="test", password="test")
    db.session.add(test_user)
    db.session.commit()


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
    file_name = sha512_hasher(file_data) + os.path.splitext(file.filename)[1]
    file_path = os.path.join(BASE_DIR, UPLOAD_FOLDER, file_name[0:2])
    if not os.path.exists(file_path):
        os.mkdir(file_path)
    elif os.path.exists(os.path.join(file_path, file_name)):
        return "File with such name already exists", 400

    with open(os.path.join(file_path, file_name), "wb") as file_to_write:
        file_to_write.write(file_data)

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
    app.run()
