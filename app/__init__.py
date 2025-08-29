"""
Application factory for the Face Recognition application.
"""
from flask import Flask
from werkzeug.security import generate_password_hash

from config import config
from app.extensions import db, migrate, login_manager
from app.models import Admin
from app.auth import auth_bp
from app.routes import main_bp, person_bp, face_bp


def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(person_bp)
    app.register_blueprint(face_bp)

    # Create database tables and default admin user
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123', method='pbkdf2:sha256')
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin created.")

    return app

