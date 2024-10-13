import pygame


class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()

    def play_sound(self, sound_file):
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
