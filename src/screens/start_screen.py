import pygame
from pathlib import Path
from src.resources.resource_manager import ResourceManager
from src.resources.music_manager import MusicManager

class StartScreen:
    def __init__(self):
        self.font_path = Path('assets') / 'fonts' / 'Cyberphont-2' / 'Cyberphont2.0.ttf'
        self.font = pygame.font.Font(self.font_path, 36)
        self.music_manager = MusicManager()
    
    def draw(self, screen):
        screen.fill((0, 0, 0))
        
        try:
            background_path = "start/overdue_screen.jpeg"
            background = ResourceManager.LoadImage(str(background_path))
            background = pygame.transform.scale(background, (1280, 960))
            screen.blit(background, (0, 0))
        except:
            pass
        
        title_text = self.font.render("Overdue", True, (255, 255, 255))
        start_text = self.font.render("Press enter to start", True, (255, 255, 255))
        
        title_rect = title_text.get_rect(center=(1280//2, 960 - 100))
        start_rect = start_text.get_rect(center=(1280//2, 960 - 50))
        
        screen.blit(title_text, title_rect)
        screen.blit(start_text, start_rect)
        pygame.display.flip()

    def play_music(self):
        self.music_manager.play_music('Amb_Loop-Extra_Strong.wav')

    def run(self, display):
        self.play_music()
        running = True
        while running:
            self.draw(display)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return True
