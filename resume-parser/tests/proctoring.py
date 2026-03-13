import cv2
import numpy as np

class ProctorMonitor:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def analyze_frame(self, frame_data):
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            return {'face_count': 1, 'head_turned': False}

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=6,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        face_count = len(faces)

        # Head turned = no frontal face detected at all
        # We require face to be missing for 1 consecutive check (handled by counter in view)
        head_turned = face_count == 0

        return {
            'face_count': face_count,
            'head_turned': head_turned,
        }

    def cleanup(self):
        pass
