import pygame
from src.resources.resource_manager import ResourceManager

# Definir tipos de items como constantes
ITEM_KEY = "key"
ITEM_COIN = "coin"

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_image, item_coord):
        super().__init__()
        # Cargar el spritesheet y las coordenadas
        self.spritesheet = ResourceManager.LoadImage(item_image)
        coord_data = ResourceManager.LoadCoordinatesFile(item_coord)
        
        # Procesar las coordenadas y crear los frames
        self.frames = []
        for line in coord_data.splitlines():
            if line.strip():
                coords = list(map(int, line.split()))
                subsurface = self.spritesheet.subsurface((coords[0], coords[1], coords[2], coords[3]))
                self.frames.append(subsurface)
        
        self.current_frame = 0
        self.animation_time = pygame.time.get_ticks()
        self.animation_delay = 100  # Milisegundos entre frames
        self.image = self.frames[self.current_frame]
        
        self.rect = self.image.get_rect()
        self.position = (x, y)  # World position
        self.rect.topleft = (x, y)

        # Determinar el tipo de item basado en el nombre de la imagen
        if "key" in item_image.lower():
            self.item_type = ITEM_KEY
        elif "coin" in item_image.lower():
            self.item_type = ITEM_COIN
        else:
            self.item_type = "unknown"

    def set_screen_position(self, scroll):
        # Update screen position based on world position and scroll
        self.rect.x = self.position[0] - scroll[0]
        self.rect.y = self.position[1] - scroll[1]

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_time >= self.animation_delay:
            self.animation_time = current_time
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def get_item_type(self):
        return self.item_type