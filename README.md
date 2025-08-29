# Face Recognition Application

A Flask-based web application for managing recognized people and captured faces.

## Project Structure

```
face_recognition_app/
├── app/
│   ├── __init__.py              # Application factory
│   ├── extensions.py            # Flask extensions initialization
│   ├── utils.py                 # Utility functions
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py            # Authentication routes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # Admin user model
│   │   ├── person.py            # RecognizedPerson and PersonImage models
│   │   └── face.py              # CapturedFace model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py              # Main dashboard routes
│   │   ├── person.py            # Person management routes
│   │   └── face.py              # Face management routes
│   ├── static/                  # Static files (CSS, JS, images)
│   └── templates/               # Jinja2 templates
├── config.py                    # Configuration settings
├── app.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Features

- User authentication with Flask-Login
- Manage recognized people with multiple images
- Handle captured faces from recognition system
- Link captured faces to existing or new recognized people
- Image storage in PostgreSQL database
- Responsive web interface

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up PostgreSQL database and update connection string in `config.py`

3. Run the application:
   ```bash
   python app.py
   ```

4. Access the application at `http://localhost:5000`

## Default Credentials

- Username: `admin`
- Password: `admin123`

## Configuration

The application supports multiple configuration environments:
- Development (default)
- Production
- Testing

Configuration can be set via the `FLASK_ENV` environment variable.

## Database Models

- **Admin**: User authentication
- **RecognizedPerson**: People known to the system
- **PersonImage**: Images associated with recognized people
- **CapturedFace**: Faces captured by the recognition system

