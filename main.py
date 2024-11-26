import cv2
import RPi.GPIO as GPIO
import time
import csv
import os
from app.faceDetector import FaceDetector
from app.eyesDetector import EyesDetector
from app.alarm import Alarm
from generar_clave import leer_clave
from paths import logs_path, sound_path, face_cascade_path, eye_cascade_path, checksum_path
import rsa
import hashlib

# GPIO setup
GPIO.setmode(GPIO.BCM)

# GPIO pins for buttons
BTN_POWER = 17
BTN_PAUSE = 27

# GPIO pins for LEDs
LED_RED = 22
LED_GREEN = 23
LED_YELLOW = 24

# GPIO pin for buzzer
BUZZER = 25

GPIO.setup(BTN_POWER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_PAUSE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_RED, GPIO.OUT)
GPIO.setup(LED_GREEN, GPIO.OUT)
GPIO.setup(LED_YELLOW, GPIO.OUT)
GPIO.setup(BUZZER, GPIO.OUT)

class SleepDetector:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.face_detector = FaceDetector(face_cascade_path)
        self.eyes_detector = EyesDetector(eye_cascade_path)
        self.alarma = Alarm(sound_path)
        self.last_detected_time = time.time()
        self.time_for_a_microsleep = 1
        self.detection_frequency = 3
        self.count = 0
        self.running = False
        self.paused = False
        self.logs_temira_csv = logs_path + 'logs_temira.csv'
        self.logs_temira_enc = logs_path + 'logs_temira_enc.csv'
        self.causa = "Off"
        GPIO.output(LED_RED, GPIO.LOW)
        GPIO.output(LED_GREEN, GPIO.LOW)
        GPIO.output(LED_YELLOW, GPIO.LOW)

    def run(self):
        try:
            while True:
                if GPIO.input(BTN_POWER) == GPIO.LOW:  # Toggle power
                    self.toggle_power()
                    time.sleep(0.5)  # Debounce delay

                if self.running:
                    if GPIO.input(BTN_PAUSE) == GPIO.LOW:  # Pause/Resume
                        self.toggle_pause()
                        time.sleep(0.5)  # Debounce delay

                    if not self.paused:
                        self.process_frame()
                else:
                    time.sleep(0.1)
        finally:
            self.cleanup()

    def toggle_power(self):
        if self.running:
            self.running = False
            self.causa = "Off"
            GPIO.output(LED_RED, GPIO.LOW)
            GPIO.output(LED_GREEN, GPIO.LOW)
            GPIO.output(LED_YELLOW, GPIO.LOW)
            self.guardar_logs()
            self.video.release()
            cv2.destroyAllWindows()
        else:
            self.running = True
            self.paused = False
            self.causa = "On"
            GPIO.output(LED_GREEN, GPIO.HIGH)

    def toggle_pause(self):
        if self.paused:
            self.paused = False
            self.causa = "Play"
            GPIO.output(LED_GREEN, GPIO.HIGH)
            GPIO.output(LED_YELLOW, GPIO.LOW)
        else:
            self.paused = True
            self.causa = "Pause"
            GPIO.output(LED_GREEN, GPIO.LOW)
            GPIO.output(LED_YELLOW, GPIO.HIGH)

    def process_frame(self):
        _, frame = self.video.read()
        self.count += 1
        if self.count % self.detection_frequency == 0:
            frame = self.format_image(frame)
            best_face = self.face_detector.get_best_face(frame)
            if best_face:
                roi_face = self.face_detector.get_roi_face(frame, best_face)
                eyes = self.eyes_detector.get_best_pair_of_eyes(roi_face)
                if eyes:
                    self.last_detected_time = time.time()
                    GPIO.output(LED_RED, GPIO.LOW)
                    GPIO.output(LED_GREEN, GPIO.HIGH)
                else:
                    self.trigger_alarm("Microsueño")
            else:
                self.trigger_alarm("Distracción")

            if time.time() - self.last_detected_time >= self.time_for_a_microsleep:
                self.trigger_alarm("Microsueño")

    def trigger_alarm(self, cause):
        self.causa = cause
        GPIO.output(LED_RED, GPIO.HIGH)
        GPIO.output(LED_GREEN, GPIO.LOW)
        GPIO.output(BUZZER, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(BUZZER, GPIO.LOW)

    def guardar_logs(self):
            # Verificar si el archivo existe
            if not os.path.exists(self.logs_temira_csv):
                # Si no existe, crear el archivo y escribir el encabezado
                with open(self.logs_temira_csv, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["inicio", "fin", "causa"])
            with open(self.logs_temira_csv, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(self.registros)
            clave_publica = leer_clave('publica')
            checksum = self.calcular_checksum(self.logs_temira_csv)
            self.encriptar_archivo(clave_publica, checksum)
            self.guardar_checksum(checksum)

    def encriptar_archivo(self, clave_publica, checksum):
        TAM_BLOQUE = 245  # Tamaño del bloque en bytes

        with open(self.logs_temira_csv, 'rb') as archivo_csv:
            with open(self.logs_temira_enc, 'wb') as archivo_encriptado:
                # Escribir el checksum como metadatos en la cabecera del archivo encriptado
                archivo_encriptado.write(f"checksum:{checksum}\n".encode())

                while True:
                    bloque = archivo_csv.read(TAM_BLOQUE)
                    if len(bloque) == 0:
                        break  # Se llegó al final del archivo

                    contenido_encriptado = rsa.encrypt(bloque, clave_publica)
                    archivo_encriptado.write(contenido_encriptado)

    def calcular_checksum(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()[:8] 

    def guardar_checksum(self, checksum):
        checksum_csv = checksum_path + 'checksum.csv'
        # Verificar si el archivo existe
        if not os.path.exists(checksum_csv):
            # Si no existe, crear el archivo y escribir el encabezado
            with open(checksum_csv, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["fecha", "checksum"])
        # Agregar el registro al archivo
        with open(checksum_csv, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([time.strftime("%d-%m-%Y %H:%M:%S"), checksum])

    def format_image(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.equalizeHist(gray_frame)

    def cleanup(self):
        GPIO.output(LED_RED, GPIO.LOW)
        GPIO.output(LED_GREEN, GPIO.LOW)
        GPIO.output(LED_YELLOW, GPIO.LOW)
        GPIO.output(BUZZER, GPIO.LOW)
        GPIO.cleanup()
        self.video.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    detector = SleepDetector()
    detector.run()