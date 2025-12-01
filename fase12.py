# -*- coding: utf-8 -*-

import pygame
from src.characters.player.player import Player
from src.characters.non_playable_characters.enemy_lvl1 import Enemy_lvl1
from src.characters.non_playable_characters.boss1 import FinalBossLvl1
from src.markers.health_bar import HealthBar
from src.markers.bullet_counter import BulletCounter
from src.markers.weapon_indicator import WeaponIndicator
from src.markers.ability_indicator import AbilityIndicator
from pygame.locals import *
from src.resources.resource_manager import *
from src.map.tilemap import *
from src.ui.player_menu import PlayerMenu
from src.markers.coin_counter import CoinCounter
from src.markers.boss_health_bar import BossHealthBar
from pathlib import Path
from src.characters.player.abilities.enhanced_body import EnhancedBody
from src.characters.player.abilities.melee_combat import MeleeCombat
from src.resources.music_manager import MusicManager
from src.weapons.weapon_factory import WeaponFactory

# -------------------------------------------------
# -------------------------------------------------
# Constantes
# -------------------------------------------------
# -------------------------------------------------

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 960

# Los bordes de la pantalla para hacer scroll
SCROLL_MARGIN_X = SCREEN_WIDTH // 4  # 320 pixels desde los bordes
SCROLL_MARGIN_Y = SCREEN_HEIGHT // 4  # 240 pixels desde los bordes

# -------------------------------------------------
# Clase Fase

class Fase12:
    def __init__(self, player, from_next_phase=False):
                # Añadir escopeta si no la tiene
        has_shotgun = any(weapon.weapon_type == "shotgun" for weapon in player.weapons)
        if not has_shotgun:
            shotgun = WeaponFactory.create_weapon("shotgun", "bullets/02.png")
            player.weapons.append(shotgun)
            print("¡Nueva arma desbloqueada: Escopeta!")
        self.player1 = player
        self.should_change_phase = False
        self.music_manager = MusicManager()
        self.initial_player_state = player.get_state()
        self.initialize()
        # Crear el menú del jugador
        self.player_menu = PlayerMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player_menu.set_callback('continue', self.resume_game)
        self.player_menu.set_callback('restart', self.reset)
        self.player_menu.set_callback('exit', self.exit_game)
        self.should_exit = False

    def resume_game(self):
        self.player_menu.hide()
        # Eliminamos pygame.mixer.music.unpause()

    def initialize(self):

        # Habria que pasarle como parámetro el número de fase, a partir del cual se cargue
        #  un fichero donde este la configuracion de esa fase en concreto, con cosas como
        #   - Nombre del archivo con el decorado
        #   - Posiciones de las plataformas
        #   - Posiciones de los enemigos
        #   - Posiciones de inicio de los jugadores
        #  etc.
        # Y cargar esa configuracion del archivo en lugar de ponerla a mano, como aqui abajo
        # De esta forma, se podrian tener muchas fases distintas con esta clase

        # Poner el fondo
    
        self.tilemap = TileMap("Level1", "Level1_2.tmx")
        self.walls_sprites = pygame.sprite.Group()
        # Inicializar lista de muros
        self.tilemap.load_layer_by_name("Collisions", self.walls_sprites)
        self.tp_sprites = pygame.sprite.Group()
        self.tilemap.load_layer_by_name("Up level", self.tp_sprites)
        self.player1.set_walls(self.walls_sprites)

        self.items_group = pygame.sprite.Group()


        # Que parte del decorado estamos visualizando
        self.scroll = [0, 0]  # [scrollx, scrolly]
        self.zoom_scale = 2  # Factor de zoom

        # Initialize player position further to the right
        self.player1.set_position((125, 120))  # X increased from default, adjust Y as needed

        # Create UI elements first
        self.health_bar = HealthBar()
        self.health_bar.set_position((0, 0))

        self.bullet_counter = BulletCounter()
        self.bullet_counter.set_position((0, 25))

        self.weapon_indicator = WeaponIndicator(self.player1.weapons)
        self.weapon_indicator.set_position((0, 45))

        self.coin_counter = CoinCounter()
        self.coin_counter.set_position((0, SCREEN_HEIGHT // self.zoom_scale - 20))

        # Create ability indicator
        self.ability_indicator = AbilityIndicator()
        self.ability_indicator.set_position((
            self.health_bar.rect.right - 8,
            self.health_bar.rect.top - 10
        ))

        # Set up player bullets group
        self.bullets_group = self.player1.bullets

        # Create and position enemies
        self.enemy1 = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)
        self.enemy2 = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)
        self.enemy3 = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)
        self.enemy4 = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)
        self.enemy5 = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)
        self.enemy6 = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)
        self.enemy7 = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)
        self.enemy8 = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)
        self.enemy9 = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)
        self.enemy10 = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)

        self.enemy1.set_position((200, 300))
        self.enemy2.set_position((200, 400))
        self.enemy3.set_position((400, 200))
        self.enemy4.set_position((600, 350))
        self.enemy5.set_position((800, 250))
        self.enemy6.set_position((300, 500))
        self.enemy7.set_position((500, 150))
        self.enemy8.set_position((700, 450))
        self.enemy9.set_position((900, 300))
        self.enemy10.set_position((250, 200))
        
        # Create enemy group with all enemies
        self.enemies_group = pygame.sprite.Group(
            self.enemy1, self.enemy2, self.enemy3, self.enemy4, self.enemy5,
            self.enemy6, self.enemy7, self.enemy8, self.enemy9, self.enemy10
        )

        # Set up all observers
        self.player1.add_health_observer(self.health_bar)
        self.player1.add_bullets_observer(self.bullet_counter)
        self.player1.add_weapon_observer(self.weapon_indicator)
        self.player1.add_coin_observer(self.coin_counter)
        self.player1.add_ability_observer(self.ability_indicator)

        # Create sprite groups in correct order
        self.dynamic_sprites_group = pygame.sprite.Group(
            self.player1,
            self.bullets_group,
            self.enemies_group
        )

        self.all_sprites_group = pygame.sprite.Group(
            self.player1,
            self.bullets_group,
            self.enemies_group,
            self.bullet_counter,
            self.health_bar,
            self.items_group,
            self.coin_counter,
            self.ability_indicator,
            self.weapon_indicator
        )

        # Initialize view
        self.view_size = (SCREEN_WIDTH // self.zoom_scale, SCREEN_HEIGHT // self.zoom_scale)
        self.zoom_surface = pygame.Surface(self.view_size)
        
    def reset(self):
        # Reiniciar todos los elementos del juego
        self.all_sprites_group.empty()
        self.bullets_group.empty()
        self.enemies_group.empty()
        self.items_group.empty()
        self.player1.reload_player_state()  # Reset player state including animation
        self.player1.load_state(self.initial_player_state)
        self.initialize()         
        self.player_menu.hide()
        self.player_menu.last_continue_click = pygame.time.get_ticks()
        
    def show_game_over_screen(self):

        # Obtener la superficie de la pantalla
        screen = pygame.display.get_surface()
        
        # Crear el texto "Game Over"
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over", True, (255, 0, 0))
        text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 50))
        
        # Mostrar el puntaje (puedes ajustar esto según tu lógica de puntuación)
        score_font = pygame.font.Font(None, 36)
        score_text = score_font.render(f"Score: {"100"}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2))
        
        # Crear un botón de reinicio
        button_font = pygame.font.Font(None, 36)
        button_text = button_font.render("Restart", True, (255, 255, 255))
        button_rect = button_text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 + 50))
        
        # Dibujar todo en la pantalla
        screen.blit(text, text_rect)
        screen.blit(score_text, score_rect)
        screen.blit(button_text, button_rect)
        pygame.display.flip()
        
        # Esperar a que el jugador haga clic en el botón de reinicio
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        waiting = False
                        self.reset()  # Reiniciar el juego
                        
                        
    def handle_player_death(self):
        # Mostrar la pantalla de "Game Over" cuando el jugador muere
        self.show_game_over_screen()

    def update_scroll(self, player):
        # Calculamos la posición deseada del jugador en el centro de la vista
        target_x = player.position[0] - self.view_size[0] // 2
        target_y = player.position[1] - self.view_size[1] // 2
        
        # Aplicamos límites del mapa
        max_scroll_x = self.tilemap.rect.width - self.view_size[0]
        max_scroll_y = self.tilemap.rect.height - self.view_size[1]
        
        # Aseguramos que el scroll no se salga de los límites del mapa
        self.scroll[0] = max(0, min(target_x, max_scroll_x))
        self.scroll[1] = max(0, min(target_y, max_scroll_y))
        
        # Convert to integers to avoid floating point errors
        self.scroll[0] = int(self.scroll[0])
        self.scroll[1] = int(self.scroll[1])

        # Update tilemap first
        self.tilemap.update(self.scroll)
        
        # Then update all other sprites
        for sprite in self.all_sprites_group:
            sprite.set_screen_position(self.scroll)


    # Se actualiza el decorado, realizando las siguientes acciones:
    #  Se indica para los personajes no jugadores qué movimiento desean realizar según su IA
    #  Se mueven los sprites dinámicos, todos a la vez
    #  Se comprueba si hay colision entre algun jugador y algun enemigo
    #  Se comprueba si algún jugador ha salido de la pantalla, y se actualiza el scroll en consecuencia
    #  Actualizar el scroll implica tener que desplazar todos los sprites por pantalla
    #  Se actualiza la posicion del sol y el color del cielo
    # Ademas, devuelve si se debe parar o no la ejecucion del juego
    def update(self, time):
        # Check if player is dead before updating
        if not self.player1.alive and self.player1.death_animation_completed:
            self.handle_player_death()
            return False
            
        # Actualizar primero los enemigos
        for enemy in self.enemies_group:
            enemy.update(time, self.player1)
        
        # Verificar si no quedan enemigos
        if len(self.enemies_group) == 0:
            self.bullets_group.empty()
            self.should_change_phase = True
        
        # Actualizar el jugador y otros sprites dinámicos que no sean enemigos
        self.player1.update(time)
        # Actualizar balas y mantener el scroll actualizado para cada una
        for bullet in self.bullets_group:
            bullet.scroll = self.scroll
            bullet.update()
        self.items_group.update()

        # Add collision detection after updating positions but before scroll
        self.check_collisions()
        
        # Actualizamos el scroll después de mover los sprites
        self.update_scroll(self.player1)

        # Actualizamos las posiciones en pantalla después del scroll
        for sprite in self.all_sprites_group:
            sprite.set_screen_position(self.scroll)
            
        # No se debe parar la ejecucion
        return False


    def draw(self, screen):
        # Limpiamos la superficie de zoom
        self.zoom_surface.fill((0, 0, 0))  # Changed to black
        
        # Dibujamos el mapa y los sprites en la superficie pequeña
        self.tilemap.draw(self.zoom_surface)
        
        self.all_sprites_group.draw(self.zoom_surface)
        self.bullets_group.draw(self.zoom_surface)
        # Check bullet collisions with walls using masks
        for bullet in self.bullets_group:
            # Get bullet's world coordinates
            bullet_x = bullet.rect.centerx + self.scroll[0] 
            bullet_y = bullet.rect.centery + self.scroll[1]
            
            # Create a small rect around bullet for initial collision check
            bullet_world_rect = pygame.Rect(
            bullet_x - 2,  # Small area around bullet center
            bullet_y - 2,
            4, 4
            )
            
            # Check collision with walls using masks
            for wall in self.walls_sprites:
                if bullet_world_rect.colliderect(wall.rect):
                    bullet.kill()
                    break
        # Escalamos la superficie y la dibujamos en la pantalla
        scaled_surface = pygame.transform.scale(self.zoom_surface, 
                                             (SCREEN_WIDTH, SCREEN_HEIGHT))
                                             
        screen.blit(scaled_surface, (0, 0))
        # Dibujar el menú encima de todo si está visible
        self.player_menu.draw(screen)


    def handle_events(self, event_list):
        # Manejar eventos del menú primero
        self.player_menu.handle_events(event_list)
        
        if self.should_exit:
            return True

        # Miramos a ver si hay algún evento de salir del programa
        for event in event_list:
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.player_menu.show()
                    return False
                
        # Solo actualizar al jugador si el menú no está visible y no hay click bloqueado
        if not self.player_menu.visible and not self.player_menu.is_click_blocked():
            keys = pygame.key.get_pressed()
            self.player1.update_player(keys)              

        return False


    def check_collisions(self):
        # Check bullet collisions with walls using masks
        for bullet in self.bullets_group:
            # Usar la posición mundial de la bala directamente
            bullet_world_pos = bullet.get_world_position()
            
            bullet_world_rect = pygame.Rect(
                bullet_world_pos[0] - 2,
                bullet_world_pos[1] - 2,
                4, 4
            )
            
            for wall in self.walls_sprites:
                if bullet_world_rect.colliderect(wall.rect):
                    bullet.kill()
                    break

        # Check bullet collisions with enemies
        for bullet in self.bullets_group:
            # Usar la posición mundial de la bala
            bullet_world_pos = bullet.get_world_position()
            bullet_world_rect = pygame.Rect(
                bullet_world_pos[0],
                bullet_world_pos[1],
                bullet.rect.width,
                bullet.rect.height
            )
            
            for enemy in self.enemies_group:
                if enemy.alive and bullet_world_rect.colliderect(enemy.get_world_hitbox()):
                    enemy_center = (
                        enemy.position[0] + enemy.rect.width // 2,
                        enemy.position[1] + enemy.rect.height // 2
                    )
                    item = enemy.take_damage(bullet.damage)
                    if item:
                        item.position = pygame.math.Vector2(
                            enemy_center[0] - item.rect.width // 2,
                            enemy_center[1] - item.rect.height // 2
                        )
                        self.items_group.add(item)
                        self.dynamic_sprites_group.add(item)
                        self.all_sprites_group.add(item)
                    bullet.kill()
                    break

        # Check melee attack collisions
        if self.player1.is_melee_attacking:
            for enemy in self.enemies_group:
                if enemy.alive and self.player1.rect.colliderect(enemy.get_world_hitbox()):
                    print("Melee hit!")
                    item = enemy.take_damage(self.player1.melee_damage)
                    if item:
                        # Calculate enemy center
                        enemy_center = (
                            enemy.position[0] + enemy.rect.width // 2,
                            enemy.position[1] + enemy.rect.height // 2
                        )
                        # Adjust item position
                        item.position = pygame.math.Vector2(
                            enemy_center[0] - item.rect.width // 2,
                            enemy_center[1] - item.rect.height // 2
                        )
                        self.items_group.add(item)
                        self.dynamic_sprites_group.add(item)
                        self.all_sprites_group.add(item)
                    print(f"Melee hit! Damage: {self.player1.melee_damage}")

        # Check collisions between player and items
        player_world_rect = pygame.Rect(
            self.player1.position[0],
            self.player1.position[1],
            self.player1.rect.width,
            self.player1.rect.height
        )
        
        for item in self.items_group:
            item_world_rect = pygame.Rect(
                item.position.x,
                item.position.y,
                item.rect.width,
                item.rect.height
            )
            if player_world_rect.colliderect(item_world_rect):
                self.player1.collect_item(item)
                item.kill()
                print("Items collected")
        
        # Check collision with teleport walls
        for tp in self.tp_sprites:
            if player_world_rect.colliderect(tp.rect):
                # Clear bullets before changing phase
                self.bullets_group.empty()
                self.should_change_phase = True
                break


    def exit_game(self):
        self.should_exit = True