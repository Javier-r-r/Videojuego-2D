from typing import List, Callable, Optional
import pygame
from src.screens.loading_screen import LoadingScreen
from src.screens.shop_screen import ShopScreen
from src.resources.music_manager import MusicManager

class Director:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Director, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        self.level1_fases = []
        self.level2_fases = []
        self.current_level = 1
        self.current_fase_index = 0
        self.current_fase = None
        self.loading_screen = LoadingScreen()
        self.music_manager = MusicManager()
        
    def set_fases(self, level1: List, level2: List):
        self.level1_fases = level1
        self.level2_fases = level2
        self.current_fase = self.level1_fases[0]
        if callable(self.current_fase):
            self.current_fase = self.current_fase()
    
    def change_fase(self, display) -> bool:
        next_fase_index = self.current_fase_index + 1
        current_fases = self.level1_fases if self.current_level == 1 else self.level2_fases
        
        if next_fase_index < len(current_fases):
            self.loading_screen.show(display, f"Fase {(self.current_level-1)*10 + 11 + next_fase_index}")
            
            if callable(current_fases[next_fase_index]):
                current_fases[next_fase_index] = current_fases[next_fase_index]()
            
            self.current_fase = current_fases[next_fase_index]
            self.current_fase_index = next_fase_index
            
            if hasattr(self.current_fase, '__class__') and self.current_fase.__class__.__name__ == 'Fase12':
                self.music_manager.play_music('Action.wav')
            return True
            
        else:
            shop = ShopScreen(self.current_fase.player1)
            player, should_continue = shop.run(display)
            
            if should_continue:
                if self.current_level == 1:
                    player.notify_health_observers()
                    self.current_level = 2
                    self.current_fase_index = 0
                    self.current_fase = self.level2_fases[0]
                    if callable(self.current_fase):
                        self.current_fase = self.current_fase()
                        self.current_fase.player1 = player
                    return True
            return False
