import math
import random
import time
import pygame
from src.resources.resource_manager import ResourceManager
from src.resources.sound_manager import SoundManager

class FireBehavior:
    def __init__(self, bullet_image):
        self.bullet_image = bullet_image
        self.sound_manager = SoundManager()

    """Interfaz para el comportamiento de disparo."""
    def fire(self, bullets_group, x, y, target_x, target_y, can_shoot):
        pass

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage, image_file):
        super().__init__()
        # Cargar y convertir la imagen original
        original_image = ResourceManager.LoadImage(image_file)
        self.original_image = original_image.convert_alpha()
        
        # Rotar la imagen según el ángulo (convertir de radianes a grados)
        # Como la imagen original mira hacia la derecha (0 grados),
        # solo necesitamos convertir el ángulo a grados
        angle_degrees = math.degrees(angle)
        self.image = pygame.transform.rotate(self.original_image, -angle_degrees)
        
        # Initialize position and rect
        self.position = pygame.math.Vector2(x, y)  # World position
        self.rect = self.image.get_rect(center=(x, y))
        
        self.speed = 10
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * self.speed
        self.damage = damage
        self.scroll = [0, 0]  # Para mantener referencia al scroll

    def update(self):
        # Actualizar posición en el mundo
        self.position += self.velocity
        
        # Actualizar rect para dibujar (posición en pantalla)
        self.rect.center = (self.position.x - self.scroll[0], 
                          self.position.y - self.scroll[1])

    def set_screen_position(self, scroll):
        """Update bullet's screen position based on scroll"""
        self.scroll = scroll
        self.rect.center = (self.position.x - scroll[0], 
                          self.position.y - scroll[1])

    def get_world_position(self):
        """Return the bullet's position in world coordinates"""
        return (self.position.x, self.position.y)

class SingleShot(FireBehavior):
    """Disparo único (Pistola)."""
    def __init__(self, bullet_image):
        super().__init__(bullet_image)
        self.last_fire_time = 0

    def fire(self, bullets_group, x, y, target_x, target_y, can_shoot):
        if (can_shoot):
            current_time = time.time()
            if current_time - self.last_fire_time >= 1:
                    self.sound_manager.play_sound('pistol_shoot')
                    print("Pistola: Disparo!")
                    angle = math.atan2(target_y - y, target_x - x)
                    bullet = Bullet(x, y, angle, 10, self.bullet_image)
                    bullets_group.add(bullet)
                    self.last_fire_time = current_time
                    return True
            else:
                print("Pistola: Esperando para volver a disparar.")
                return False

class AutomaticFire(FireBehavior):

    def __init__(self, bullet_image):
        super().__init__(bullet_image)
        self.last_fire_time = 0 
        self.rifle_fire_rate = 100  # 1 segundo entre disparos (en milisegundos)

    """Disparo automático continuo (Rifle de asalto)."""
    def fire(self, bullets_group, x, y, target_x, target_y, can_shoot):
        print("Rifle de asalto: Disparo automático!")
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time > self.rifle_fire_rate:
            self.sound_manager.play_sound('rifle_shoot')
            angle = math.atan2(target_y - y, target_x - x)
            bullet = Bullet(x, y, angle, 5, self.bullet_image)
            bullets_group.add(bullet)
            self.last_fire_time = current_time
            return True

        else:
            print("Rifle de asalto: Esperando para volver a disparar.")


class ShotgunFire(FireBehavior):
    """Disparo de cartuchos con perdigones (Escopeta)."""
    
    NUM_PELLETS = 3  # Número reducido de perdigones
    
    def __init__(self, bullet_image):
        super().__init__(bullet_image)

    def fire(self, bullets_group, x, y, target_x, target_y, can_shoot):
        if (can_shoot):
            self.sound_manager.play_sound('shotgun_shoot')
            print("Escopeta: Disparando cartucho!")
            base_angle = math.atan2(target_y - y, target_x - x)
            spread_angles = [-0.2, 0, 0.2]  # Ángulos de dispersión ajustados para los perdigones
            
            for spread in spread_angles:
                angle = base_angle + spread
                bullet = Bullet(x, y, angle, 5, self.bullet_image)
                bullet.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * bullet.speed
                bullets_group.add(bullet)
        
            return True


