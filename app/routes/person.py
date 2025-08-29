"""
Person-related routes for managing RecognizedPerson entities.
"""
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, flash, send_file
from flask_login import login_required
from app.models import RecognizedPerson, PersonImage
from app.extensions import db
import os
import shutil
from pathlib import Path
import io
from PIL import Image

person_bp = Blueprint('person', __name__)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@person_bp.route('/add_person_form')
@login_required
def add_person_form():
    """Display form to add a new person."""
    return render_template('add_person.html')

@person_bp.route('/add_person', methods=['POST'])
@login_required
def add_person():
    """Add a new recognized person with images from form submission."""
    name = request.form['name']
    title = request.form['title']
    main_image_index = request.form.get('main_image_index', '0')
    temp_folder = request.form.get('temp_folder')
    images = request.files.getlist('images')  # Get the list of files from the form

    if not images or all(not image.filename for image in images):
        flash('No valid images provided.')
        return redirect(url_for('person.add_person_form'))

    try:
        # Create the person
        person = RecognizedPerson(name=name, title=title)
        db.session.add(person)
        db.session.flush()

        # Rename temporary folder to final folder
        final_folder = f"dataset/{name}"
        if temp_folder and os.path.exists(temp_folder):
            if os.path.exists(final_folder):
                shutil.rmtree(final_folder)  # Remove existing folder if any
            shutil.move(temp_folder, final_folder)  # Rename temp folder to final
        else:
            os.makedirs(final_folder, exist_ok=True)

        # Process uploaded images
        for index, image in enumerate(images):
            if image and allowed_file(image.filename):
                # Save the image to the dataset folder (if not already saved via temp folder)
                image_path = os.path.join(final_folder, image.filename)
                if not os.path.exists(image_path):  # Avoid overwriting if already moved
                    image.save(image_path)

                # Save the image to the database
                img = Image.open(image)
                img_byte_arr = io.BytesIO()
                img_format = img.format if img.format else 'PNG'
                img.save(img_byte_arr, format=img_format)
                img_byte_arr.seek(0)  # Reset buffer position
                new_img = PersonImage(
                    person_id=person.id,
                    image_data=img_byte_arr.getvalue(),
                    image_format=img_format,
                    is_main=(str(index) == main_image_index)
                )
                db.session.add(new_img)

        db.session.commit()
        flash('Person added successfully')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        print(f"Error processing images: {e}")
        flash(f'Error processing images: {e}')
        if temp_folder and os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)  # Clean up temp folder on failure
        return redirect(url_for('person.add_person_form'))

@person_bp.route('/edit_person/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_person(id):
    """Edit an existing recognized person."""
    person = RecognizedPerson.query.get_or_404(id)

    if request.method == 'POST':
        # Update person details
        old_name = person.name
        person.name = request.form["name"]
        person.title = request.form["title"]

        # Handle folder renaming if name changed
        if old_name != person.name:
            old_folder = f"dataset/{old_name}"
            new_folder = f"dataset/{person.name}"
            if os.path.exists(old_folder):
                shutil.move(old_folder, new_folder)
            else:
                os.makedirs(new_folder, exist_ok=True)

        # Handle deleted images
        deleted_images = request.form.get("deleted_images", "")
        current_images_count = len(person.images)  # Define the count of current images
        if deleted_images:
            deleted_image_ids = [img_id for img_id in deleted_images.split(",") if img_id.isdigit()]

            if current_images_count - len(deleted_image_ids) < 1:
                flash('Cannot delete all images. At least one image must remain.')
                db.session.rollback()
                return redirect(url_for('person.edit_person', id=id))

            for image_id in deleted_image_ids:
                image = PersonImage.query.get(int(image_id))
                if image and image.person_id == person.id:
                    # Delete from file system
                    image_path = os.path.join(f"dataset/{person.name}", f"{image.id}.{image.image_format.lower()}")
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    db.session.delete(image)  # Delete from database

        # Handle new images from form submission
        images = request.files.getlist('images')
        folder = f"dataset/{person.name}"
        os.makedirs(folder, exist_ok=True)
        new_images = []

        for index, image in enumerate(images):
            if image and allowed_file(image.filename):
                img = Image.open(image)
                img_byte_arr = io.BytesIO()
                img_format = img.format if img.format else 'PNG'
                img.save(img_byte_arr, format=img_format)  # Save image to BytesIO first
                img_byte_arr.seek(0)  # Reset buffer position

                new_img = PersonImage(
                    person_id=person.id,
                    image_data=img_byte_arr.getvalue(),  # Use populated img_byte_arr
                    image_format=img_format,
                    is_main=False
                )
                db.session.add(new_img)
                db.session.flush()

                image_filename = f"{new_img.id}.{img_format.lower()}"
                image_path = os.path.join(folder, image_filename)
                img.save(image_path, format=img_format)  # Save to file system
                new_images.append((new_img, f"new-{index}"))

        # Handle main image selection
        main_img_id = request.form.get('main_image')
        if main_img_id:
            # Reset all images to not main
            for img in person.images:
                img.is_main = False
            # Set main image for existing images
            found_main = False
            for img in person.images:
                if str(img.id) == main_img_id:
                    img.is_main = True
                    found_main = True
                    break
            # If main image is a new image, set its is_main to True
            if not found_main:
                for new_img, temp_id in new_images:
                    if temp_id == main_img_id:
                        new_img.is_main = True
                        break

        try:
            db.session.commit()
            flash('Person updated successfully')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating person: {e}")
            flash(f'Error updating person: {e}')
            return redirect(url_for('person.edit_person', id=id))

    # Sort images by id in ascending order before rendering
    person.images = PersonImage.query.filter_by(person_id=person.id).order_by(PersonImage.id.asc()).all()
    return render_template('edit_person.html', person=person)

@person_bp.route('/person_image/<int:image_id>')
@login_required
def serve_person_image(image_id):
    """Serve a person's image."""
    img = PersonImage.query.get_or_404(image_id)
    mimetype = f'image/{img.image_format.lower()}'
    return send_file(io.BytesIO(img.image_data), mimetype=mimetype)

@person_bp.route('/delete_person/<int:id>')
@login_required
def delete_person(id):
    """Delete a recognized person."""
    person = RecognizedPerson.query.get_or_404(id)
    folder = f"dataset/{person.name}"
    if os.path.exists(folder):
        shutil.rmtree(folder)
    db.session.delete(person)
    db.session.commit()
    flash('Person deleted successfully')
    return redirect(url_for('main.index'))

@person_bp.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    """Create a folder named dataset/{name}."""
    try:
        data = request.get_json()
        folder_name = data.get('folder_name')
        if not folder_name:
            return jsonify({'status': 'error', 'message': 'Folder name is required'}), 400
        os.makedirs(folder_name, exist_ok=True)
        return jsonify({'status': 'success', 'message': f'Folder {folder_name} created'}), 200
    except Exception as e:
        print(f"Error creating folder: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@person_bp.route('/save_photo', methods=['POST'])
@login_required
def save_photo():
    """Save a photo to the specified folder."""
    try:
        image = request.files.get('image')
        folder = request.form.get('folder')
        if not image or not folder:
            return jsonify({'status': 'error', 'message': 'Image and folder are required'}), 400
        if not allowed_file(image.filename):
            return jsonify({'status': 'error', 'message': 'Invalid file type. Allowed types: png, jpg, jpeg'}), 400
        image_path = os.path.join(folder, image.filename)
        image.save(image_path)
        return jsonify({'status': 'success', 'message': f'Photo saved to {image_path}'}), 200
    except Exception as e:
        print(f"Error saving photo: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@person_bp.route('/cleanup_temp', methods=['POST'])
@login_required
def cleanup_temp():
    """Delete a temporary folder and its contents."""
    try:
        data = request.get_json()
        temp_folder = data.get('folder')
        if not temp_folder:
            return jsonify({'status': 'error', 'message': 'Folder name is required'}), 400
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        return jsonify({'status': 'success', 'message': f'Folder {temp_folder} deleted'}), 200
    except Exception as e:
        print(f"Error cleaning up folder: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@person_bp.route('/capture_photos')
@login_required
def capture_photos():
    """Display the photo capture page."""
    temp_folder = request.args.get('temp_folder')
    name = request.args.get('name')
    return render_template('capture_photos.html', temp_folder=temp_folder, name=name)