import pygame
from src.characters.my_sprite import MySprite
from src.resources.resource_manager import ResourceManager

class BossHealthBar(MySprite):
    def __init__(self):
        super().__init__()
        self.fixed_position = True
        self.health = 200
        self.max_health = 200
        
        # Create a simple rectangular health bar
        self.bar_width = 550
        self.bar_height = 10
        self.image = pygame.Surface((self.bar_width, self.bar_height))
        self.rect = self.image.get_rect()
        self.update(self.health)

    def update(self, health):
        self.health = health
        # Create background (empty health bar)
        self.image.fill((100, 0, 0))
        
        # Calculate health percentage and width
        health_percentage = max(0, min(self.health / self.max_health, 1))
        health_width = int(self.bar_width * health_percentage)
        
        # Draw health bar
        health_rect = pygame.Rect(0, 0, health_width, self.bar_height)
        pygame.draw.rect(self.image, (200, 0, 0), health_rect)
