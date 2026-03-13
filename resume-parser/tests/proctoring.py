import cv2
import numpy as np

class ProctorMonitor:
    def __init__(self):
        # Use Haar Cascade for face detection (built into OpenCV)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.profile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_profileface.xml'
        )
        
    def analyze_frame(self, frame_data):
        """Analyze frame for violations"""
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect frontal faces - More lenient settings
        frontal_faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=7, minSize=(50, 50)
        )
        
        # Detect profile faces (head turned) - More lenient settings
        profile_faces = self.profile_cascade.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=7, minSize=(50, 50)
        )
        
        violations = {
            'face_count': len(frontal_faces),
            'head_turned': len(profile_faces) > 0,
            'head_angle': len(profile_faces)
        }
        
        return violations
    
    def cleanup(self):
        pass
