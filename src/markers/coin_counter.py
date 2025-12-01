import pygame
from src.patterns.Observer import Observer
from src.characters.my_sprite import MySprite
from src.resources.resource_manager import ResourceManager

class CoinCounter(MySprite, Observer):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font(None, 24)
        self.coins = 0
        self.position = (0, 0)
        
        # Load coin sprite
        self.image = ResourceManager.LoadImage('items/CoinCounter.png')
         

    def update(self, Subject):
        self.coins = Subject.coins_collected
        # Create a surface wide enough for both coin image and text
        text_surface = self.font.render(f"x{self.coins}", True, (255, 255, 255))
        combined_width = self.image.get_width() + text_surface.get_width() + 5  # 5 pixels spacing
        combined_height = max(self.image.get_height(), text_surface.get_height())
        
        self.image = pygame.Surface((combined_width, combined_height), pygame.SRCALPHA)
        
        # Draw coin first, then text
        self.image.blit(self.image, (0, 0))
        self.image.blit(text_surface, (self.image.get_width() + 5, 0))
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.position

    def set_position(self, pos):
        self.position = pos
        if hasattr(self, 'rect'):
            self.rect.topleft = pos

    def set_screen_position(self, scroll):
        # UI elements don't scroll
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)
