"""
CapturedFace model for storing captured face data.
"""
from datetime import datetime
from app.extensions import db


class CapturedFace(db.Model):
    """Model for storing captured face data from recognition system."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='Unknown')
    capture_date = db.Column(db.DateTime, default=datetime.utcnow)
    image_data = db.Column(db.LargeBinary)
    confidence = db.Column(db.Float)
    recognized_person_id = db.Column(db.Integer, db.ForeignKey('recognized_person.id'))
    image_format = db.Column(db.String(10))
    recognized_person = db.relationship('RecognizedPerson', backref='captured_faces')

