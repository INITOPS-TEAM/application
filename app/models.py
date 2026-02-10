from sqlalchemy import text
from . import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    last_ip = db.Column(db.Text)

class Image(db.Model):
    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    original_filename = db.Column(db.Text, nullable=False)
    stored_filename = db.Column(db.Text, nullable=False, unique=True)
    stored_path = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=text("now()"), nullable=False)

class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    image_id = db.Column(db.Integer, nullable=False, index=True)

class Banned(db.Model):
    __tablename__ = "banned"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.Text, unique=True)