import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")
import time
import cv2
import numpy as np
import mediapipe as mp

from Utils import get_face_area
from Eye_Dector_Module import EyeDetector as EyeDet
from Pose_Estimation_Module import HeadPoseEstimator as HeadPoseEst
from Attention_Scorer_Module import AttentionScorer as AttScorer

# Create FaceMesh ONCE at module level to avoid repeated TFLite model loading
detector = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    refine_landmarks=True
)

eyes_closed_time_global = 0

# Updated main to accept a frame and return (frame, description)
def main(frame, args=None):
    global eyes_closed_time_global
    class Args:
        show_eye_proc = False
        show_axis = True
        verbose = False
        ear_thresh = 0.15
        ear_time_thresh = 0.7
        gaze_thresh = 0.015
        gaze_time_thresh = 2
        pitch_thresh = 20
        yaw_thresh = 20
        roll_thresh = 20
        pose_time_thresh = 2.5

    if args is None:
        args = Args()
    else:
        for k, v in args.items():
            setattr(args, k, v)

    if not cv2.useOptimized():
        try:
            cv2.setUseOptimized(True)
        except:
            print("OpenCV optimization could not be set to True, the script may be slower than expected")

    Eye_det = EyeDet(show_processing=args.show_eye_proc)
    Head_pose = HeadPoseEst(show_axis=args.show_axis)

    t0 = time.perf_counter()
    Scorer = AttScorer(
        t_now=t0,
        ear_thresh=args.ear_thresh,
        gaze_time_thresh=args.gaze_time_thresh,
        roll_thresh=args.roll_thresh,
        pitch_thresh=args.pitch_thresh,
        yaw_thresh=args.yaw_thresh,
        ear_time_thresh=args.ear_time_thresh,
        gaze_thresh=args.gaze_thresh,
        pose_time_thresh=args.pose_time_thresh,
        verbose=args.verbose
    )

    # Processing single frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_size = frame.shape[1], frame.shape[0]
    gray = np.expand_dims(cv2.bilateralFilter(gray, 5, 10, 10), axis=2)
    gray = np.concatenate([gray, gray, gray], axis=2)

    lms = detector.process(gray).multi_face_landmarks

    if lms:
        landmarks = _get_landmarks(lms)

        Eye_det.show_eye_keypoints(color_frame=frame, landmarks=landmarks, frame_size=frame_size)

        ear = Eye_det.get_EAR(frame=gray, landmarks=landmarks)
        tired, perclos_score = Scorer.get_PERCLOS(time.perf_counter(), 10, ear)
        gaze = Eye_det.get_Gaze_Score(frame=gray, landmarks=landmarks, frame_size=frame_size)

        frame_det, roll, pitch, yaw = Head_pose.get_pose(
            frame=frame, landmarks=landmarks, frame_size=frame_size)

        asleep, looking_away, distracted = Scorer.eval_scores(
            t_now=time.perf_counter(),
            ear_score=ear,
            gaze_score=gaze,
            head_roll=roll,
            head_pitch=pitch,
            head_yaw=yaw
        )

        if frame_det is not None:
            frame = frame_det

        # Eyes closed logic
        if ear <= args.ear_thresh:
            eyes_closed_time_global += 1 / 10
        else:
            eyes_closed_time_global = 0

        if eyes_closed_time_global >= args.ear_time_thresh or asleep:
            return frame, "ASLEEP!"
        elif distracted:
            return frame, "DISTRACTED!"
        elif not asleep and not distracted and abs(pitch) <= args.pitch_thresh and abs(yaw) <= args.yaw_thresh and abs(roll) <= args.roll_thresh:
            return frame, "DRIVING PROPERLY!"
        else:
            return frame, "DISTRACTED!"

    return None

def _get_landmarks(lms):
    surface = 0
    biggest_face = None
    for lms0 in lms:
        landmarks = [np.array([point.x, point.y, point.z]) for point in lms0.landmark]
        landmarks = np.array(landmarks)
        landmarks[landmarks[:, 0] < 0., 0] = 0.
        landmarks[landmarks[:, 0] > 1., 0] = 1.
        landmarks[landmarks[:, 1] < 0., 1] = 0.
        landmarks[landmarks[:, 1] > 1., 1] = 1.

        dx = landmarks[:, 0].max() - landmarks[:, 0].min()
        dy = landmarks[:, 1].max() - landmarks[:, 1].min()
        new_surface = dx * dy
        if new_surface > surface:
            biggest_face = landmarks

    return biggest_face