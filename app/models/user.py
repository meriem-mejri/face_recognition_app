"""
User models for authentication.
"""
from flask_login import UserMixin
from app.extensions import db


class Admin(UserMixin, db.Model):
    """Admin user model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

