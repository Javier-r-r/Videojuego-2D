import random
import pygame
from src.characters.character import Character
from src.characters.constants import *
from src.items.item import Item


class Enemy(Character):
    def __init__(self, walls, item_image, item_coord, image_file, coordinates_file, num_images, animation_delay):
        # Inicializar atributos antes de llamar al constructor padre
        self.attacking = False
        self.death_animation_completed = False
        self.is_hurt = False
        self.hurt_animation_completed = False
        self.hurt_timer = 0
        self.hurt_duration = 500  # duración de la animación de daño en ms
        
        Character.__init__(self,
            image_file,
            coordinates_file,
            num_images,
            animation_delay)
            
        # Specific attributes for the enemy
        self.attack_range = 25  # Reducido de 50 a 25
        self.perception_range = 150  # Reducido de 200 a 150
        self.damage = 10
        self.run_speed *= 0.5
        self.last_attack_time = 0
        self.attack_cooldown = 1000
        self.walls = walls
        
        # Ajustar el tamaño de la hitbox para que coincida con el sprite
        self.hitbox = pygame.Rect(0, 0, 16, 16)  # Tamaño reducido para coincidir con el sprite
        self.update_hitbox()
        
        # Initial state
        self.state = STATE_IDLE

        self.max_health = 25
        self.current_health = self.max_health
        self.alive = True
        self.attacking = False
        self.attack_frame = 0
        self.death_animation_completed = False
        self.item_image = item_image
        self.item_coord = item_coord

    def take_damage(self, damage):
        self.current_health -= damage
        # Solo activar el estado de daño si no estaba ya dañado
        if not self.is_hurt:
            self.is_hurt = True
            self.hurt_timer = pygame.time.get_ticks()
        
        if self.current_health <= 0:
            self.current_health = 0
            self.alive = False
            self.numImagePosture = 0  
            self.numPosture = DEATH_SPRITE + 1  
            self.death_timer = pygame.time.get_ticks()
            item = self.drop_loot()
            if item:
                print(f"Enemy dropped {item}")
                return item
        return None

    def update_hitbox(self):
        # Actualizar la posición de la hitbox para que siga al enemigo
        self.hitbox = pygame.Rect(
            self.position[0] + 8,  # Centrar la hitbox en el sprite
            self.position[1] + 8,
            16, 16  # Tamaño del sprite visible
        )

    def get_world_hitbox(self):
        # Retorna la hitbox en coordenadas del mundo
        return pygame.Rect(
            self.position[0] + 8,  # Centrar la hitbox
            self.position[1] + 8,
            16, 16
        )

    def set_screen_position(self, scroll):
        # Guardar el scroll actual
        self.scroll = scroll
        # Actualizar la posición en pantalla basada en la posición del mundo y el scroll
        self.rect.x = self.position[0] - scroll[0]
        self.rect.y = self.position[1] - scroll[1]
        # Actualizar la hitbox
        self.update_hitbox()

    def get_collision_side(self, wall):
        # Calculate the center points
        wall_centerx = wall.rect.centerx
        wall_centery = wall.rect.centery
        enemy_centerx = self.hitbox.centerx
        enemy_centery = self.hitbox.centery
        
        # Calculate distances between centers
        dx = enemy_centerx - wall_centerx
        dy = enemy_centery - wall_centery
        
        # Get absolute values for comparison
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        
        # Compare the differences to determine which side is colliding
        if abs_dx > abs_dy:
            if dx > 0:
                print("Collision on player's LEFT side")
                return "left"
            else:
                print("Collision on player's RIGHT side")
                return "right"
        else:
            if dy > 0:
                print("Collision on player's TOP side")
                return "top"
            else:
                print("Collision on player's BOTTOM side")
                return "bottom"   

    def move_towards_player(self, player):
        # Calculate direction using world coordinates
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        
        # Determine the direction of the animation
        if abs(dx) > abs(dy):
            self.facing = RIGHT_DOWN if dx > 0 else LEFT_DOWN
        else:
            self.facing = DOWN if dy > 0 else UP

        # Solo moverse si no está en rango de ataque
        if not self.is_player_in_attack_range(player):
            # Normalize the movement vector
            length = (dx * dx + dy * dy) ** 0.5
            if length > 0:
                dx = dx / length
                dy = dy / length
                
                # Calcular nueva posición
                new_x = self.position[0] + dx * self.run_speed
                new_y = self.position[1] + dy * self.run_speed
                
                # Guardar velocidad actual
                self.velocity = (dx * self.run_speed, dy * self.run_speed)

                # Actualizar posición del mundo
                self.position = (new_x, new_y)
                
                # Actualizar posición en pantalla
                self.rect.x = new_x
                self.rect.y = new_y

                # Comprobar colisiones
                collided_wall = pygame.sprite.spritecollideany(self, self.walls, collided=pygame.sprite.collide_mask)
                if collided_wall:
                    collision_side = self.get_collision_side(collided_wall)
                    
                    if collision_side == "right":
                        self.position = (collided_wall.rect.x - (collided_wall.rect.width + 1), self.position[1])
                    elif collision_side == "left":
                        self.position = (collided_wall.rect.x + (collided_wall.rect.width + 1), self.position[1])
                    elif collision_side == "bottom":
                        self.position = (self.position[0], collided_wall.rect.y - (collided_wall.rect.height + 2))
                    elif collision_side == "top":
                        self.position = (self.position[0], collided_wall.rect.y + (collided_wall.rect.height + 2))
                    
                    # Actualizar rect después de la colisión
                    self.rect.x = self.position[0]
                    self.rect.y = self.position[1]
        else:
            self.velocity = (0, 0)

        self.update_hitbox()

    def is_player_in_perception_range(self, player):
        # Calculate distance using world coordinates
        dx = self.position[0] - player.position[0]
        dy = self.position[1] - player.position[1]
        distance = (dx * dx + dy * dy) ** 0.5
        return distance <= self.perception_range
    
    def is_player_in_attack_range(self, player):
        # Calculate distance using world coordinates
        dx = self.position[0] - player.position[0]
        dy = self.position[1] - player.position[1]
        distance = (dx * dx + dy * dy) ** 0.5
        return distance <= self.attack_range

    def has_line_of_sight(self, player):
        # Check if there is a direct line of sight between the NPC and the player.
        start_pos = self.hitbox.center
        end_pos = player.hitbox.center
        for obstacle in self.obstacles:
            if obstacle.rect.clipline(start_pos, end_pos):
                return False
        return True

    def aggressive_behavior(self, player):
        if self.is_player_in_attack_range(player) and self.has_line_of_sight(player):
            # Si está en rango de ataque, detenerse y atacar
            self.state = STATE_ATTACK
            self.attack_behavior(player)
        elif self.is_player_in_perception_range(player) and self.has_line_of_sight(player):
            # Si no está en rango, perseguir
            self.state = STATE_CHASE
            self.chase_behavior(player)
        
    def idle_behavior(self):
        # Behavior in idle state
        self.velocity = (0, 0)
        self.posture = IDLE_SPRITE

    def patrol_behavior(self):
        # Behavior in patrol state
        pass

    def chase_behavior(self, player):
        # Behavior in chase state
        self.move_towards_player(player)

    def attack_behavior(self, player):
        # Detener al enemigo cuando ataca
        self.velocity = (0, 0)
        current_time = pygame.time.get_ticks()
        
        # Solo realizar el ataque si ha pasado el cooldown
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.attack(player)
            self.last_attack_time = current_time

    # def _handle_attack_animation(self):
    #     # Manejar animación de ataque
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

    def update(self, time, player):
        current_time = pygame.time.get_ticks()
        
        if not self.alive:
            self.velocity = (0, 0)
            self.update_posture()
            # Check if death animation is complete
            if self.numPosture == DEATH_SPRITE + 1 and self.numImagePosture >= len(self.sheet_coordinates[self.numPosture]) - 1:
                self.death_animation_completed = True
            return
            
        # Remover el return para que siga actualizando aunque esté herido
        if self.is_hurt:
            if current_time - self.hurt_timer >= self.hurt_duration:
                self.is_hurt = False
                self.hurt_animation_completed = True
        
        # Update state based on player position
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
        elif self.state == STATE_PATROL:
            self.patrol_behavior()
        elif self.state == STATE_CHASE:
            self.chase_behavior(player)
        elif self.state == STATE_ATTACK:
            self.attack_behavior(player)
        
        # Update position and animation
        Character.update(self, time)
        
        # Update hitbox
        self.update_hitbox()

    def drop_loot(self):
        # Probabilidad de soltar un objeto (por ejemplo, 100%)
        if random.random() < 1:
            return Item(self.rect.x, self.rect.y, self.item_image, self.item_coord)
        return None
