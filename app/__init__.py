import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .utils import get_client_ip
db = SQLAlchemy()
migrate = Migrate()

def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL isn't set. Run this app on app VM with Postgres")

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["AWS_REGION"] = os.environ["AWS_REGION"]
    app.config["S3_BUCKET_NAME"] = os.environ["S3_BUCKET_NAME"]

    db.init_app(app)
    migrate.init_app(app, db)

    from .models import User, Image, Like, Banned
    from .auth import auth_routes
    from .images import image_routes
    from .admin import admin_routes

    app.register_blueprint(auth_routes)
    app.register_blueprint(image_routes)
    app.register_blueprint(admin_routes)

    @app.route("/health")
    def health():
        return "OK", 200

    @app.before_request
    def check_banned():
        from flask import session, request, redirect
        from .models import Banned

        if request.endpoint in ("auth.login", "auth.logout", "auth.register", "static", "admin.admin_index"):
            return None
        
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user and user.username == "admin":
                return None
        
        ip = get_client_ip()

        if Banned.query.filter_by(ip=ip).first():
            return redirect("https://zakon.rada.gov.ua/laws/show/2341-14/conv/paran1661#n1661")

        return None

    return app