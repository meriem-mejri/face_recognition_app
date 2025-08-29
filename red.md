# Face Recognition App

A Flask-based application for real-time face recognition using a camera feed, with features for managing recognized persons, capturing faces, and storing data in a PostgreSQL database.

## Overview

This application uses computer vision to detect and recognize faces from a video stream (e.g., webcam or IP camera). It includes a web interface for managing recognized individuals, capturing photos, and viewing captured faces with confidence scores. The face recognition model is trained using images stored in the `dataset` folder, and encodings are saved in `encodings.pickle`.

## Project Structure
Face Recognition App/
├── pycache/
├── app/
│   ├── pycache/
│   ├── init.py
│   ├── extensions.py
│   ├── utils.py
│   ├── config.py
│   ├── app.py
├── auth/
│   ├── pycache/
│   ├── init.py
│   ├── routes.py
├── models/
│   ├── init.py
│   ├── face.py
│   ├── user.py
│   ├── person.py
├── routes/
│   ├── init.py
│   ├── main.py
│   ├── person.py
│   ├── face.py
├── templates/
│   ├── add_person.html
│   ├── add_recognized_from_face.html
│   ├── capture_photos.html
│   ├── edit_person.html
│   ├── index.html
│   ├── login.html
├── routes/
│   ├── init.py
├── dataset/           # Folder for storing training images
├── door_monitor.py    # Real-time face recognition script
├── encodings.pickle   # Serialized face encodings
├── README.md
├── requirements.txt   # Python dependencies
├── train_model.py     # Script to train the face recognition model


## Features

- Real-time face detection and recognition using a camera feed.
- Web-based dashboard to manage recognized persons and captured faces.
- Admin authentication with login/logout functionality.
- Capture and store up to 50 photos per person.
- Export recognized people and captured faces to CSV.
- Store images and face data in a PostgreSQL database.

## Prerequisites

- Python 3.7+
- PostgreSQL database server
- System dependencies (for `face_recognition`):
  - Linux: `cmake`, `libopenblas-dev`, `liblapack-dev`, `libblas-dev`
  - Windows/macOS: Ensure CMake is installed
- A webcam or IP camera (e.g., RTSP/HTTP stream)

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/your-username/face-recognition-app.git
cd face-recognition-app
```

2. **Install Python dependencies:Ensure you have pip installed, then run**:
```bash
pip install -r requirements.txt
```

3. **Set up the PostgreSQL database**:
Install PostgreSQL and create a database named face_recognition_db.
Create a user face_recognition with password stage2025 (or update config.py with your credentials).
Example SQL commands:

```sql
sqlCREATE DATABASE face_recognition_db;
CREATE USER face_recognition WITH PASSWORD 'stage2025';
GRANT ALL PRIVILEGES ON DATABASE face_recognition_db TO face_recognition;
```

4. **Configure environment variables (optional)**:
Set SECRET_KEY and DATABASE_URL in your environment:
```bash
export SECRET_KEY='your-secret-key'
export DATABASE_URL='postgresql://face_recognition:stage2025@localhost/face_recognition_db'
```
Alternatively, update config.py with your settings.

5. **Prepare the dataset**:
Place training images in the dataset folder, organized by subfolders (e.g., dataset/person_name/image.jpg).
Run the training script to generate face encodings:
```bash
python train_model.py
```

## Usage

1. **Run the Flask application**:
```bash
python app.py
```
Access the web interface at http://localhost:5000.
Log in with the default admin credentials: username: admin, password: admin123.

2. **Run the door monitoring script**:
Start real-time face recognition:
```bash
python door_monitor.py
```
Press Esc to exit the camera window (resizable, initially 800x600 pixels).
Ensure CAMERA_SOURCE in door_monitor.py is set to your camera (e.g., 0 for webcam or an RTSP URL).

3. **Manage recognized persons**:
Use the web dashboard to add new persons, capture photos, or link captured faces to existing persons.

## Configuration
Edit config.py to adjust settings:
    SECRET_KEY: A secure key for Flask sessions.
    SQLALCHEMY_DATABASE_URI: Database connection string (defaults to PostgreSQL).
    DEBUG: Enable/disable debug mode (True for development, False for production).
Update door_monitor.py for camera settings (e.g., CAMERA_SOURCE, MATCH_THRESHOLD).

## License
[Add your license here, e.g., MIT, GPL, etc. If none, state that the project is unlicensed or proprietary.]

## Acknowledgments
Built with Flask, OpenCV, and face_recognition libraries.
Thanks to the open-source community for tools like imutils and Pillow.

## Troubleshooting
Camera not working: Verify CAMERA_SOURCE in door_monitor.py matches your setup (e.g., RTSP URL or device index).
Database errors: Ensure PostgreSQL is running and credentials in config.py are correct.
Face recognition issues: Check that encodings.pickle was generated and contains valid data.