import pygame
from pathlib import Path
from src.resources.resource_manager import ResourceManager

class LoadingScreen:
    def __init__(self):
        self.font_path = Path('assets') / 'fonts' / 'Cyberphont-2' / 'Cyberphont2.0.ttf'
        self.font = pygame.font.Font(self.font_path, 36)
        self.loading_sprite = ResourceManager.LoadImage('levels/Loading.png')
        self.sprite_rects = self._load_coordinates()
    
    def _load_coordinates(self):
        coords_data = ResourceManager.LoadCoordinatesFile('levels/coordLoading.txt')
        sprite_rects = []
        for line in coords_data.split('\n'):
            if line.strip():
                x, y, w, h = map(int, line.split())
                sprite_rects.append(pygame.Rect(x, y, w, h))
        return sprite_rects

    def show(self, screen, next_phase):
        start_time = pygame.time.get_ticks()
        frame = 0
        
        while pygame.time.get_ticks() - start_time < 2000:
            screen.fill((0, 0, 0))
            
            current_rect = self.sprite_rects[frame % len(self.sprite_rects)]
            frame_surface = self.loading_sprite.subsurface(current_rect)
            
            sprite_x = 1280//2 - current_rect.width//2
            sprite_y = 960//2 - current_rect.height//2
            screen.blit(frame_surface, (sprite_x, sprite_y))
            
            loading_text = self.font.render(f"Loading {next_phase}...", True, (255, 255, 255))
            loading_rect = loading_text.get_rect(center=(1280//2, 960//2 + 150))
            screen.blit(loading_text, loading_rect)
            
            pygame.display.flip()
            frame += 1
            pygame.time.wait(100)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
        return True
