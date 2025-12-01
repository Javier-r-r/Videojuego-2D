import pygame
from src.characters.character import *
from src.characters.non_playable_characters.enemy import Enemy
from src.resources.sound_manager import SoundManager  # Add this import
import math


class FinalBossLvl1(Enemy):
    def __init__(self, walls):
        # Initialize attributes before calling parent constructor
        self.attacking = False
        self.death_animation_completed = False
        self.is_invisible = False
        self.last_invisibility_time = 0
        self.invisibility_duration = 5000  # Changed to 5000ms (5 seconds)
        self.is_invulnerable = False
        self.visibility_alpha = 255  # Full visibility
        self.invisibility_alpha = 0  # Completely invisible (new)
        self.invisibility_duration = 5000  # 5 seconds of invulnerability
        self.is_invulnerable = False
        self.minions_spawned = False
        self.minion_positions = [
            (-100, -100), (100, -100),
            (-100, 100), (100, 100)
        ]  # Posiciones relativas para los minions
        self.invisibility_triggered = False  # Nueva variable para controlar si ya se activó la invisibilidad
        self.projectiles = []  # Store active projectiles
        self.projectile_speed = 2
        self.projectile_damage = 15
        self.last_projectile_time = 0
        self.projectile_cooldown = 3000  # 3 seconds between projectile attacks
        self.is_casting = False
        self.cast_start_time = 0
        self.cast_duration = 1000  # 1 segundo en milisegundos
        self.projectile_phase_activated = False  # Nueva variable para controlar cuando empieza la fase de proyectiles
        self.projectiles_shot = False  # Para controlar si ya se dispararon los proyectiles en el casteo actual
        self.walls = walls
        self.is_hurt = False
        self.hurt_animation_completed = False
        self.hurt_timer = 0
        self.hurt_duration = 500  # duración de la animación de daño en ms
        self.sound_manager = SoundManager()

        Character.__init__(self,
            'enemies/Slime1/Slime1.png',  # Using Slime1 sprites
            'enemies/Slime1/coordSlime.txt',      # Using same coordinates
            [8, 8, 8, 8, 6, 6, 6, 6, 10, 10, 10, 10, 11, 11, 11, 11, 5, 5, 5, 5],  
            ANIMATION_SPEED * 2.0)
            
        # Boss specific attributes
        self.attack_range = 35           # Larger attack range than regular enemies
        self.perception_range = 200      # Larger perception range
        self.damage = 20                 # More damage than regular enemies
        self.last_attack_time = 0
        self.attack_cooldown = 1500      # Longer cooldown for balance
        self.run_speed *= 0.7
        
        self.hitbox = pygame.Rect(0, 0, 24, 24)  # Ajustado al tamaño del sprite del boss
        self.update_hitbox()
        
        self.state = STATE_IDLE
        self.max_health = 200            # More health than regular enemies
        self.current_health = self.max_health
        self.alive = True
        
        # Add health observer
        self.health_observer = None

    def add_health_observer(self, observer):
        self.health_observer = observer
        self.health_observer.update(self.current_health)

    def toggle_invisibility(self):
        current_time = pygame.time.get_ticks()
        
        # Si ya está invisible, comprobar si debe volver a ser visible
        if self.is_invulnerable:
            if current_time - self.last_invisibility_time >= self.invisibility_duration:
                self.is_invisible = False
                self.is_invulnerable = False
                self.minions_spawned = False
                self.image.set_alpha(255)
                self.projectile_phase_activated = True  # Activar fase de proyectiles
                print("¡El jefe vuelve a ser visible y comienza a usar proyectiles!")
            return False
        
        # Si no está invisible y aún no se ha activado la habilidad
        if not self.invisibility_triggered and self.current_health <= self.max_health * 0.5:
            self.is_invisible = True
            self.is_invulnerable = True
            self.last_invisibility_time = current_time
            self.invisibility_triggered = True
            self.image.set_alpha(0)
            print("¡El jefe se ha vuelto invisible!")
            return True
            
        return False

    def take_damage(self, damage):
        if not self.is_invulnerable:
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

    def get_minion_spawn_positions(self):
        # Calculate absolute positions based on boss position
        return [(self.position[0] + dx, self.position[1] + dy) 
                for dx, dy in self.minion_positions]

    def shoot_projectiles(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_projectile_time < self.projectile_cooldown:
            return

        self.last_projectile_time = current_time
        self.is_casting = True
        self.cast_start_time = current_time
        self.projectiles_shot = False
        self.velocity = (0, 0)  # Detener al boss mientras dispara

    def create_projectiles(self):
        angles = [i * (360 / 16) for i in range(16)]  # 16 directions
        base_speed = 5  # Velocidad base constante
        
        # Calcular el centro del boss
        center_x = self.position[0] + self.rect.width / 2
        center_y = self.position[1] + self.rect.height / 2
        
        for angle in angles:
            rad = math.radians(angle)
            vx = base_speed * math.cos(rad)
            vy = base_speed * math.sin(rad)
            
            projectile = {
                'pos': [center_x, center_y],  # Empezar desde el centro del boss
                'vel': [vx, vy],
                'radius': 8,
                'color': (152, 240, 191),
                'active': True
            }
            self.projectiles.append(projectile)

    def update_projectiles(self):
        delta_time = pygame.time.get_ticks() - self.last_update_time if hasattr(self, 'last_update_time') else 16.67
        self.last_update_time = pygame.time.get_ticks()
        
        # Update projectile positions using delta time for consistent speed
        for p in self.projectiles:
            if p['active']:
                # Update world positions
                p['pos'][0] += p['vel'][0] * (delta_time / 33.33)
                p['pos'][1] += p['vel'][1] * (delta_time / 33.33)

        # Remove projectiles that are too far from boss's world position
        self.projectiles = [p for p in self.projectiles if p['active'] and 
                          abs(p['pos'][0] - self.position[0]) < 800 and 
                          abs(p['pos'][1] - self.position[1]) < 800]

    def draw_projectiles(self, surface, scroll):
        for p in self.projectiles:
            if p['active']:
                # Convert world position to screen position
                screen_x = int(p['pos'][0] - scroll[0])
                screen_y = int(p['pos'][1] - scroll[1])
                pygame.draw.circle(surface, p['color'], 
                                (screen_x, screen_y), 
                                p['radius'])

    def get_projectile_rect(self, projectile):
        # Return world space rect for collision detection
        return pygame.Rect(
            projectile['pos'][0] - projectile['radius'],
            projectile['pos'][1] - projectile['radius'],
            projectile['radius'] * 2,
            projectile['radius'] * 2
        )

    def update(self, time, player):
        current_time = pygame.time.get_ticks()
        
        if not self.alive:
            self.velocity = (0, 0)
            self.update_posture()  # Let parent class handle death animation
            return

        # Update projectiles regardless of boss state
        self.update_projectiles()
        
        # Check if we're still in casting state
        if self.is_casting:
            # Check if we should create projectiles at half cast time
            if not self.projectiles_shot and current_time - self.cast_start_time >= self.cast_duration / 2:
                self.create_projectiles()
                self.projectiles_shot = True
            
            if current_time - self.cast_start_time >= self.cast_duration:
                self.is_casting = False
            else:
                self.velocity = (0, 0)  # Solo mantener al boss inmóvil
                Character.update(self, time)
                self.update_hitbox()
                return None
            
        # Check hurt state but continue with other updates
        if self.is_hurt:
            if current_time - self.hurt_timer >= self.hurt_duration:
                self.is_hurt = False
                self.hurt_animation_completed = True

        invisibility_triggered = self.toggle_invisibility()
        
        if invisibility_triggered:
            self.minions_spawned = True
            self.velocity = (0, 0)
            return "spawn_minions"
            
        # Only proceed with normal behavior if not invulnerable/invisible
        if not self.is_invulnerable:
            if self.is_player_in_perception_range(player):
                if self.is_player_in_attack_range(player):
                    self.state = STATE_ATTACK
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
        else:
            # Force stop movement while invisible
            self.velocity = (0, 0)
        
        # Update position and animation
        Character.update(self, time)
        self.update_hitbox()

        # Asegurar que siempre se mantiene invisible después de cualquier actualización
        if self.is_invisible:
            self.image.set_alpha(0)

        # Add projectile update
        self.update_projectiles()

        # Check if should shoot projectiles (only after becoming visible again)
        if self.projectile_phase_activated and not self.is_invulnerable:
            self.shoot_projectiles()

        return None

    def attack(self, player):
        if not self.is_invulnerable:  # Only attack if not invulnerable
            current_time = pygame.time.get_ticks()
            self.velocity = (0, 0)
            self.last_attack_time = current_time
            self.attacking = True
            self.attack_frame = 0
            
            # More damage when invisible
            actual_damage = self.damage * 1.5 if self.is_invisible else self.damage
            player.take_damage(actual_damage)
            self.sound_manager.play_sound('slime_attack')
            print(f"Boss attacked player! Player health: {player.health}")

    def _handle_attack_animation(self):
        # Igual que NonPlayerCharacter pero con posibilidad de personalización
        if self.facing == DOWN:
            self.numPosture = ATTACK_SPRITE
        elif self.facing == LEFT_DOWN:
            self.numPosture = ATTACK_SPRITE + 1
        elif self.facing == RIGHT_DOWN:
            self.numPosture = ATTACK_SPRITE + 2
        elif self.facing == UP:
            self.numPosture = ATTACK_SPRITE + 3

        self.numImagePosture += 1
        if self.numImagePosture >= len(self.sheet_coordinates[self.numPosture]):
            self.numImagePosture = 0
            self.attacking = False

    def _handle_hurt_animation(self):
        hurt_base = HURT_SPRITE
        if self.facing == DOWN:
            self.numPosture = hurt_base
        elif self.facing == LEFT_DOWN:
            self.numPosture = hurt_base + 1
        elif self.facing == RIGHT_DOWN:
            self.numPosture = hurt_base + 2
        elif self.facing == UP:
            self.numPosture = hurt_base + 3

        # Continuar la animación sin reiniciarla
        self.numImagePosture = (self.numImagePosture + 1) % len(self.sheet_coordinates[self.numPosture])
        
        # Solo marcar como completada cuando pase el tiempo
        current_time = pygame.time.get_ticks()
        if current_time - self.hurt_timer >= self.hurt_duration:
            self.is_hurt = False
            self.hurt_animation_completed = True

    def update_posture(self):
        # Primero actualizamos la postura normalmente
        super().update_posture()
        # Luego aseguramos que se mantiene invisible si debe estarlo
        if self.is_invisible:
            self.image.set_alpha(0)

    def get_world_hitbox(self):
        # Retorna la hitbox en coordenadas del mundo
        return pygame.Rect(
            self.position[0] + 4,  # Centrar la hitbox
            self.position[1] + 4,
            24, 24
        )

    def update_hitbox(self):
        # Actualizar la posición de la hitbox para que siga al boss
        self.hitbox = pygame.Rect(
            self.position[0] + 4,  # Centrar la hitbox
            self.position[1] + 4,
            24, 24  # Tamaño del sprite visible
        )