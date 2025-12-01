import pygame
from pytmx.util_pygame import load_pygame
from os.path import join, abspath, dirname, normpath


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos , surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
    

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos , surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        

class TileMap:
    def __init__(self, level_folder, tmx_file):
        
        # Construir la ruta completa al archivo .tmx
        tmx_path = join("assets", "levels", "tmx", level_folder, tmx_file)
        
        # Cargar el archivo .tmx
        self.tmx_data = load_pygame(tmx_path)
        self.tile_size = self.tmx_data.tilewidth
        self.map_size = (
            self.tmx_data.width * self.tile_size + 2000,
            self.tmx_data.height * self.tile_size + 2000
        )
        self.rect = pygame.Rect(0, 0, *self.map_size)
        # Add display rect for scroll handling
        self.display_rect = pygame.Rect(0, 0, *self.map_size)
        self.scroll = [0, 0]
    
    
    def load_layers(self, group):
        """Carga todas las capas en un grupo de sprites"""
        for layer in self.tmx_data.visible_layers:
            for x, y, surf in layer.tiles():
                pos = (x * self.tile_size, y * self.tile_size)
                Sprite(pos, surf, group)
    
    
    def load_layer_by_name(self, layer_name, group):
        """Carga una capa específica en un grupo de sprites"""
        try:
            layer = self.tmx_data.get_layer_by_name(layer_name)
            
            # Si es una capa de tiles
            if hasattr(layer, 'tiles'):
                for x, y, tile in layer.tiles():
                    if tile:  # Asegurarse de que el tile no sea None
                        Sprite(
                            (x * self.tile_size, y * self.tile_size),
                            tile,  
                            group
                        )
            
            # Si es una capa de objetos
            else:
                for obj in layer:
                    if obj.image:  # Verificar si el objeto tiene una imagen
                        Sprite(
                            (obj.x, obj.y),
                            obj.image,  # Usar obj.image para capas de objetos
                            group
                        )
        except ValueError as e:
            print(f"Error al cargar la capa '{layer_name}': {e}")
            
            
    def draw(self, screen):
        """Dibuja el mapa en la pantalla"""
        if hasattr(self, 'tmx_data'):
            # Aplicar scroll al dibujar
            for layer in self.tmx_data.visible_layers:
                for x, y, surf in layer.tiles():
                    screen_x = x * self.tile_size - self.scroll[0]
                    screen_y = y * self.tile_size - self.scroll[1]
                    screen.blit(surf, (screen_x, screen_y))
        elif hasattr(self, 'tiles'):
            # Dibujar capas de .tmj
            for layer in self.tiles:
                for y, row in enumerate(layer):
                    for x, tile in enumerate(row):
                        if tile:
                            screen_x = x * self.tile_size
                            screen_y = y * self.tile_size
                            screen.blit(tile, (screen_x, screen_y))
                            
    def update(self, scroll):
        """Updates the tilemap position based on scroll values"""
        self.scroll = scroll
        # Update both rect and display_rect based on scroll
        self.display_rect.x = -scroll[0]
        self.display_rect.y = -scroll[1]
                            