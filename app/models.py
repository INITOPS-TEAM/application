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
    stored_filename = db.Column(db.Text, nullable=False, unique=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=text("now()"), nullable=False)
    description = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=True)
    location_is_hidden = db.Column(db.Boolean, default=False)
    location_password_hash = db.Column(db.String(255), nullable=True)

class Like(db.Model):
    __tablename__ = "likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    image_id = db.Column(db.Integer, nullable=False, index=True)

class Banned(db.Model):
    __tablename__ = "banned"
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.Text, unique=True)