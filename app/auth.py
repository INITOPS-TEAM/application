from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from .utils import require_login

auth_routes = Blueprint("auth", __name__)

@auth_routes.get("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("auth.profile"))
    return redirect(url_for("auth.login"))

@auth_routes.get("/profile")
def profile():
    r = require_login()
    if r:
        return r
    return render_template("profile.html")

@auth_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if not username or not password:
            flash("Username and password are required.")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return render_template("register.html")

        u = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()

        session["user_id"] = int(u.id)
        return redirect(url_for("auth.profile"))

    return render_template("register.html")

@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        u = User.query.filter_by(username=username).first()
        if not u or not check_password_hash(u.password_hash, password):
            flash("Invalid credentials")
            return render_template("login.html")

        session["user_id"] = int(u.id)
        return redirect(url_for("auth.profile"))

    return render_template("login.html")

@auth_routes.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))