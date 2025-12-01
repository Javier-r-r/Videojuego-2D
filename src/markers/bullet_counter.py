import pygame
from src.patterns.Observer import Observer
from src.characters.my_sprite import MySprite
from src.resources.resource_manager import ResourceManager

class BulletCounter(MySprite, Observer):
    def __init__(self):
        super().__init__()
        self.fixed_position = True
        self.bullet_count = 30
        
        # Cargar spritesheet de munición
        self.ammo_sheet = ResourceManager.LoadImage('bullets/ammo.png', -1)
        self.ammo_sheet = self.ammo_sheet.convert_alpha()
        
        # Cargar coordenadas
        data = ResourceManager.LoadCoordinatesFile('bullets/coordAmmo.txt')
        data = data.split()
        
        # Crear rectángulos para cada tipo de munición (con y sin munición)
        self.ammo_coords = {
            "pistol": {
                "with_ammo": pygame.Rect(int(data[0]), int(data[1]), int(data[2]), int(data[3])),
                "no_ammo": pygame.Rect(int(data[12]), int(data[13]), int(data[14]), int(data[15]))
            },
            "shotgun": {
                "with_ammo": pygame.Rect(int(data[4]), int(data[5]), int(data[6]), int(data[7])),
                "no_ammo": pygame.Rect(int(data[16]), int(data[17]), int(data[18]), int(data[19]))
            },
            "assault_rifle": {
                "with_ammo": pygame.Rect(int(data[8]), int(data[9]), int(data[10]), int(data[11])),
                "no_ammo": pygame.Rect(int(data[20]), int(data[21]), int(data[22]), int(data[23]))
            }
        }
        
        self.current_weapon_type = "pistol"
        # Crear fuente para el número
        self.font = pygame.font.Font(None, 20)
        
        # Crear superficie combinada
        self.create_combined_surface()

    def create_combined_surface(self):
        # Obtener el icono apropiado
        weapon_coords = self.ammo_coords[self.current_weapon_type]
        icon = self.ammo_sheet.subsurface(
            weapon_coords["with_ammo"] if self.bullet_count > 0 else weapon_coords["no_ammo"]
        )
        
        # Crear el texto
        text_surface = self.font.render(str(self.bullet_count), True, (255, 255, 255))
        
        # Crear una superficie combinada
        width = icon.get_width() + text_surface.get_width() + 5  # 5 píxeles de separación
        height = max(icon.get_height(), text_surface.get_height())
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Dibujar el icono y el texto
        self.image.blit(icon, (0, 0))
        self.image.blit(text_surface, (icon.get_width() + 5, 0))
        
        # Actualizar el rect
        self.rect = self.image.get_rect(topleft=(10, 30))

    def update(self, Subject):
        self.bullet_count = Subject.current_weapon.get_ammo()
        self.current_weapon_type = Subject.current_weapon.weapon_type
        self.create_combined_surface()
        