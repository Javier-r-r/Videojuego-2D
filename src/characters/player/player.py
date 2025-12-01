# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from src.patterns.Observer import Subject
from src.characters.character import Character
from src.characters.constants import *
from src.resources.resource_manager import *
from src.weapons.weapon_factory import WeaponFactory
from src.items.item import *
from src.characters.player.abilities.base_player import BasePlayer
from src.characters.player.abilities.enhanced_body import EnhancedBody
from src.characters.player.abilities.melee_combat import MeleeCombat
from src.resources.sound_manager import SoundManager


# Clase Jugador

class Player(Character, Subject):
    "Cualquier personaje del juego"

    def __init__(self, bullet_group, walls, available_weapons=None):
        # Remove incorrect super() call
        # super().__init__()
        
        # Initialize melee attack variables first
        self.is_melee_attacking = False
        self.melee_damage = 0
        self.melee_range = 0
        self.melee_cooldown = 0
        self.can_melee = False
        self.last_melee_time = 0
        self.melee_rect = pygame.Rect(0, 0, 50, 50)

        # Call parent constructor with correct arguments
        Character.__init__(self,
            'mainCharacter/MainCharacter.png',
            'mainCharacter/coordPlayer.txt',
            [8, 8, 8, 8,  # Walking animations
             8, 8, 8, 8,  # Idle animations
             8, 8, 8, 8,  # Death animations
             8, 8, 8, 8], # Melee animations
            ANIMATION_SPEED)

        Subject.__init__(self)

        # ...rest of initialization...
        # Create only available weapons or default to pistol if none specified
        if available_weapons is None:
            available_weapons = ["pistol"]
        
        self.weapons = []
        for weapon_type in available_weapons:
            if weapon_type == "pistol":
                pistol = WeaponFactory.create_weapon("pistol", "bullets/01.png")
                self.weapons.append(pistol)
            elif weapon_type == "shotgun":
                shotgun = WeaponFactory.create_weapon("shotgun", "bullets/02.png")
                self.weapons.append(shotgun)
            elif weapon_type == "assault_rifle":
                assaultRifle = WeaponFactory.create_weapon("assault_rifle", "bullets/08.png")
                self.weapons.append(assaultRifle)
        self.current_weapon = self.weapons[0]
        self.bullets = bullet_group
        self.on_death_callback = None 
        self.health_observers = []
        self.bullets_observers = []
        self.weapon_observers = []
        self.last_shot_time = 0
        self.can_shoot = True
        self.score = 0
        self.death_animation_completed = False
        self.walls = walls
        self.enemies = pygame.sprite.Group()  # Añadir grupo de enemigos
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.keys_collected = 0
        self.coins_collected = 0
        self.powerups_collected = 0
        self.health_pickups_collected = 0
        self.coin_observers = []

        # Añadir hitbox
        self.hitbox = pygame.Rect(0, 0, 28, 28)  # Mismo tamaño que los enemigos
        self.update_hitbox()
        
        self.melee_hitbox = pygame.Rect(200,200,self.sheet_coordinates[self.numPosture][self.numImagePosture][2],self.sheet_coordinates[self.numPosture][self.numImagePosture][3])
        
        # Initialize base component
        self.player_component = BasePlayer()
        stats = self.player_component.get_stats()
        
        # Set initial stats
        self.max_health = stats["health"]
        self.health = self.max_health
        self.run_speed = stats["speed"]
        self.damage_reduction = stats["damage_reduction"]
        self.melee_damage = stats["melee_damage"]
        self.melee_cooldown = stats["melee_cooldown"]
        self.can_melee = stats["can_melee"]
        
        self.last_melee_time = 0
        self.ability_observers = []

        # Initialize ability instances as None
        self.enhanced_body = None
        self.melee_combat = None

    def add_ability_observer(self, observer):
        """Add an observer for ability status changes"""
        self.ability_observers.append(observer)
        self.notify_ability_observers()

    def notify_ability_observers(self):
        """Notify observers about ability status changes"""
        current_time = pygame.time.get_ticks()
        
        for observer in self.ability_observers:
            if self.melee_combat:
                melee_ready = (current_time - self.last_melee_time) / 1000.0 > self.melee_cooldown
                observer.update_melee_status(melee_ready)
            
            if self.enhanced_body:
                enhanced_ready = not self.enhanced_body.is_active and \
                               (current_time - self.enhanced_body.last_use) > self.enhanced_body.cooldown
                observer.update_enhanced_status(enhanced_ready)

    def add_ability(self, ability_class):
        """Adds a new ability by decorating the current component"""
        decorated = ability_class(self.player_component)
        
        # Store reference to specific abilities
        if ability_class == MeleeCombat:
            self.melee_combat = decorated
        elif ability_class == EnhancedBody:
            self.enhanced_body = decorated
        
        self.player_component = decorated
        stats = self.player_component.get_stats()
        
        # Update stats from decorated component
        self.health = stats["health"]
        self.run_speed = stats["speed"]
        self.damage_reduction = stats["damage_reduction"]
        self.melee_damage = stats["melee_damage"]
        self.melee_cooldown = stats["melee_cooldown"]
        self.can_melee = stats["can_melee"]
        
        self.notify_ability_observers()

    
    def update_hitbox(self):
        # Actualizar la posición de la hitbox para que siga al jugador
        self.hitbox.centerx = self.rect.centerx + self.scroll[0]
        self.hitbox.centery = self.rect.centery + self.scroll[1]

    def set_screen_position(self, scroll):
        # Guardar el scroll actual
        self.scroll = scroll
        # Actualizar la posición en pantalla basada en la posición del mundo y el scroll
        self.rect.x = self.position[0] - scroll[0]
        self.rect.y = self.position[1] - scroll[1]
        # Actualizar la hitbox
        self.update_hitbox()

    def update(self, time):
        # Check Enhanced Body duration if active
        if self.enhanced_body and self.enhanced_body.check_duration(self):
            stats = self.enhanced_body.get_stats()
            self.health = stats["health"]
            self.run_speed = stats["speed"]
            self.damage_reduction = stats["damage_reduction"]
        
        # Update ability states
        self.notify_ability_observers()
        
        super().update(time)


    def update_player(self, keys_pressed):
        movx, movy = 0, 0
        
        # Weapon selection with checks for available weapons
        if keys_pressed[K_1]:
            if len(self.weapons) >= 1:
                self.current_weapon = self.weapons[0]
            else:
                print("¡Pistola no disponible!")
        elif keys_pressed[K_2]:
            if len(self.weapons) >= 2:
                self.current_weapon = self.weapons[1]
            else:
                print("¡Escopeta no disponible!")
        elif keys_pressed[K_3]:
            if len(self.weapons) >= 3:
                self.current_weapon = self.weapons[2]
            else:
                print("¡Rifle de asalto no disponible!")

        
        elif keys_pressed[K_r]:
            self.reload()
            return 
        # Add reload update check
        if self.current_weapon.update_reload():
            print(f"{self.current_weapon.weapon_type} recargada!")

        # Handle shooting independently
        if pygame.mouse.get_pressed()[0]:  # Check if the left mouse button is pressed
            self.shoot(self.can_shoot)
            self.can_shoot = False
        else:
            self.can_shoot = True
        # Movement
        if keys_pressed[K_a]:
            movx = -1
            self.facing = LEFT_DOWN
        if keys_pressed[K_d]:
            movx = 1
            self.facing = RIGHT_DOWN 
        if keys_pressed[K_w]:
            movy = -1
            self.facing = UP
        if keys_pressed[K_s]:    
            movy = 1
            self.facing = DOWN
            
        # Set direction
        self.direction = pygame.Vector2(movx, movy)
        
        # Apply movement
        if movx != 0 or movy != 0: 
            self.move(movx, movy)
        else:
            self.velocity = (0, 0)
            self.numPosture = IDLE_SPRITE
        
        # Melee attack
        if keys_pressed[K_q] and self.melee_combat and self.can_melee and not self.is_melee_attacking:
            self.melee_attack()

        # Enhanced Body activation
        if keys_pressed[K_e] and self.enhanced_body:
            if self.enhanced_body.activate(self):
                self.notify()

        # Melee attack (Q key)
        if keys_pressed[K_q] and self.can_melee:
            current_time = pygame.time.get_ticks()
            if (current_time - self.last_melee_time) / 1000.0 > self.melee_cooldown:
                self.melee_attack()
                self.last_melee_time = current_time

        # Enhanced Body (E key)
        if keys_pressed[K_e]:
            if isinstance(self.player_component, EnhancedBody):
                self.player_component.activate(self)

        self.notify()

    def melee_attack(self):
        """Perform a melee attack"""
        if not self.can_melee:
            return
            
        current_time = pygame.time.get_ticks()
        time_since_last_attack = (current_time - self.last_melee_time) / 1000.0
        
        if time_since_last_attack > self.melee_cooldown:
            self.is_melee_attacking = True
            self.numImagePosture = 0
            self.last_melee_time = current_time
            print(f"Melee attack! Damage: {self.melee_damage}")
            self.notify()  # Update icon state
        else:
            remaining_cooldown = self.melee_cooldown - time_since_last_attack
            print(f"Melee attack on cooldown! {remaining_cooldown:.1f}s remaining")

    def set_enemies_group(self, enemies_group):
        """Sets the enemy group for melee attacks"""
        self.enemies = enemies_group

    def get_collision_side(self, wall):
        # Calculate the center points
        wall_centerx = wall.rect.centerx
        wall_centery = wall.rect.centery
        player_centerx = self.hitbox.centerx
        player_centery = self.hitbox.centery
        
        # Calculate distances between centers
        dx = player_centerx - wall_centerx
        dy = player_centery - wall_centery
        
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

    def move(self, movx=0, movy=0):
        # Normalizar para movimiento diagonal
        if movx != 0 and movy != 0:
            movx *= 0.7071
            movy *= 0.7071

        # Calcular nueva posición en coordenadas del mundo
        new_x = self.position[0] + movx * self.run_speed
        new_y = self.position[1] + movy * self.run_speed
        
        # Guardar velocidad actual
        self.velocity = (movx * self.run_speed, movy * self.run_speed)
        
        # Actualizar posición en pantalla considerando el scroll
        self.rect.x = new_x 
        self.rect.y = new_y 

        # Comprobar colisiones
        collided_wall = pygame.sprite.spritecollideany(self, self.walls, collided=pygame.sprite.collide_mask)
        if collided_wall:
            collision_side = self.get_collision_side(collided_wall)
            
            if collision_side == "right":
                self.set_position((collided_wall.rect.x - (collided_wall.rect.width + 1), self.position[1]))
            if collision_side == "left":
                self.set_position((collided_wall.rect.x + (collided_wall.rect.width + 1), self.position[1]))
            if collision_side == "bottom":
                self.set_position((self.position[0], collided_wall.rect.y - (collided_wall.rect.height + 2)))
            if collision_side == "top":
                self.set_position((self.position[0], collided_wall.rect.y + (collided_wall.rect.height + 2)))

        self.numPosture = WALK_SPRITE
        self.update_hitbox()
        
    def reload(self):
        # Iniciar recarga si es posible
        if self.current_weapon.start_reload():
            print(f"Comenzando recarga de {self.current_weapon.weapon_type}... ({self.current_weapon.reload_time}s)")
            self.notify()

    def reload_all_weapons(self):
        """Reload all weapons to their maximum capacity"""
        for weapon in self.weapons:
            weapon.set_ammo(weapon.get_max_ammo())
            weapon.is_reloading = False
            weapon.reload_progress = 0
        self.notify()

    def shoot(self, can_shoot):
        # Si está recargando, mostrar mensaje y no hacer nada más
        if self.current_weapon.is_reloading:
            print("¡No puedes disparar mientras recargas!")
            return
            
        # Obtener posición del ratón en coordenadas de la ventana
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convertir coordenadas del ratón al espacio del mundo
        world_mouse_x = mouse_x/2 + self.scroll[0]
        world_mouse_y = mouse_y/2 + self.scroll[1]
        
        # Calcular el centro exacto del jugador para el punto de origen de la bala
        # Usar el tamaño del sprite para centrar exactamente
        sprite_center_x = self.position[0] + (self.rect.width / 2)
        sprite_center_y = self.position[1] + (self.rect.height / 2)
        
        # Disparar usando el centro exacto del jugador como origen
        self.current_weapon.fire(self.bullets, sprite_center_x, sprite_center_y,
                               world_mouse_x, world_mouse_y, can_shoot)
        
        self.notify()

    def take_damage(self, damage):
        # Get sound manager instance
        sound_manager = SoundManager()
        
        # Aplicar reducción de daño
        reduced_damage = damage * (1 - self.damage_reduction)
        self.health -= reduced_damage
        
        # Notify observers immediately
        self.notify()
        # Play hit sound
        sound_manager.play_sound('hit')
        
        print(f"Player took {reduced_damage:.1f} damage! Health: {self.health:.1f}")
        
        if self.health <= 0 and self.alive:
            self.health = 0
            self.alive = False
            self.numImagePosture = 0
            self.numPosture = DEATH_SPRITE + 1
            self.death_timer = pygame.time.get_ticks()
            self.death_animation_completed = False
            print("Player has died!")  # Debug message

    # def update_posture(self):
    #     self.movement_delay -= 1
    #     if self.movement_delay < 0:
    #         self.movement_delay = self.animation_delay

    #         if not self.alive:
    #             current_time = pygame.time.get_ticks()
    #             death_base_row = DEATH_SPRITE + 1
    #             if self.facing == DOWN:
    #                 self.numPosture = death_base_row 
    #             elif self.facing == LEFT_DOWN:
    #                 self.numPosture = death_base_row + 1
    #             elif self.facing == RIGHT_DOWN:
    #                 self.numPosture = death_base_row + 2
    #             elif self.facing == UP:
    #                 self.numPosture = death_base_row + 3

    #             # Si no hemos terminado la animación, avanzar frames
    #             if self.numImagePosture < len(self.sheet_coordinates[self.numPosture]) - 1:
    #                 self.numImagePosture += 1
    #             elif not self.death_animation_completed:
    #                 # Si terminamos la animación y no hemos llamado a handle_death
    #                 if not self.death_animation_completed:
    #                     print("Death animation completed!")  # Debug message
    #                     self.death_animation_completed = True
    #                     self.handle_death()

    #         else:
    #             # Lógica normal de animación para personaje vivo
    #             self.numImagePosture += 1
                
    #             # Determinar qué conjunto de animaciones usar
    #             if self.is_melee_attacking:
    #                 base_row = 12  # Starting row for melee animations
    #                 # Ajustar postura de melee según dirección
    #                 if self.facing == UP:
    #                     self.numPosture = base_row  # Row 12 - Up animations
    #                 elif self.facing == RIGHT_DOWN:
    #                     self.numPosture = base_row + 1  # Row 13 - Right animations
    #                 elif self.facing == LEFT_DOWN:
    #                     self.numPosture = base_row + 2  # Row 14 - Left animations
    #                 elif self.facing == DOWN:
    #                     self.numPosture = base_row + 3  # Row 15 - Down animations
                    
    #                 # Si terminamos la animación de melee
    #                 if self.numImagePosture >= len(self.sheet_coordinates[self.numPosture]):
    #                     self.is_melee_attacking = False
    #                     self.numImagePosture = 0
    #             elif self.velocity[0] == 0 and self.velocity[1] == 0:
    #                 base_row = 4  # Animaciones idle
    #             else:
    #                 base_row = 0  # Animaciones de movimiento

    #             # Ajustar postura según dirección
    #             if self.facing == DOWN:
    #                 self.numPosture = base_row + DOWN_ROW
    #             elif self.facing == LEFT_DOWN:
    #                 self.numPosture = base_row + LEFT_ROW
    #             elif self.facing == RIGHT_DOWN:
    #                 self.numPosture = base_row + RIGHT_ROW
    #             elif self.facing == UP:
    #                 self.numPosture = base_row + UP_ROW

    #             # Loop de animación para personaje vivo (excepto durante melee)
    #             if not self.is_melee_attacking and self.numImagePosture >= len(self.sheet_coordinates[self.numPosture]):
    #                 self.numImagePosture = 0

    #         # Actualizar sprite con comprobación de seguridad
    #         if (0 <= self.numPosture < len(self.sheet_coordinates) and 
    #             0 <= self.numImagePosture < len(self.sheet_coordinates[self.numPosture])):
    #             self.image = self.sprite_sheet.subsurface(self.sheet_coordinates[self.numPosture][self.numImagePosture])

    def collect_item(self, item):
        item_type = item.get_item_type()

        if item_type == ITEM_KEY:
            self.keys_collected += 1
            print(f"Key collected! Total keys: {self.keys_collected}")
        elif item_type == ITEM_COIN:
            self.coins_collected += 1
            self.notify_coin_observers()
            print(f"Coin collected! Total coins: {self.coins_collected}")
        else:
            print("Unknown item collected!")
            
    def set_walls(self, new_walls):
        """Updates the walls group used for collision detection"""
        self.walls = new_walls

    def reload_player_state(self):
        """Reset all player states to their initial values"""
        # Reset health to max
        stats = self.player_component.get_stats()
        self.health = stats["health"]
        
        # Reset animation state
        self.alive = True
        self.numPosture = IDLE_SPRITE
        self.numImagePosture = 0
        self.death_animation_completed = False
        
        # Reset ability states
        self.is_melee_attacking = False
        self.last_melee_time = 0
        
        # Reset weapon states
        self.can_shoot = True
        self.last_shot_time = 0
        
        # Notify observers of changes
        self.notify_health_observers()
        self.notify_bullets_observers()
        self.notify_weapon_change()

    def get_world_hitbox(self):
        """Returns the hitbox in world coordinates"""
        return pygame.Rect(
            self.position[0] + 4,  # Centrar la hitbox
            self.position[1] + 4,
            24, 24  # Tamaño del sprite visible
        )

    def get_player_component(self):
        """Get the current player component for decoration"""
        return self.player_component

    def set_player_component(self, component):
        """Set a new decorated component and update stats"""
        self.player_component = component
        stats = component.get_stats()
        self.health = stats["health"]
        self.run_speed = stats["speed"]
        self.damage_reduction = stats["damage_reduction"]
        self.melee_damage = stats["melee_damage"]
        self.melee_cooldown = stats["melee_cooldown"]
        self.can_melee = stats["can_melee"]

    def get_state(self):
        """Guarda el estado actual del jugador"""
        state = {
            "health": self.max_health,
            "position": self.position,
            "weapons": [],
            "coins": self.coins_collected,
            "abilities": {
                "enhanced_body": self.enhanced_body is not None,
                "melee_combat": self.melee_combat is not None
            }
        }
        
        # Guardar estado de las armas
        for weapon in self.weapons:
            weapon_state = {
                "type": weapon.weapon_type,
                "ammo": weapon.get_ammo()
            }
            state["weapons"].append(weapon_state)
            
        return state

    def load_state(self, state):
        """Carga un estado guardado"""
        self.health = state["health"]
        self.position = state["position"]
        self.coins_collected = state["coins"]
        
        # Limpiar armas actuales
        self.weapons = []
        
        # Restaurar armas y su munición
        for weapon_state in state["weapons"]:
            bullet_sprite = ""
            if weapon_state["type"] == "pistol":
                bullet_sprite = "bullets/01.png"
            elif weapon_state["type"] == "shotgun":
                bullet_sprite = "bullets/02.png"
            elif weapon_state["type"] == "assault_rifle":
                bullet_sprite = "bullets/08.png"
            
            weapon = WeaponFactory.create_weapon(weapon_state["type"], bullet_sprite)
            weapon.set_ammo(weapon_state["ammo"])
            self.weapons.append(weapon)
        
        # Restaurar la primera arma como arma actual
        if self.weapons:
            self.current_weapon = self.weapons[0]
        
        # Restaurar habilidades
        if state["abilities"]["enhanced_body"] and not self.enhanced_body:
            self.add_ability(EnhancedBody)
        if state["abilities"]["melee_combat"] and not self.melee_combat:
            self.add_ability(MeleeCombat)
            
        # Notificar a todos los observadores
        self.notify()