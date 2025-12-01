# -*- coding: utf-8 -*-

import pygame
from src.characters.non_playable_characters.enemy_lvl1 import Enemy_lvl1
from src.characters.non_playable_characters.boss1 import FinalBossLvl1
from src.markers.health_bar import HealthBar
from src.markers.bullet_counter import BulletCounter
from src.markers.weapon_indicator import WeaponIndicator
from pygame.locals import *
from src.resources.resource_manager import *
from src.map.tilemap import *
from src.ui.player_menu import PlayerMenu
from src.markers.coin_counter import CoinCounter
from src.markers.boss_health_bar import BossHealthBar
from src.resources.music_manager import MusicManager
from src.weapons.weapon_factory import WeaponFactory
from src.markers.ability_indicator import AbilityIndicator
from src.characters.player.abilities.melee_combat import MeleeCombat

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

class Fase14:
    def __init__(self, player):
        # Añadir rifle de asalto si no lo tiene
        has_rifle = any(weapon.weapon_type == "assault_rifle" for weapon in player.weapons)
        if not has_rifle:
            assault_rifle = WeaponFactory.create_weapon("assault_rifle", "bullets/08.png")
            player.weapons.append(assault_rifle)
            print("¡Nueva arma desbloqueada: Rifle de Asalto!")
        
        self.player1 = player
        self.boss = None
        self.boss_spawned = False
        self.boss_health_bar = None
        self.should_change_phase = False
        self.should_go_back = False  # Add this line
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
    
        self.tilemap = TileMap("Level1", "Level1_4.tmx")
        self.walls_sprites = pygame.sprite.Group()
        
        # Inicializar lista de muros
        self.tilemap.load_layer_by_name("Colissions", self.walls_sprites)

        self.items_group = pygame.sprite.Group()
        self.player1.set_walls(self.walls_sprites)

        # Que parte del decorado estamos visualizando
        self.scroll = [0, 0]  # [scrollx, scrolly]
        self.zoom_scale = 2  # Factor de zoom

        # Creamos la barra de vida y los contadores de balas
        self.health_bar = HealthBar()   
        self.health_bar.set_position((0,0))
        
        # Create and position ability indicator aligned with health bar
        self.ability_indicator = AbilityIndicator()
        self.ability_indicator.set_position((
            self.health_bar.rect.width + 5,  # 5px spacing from health bar
            self.health_bar.rect.top          # Same vertical position as health bar
        ))
        self.player1.add_ability_observer(self.ability_indicator)
        
        self.bullet_counter = BulletCounter()
        self.bullet_counter.set_position((0, 25))

        # Creamos los sprites de los jugadores
        self.bullets_group = self.player1.bullets  # Usar el grupo de balas del jugador

        self.weapon_indicator = WeaponIndicator(self.player1.weapons)
        self.weapon_indicator.set_position((0, 45))

        self.coin_counter = CoinCounter()
        self.coin_counter.set_position((0, SCREEN_HEIGHT // self.zoom_scale - 20))  # Adjust for zoom scale

        self.player_group = pygame.sprite.Group(self.player1)
        
        # Registrar el callback para cuando el jugador muera
        self.player1.set_on_death_callback(self.show_game_over_screen)

        # Ponemos a los jugadores en sus posiciones iniciales
        self.player1.set_position((100, 250))

        # Vincular los observadores al jugador
        self.health_bar.set_position((0,0))
        self.player1.add_health_observer(self.health_bar)
        
        self.bullet_counter.set_position((0, 25))
        self.player1.add_bullets_observer(self.bullet_counter)
        
        self.weapon_indicator.set_position((0, 45))
        self.player1.add_weapon_observer(self.weapon_indicator)
        self.player1.notify_weapon_change()  # Update weapon indicator
        
        self.coin_counter.set_position((0, SCREEN_HEIGHT // self.zoom_scale - 20))
        self.player1.add_coin_observer(self.coin_counter)

        # Creamos un grupo con los Sprites que se mueven
        #  En este caso, solo los personajes, pero podría haber más (proyectiles, etc.)
        self.dynamic_sprites_group = pygame.sprite.Group(self.player1, self.bullets_group)
        # Creamos otro grupo con todos los Sprites
        self.all_sprites_group = pygame.sprite.Group(
            self.player1, 
            self.bullets_group, 
            self.bullet_counter, 
            self.health_bar,
            self.ability_indicator,  # Add ability indicator here
            self.items_group, 
            self.coin_counter,
            self.weapon_indicator
        )

        # Añadir después de inicializar grupos de sprites

        self.view_size = (SCREEN_WIDTH // self.zoom_scale, SCREEN_HEIGHT // self.zoom_scale)  # Tamaño de la vista antes del zoom
        self.zoom_surface = pygame.Surface(self.view_size)

        # Crear y configurar el jefe final
        self.boss = FinalBossLvl1(self.walls_sprites)
        self.boss.set_position((470, 90))
        
        # Crear y configurar la barra de vida del jefe
        self.boss_health_bar = BossHealthBar()
        self.boss_health_bar.set_position((50, SCREEN_HEIGHT // self.zoom_scale - 20))
        self.boss.add_health_observer(self.boss_health_bar)
        
        # Agregar el jefe y su barra de vida a los grupos de sprites
        self.enemies_group = pygame.sprite.Group(self.boss)
        self.dynamic_sprites_group.add(self.enemies_group)
        self.all_sprites_group.add(self.enemies_group)
        self.all_sprites_group.add(self.boss_health_bar)
        
        self.boss_spawned = True
        
    def reset(self):
        # Reiniciar todos los elementos del juego
        self.all_sprites_group.empty()
        self.bullets_group.empty()
        self.enemies_group.empty()
        self.items_group.empty()
        self.boss = None
        self.boss_spawned = False
        self.player1.reload_all_weapons()  # Recargar todas las armas
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
        # Actualizar primero los enemigos
        for enemy in self.enemies_group:
            if isinstance(enemy, FinalBossLvl1):
                result = enemy.update(time, self.player1)
                # Guardamos una referencia al jefe para verificar su estado después
                current_boss = enemy
                if result == "spawn_minions":
                    # Generar 4 minions en las posiciones calculadas
                    spawn_positions = enemy.get_minion_spawn_positions()
                    for pos in spawn_positions:
                        minion = Enemy_lvl1(self.walls_sprites, "items/Coin.png", "items/coordCoin.txt", 10)
                        minion.set_position(pos)
                        self.enemies_group.add(minion)
                        self.dynamic_sprites_group.add(minion)
                        self.all_sprites_group.add(minion)
            else:
                enemy.update(time, self.player1)
                
        # Actualizar el jugador y otros sprites dinámicos que no sean enemigos
        self.player1.update(time)
        # Actualizar balas y mantener el scroll actualizado para cada una
        for bullet in self.bullets_group:
            bullet.scroll = self.scroll
            bullet.update()
        self.items_group.update()

        # Add collision detection after updating positions but before scroll
        self.check_collisions()

        # Verificar el estado del jefe después de las actualizaciones
        if hasattr(self, 'boss') and self.boss and not self.boss.alive and self.boss.death_animation_completed:
            self.show_boss_choice()

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
        
        # Dibujar los proyectiles del jefe si existe
        if self.boss and self.boss.alive:
            self.boss.draw_projectiles(self.zoom_surface, self.scroll)
            
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
                elif event.key == pygame.K_p:  # Add P key check
                    self.should_change_phase = True
                
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
                    # Skip collision if enemy is boss and invisible
                    if isinstance(enemy, FinalBossLvl1) and enemy.is_invisible:
                        continue
                        
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
                         
        # Check boss projectile collisions with player
        if self.boss and self.boss.alive:
            player_world_rect = pygame.Rect(
                self.player1.position[0],
                self.player1.position[1],
                self.player1.rect.width,
                self.player1.rect.height
            )
            
            for projectile in self.boss.projectiles:
                if projectile['active']:
                    proj_rect = self.boss.get_projectile_rect(projectile)
                    if proj_rect.colliderect(player_world_rect):
                        self.player1.take_damage(self.boss.projectile_damage)
                        projectile['active'] = False

    def show_boss_choice(self):
        # Obtener la superficie de la pantalla
        screen = pygame.display.get_surface()
        
        # Crear el texto principal
        font = pygame.font.Font(None, 74)
        text = font.render("You have defeated the boss", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 100))
        
        # Crear los botones
        button_font = pygame.font.Font(None, 50)
        spare_text = button_font.render("Forgive", True, (0, 255, 0))
        execute_text = button_font.render("Execute", True, (255, 0, 0))
        
        spare_rect = spare_text.get_rect(center=(screen.get_width() / 3, screen.get_height() / 2 + 50))
        execute_rect = execute_text.get_rect(center=(2 * screen.get_width() / 3, screen.get_height() / 2 + 50))
        
        # Bucle de espera para la elección
        waiting = True
        while waiting:
            screen.fill((0, 0, 0))  # Fondo negro
            screen.blit(text, text_rect)
            screen.blit(spare_text, spare_rect)
            screen.blit(execute_text, execute_rect)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if spare_rect.collidepoint(mouse_pos):
                        waiting = False
                        # Show message about the new ability
                        message = [
                            "As a token of gratitude for sparing his life,",
                            "the boss grants you a bionic enhancement.",
                            "",
                            "Press Q to activate enhanced body mode.",
                            "While active, you'll deal damage to enemies during dash,",
                            "but be careful - they can hurt you too!"
                        ]
                        
                        # Create a semi-transparent background
                        info_surface = pygame.Surface((screen.get_width(), screen.get_height()))
                        info_surface.fill((0, 0, 0))
                        info_surface.set_alpha(200)
                        screen.blit(info_surface, (0, 0))
                        
                        # Render and display each line
                        message_font = pygame.font.Font(None, 36)
                        y_offset = screen.get_height() // 3
                        for line in message:
                            text = message_font.render(line, True, (255, 255, 255))
                            text_rect = text.get_rect(center=(screen.get_width() // 2, y_offset))
                            screen.blit(text, text_rect)
                            y_offset += 40
                            
                        # Add a continue prompt
                        continue_text = message_font.render("Press any key to continue", True, (255, 255, 255))
                        continue_rect = continue_text.get_rect(center=(screen.get_width() // 2, y_offset + 40))
                        screen.blit(continue_text, continue_rect)
                        pygame.display.flip()
                        
                        # Wait for key press
                        waiting_key = True
                        while waiting_key:
                            for evt in pygame.event.get():
                                if evt.type == pygame.KEYDOWN or evt.type == pygame.MOUSEBUTTONDOWN:
                                    waiting_key = False
                                elif evt.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                        
                        # Continue with original logic
                        self.player1.add_ability(MeleeCombat)
                        self.bullets_group.empty()
                        self.should_change_phase = True
                        
                    elif execute_rect.collidepoint(mouse_pos):
                        waiting = False
                        print("Has ejecutado al jefe. No has obtenido ninguna habilidad.")
                        self.bullets_group.empty()  # Clear bullets before phase change
                        self.should_change_phase = True

    def exit_game(self):
        # Remove music stop since MusicManager will handle it globally
        self.should_exit = True