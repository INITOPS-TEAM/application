from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from .models import User, Banned
from . import db

admin_routes = Blueprint("admin", __name__, url_prefix="/admin")

def is_admin():
    user_id = session.get("user_id")
    if not user_id:
        return False
    user = User.query.get(user_id)
    return user and user.username == "admin"

@admin_routes.get("/")
def admin_index():
    if not is_admin():
        return redirect(url_for("auth.login"))

    ip_filter = request.args.get("ip", None)
    if ip_filter:
        users = User.query.filter(User.last_ip.like(f"%{ip_filter}%")).all()
    else:
        users = User.query.order_by(User.id.asc()).all()

    banned_ips = {b.ip for b in Banned.query.filter(Banned.ip.isnot(None)).all()}
    for user in users:
        user.is_banned = user.last_ip in banned_ips

    return render_template("admin.html", users=users)

@admin_routes.post("/ban/<int:user_id>")
def admin_ban_user(user_id):
    if not is_admin():
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if not user:
        flash("User not found")
        return redirect(url_for("admin.admin_index"))

    if not user.last_ip:
        flash("User has no IP address to ban")
        return redirect(url_for("admin.admin_index"))

    if Banned.query.filter_by(ip=user.last_ip).first():
        flash("IP already banned")
        return redirect(url_for("admin.admin_index"))

    ban = Banned(ip=user.last_ip)
    db.session.add(ban)
    db.session.commit()

    flash(f"User {user.username} banned by IP {user.last_ip}")
    return redirect(url_for("admin.admin_index"))

@admin_routes.post("/unban/<int:user_id>")
def admin_unban_user(user_id):
    if not is_admin():
        return redirect(url_for("auth.login"))

    user = User.query.get(user_id)
    if not user or not user.last_ip:
        flash("User or IP not found")
        return redirect(url_for("admin.admin_index"))

    banned_entry = Banned.query.filter_by(ip=user.last_ip).first()
    if banned_entry:
        db.session.delete(banned_entry)
        db.session.commit()
        flash("User unbanned successfully")
    else:
        flash("User was not banned")

    return redirect(url_for("admin.admin_index"))
