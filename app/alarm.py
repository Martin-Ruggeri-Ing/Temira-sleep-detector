import pygame.mixer

class Alarm:
    def __init__(self, sound_path):
        pygame.mixer.init()
        self.sonido = sound_path
        self.activa = False

    def iniciar_alarma(self):
        if not self.activa:
            self.activa = True
            pygame.mixer.music.load(self.sonido)
            pygame.mixer.music.play(loops=-1)

    def detener_alarma(self):
        if self.activa:
            self.activa = False
            pygame.mixer.music.stop()
