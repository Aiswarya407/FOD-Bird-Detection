from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Load Models
coco_model = YOLO('models/coco_model.pt')         # COCO-trained YOLOv8 model
material_model = YOLO('models/material_model.pt') # Custom-trained Material Detection YOLOv8 model

# Function to detect objects using COCO model
def detect_objects(frame):
    results = coco_model(frame)
    detected_objects = []
    
    for box in results[0].boxes:
        label = results[0].names[int(box.cls)]  # Object label
        if label in ["bird", "airplane", "debris"]:  # Focused objects
            x1, y1, x2, y2 = map(int, box.xyxy[0])   # Bounding box coordinates
            detected_object = frame[y1:y2, x1:x2]     # Crop detected region
            detected_objects.append((detected_object, (x1, y1, x2, y2), label))
    
    return detected_objects

# Function to classify materials using the custom model
def classify_materials(detected_objects, frame):
    for obj, coords, label in detected_objects:
        results = material_model(obj)
        material_label = results[0].names[int(results[0].boxes[0].cls)]

        # Draw bounding box and label
        cv2.rectangle(frame, (coords[0], coords[1]), (coords[2], coords[3]), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} ({material_label})", 
                    (coords[0], coords[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.8, (0, 255, 0), 2)
        
        # 🚨 Alert Logic
        if material_label in ["plastic", "metal", "concrete"]:
            print(f"🚨 ALERT: {label} with {material_label} detected on runway!")
    
    return frame

# Generator for streaming video
def generate_frames():
    cap = cv2.VideoCapture(0)  # Live Webcam Feed
    while True:
        success, frame = cap.read()
        if not success:
            break

        detected_objects = detect_objects(frame)        # Step 1: COCO Model Detection
        processed_frame = classify_materials(detected_objects, frame)  # Step 2: Custom Model Classification

        _, buffer = cv2.imencode('.jpg', processed_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
