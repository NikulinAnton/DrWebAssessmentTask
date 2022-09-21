from database import db
from werkzeug.security import generate_password_hash


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
