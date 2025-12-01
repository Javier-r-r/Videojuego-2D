import pygame
from pathlib import Path

class MusicManager:
    _instance = None
    _MUSIC_CHANNEL = 8  # Último canal reservado para música
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current_song = None
            cls._instance._volume = 0.5
            # Asegurar que hay suficientes canales disponibles
            if pygame.mixer.get_num_channels() <= cls._MUSIC_CHANNEL:
                pygame.mixer.set_num_channels(cls._MUSIC_CHANNEL + 1)
            cls._instance._music_channel = pygame.mixer.Channel(cls._MUSIC_CHANNEL)
        return cls._instance

    def play_music(self, song_name):
        if self._current_song != song_name:
            try:
                music_path = Path('assets') / 'music' / song_name
                sound = pygame.mixer.Sound(str(music_path))
                sound.set_volume(self._volume)
                self._music_channel.play(sound, loops=-1)
                self._current_song = song_name
            except:
                print(f"Could not load music: {song_name}")
                
    def stop_music(self):
        self._music_channel.stop()
        self._current_song = None
        
    def set_volume(self, volume):
        self._volume = volume
        if self._music_channel:
            self._music_channel.set_volume(volume)
            # También actualizar el volumen del sonido actual si existe
            if self._music_channel.get_sound():
                self._music_channel.get_sound().set_volume(volume)
