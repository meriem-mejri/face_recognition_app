"""
Routes package for the Face Recognition application.
"""
from .main import main_bp
from .person import person_bp
from .face import face_bp

__all__ = ['main_bp', 'person_bp', 'face_bp']
