from pathlib import Path
from flask import session, redirect, url_for, request
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}

def require_login():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    return None

def upload_root(app):
    return Path(app.config["UPLOAD_ROOT"])

def user_upload_dir(app, user_id: int) -> Path:
    return upload_root(app) / f"u{user_id}"

def pick_ext(filename: str) -> str:
    safe = secure_filename(filename or "")
    ext = Path(safe).suffix.lower()
    if ext not in ALLOWED_EXT:
        raise ValueError("Unsupported file type. Use jpg,jpeg,png,webp")
    return ext

def get_client_ip():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    return ip

def handle_hidden_location(form_data, image):
    hide_location = "hide_location" in form_data
    password = form_data.get("location_password", "").strip()
    location_value = form_data.get("location", "").strip()

    if hide_location and not password:
        return False

    image.location_is_hidden = hide_location
    if location_value:
        image.location = location_value
    image.location_password_hash = generate_password_hash(password) if hide_location else None

    return True