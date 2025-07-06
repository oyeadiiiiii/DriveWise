from flask import Flask, Response, render_template, jsonify, request
import cv2
import queue
import numpy as np
import time

from act import main as act_main
from FaceRecog import facerecog as facerecog_main, register_driver

app = Flask(__name__)

# Store latest frame from browser
latest_frame = None
frame_queue = queue.Queue(maxsize=3)  # for future use if needed

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_frame', methods=['POST'])
def upload_frame():
    global latest_frame
    try:
        if 'frame' not in request.files:
            return jsonify(success=False, error='No frame part'), 400

        file = request.files['frame']
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if frame is None:
            return jsonify(success=False, error='Invalid image'), 400

        latest_frame = frame  # ✅ Save the latest browser webcam frame

        if not frame_queue.full():
            frame_queue.put(frame)

        return jsonify(success=True)
    except Exception as e:
        print(f"Error in upload_frame: {e}")
        return jsonify(success=False, error=str(e)), 500

def get_current_frame():
    global latest_frame
    return latest_frame.copy() if latest_frame is not None else None

@app.route('/state_feed')
def state_feed():
    def generate():
        try:
            while True:
                frame = get_current_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                result = act_main(frame)
                if result is not None:
                    _, state = result
                    yield f"data: {state}\n\n"
                time.sleep(0.2)  # Update state ~5 FPS
        except Exception as e:
            print(f"Error in state_feed: {e}")
            yield f"data: Error: {e}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/get_driver_name')
def get_driver_name():
    try:
        frame = get_current_frame()
        if frame is None:
            return jsonify(driverName=None)
        name = facerecog_main(frame)
        return jsonify(driverName=name if name else None)
    except Exception as e:
        print(f"Error in get_driver_name: {e}")
        return jsonify(driverName=None)

register_progress = {"clicks_left": 50}

@app.route('/register_driver', methods=['POST'])
def register_driver_route():
    global register_progress
    try:
        data = request.get_json()
        name = data.get('name')
        progress = {"current": 0}

        def progress_callback(val):
            progress["current"] = val
            register_progress["clicks_left"] = 50 - val

        register_driver(get_current_frame, name, progress_callback=progress_callback)
        register_progress["clicks_left"] = 0
        return jsonify(success=True, clicks_left=0)
    except Exception as e:
        print(f"Error registering driver: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/register_progress')
def get_register_progress():
    return jsonify(clicks_left=register_progress["clicks_left"])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
