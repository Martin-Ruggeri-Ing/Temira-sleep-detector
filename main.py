import cv2
from app.faceDetector import FaceDetector
from app.eyesDetector import EyesDetector
from app.alarm import Alarm
from generar_clave import leer_clave
import time
import csv
import os
from paths import logs_path, sound_path, face_cascade_path, eye_cascade_path
import tkinter as tk
from PIL import Image, ImageTk
import rsa


class SleepDetector:
    def __init__(self):
        # Se crea un objeto video que captura el video de la cámara del dispositivo
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        # Se crea un objeto detector de rostros
        self.face_detector = FaceDetector(face_cascade_path)
        # Se crea un objeto detector de ojos
        self.eyes_detector = EyesDetector(eye_cascade_path)
        # Se crea un objeto alarma
        self.alarma = Alarm(sound_path)
        # Se inicializan las variables
        self.best_face = None
        self.eyes = None
        self.last_detected_time = time.time()
        self.time_for_a_microsleep = 1
        self.detection_frequency = 3
        self.count = 0
        self.registros = []
        self.inicio = time.strftime("%d-%m-%Y %H:%M:%S")
        self.causa = "On"
        self.registros.append([self.inicio, self.inicio, self.causa])
        self.logs_temira_csv = logs_path + 'logs_temira.csv'
        # Se crea una ventana de Tkinter
        self.root = tk.Tk()
        self.root.title("Detector de Somnolencia")
        # Se crea un lienzo de Tkinter para mostrar la imagen del frame
        self.canvas = tk.Canvas(self.root, width=640, height=480)
        self.canvas.pack()
        # Crear botón para apagar la aplicación
        self.btn_apagar = tk.Button(self.root, text="Apagar", command=self.apagar_app)
        self.btn_apagar.pack()
        # Crear botón para pausar/reanudar la aplicación
        self.btn_pause = tk.Button(self.root, text="Pause", command=self.pausar_reanudar_app)
        self.btn_pause.pack()
        # Variables para controlar la ejecución del bucle
        self.running = True
        self.paused = False

    def run(self):
        # Bucle principal del programa
        while self.running:
            # Se verifica si la aplicación está pausada
            if self.paused:
                self.root.update()  # Actualizar la ventana de Tkinter
                time.sleep(0.1)
                continue
            # Se lee un frame del video
            _, frame = self.video.read()
            # Se incrementa el contador de frames
            self.count += 1
            # Se comprueba si ha llegado el momento de realizar una detección
            if self.count % self.detection_frequency == 0:
                # formatear el frame
                frame = self.format_image(frame)
                # Se obtiene el mejor rostro de la imagen
                self.best_face = self.face_detector.get_best_face(frame)
                # Si se ha detectado un rostro
                if self.best_face is not None:
                    # Se obtiene la región de interés del rostro
                    roi_face = self.face_detector.get_roi_face(frame, self.best_face)
                    # Se obtiene el par de ojos más adecuado para la región de interés
                    self.eyes = self.eyes_detector.get_best_pair_of_eyes(roi_face)
                    # Si se han detectado los ojos
                    if self.eyes is not None:
                        # Se actualiza el tiempo de la última detección
                        self.last_detected_time = time.time()
                        # Se dibuja el detector en el frame
                        self.draw_detector(frame)
                        if self.alarma.activa:
                            # Se detiene la alarma
                            self.alarma.detener_alarma()
                            # Agregar el registro al array
                            self.registros.append([self.inicio, time.strftime("%d-%m-%Y %H:%M:%S"), self.causa_alarma])
                    else:
                        self.causa = "Microsueño"
                else:
                    self.causa = "Distraccion"
                # si ha pasado el tiempo suficiente para ser un microsueño
                if time.time() - self.last_detected_time >= self.time_for_a_microsleep and not self.alarma.activa:
                    # Se inicia la alarma
                    self.alarma.iniciar_alarma()
                    self.inicio = time.strftime("%d-%m-%Y %H:%M:%S")
                    self.causa_alarma = self.causa
                # Se muestra el frame en la ventana de Tkinter
                self.show_frame(frame)

    def guardar_logs(self):
        # Verificar si el archivo existe
        if not os.path.exists(self.logs_temira_csv):
            # Si no existe, crear el archivo y escribir el encabezado
            with open(self.logs_temira_csv, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["inicio", "fin", "causa"])
        with open(self.logs_temira_csv, "a", newline="") as file:
            writer = csv.writer(file)
            for registro in self.registros:
                writer.writerow(registro)
        clave_publica = leer_clave('publica')
        self.encriptar_archivo(clave_publica)
    
    def encriptar_archivo(self, clave_publica):
        TAM_BLOQUE = 200  # Tamaño del bloque en bytes
        encriptado_exitoso = False

        with open(self.logs_temira_csv, 'rb') as archivo_csv:
            with open('logs/logs_enc.csv', 'wb') as archivo_encriptado:
                while True:
                    bloque = archivo_csv.read(TAM_BLOQUE)
                    if len(bloque) == 0:
                        break  # Se llegó al final del archivo

                    contenido_encriptado = rsa.encrypt(bloque, clave_publica)
                    archivo_encriptado.write(contenido_encriptado)
                encriptado_exitoso = True

        if encriptado_exitoso:
            os.remove(self.logs_temira_csv)

    def format_image(self, frame):
        # Se convierte el frame a escala de grises
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # se mejora el contraste de la imagen
        gray_frame = cv2.equalizeHist(gray_frame)
        return gray_frame

    def draw_detector(self, image):
        if self.best_face is not None:
            (x, y, w, h) = self.best_face
            cv2.rectangle(image, (x, y), (x+w, y+h), 255, 2)
            if self.eyes is not None:
                for (ex, ey, ew, eh) in self.eyes:
                    cv2.rectangle(image, (x+ex, y+ey+h//4), (x+ex+ew, y+ey+eh+h//4), 255, 2)

    def show_frame(self, frame):
        # Convierte el frame de OpenCV a un objeto Image de PIL 
        image = Image.fromarray(frame, "L")
        # Convierte el objeto Image de PIL a un objeto PhotoImage de Tkinter
        photo = ImageTk.PhotoImage(image)
        # Actualiza el lienzo de Tkinter con la nueva imagen
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        # Actualiza la ventana de Tkinter
        self.root.update()
    
    def pausar_reanudar_app(self):
            if self.paused:
                self.paused = False
                self.btn_pause.config(text="Pause")
                self.registros.append([time.strftime("%d-%m-%Y %H:%M:%S"), time.strftime("%d-%m-%Y %H:%M:%S"), "play"])
            else:
                if self.alarma.activa:
                    # Se detiene la alarma
                    self.alarma.detener_alarma()
                self.paused = True
                self.btn_pause.config(text="Play")
                self.registros.append([time.strftime("%d-%m-%Y %H:%M:%S"), time.strftime("%d-%m-%Y %H:%M:%S"), "pause"])

    def apagar_app(self):
        # Detener la ejecución del bucle
        self.running = False
        # Liberar el objeto video y cerrar la ventana de Tkinter
        self.video.release()
        cv2.destroyAllWindows()
        # si el ultimo registro es "pause" agregar registro "play"
        if self.registros[-1][2] == "pause":
            self.causa = "play"
            self.registros.append([time.strftime("%d-%m-%Y %H:%M:%S"), time.strftime("%d-%m-%Y %H:%M:%S"), self.causa])
        # Se guarda el registro de la última vez que se ejecutó la app
        self.causa = "Off"
        self.registros.append([time.strftime("%d-%m-%Y %H:%M:%S"), time.strftime("%d-%m-%Y %H:%M:%S"), self.causa])
        # Guardar el los registros en el archivo CSV
        self.guardar_logs()
        self.root.destroy()


if __name__ == '__main__':
    detector = SleepDetector()
    detector.run()