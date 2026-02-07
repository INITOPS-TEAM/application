import uuid
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, session, url_for, flash, send_file, current_app, jsonify
from werkzeug.utils import secure_filename
from .models import Image, Like
from . import db
from .utils import require_login, user_upload_dir, ALLOWED_EXT

image_routes = Blueprint("images", __name__)

@image_routes.get("/images")
def images_list():
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    images = Image.query.order_by(Image.created_at.desc()).all()

    for img in images:
        img.likes_count = Like.query.filter_by(image_id=img.id).count()
        img.is_liked_by_user = Like.query.filter_by(image_id=img.id, user_id=user_id).first() is not None

    return render_template("images.html", images=images, current_user_id=user_id)

@image_routes.get("/images/<int:image_id>/file")
def images_file(image_id: int):
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    img = Image.query.get(image_id)

    if not img:
        flash("Image not found")
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

@image_routes.post("/images/<int:image_id>/like")
def like_image(image_id: int):
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    img = Image.query.get(image_id)
    if not img:
        flash("Image not found")
        return redirect(url_for("images.images_list"))

    existing_like = Like.query.filter_by(user_id=user_id, image_id=image_id).first()
    if existing_like:
        flash("You already liked this image.")
        return redirect(url_for("images.images_list"))

    like = Like(user_id=user_id, image_id=image_id)
    db.session.add(like)
    db.session.commit()

    flash("Image liked.")
    return redirect(url_for("images.images_list"))

@image_routes.post("/images/<int:image_id>/unlike")
def unlike_image(image_id: int):
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    like = Like.query.filter_by(user_id=user_id, image_id=image_id).first()
    if not like:
        flash("You haven't liked this image.")
        return redirect(url_for("images.images_list"))

    db.session.delete(like)
    db.session.commit()

    flash("Like removed.")
    return redirect(url_for("images.images_list"))