import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
db = SQLAlchemy()

def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL isn't set. Run this app on app VM with Postgres")

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_ROOT"] = os.environ.get("UPLOAD_ROOT", "/var/lib/pictapp/uploads")

    db.init_app(app)

    from .models import User, Image
    from .auth import auth_routes
    from .images import image_routes

    app.register_blueprint(auth_routes)
    app.register_blueprint(image_routes)

    with app.app_context():
        required = {"users", "images"}
        rows = db.session.execute(
            text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public';")
        ).fetchall()
        existing = {r[0] for r in rows}
        missing = required - existing
        if missing:
            raise RuntimeError(
                f"Missing DB tables: {sorted(missing)}. Run DB setup first."
            )

    return app