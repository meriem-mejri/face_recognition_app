"""
Main application routes.
"""
from flask import Blueprint, render_template, request
from flask_login import login_required
from datetime import datetime
from sqlalchemy import and_
from app.models import RecognizedPerson, CapturedFace
from app.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """Main dashboard showing recognized people and captured faces."""
    recognized_people = RecognizedPerson.query.order_by(RecognizedPerson.date_added.desc()).all()
    
    # Get filter parameters
    capture_date = request.args.get('capture_date')
    person_filter = request.args.get('person_filter')
    
    # Base query for captured faces
    query = CapturedFace.query
    
    # Apply filters
    if capture_date:
        try:
            # Parse the date and filter for the entire day
            filter_date = datetime.strptime(capture_date, '%Y-%m-%d')
            query = query.filter(
                db.func.date(CapturedFace.capture_date) == filter_date.date()
            )
        except ValueError:
            pass  # Ignore invalid date formats
    
    if person_filter:
        # Handle person name or ID filter
        if person_filter.isdigit():
            # If the filter is a number, treat it as an ID
            query = query.filter(CapturedFace.recognized_person_id == int(person_filter))
        else:
            # Otherwise, treat it as a partial name match
            query = query.filter(CapturedFace.name.ilike(f'%{person_filter}%'))
    
    # Execute query with ordering
    captured_faces = query.order_by(CapturedFace.capture_date.desc()).all()
    
    return render_template('index.html', recognized_people=recognized_people, captured_faces=captured_faces)