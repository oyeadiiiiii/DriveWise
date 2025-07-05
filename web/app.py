from flask import Flask, Response, render_template, jsonify, request
import cv2
import threading
import queue
import numpy as np
from os import path
import time

from act import main as act_main
from FaceRecog import facerecog as facerecog_main, register_driver

app = Flask(__name__)

# Centralized camera frame queue
frame_queue = queue.Queue(maxsize=3)  # Reduce queue size to save memory
camera_thread_started = False

def camera_reader():
    print("Starting camera_reader thread")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera could not be opened!")
        return
    time.sleep(1)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from camera.")
                time.sleep(0.1)
                continue
            if not frame_queue.full():
                frame_queue.put(frame)
            time.sleep(0.1)  # Limit to ~10 FPS to reduce CPU usage
    finally:
        cap.release()

def get_latest_frame():
    frame = None
    while not frame_queue.empty():
        frame = frame_queue.get()
    if frame is None:
        try:
            frame = frame_queue.get(timeout=2)
        except queue.Empty:
            print("No frame available from camera.")
            return None
    return frame

def gen_frames_act():
    while True:
        frame = get_latest_frame()
        if frame is None:
            time.sleep(0.05)  # Sleep to avoid busy loop
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            time.sleep(0.05)
            continue
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.05)  # Limit to ~20 FPS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed_act')
def video_feed_act():
    try:
        return Response(gen_frames_act(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except Exception as e:
        print(f"Error in video_feed_act: {e}")
        return str(e), 500

@app.route('/state_feed')
def state_feed():
    def generate():
        try:
            while True:
                frame = get_latest_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                result = act_main(frame)
                if result is not None:
                    _, state = result
                    yield f"data: {state}\n\n"
                time.sleep(0.2)  # Limit state updates to 5 FPS
        except Exception as e:
            print(f"Error in state_feed: {e}")
            yield f"data: Error: {e}\n\n"

    return Response(generate(), mimetype='text/event-stream')
@app.route('/get_driver_name')
def get_driver_name():
    try:
        frame = get_latest_frame()
        if frame is None:
            return jsonify(driverName=None)
        name = facerecog_main(frame)
        if name:
            return jsonify(driverName=name)
        else:
            return jsonify(driverName=None)
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

        register_driver(get_latest_frame, name, progress_callback=progress_callback)
        register_progress["clicks_left"] = 0
        return jsonify(success=True, clicks_left=0)
    except Exception as e:
        print(f"Error registering driver: {e}")
        return jsonify(success=False, error=str(e)), 500

@app.route('/register_progress')
def get_register_progress():
    return jsonify(clicks_left=register_progress["clicks_left"])

def start_camera_thread():
    global camera_thread_started
    if not camera_thread_started:
        threading.Thread(target=camera_reader, daemon=True).start()
        camera_thread_started = True

if __name__ == '__main__':
    start_camera_thread()
    app.run(debug=False, use_reloader=False)