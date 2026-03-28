import config

from app.extensions import db, migrate, mail
from app.models import User, VegetableCategory
from app.blueprints.main import bp as main_bp
from app.blueprints.auth import bp as auth_bp
from app.blueprints.vegetable import bp as vegetable_bp
from app.blueprints.upload import bp as upload_bp

from flask import Flask, g, jsonify, session ,render_template, request, redirect, url_for
from werkzeug.exceptions import RequestEntityTooLarge

def create_app():

    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static'
                )
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    @app.before_request
    def before_request():
        user_id = session.get("user_id")
        if user_id:
            user = db.session.scalar(
                db.select(User).where(User.id == user_id)
            )
            g.user = user
        else:
            g.user = None
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        return jsonify({
            "result": False,
            "message": "图片大小不能超过 5MB"
        }), 413

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html') , 404

    @app.errorhandler(403)
    def handle_403(e):
        return render_template("403.html"), 403

    @app.context_processor
    def context_processor():
        categories = db.session.scalars(
            db.select(VegetableCategory).order_by(VegetableCategory.id)
        ).all()
        return {
            "user": g.user,
            "categories": categories,
        }

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(vegetable_bp)
    app.register_blueprint(upload_bp)

    return app
