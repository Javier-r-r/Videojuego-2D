import pygame
from pathlib import Path

class SoundManager:
    _instance = None
    _sounds = {}
    _MAX_CHANNELS = 8  # Canales 0-7 para efectos, 8 para música
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._volume = 0.5
            # Asegurar que hay suficientes canales para efectos y música
            total_channels = cls._MAX_CHANNELS + 1  # +1 para el canal de música
            pygame.mixer.set_num_channels(total_channels)
            # Usar solo los primeros 8 canales para efectos
            cls._instance._channels = [pygame.mixer.Channel(i) for i in range(cls._MAX_CHANNELS)]
            cls._instance._current_channel = 0
            cls._instance._load_sounds()
        return cls._instance
    
    def _load_sounds(self):
        """Precarga todos los efectos de sonido"""
        sound_files = {
            'shoot': 'shoot.wav',
            'pistol_shoot': 'pistol_shoot.wav',
            'rifle_shoot': 'rifle_shoot.wav',
            'shotgun_shoot': 'shotgun_shoot.wav',
            'hit': 'hurt.wav',
            'pickup': 'pickup.wav',
            'death': 'death.wav',
            'dagger': 'dagger.flac',
            'slime_attack': 'slime_attack.ogg'
        }
        
        for sound_name, file_name in sound_files.items():
            try:
                sound_path = Path('assets') / 'sounds' / file_name
                self._sounds[sound_name] = pygame.mixer.Sound(str(sound_path))
            except:
                print(f"Could not load sound: {file_name}")
    
    def play_sound(self, sound_name):
        """Reproduce un efecto de sonido en el siguiente canal disponible"""
        if sound_name in self._sounds:
            self._sounds[sound_name].set_volume(self._volume)
            # Usar el siguiente canal disponible
            self._channels[self._current_channel].play(self._sounds[sound_name])
            self._current_channel = (self._current_channel + 1) % self._MAX_CHANNELS
    
    def set_volume(self, volume):
        """Ajusta el volumen de los efectos (0.0 a 1.0)"""
        self._volume = max(0.0, min(1.0, volume))
        for sound in self._sounds.values():
            sound.set_volume(self._volume)
        for channel in self._channels:
            channel.set_volume(self._volume)
