import pygame
from src.characters.my_sprite import MySprite
from src.resources.resource_manager import ResourceManager

class HealthBar(MySprite):
    def __init__(self):
        super().__init__()
        self.fixed_position = True
        self.current_health = 100
        self.max_health = 100
        
        # Cargar la imagen de la barra de salud
        self.health_sprite = ResourceManager.LoadImage('health/HP_Bar.png', -1)
        self.health_sprite = self.health_sprite.convert_alpha()
        
        # Cargar coordenadas
        data = ResourceManager.LoadCoordinatesFile('health/coordHealth.txt')
        data = data.split()
        
        # Crear rectángulos para cada nivel de vida
        self.health_coords = []
        count = 0
        
        # Procesar las coordenadas (11 niveles de vida, de 100% a 0%)
        for i in range(11):
            if count + 3 < len(data):
                self.health_coords.append(pygame.Rect(
                    int(data[count]), int(data[count+1]),
                    int(data[count+2]), int(data[count+3])
                ))
                count += 4
        
        self.create_health_surface()

    def create_health_surface(self):
        # Calcular el porcentaje de vida actual
        health_percentage = (self.current_health / self.max_health) * 100
        
        # Convertir porcentaje a índice (100%->0, 90%->1, 80%->2, etc.)
        health_index = int((100 - min(health_percentage, 100)) // 10)
        health_index = max(0, min(health_index, 10))  # Asegurar índice válido
        
        # Obtener el rectángulo correspondiente al nivel de vida
        rect = self.health_coords[health_index]
        
        # Crear la imagen recortada
        self.image = self.health_sprite.subsurface(rect)
        
        # Actualizar el rect
        self.rect = self.image.get_rect(topleft=(10, 10))

    def update(self, Subject):
        self.current_health = Subject.health
        max_health = Subject.player_component.get_stats()["health"]
        if max_health is not None:
            self.max_health = float(max_health)
        self.create_health_surface()