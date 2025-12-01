import pygame
from src.characters.non_playable_characters.enemy import Enemy
from src.characters.constants import *
from src.resources.resource_manager import ResourceManager
from src.resources.sound_manager import SoundManager
import math

class FinalBossLvl2(Enemy):
    def __init__(self, walls):
        # Llamar al constructor del padre (Enemy)
        super().__init__(
            walls,
            None, 
            None,
            'enemies/Crimson/CrimsonQueen.png',
            'enemies/Crimson/coordQueen.txt',
            [9, 9, 9, 9, 2, 2, 2, 2, 6, 6, 6, 6, 6, 6, 6, 6, 5, 5, 5, 5, 13, 13, 13, 13],
            (ANIMATION_SPEED * 1.5),
        )
        # Inicialización de atributos específicos antes de llamar al constructor padre
        self.attacking = False
        self.speed_boosted = False
        self.regen_amount = 5
        self.regen_cooldown = 3000
        self.last_regen_time = 0
        self.blades = []
        self.blade_cooldown = 5000  # Cambiado a 5 segundos
        self.last_blade_time = 0
        self.blade_damage = 10
        self.blade_speed = 6
        self.health_observer = None  # Add health observer attribute
        self.blade_sprite = ResourceManager.LoadImage("bullets/dagger.png")
        self.is_shooting = False
        self.shoot_animation_completed = False
        self.shoot_start_time = 0  # Añadir esta línea
        self.shoot_delay = 1000    # Añadir esta línea - 1000ms = 1 segundo

        
        # Sobrescribir atributos del Enemy para el boss
        self.state = STATE_IDLE
        self.attack_range = 40
        self.perception_range = 250
        self.damage = 25
        self.attack_cooldown = 1800
        self.base_speed = self.run_speed
        self.hitbox = pygame.Rect(0, 0, 32, 48)  # Adjusted to match sprite size
        self.max_health = 200
        self.current_health = self.max_health
        self.is_hurt = False
        self.hurt_animation_completed = False
        self.hurt_timer = 0
        self.hurt_duration = 500  # duración de la animación de daño en ms

    def add_health_observer(self, observer):
        self.health_observer = observer
        self.health_observer.update(self.current_health)

    def take_damage(self, damage):
        self.current_health -= damage
        # Activar estado de daño si no estaba ya dañado
        if not self.is_hurt:
            self.is_hurt = True
            self.hurt_timer = pygame.time.get_ticks()
        
        if self.health_observer:
            self.health_observer.update(self.current_health)
        if self.current_health <= 0:
            self.current_health = 0
            self.alive = False
            self.death_animation_completed = False  # Reset this flag
            self.numImagePosture = 0
            self.numPosture = DEATH_SPRITE + 1
            self.death_timer = pygame.time.get_ticks()

    def regenerate_health(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_regen_time >= self.regen_cooldown:
            if self.current_health < self.max_health:
                self.current_health = min(self.current_health + self.regen_amount, self.max_health)
                if self.health_observer:
                    self.health_observer.update(self.current_health)
                self.last_regen_time = current_time

    def throw_blades(self, player):
        """Lanza una única daga dirigida al jugador"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_blade_time >= self.blade_cooldown:
            if not self.is_shooting:
                # Iniciar la animación de disparo
                self.is_shooting = True
                self.numImagePosture = 0
                self.shoot_start_time = current_time
                return
            
            # Comprobar si ha pasado el tiempo de retraso
            if current_time - self.shoot_start_time < self.shoot_delay:
                return

            # Reproducir sonido de daga
            sound_manager = SoundManager()
            sound_manager.play_sound('dagger')
            
            # Calcular dirección hacia el jugador
            dx = player.position[0] - self.position[0]
            dy = player.position[1] - self.position[1]
            
            # Ajustar la dirección del personaje para la animación
            if abs(dx) > abs(dy):
                self.facing = RIGHT_DOWN if dx > 0 else LEFT_DOWN
            else:
                self.facing = DOWN if dy > 0 else UP
            
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
                
                # Calcular ángulo de la daga basado en su velocidad
                # Como el sprite base apunta hacia arriba (90 grados),
                # ajustamos el ángulo sumando 90 grados
                angle = math.degrees(math.atan2(blade['vel'][1], blade['vel'][0])) + 90
                
                # Rotar el sprite
                rotated_blade = pygame.transform.rotate(self.blade_sprite, -angle)
                
                # Obtener el rectángulo centrado
                blade_rect = rotated_blade.get_rect()
                blade_rect.center = (screen_x, screen_y)
                
                # Dibujar el sprite
                surface.blit(rotated_blade, blade_rect)

    def get_blade_rect(self, blade):
        # Ajustar el hitbox para que sea más preciso con la nueva forma
        return pygame.Rect(
            blade['pos'][0] - 8,  # Ancho total 16
            blade['pos'][1] - 4,  # Alto total 8
            16,
            8
        )

    def check_speed_boost(self):
        health_percentage = (self.current_health / self.max_health) * 100
        if health_percentage <= 20 and not self.speed_boosted:
            self.run_speed = self.base_speed * 2
            self.speed_boosted = True
            print("¡El jefe se ha enfurecido y aumentado su velocidad!")

    def attack(self, player):
        """Execute melee attack on player"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.velocity = (0, 0)
            self.last_attack_time = current_time
            self.attacking = True
            self.attack_frame = 0
            player.take_damage(self.damage)
            print(f"Boss2 melee attacked player! Player health: {player.health}")

    # def _handle_attack_animation(self):
    #     """Handle attack animation frames"""
    #     if self.facing == DOWN:
    #         self.numPosture = ATTACK_SPRITE
    #     elif self.facing == LEFT_DOWN:
    #         self.numPosture = ATTACK_SPRITE + 1
    #     elif self.facing == RIGHT_DOWN:
    #         self.numPosture = ATTACK_SPRITE + 2
    #     elif self.facing == UP:
    #         self.numPosture = ATTACK_SPRITE + 3

    #     self.numImagePosture += 1
    #     if self.numImagePosture >= len(self.sheet_coordinates[self.numPosture]):
    #         self.numImagePosture = 0
    #         self.attacking = False

    # def _handle_hurt_animation(self):
    #     """Handle hurt animation frames"""
    #     hurt_base = HURT_SPRITE
    #     if self.facing == DOWN:
    #         self.numPosture = hurt_base
    #     elif self.facing == LEFT_DOWN:
    #         self.numPosture = hurt_base + 1
    #     elif self.facing == RIGHT_DOWN:
    #         self.numPosture = hurt_base + 2
    #     elif self.facing == UP:
    #         self.numPosture = hurt_base + 3

    #     # Continuar la animación sin reiniciarla
    #     self.numImagePosture = (self.numImagePosture + 1) % len(self.sheet_coordinates[self.numPosture])
        
    #     # Solo marcar como completada cuando pase el tiempo
    #     current_time = pygame.time.get_ticks()
    #     if current_time - self.hurt_timer >= self.hurt_duration:
    #         self.is_hurt = False
    #         self.hurt_animation_completed = True

    # def update_posture(self):
    #     """Update sprite posture and animation frames"""
    #     if self.attacking:
    #         self._handle_attack_animation()
    #     elif self.is_hurt:
    #         self._handle_hurt_animation()
    #     else:
    #         super().update_posture()

    def get_world_hitbox(self):
        """Returns the hitbox in world coordinates"""
        return pygame.Rect(
            self.position[0],  # Remove offset since we want the full sprite
            self.position[1],
            32,  # Match sprite width
            48   # Match sprite height
        )

    def update(self, time, player):
        if not self.alive:
            self.velocity = (0, 0)
            return super().update(time, player)

        self.check_speed_boost()
        self.regenerate_health()
        self.update_blades()
        
        if self.is_player_in_perception_range(player):
            # Determinar el estado basado en la distancia
            if self.is_player_in_attack_range(player):
                self.state = STATE_ATTACK  # Ataque melee cuando está cerca
            else:
                # Alternar entre perseguir y disparar cuando está lejos
                current_time = pygame.time.get_ticks()
                if current_time - self.last_blade_time >= self.blade_cooldown:
                    self.state = STATE_SHOOT
                    self.throw_blades(player)
                else:
                    self.state = STATE_CHASE
        else:
            self.state = STATE_IDLE

        # Execute behavior based on state
        if self.state == STATE_IDLE:
            self.idle_behavior()
        elif self.state == STATE_CHASE and not self.is_shooting:
            self.chase_behavior(player)
        elif self.state == STATE_ATTACK and not self.is_shooting:
            self.attack_behavior(player)

        super().update(time, player)
        self.update_hitbox()

    def drop_loot(self):
        # Este boss no dropea items
        return None
