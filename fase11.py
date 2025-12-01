import pygame
from src.characters.player.player import Player
from src.markers.health_bar import HealthBar
from src.markers.bullet_counter import BulletCounter
from src.markers.weapon_indicator import WeaponIndicator
from pygame.locals import *
from src.resources.resource_manager import *
from src.map.tilemap import *
from src.ui.player_menu import PlayerMenu
from src.markers.coin_counter import CoinCounter
from pathlib import Path
from src.characters.player.abilities.enhanced_body import EnhancedBody
from src.characters.player.abilities.melee_combat import MeleeCombat
from src.resources.music_manager import MusicManager
from src.characters.non_playable_characters.boss2 import FinalBossLvl2
from src.markers.boss_health_bar import BossHealthBar  # Nueva importación

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 960

# Los bordes de la pantalla para hacer scroll
SCROLL_MARGIN_X = SCREEN_WIDTH // 4  # 320 pixels desde los bordes
SCROLL_MARGIN_Y = SCREEN_HEIGHT // 4  # 240 pixels desde los bordes

class Fase11:
    def __init__(self):
        self.music_manager = MusicManager()
        self.initialize()
        # Crear el menú del jugador
        self.player_menu = PlayerMenu(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player_menu.set_callback('continue', self.resume_game)
        self.player_menu.set_callback('restart', self.reset)
        self.player_menu.set_callback('exit', self.exit_game)
        self.should_exit = False
        self.tp_sprites = pygame.sprite.Group()
        self.tilemap.load_layer_by_name("Up level", self.tp_sprites)
        self.should_change_phase = False

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
    
        self.tilemap = TileMap("Level1", "Level1_1.tmx")
        self.walls_sprites = pygame.sprite.Group()
        # Inicializar lista de muros
        self.tilemap.load_layer_by_name("Collisions", self.walls_sprites)

        self.items_group = pygame.sprite.Group()
        
        # Crear grupo de jefes y añadir el BladeBoosLvl2
        # self.boss_group = pygame.sprite.Group()
        # self.boss2 = FinalBossLvl2(self.walls_sprites)
        # self.boss2.set_position((800, 450))  # Posición del jefe

        # Que parte del decorado estamos visualizando
        self.scroll = [0, 0]  # [scrollx, scrolly]
        self.zoom_scale = 2  # Factor de zoom

        # Crear y configurar la barra de vida del jefe
        # self.boss_health_bar = BossHealthBar()
        # self.boss_health_bar.set_position((SCREEN_WIDTH // (2 * self.zoom_scale), 10))
        # self.boss2.add_health_observer(self.boss_health_bar)
        
        # self.boss_group.add(self.boss2)

        # Creamos la barra de vida y los contadores de balas
        self.health_bar = HealthBar()   
        self.health_bar.set_position((0,0))
        self.bullet_counter = BulletCounter()
        self.bullet_counter.set_position((0, 25))

        
        # Create the base player first
        self.bullets_group = pygame.sprite.Group()
        self.player1 = Player(self.bullets_group, self.walls_sprites, ["pistol"])
        self.player1.set_walls(self.walls_sprites)

        
        # Create UI elements
        self.weapon_indicator = WeaponIndicator(self.player1.weapons)
        self.weapon_indicator.set_position((0, 45))

        self.coin_counter = CoinCounter()
        self.coin_counter.set_position((0, SCREEN_HEIGHT // self.zoom_scale - 20))  # Adjust for zoom scale

        self.player1.add_bullets_observer(self.bullet_counter)
        self.player1.add_health_observer(self.health_bar)
        self.player1.add_weapon_observer(self.weapon_indicator)
        self.player1.add_coin_observer(self.coin_counter)
        
        self.player_group = pygame.sprite.Group(self.player1)

        # Ponemos a los jugadores en sus posiciones iniciales
        self.player1.set_position((50, 450))

        # Creamos un grupo con los Sprites que se mueven
        #  En este caso, solo los personajes, pero podría haber más (proyectiles, etc.)
        self.dynamic_sprites_group = pygame.sprite.Group(self.player1, self.bullets_group)
        # Creamos otro grupo con todos los Sprites
        self.all_sprites_group = pygame.sprite.Group(self.player1, self.bullets_group, 
                                                   self.bullet_counter, self.health_bar, 
                                                   self.items_group, self.coin_counter)  # Añadir boss_group
        self.all_sprites_group.add(self.weapon_indicator)

        # Añadir después de inicializar grupos de sprites

        self.view_size = (SCREEN_WIDTH // self.zoom_scale, SCREEN_HEIGHT // self.zoom_scale)  # Tamaño de la vista antes del zoom
        self.zoom_surface = pygame.Surface(self.view_size)
        
    def reset(self):
        # Reiniciar todos los elementos del juego
        self.all_sprites_group.empty()
        self.bullets_group.empty()
        self.items_group.empty()
        self.player1.reload_all_weapons()  # Recargar todas las armas
        self.initialize()         
        self.player_menu.hide()
        self.player_menu.last_continue_click = pygame.time.get_ticks()

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

    def update(self, time):
        
        # Actualizar el jugador y otros sprites dinámicos que no sean enemigos
        self.player1.update(time)
        
        # Actualizar balas y mantener el scroll actualizado para cada una
        for bullet in self.bullets_group:
            bullet.scroll = self.scroll
            bullet.update()
        
        self.items_group.update()

        # Actualizar jefes
        # for boss in self.boss_group:
        #     boss.update(time, self.player1)

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
        self.zoom_surface.fill((0, 0, 0))
        
        # Dibujamos el mapa
        self.tilemap.draw(self.zoom_surface)
        
        # Dibujamos los sprites sin las balas
        for sprite in self.all_sprites_group:
            if sprite not in self.bullets_group:
                self.zoom_surface.blit(sprite.image, sprite.rect)
        
        # Dibujamos las balas por separado
        for bullet in self.bullets_group:
            self.zoom_surface.blit(bullet.image, bullet.rect)

        # Dibujamos las cuchillas del jefe si existe
        # if hasattr(self, 'boss2') and self.boss2.alive:
        #     self.boss2.draw_blades(self.zoom_surface, self.scroll)

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
            if keys[pygame.K_p]:
                self.bullets_group.empty()
                self.should_change_phase = True
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

        # Colisiones entre jugador y cuchillas del jefe
        # if hasattr(self, 'boss2') and self.boss2.alive:
        #     player_rect = self.player1.get_world_hitbox()
        #     for blade in self.boss2.blades:
        #         if blade['active']:
        #             blade_rect = self.boss2.get_blade_rect(blade)
        #             if player_rect.colliderect(blade_rect):
        #                 self.player1.take_damage(self.boss2.blade_damage)
        #                 blade['active'] = False

        # Check collisions between bullets and boss
        for bullet in self.bullets_group:
            bullet_rect = pygame.Rect(
                bullet.rect.centerx + self.scroll[0],
                bullet.rect.centery + self.scroll[1],
                bullet.rect.width,
                bullet.rect.height
            )
            # for boss in self.boss_group:
            #     if boss.alive and boss.get_world_hitbox().colliderect(bullet_rect):
            #         boss.take_damage(bullet.damage)
            #         bullet.kill()
            #         break

    def exit_game(self):
        self.should_exit = True