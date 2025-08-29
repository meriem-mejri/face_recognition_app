"""
Routes for managing captured faces.
"""
import io
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required
from PIL import Image

from app.extensions import db
from app.models import CapturedFace, RecognizedPerson, PersonImage

face_bp = Blueprint('face', __name__)


@face_bp.route('/delete_face/<int:id>')
@login_required
def delete_face(id):
    """Delete a captured face."""
    face = CapturedFace.query.get_or_404(id)
    db.session.delete(face)
    db.session.commit()
    flash('Face deleted successfully')
    return redirect(url_for('main.index'))


@face_bp.route('/add_recognized_from_face/<int:id>', methods=['GET', 'POST'])
@login_required
def add_recognized_from_face(id):
    """Add a captured face as a recognized person or link to existing person."""
    face = CapturedFace.query.get_or_404(id)
    recognized_people = RecognizedPerson.query.all()

    if request.method == 'POST':
        action = request.form.get('action')
        print(f"Received form data: {request.form}")  # Debug log
        
        if not action:
            flash("Invalid action selected. Please try again.", "error")
            return redirect(url_for('face.add_recognized_from_face', id=id))
        
        try:    
            if action == 'new':
                name = request.form.get('name', '').strip()
                title = request.form.get('title', '').strip()
                if not name:
                    flash("Name is required for new person.", "error")
                    return redirect(url_for('face.add_recognized_from_face', id=id))

                new_person = RecognizedPerson(name=name, title=title)
                db.session.add(new_person)
                db.session.flush()

                # Create folder for the new person
                folder = f"dataset/{name}"
                os.makedirs(folder, exist_ok=True)

                if face.image_data and face.image_format:
                    print(f"Adding image for {name}: format={face.image_format}, data length={len(face.image_data)}")
                    
                    # Save image to folder
                    img = Image.open(io.BytesIO(face.image_data))
                    ext = face.image_format.lower()
                    filename = f"face_{face.id}.{ext}"
                    image_path = os.path.join(folder, filename)
                    img.save(image_path)
                    
                    # Save image to DB
                    new_img = PersonImage(
                        person_id=new_person.id,
                        image_data=face.image_data,
                        image_format=face.image_format,
                        is_main=True
                    )
                    db.session.add(new_img)
                else:
                    print(f"Warning: No valid image data for {name}")
                    flash("Failed to add image due to invalid data.", "warning")

                face.recognized_person_id = new_person.id
                face.name = name
                db.session.commit()
                flash(f"Face {id} added as recognized person '{name}'.", "success")
                
            elif action == 'existing':
                existing_person_id = request.form.get('existing_person_id', '')
                if not existing_person_id or existing_person_id == "":
                    flash("Please select a person to link.", "error")
                    return redirect(url_for('face.add_recognized_from_face', id=id))
                    
                existing_person = RecognizedPerson.query.get_or_404(int(existing_person_id))
                face.recognized_person_id = existing_person.id
                face.name = existing_person.name

                # Get or create folder for the existing person
                folder = f"dataset/{existing_person.name}"
                os.makedirs(folder, exist_ok=True)

                if face.image_data and face.image_format:
                    print(f"Adding image to existing person {existing_person.name}")
                    
                    # Save image to folder
                    img = Image.open(io.BytesIO(face.image_data))
                    ext = face.image_format.lower()
                    filename = f"face_{face.id}.{ext}"
                    image_path = os.path.join(folder, filename)
                    img.save(image_path)
                    
                    # Save image to DB
                    new_img = PersonImage(
                        person_id=existing_person.id,
                        image_data=face.image_data,
                        image_format=face.image_format,
                        is_main=False
                    )
                    db.session.add(new_img)
                else:
                    print(f"Warning: No valid image data for {existing_person.name}")
                    flash("Failed to add image due to invalid data.", "warning")

                db.session.commit()
                flash(f"Face {id} linked to existing person '{existing_person.name}' (ID: {existing_person.id}).", "success")
            
            return redirect(url_for('main.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error processing request: {str(e)}", "error")
            return redirect(url_for('face.add_recognized_from_face', id=id))

    return render_template('add_recognized_from_face.html', face=face, recognized_people=recognized_people)


@face_bp.route('/image/<int:id>')
@login_required
def serve_image(id):
    """Serve captured face images."""
    if request.args.get('table') == 'recognized':
        person = RecognizedPerson.query.get(id)
        if person and person.image_data:
            mimetype = f'image/{person.image_format.lower()}' if person.image_format else 'image/jpeg'
            return send_file(io.BytesIO(person.image_data), mimetype=mimetype)
            
    face = CapturedFace.query.get(id)
    if face and face.image_data:
        mimetype = f'image/{face.image_format.lower()}' if face.image_format else 'image/jpeg'
        return send_file(io.BytesIO(face.image_data), mimetype=mimetype)
        
    person = RecognizedPerson.query.get(id)
    if person and person.image_data:
        mimetype = f'image/{person.image_format.lower()}' if person.image_format else 'image/jpeg'
        return send_file(io.BytesIO(person.image_data), mimetype=mimetype)
        
    return "Image not found", 404