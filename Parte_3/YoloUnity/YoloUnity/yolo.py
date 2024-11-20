import cv2
from ultralytics import YOLO
import numpy as np
from flask import Flask, jsonify

# Initialize Flask app
app = Flask(__name__)

# YOLO model setup
model = YOLO("yolov8m.pt")

# Global variable to store the latest detection
latest_detection = None

def process_frame(frame):
    global latest_detection
    results = model(frame, device="mps")
    result = results[0]

    # Use bboxes and classes to identify objects
    bboxes = np.array(result.boxes.xyxy.cpu(), dtype="int")
    classes = np.array(result.boxes.cls.cpu(), dtype="int")

    for cls, bbox in zip(classes, bboxes):
        (x, y, x2, y2) = bbox
        # Calculate center of the bounding box
        center_x = (x + x2) // 2
        center_y = (y + y2) // 2

        # If the object is "in front" of the robot, store detection
        if 300 < center_x < 400 and 200 < center_y < 300:  # Adjust thresholds as needed
            latest_detection = {
                "class": int(cls),
                "center_x": center_x,
                "center_y": center_y,
                "bbox": [int(x), int(y), int(x2), int(y2)]
            }
            break
    else:
        latest_detection = None  # No relevant object detected

# Flask route to get the latest detection
@app.route('/get_detection', methods=['GET'])
def get_detection():
    if latest_detection:
        return jsonify(latest_detection)
    else:
        return jsonify({"message": "No object detected"}), 204

if __name__ == "__main__":
    cap = cv2.VideoCapture("../../assets/aerial-drone.mp4")

    while True:
        ret, frame = cap.read()

        # If there are no more frames
        if not ret:
            break

        process_frame(frame)

        # Display the frame with YOLO annotations
        cv2.imshow("YOLO Detection", frame)
        key = cv2.waitKey(1)

        # Key to break the simulation by pressing "esc"
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

    # Start the Flask server
    app.run(host="127.0.0.1", port=5000)
