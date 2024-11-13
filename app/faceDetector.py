import cv2
import numpy as np

class FaceDetector:
    def __init__(self, face_cascade_path):
        self.face_cascade = cv2.CascadeClassifier(face_cascade_path)

    def get_best_face(self, image):
        self.faces = self.face_cascade.detectMultiScale(image, scaleFactor=1.05, minNeighbors=7)
        if len(self.faces) == 0:
            return None
        elif len(self.faces) == 1:
            return self.faces[0]
        else:
            # return the face with the largest area
            areas = np.prod(self.faces[:, 2:], axis=1)
            max_idx = np.argmax(areas)
            return self.faces[max_idx]
    
    def get_roi_face(self, image, face):
        if face is None:
            return None
        else:
            (x, y, w, h) = face
            roi_y = int(y + 0.25 * h) # ajustar la coordenada y de la región de interés
            return image[roi_y:y+h, x:x+w]
            # return image[y:y+h, x:x+w]
