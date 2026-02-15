import uuid
import boto3
import os
from pathlib import Path
from flask import Blueprint, render_template, request, redirect, session, url_for, flash, send_file, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Image, Like
from . import db
from .utils import require_login, user_upload_dir, ALLOWED_EXT, handle_hidden_location

image_routes = Blueprint("images", __name__)

def get_s3():
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION"),
    )

@image_routes.get("/images")
def images_list():
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    images = Image.query.order_by(Image.created_at.desc()).all()
    editing_image_id = request.args.get("editing_image_id", type=int)
    unlocked_images = session.get("unlocked_images", [])
    s3 = get_s3()
    
    for img in images:
        img.likes_count = Like.query.filter_by(image_id=img.id).count()
        img.is_liked_by_user = Like.query.filter_by(image_id=img.id, user_id=user_id).first() is not None

        img.s3_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': current_app.config['S3_BUCKET_NAME'], 'Key': img.stored_filename},
            ExpiresIn=3600
        )

    return render_template("images.html", images=images, current_user_id=user_id, editing_image_id=editing_image_id, unlocked_images=unlocked_images)

@image_routes.post("/images/upload")
def images_upload():
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    f = request.files.get("image")
    description = request.form.get("description")

    if not f or not f.filename:
        flash("No file selected")
        return redirect(url_for("images.images_list"))

    original = secure_filename(f.filename)
    ext = "." + original.rsplit(".", 1)[-1].lower()

    if ext not in ALLOWED_EXT:
        flash("Unsupported file type")
        return redirect(url_for("images.images_list"))

    stored_filename = f"{uuid.uuid4().hex}{ext}"
    s3 = get_s3()
    s3.upload_fileobj(
        f,
        current_app.config["S3_BUCKET_NAME"],
        stored_filename,
        ExtraArgs={"ContentType": f.content_type}
    )

    img = Image(
        user_id=user_id,
        stored_filename=stored_filename,
        description=description,
    )
    if not handle_hidden_location(request.form, img):
        flash("Password is required when hiding location.")
        return redirect(url_for("images.images_list"))

    db.session.add(img)
    db.session.commit()

    flash("Uploaded")
    return redirect(url_for("images.images_list"))

@image_routes.route("/images/<int:image_id>/edit", methods=["GET", "POST"])
def images_edit(image_id: int):
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    user_id = int(session["user_id"])
    img = Image.query.get(image_id)
    if not img or img.user_id != user_id:
        flash("Access denied")
        return redirect(url_for("images.images_list"))

    if request.method == "POST":
        img.description = request.form.get("description", "").strip()
        if not handle_hidden_location(request.form, img):
            flash("Password is required when hiding location.")
            return redirect(url_for("images.images_list"))

        db.session.commit()
        flash("Image updated")
        return redirect(url_for("images.images_list"))

    return redirect(url_for("images.images_list", editing_image_id=image_id))

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

    s3 = get_s3()
    s3.delete_object(
        Bucket=current_app.config["S3_BUCKET_NAME"],
        Key=img.stored_filename
    )

    db.session.delete(img)
    db.session.commit()

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

@image_routes.post("/images/<int:image_id>/unlock")
def unlock_location(image_id: int):
    login_redirect = require_login()
    if login_redirect:
        return login_redirect

    img = Image.query.get(image_id)
    if not img:
        flash("Image not found")
        return redirect(url_for("images.images_list"))

    password = request.form.get("password", "")
    if img.location_password_hash and check_password_hash(img.location_password_hash, password):
        unlocked = session.get("unlocked_images", [])
        if image_id not in unlocked:
            unlocked.append(image_id)
        session["unlocked_images"] = unlocked
    else:
        flash("Wrong password")

    return redirect(url_for("images.images_list"))