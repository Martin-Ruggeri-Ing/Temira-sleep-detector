import cv2
import numpy as np

class EyesDetector:
    def __init__(self, eye_cascade_path):
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
    
    def get_best_pair_of_eyes(self, roi_face):
        # Detectar los ojos en la región de interés usando el clasificador de Haar cascade
        eyes = self.eye_cascade.detectMultiScale(roi_face, scaleFactor=1.05, minNeighbors=7)
        if len(eyes) == 2:
            return eyes
        elif len(eyes) > 2:
            # Ordenar los ojos por tamaño (área)
            sorted_eyes = np.array(sorted(eyes, key=lambda eye: eye[2] * eye[3], reverse=True))
            # Seleccionar los dos ojos más grandes
            best_eyes = sorted_eyes[:2, :]
            return best_eyes
        # Si no se detectaron dos ojos, devolver None
        else: # len(eyes) < 1
            return None
