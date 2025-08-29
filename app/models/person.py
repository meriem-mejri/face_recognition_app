"""
Person and PersonImage models for recognized people.
"""
from datetime import datetime
from app.extensions import db


class RecognizedPerson(db.Model):
    """Model for recognized people in the system."""
    __tablename__ = 'recognized_person'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('PersonImage', backref='person', lazy=True, cascade="all, delete-orphan")


class PersonImage(db.Model):
    """Model for storing images of recognized people."""
    __tablename__ = 'person_image'
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('recognized_person.id'), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)
    image_format = db.Column(db.String(10), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    is_main = db.Column(db.Boolean, default=False)
