import uuid
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, session, url_for, flash, send_file, current_app
from werkzeug.utils import secure_filename
from .models import Image
from . import db
from .utils import require_login, user_upload_dir, ALLOWED_EXT

image_routes = Blueprint("images", __name__)

@image_routes.get("/images")
def images_list():
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    images = (
        Image.query.filter_by(user_id=user_id)
        .order_by(Image.created_at.desc())
        .all()
    )
    return render_template("images.html", images=images)

@image_routes.get("/images/<int:image_id>/file")
def images_file(image_id: int):
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    img = Image.query.get(image_id)

    if not img or img.user_id != user_id:
        flash("Access denied")
        return redirect(url_for("images.images_list"))

    return send_file(img.stored_path)

@image_routes.post("/images/upload")
def images_upload():
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    f = request.files.get("image")

    if not f or not f.filename:
        flash("No file selected")
        return redirect(url_for("images.images_list"))

    original = secure_filename(f.filename)
    ext = Path(original).suffix.lower()
    if ext not in ALLOWED_EXT:
        flash("Unsupported file type")
        return redirect(url_for("images.images_list"))

    stored_filename = f"{uuid.uuid4().hex}{ext}"
    dir_path = user_upload_dir(current_app, user_id)
    dir_path.mkdir(parents=True, exist_ok=True)

    final_path = dir_path / stored_filename
    f.save(final_path)

    img = Image(
        user_id=user_id,
        original_filename=original,
        stored_filename=stored_filename,
        stored_path=str(final_path),
    )

    db.session.add(img)
    db.session.commit()

    flash("Uploaded")
    return redirect(url_for("images.images_list"))

@image_routes.post("/images/<int:image_id>/delete")
def images_delete(image_id: int):
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    img = Image.query.get(image_id)

    if not img or img.user_id != user_id:
        flash("Access denied")
        return redirect(url_for("images.images_list"))

    file_path = Path(img.stored_path)

    db.session.delete(img)
    db.session.commit()

    file_path.unlink(missing_ok=True)

    flash("Deleted")
    return redirect(url_for("images.images_list"))