import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import os

def register_driver(frame_getter, name, progress_callback=None):
    classifier = cv2.CascadeClassifier("web/haarcascade_frontalface_default.xml")
    count = 50
    face_list = []

    while count > 0:
        frame = frame_getter()
        if frame is None:
            continue
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = classifier.detectMultiScale(gray)
        if len(faces) == 1:
            x, y, w, h = faces[0]
            if w > 100 and h > 100:
                face_img = gray[y:y + h, x:x + w]
                face_img = cv2.resize(face_img, (100, 100))
                face_list.append(face_img.flatten())
                count -= 1
                if progress_callback:
                    progress_callback(50 - count)
                if count <= 0:
                    break

    face_list = np.array(face_list)
    name_list = np.full((len(face_list), 1), name)
    total = np.hstack([name_list, face_list])
    if os.path.exists("faces.npy"):
        existing_data = np.load("faces.npy", allow_pickle=True)
        data = np.vstack([existing_data, total])
    else:
        data = total
    np.save("faces.npy", data)
    return True

def facerecog(frame):
    try:
        # Load the saved faces
        if not os.path.exists("faces.npy"):
            print("faces.npy not found")
            return None
        
        data = np.load("faces.npy", allow_pickle=True)
        if data.size == 0:
            print("faces.npy is empty")
            return None

        X = data[:, 1:].astype(int)
        y = data[:, 0]

        model = KNeighborsClassifier(n_neighbors=4)
        model.fit(X, y)

        # Load Haar cascade
        classifier = cv2.CascadeClassifier("web/haarcascade_frontalface_default.xml")

        predicted_name = None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = classifier.detectMultiScale(gray)

        if len(faces) > 0:
            x, y, w, h = faces[0]
            if w > 50 and h > 50:
                face_img = gray[y:y + h, x:x + w]
                face_img = cv2.resize(face_img, (100, 100))

                flat = face_img.flatten()
                res = model.predict([flat])
                predicted_name = str(res[0])

        return predicted_name

    except Exception as e:
        print(f"An error occurred in facerecog(): {e}")
        return None
