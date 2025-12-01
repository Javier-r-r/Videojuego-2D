import pygame
from src.characters.character import Character
import math
from src.resources.sound_manager import SoundManager
from src.resources.resource_manager import ResourceManager
from src.characters.non_playable_characters.enemy import Enemy
from src.characters.constants import *

# NonPlayerCharacter Class

class Enemy_lvl2(Enemy):
    def __init__(self, walls, items_image, items_coord, damage):
        super().__init__(
            walls,
            items_image,
            items_coord,
            'enemies/Ninja/Ninja.png',
            'enemies/Ninja/coordNinja.txt',
            [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 3, 3, 3, 3, 6,6,6,6,6,6,6,6],
            ANIMATION_SPEED * 1.5,
        )
        self.attack_range = 25
        self.perception_range = 150
        self.max_health = 25
        self.current_health = self.max_health
        self.damage = damage
        self.blades = []
        self.blade_cooldown = 5000  # Cambiado a 5 segundos
        self.last_blade_time = 0
        self.blade_damage = 10
        self.blade_speed = 5
        self.blade_sprite = ResourceManager.LoadImage("bullets/shuriken.png")

    def attack(self, player):
        """Execute melee attack on player"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.velocity = (0, 0)
            self.last_attack_time = current_time
            self.attacking = True
            self.attack_frame = 0
            player.take_damage(self.damage)
            print(f"Enemy2 melee attacked player! Player health: {player.health}")


    def throw_blades(self, player):
        """Lanza una única daga dirigida al jugador"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_blade_time >= self.blade_cooldown:
            # Reproducir sonido de daga
            sound_manager = SoundManager()
            sound_manager.play_sound('dagger')
            
            # Calcular dirección hacia el jugador
            dx = player.position[0] - self.position[0]
            dy = player.position[1] - self.position[1]
            
            # Normalizar el vector
            length = (dx * dx + dy * dy) ** 0.5
            if length > 0:
                dx = dx / length
                dy = dy / length
            
            # Crear una única daga
            blade = {
                'pos': [self.position[0] + self.rect.width / 2,
                       self.position[1] + self.rect.height / 2],
                'vel': [dx * self.blade_speed, dy * self.blade_speed],
                'radius': 6,
                'color': (255, 0, 0),
                'active': True
            }
            self.blades.append(blade)
            self.last_blade_time = current_time

    def update_blades(self):
        for blade in self.blades[:]:
            blade['pos'][0] += blade['vel'][0]
            blade['pos'][1] += blade['vel'][1]
            
            if (abs(blade['pos'][0] - self.position[0]) > 800 or 
                abs(blade['pos'][1] - self.position[1]) > 800):
                self.blades.remove(blade)

    def draw_blades(self, surface, scroll):
        for blade in self.blades:
            if blade['active']:
                # Convertir posición del mundo a pantalla
                screen_x = int(blade['pos'][0] - scroll[0])
                screen_y = int(blade['pos'][1] - scroll[1])
                
                # Incrementar el ángulo de rotación del shuriken
                if 'rotation_angle' not in blade:
                    blade['rotation_angle'] = 0  # Inicializar el ángulo si no existe
                blade['rotation_angle'] += 10  # Incrementar el ángulo para simular giro
                
                # Rotar el sprite del shuriken
                rotated_shuriken = pygame.transform.rotate(self.blade_sprite, -blade['rotation_angle'])
                
                # Obtener el rectángulo centrado
                shuriken_rect = rotated_shuriken.get_rect()
                shuriken_rect.center = (screen_x, screen_y)
                
                # Dibujar el sprite
                surface.blit(rotated_shuriken, shuriken_rect)

    def get_blade_rect(self, blade):
        # Ajustar el hitbox para que sea más preciso con la nueva forma
        return pygame.Rect(
            blade['pos'][0] - 8,  # Ancho total 16
            blade['pos'][1] - 4,  # Alto total 8
            16,
            8
        )
    
    def update(self, time, player):
        if not self.alive:
            self.velocity = (0, 0)
            return super().update(time, player)

        self.update_blades()
        
        if self.is_player_in_perception_range(player):
            # Lanzar daga si el jugador está en rango de percepción
            self.throw_blades(player)
            
            if self.is_player_in_attack_range(player):
                self.state = STATE_ATTACK  # Ataque melee cuando está cerca
            else:
                self.state = STATE_CHASE
        else:
            self.state = STATE_IDLE

        # Execute behavior based on state
        if self.state == STATE_IDLE:
            self.idle_behavior()
        elif self.state == STATE_CHASE:
            self.chase_behavior(player)
        elif self.state == STATE_ATTACK:
            self.attack_behavior(player)

        super().update(time, player)
        self.update_hitbox()