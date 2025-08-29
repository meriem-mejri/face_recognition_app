import cv2
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import numpy as np
import pickle
import time
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PIL import Image
import io
from datetime import datetime
from app.models import RecognizedPerson, PersonImage, CapturedFace

# === Config ===
CAMERA_SOURCE = 0
# 'rtsp://rtsp:sdi_cam_3109@172.20.95.212:554/media/video1'  # Default webcam or RTSP/HTTP URL
MATCH_THRESHOLD = 0.45  # Face match threshold
ENCODINGS_FILE = "encodings.pickle"
DATABASE_URI = 'postgresql://face_recognition:stage2025@localhost/face_recognition_db'
MIN_MOTION_AREA = 500  # Minimum area (pixels) to consider motion
CAPTURE_DELAY = 2.0  # Seconds between captures during motion
MOTION_THRESHOLD = 0.1  # Percentage of frame area for motion detection

# === Database Setup ===
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# === Load known faces ===
print("[INFO] Loading known faces...")
try:
    data = pickle.loads(open(ENCODINGS_FILE, "rb").read())
    known_encodings = data["encodings"]
    known_names = data["names"]
    print(f"[DEBUG] Total known encodings loaded: {len(known_encodings)}")
except FileNotFoundError:
    print(f"[ERROR] Could not find {ENCODINGS_FILE}.")
    exit(1)
except Exception as e:
    print(f"[ERROR] Failed to load encodings: {e}")
    exit(1)

# Initialize variables
currentname = "unknown"
last_capture_time = 0  # Track time of last capture
motion_detected = False

# Initialize video stream and background subtractor
print("[INFO] Starting video stream...")
vs = VideoStream(src=CAMERA_SOURCE, framerate=10).start()
time.sleep(2.0)
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=25, detectShadows=True)

# Start FPS counter
fps = FPS().start()
cv2.namedWindow("Facial Recognition is Running", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Facial Recognition is Running", 600, 400)  

try:
    while True:
        # Grab frame
        frame = vs.read()
        if frame is None:
            print("[ERROR] Failed to read frame.")
            continue
        frame = imutils.resize(frame, width=500)
        frame_area = frame.shape[0] * frame.shape[1]

        # Motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)  # Reduce noise
        fg_mask = bg_subtractor.apply(gray)
        _, thresh = cv2.threshold(fg_mask, 25, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_area = sum(cv2.contourArea(c) for c in contours if cv2.contourArea(c) > MIN_MOTION_AREA)
        motion_detected = motion_area > (MOTION_THRESHOLD * frame_area)

        # Face detection and recognition (runs every frame)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, boxes)
        names = []

        print(f"[DEBUG] Detected {len(boxes)} faces")

        for idx, (encoding, (top, right, bottom, left)) in enumerate(zip(encodings, boxes)):
            name = "Unknown"
            confidence = 0.0

            if known_encodings:
                distances = face_recognition.face_distance(known_encodings, encoding)
                min_distance = np.min(distances)
                best_match_index = np.argmin(distances)
                confidence = max(0.0, 1 - min_distance)
                if min_distance < MATCH_THRESHOLD:
                    name = known_names[best_match_index]
                    print(f"[MATCH] Recognized {name} (Confidence: {confidence:.2f})")
                else:
                    print(f"[NO MATCH] Distance {min_distance:.3f} > {MATCH_THRESHOLD}")

            if currentname != name:
                currentname = name
                print(currentname)

            names.append(name)

            # Save face to database only if motion detected and delay has passed
            if motion_detected and (time.time() - last_capture_time >= CAPTURE_DELAY):
                print("[INFO] Motion detected, saving face...")
                try:
                    img_crop = frame[max(0, top):bottom, max(0, left):right]
                    if img_crop.size == 0:
                        print(f"[WARNING] Empty crop for face {idx}, skipping")
                        continue
                    pil_img = Image.fromarray(cv2.cvtColor(img_crop, cv2.COLOR_BGR2RGB))
                    img_byte_arr = io.BytesIO()
                    pil_img.save(img_byte_arr, format='JPEG')
                    image_data = img_byte_arr.getvalue()

                    person_id = None
                    if name != "Unknown":
                        person = session.query(RecognizedPerson).filter_by(name=name).first()
                        if person:
                            person_id = person.id

                    new_face = CapturedFace(
                        name=name,
                        capture_date=datetime.utcnow(),
                        image_data=image_data,
                        image_format='JPEG',
                        confidence=float(confidence),
                        recognized_person_id=person_id
                    )
                    session.add(new_face)
                    session.commit()
                    print(f"[INFO] Saved face {idx}: {name} (Confidence: {confidence:.2f})")
                    last_capture_time = time.time()  # Update last capture time
                except Exception as e:
                    session.rollback()
                    print(f"[ERROR] Failed to save face {idx}: {e}")

        # Draw rectangles and names for all detected faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Display frame
        cv2.imshow("Facial Recognition is Running", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

        fps.update()

finally:
    fps.stop()
    print("[INFO] Elapsed time: {:.2f}".format(fps.elapsed()))
    if fps._numFrames > 0:
        print("[INFO] Approx. FPS: {:.2f}".format(fps.fps()))
    cv2.destroyAllWindows()
    vs.stop()
    session.close()
