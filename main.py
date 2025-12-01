#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Importar modulos
import pygame
from fase12 import *
from fase13 import Fase13
from fase14 import Fase14
from src.map.tilemap import *
from pathlib import Path
from src.resources.resource_manager import ResourceManager
from fase11 import Fase11
from fase14 import Fase14
from src.resources.music_manager import MusicManager
from src.screens.shop_screen import ShopScreen
from src.screens.start_screen import StartScreen
from src.screens.loading_screen import LoadingScreen
from src.director.director import Director

if __name__ == '__main__':
    # Inicializar pygame
    pygame.init()
    pygame.mixer.init()  # Inicializar el módulo de sonido

    # Cargar y establecer el cursor personalizado
    cursor_path = Path('assets') / 'crosshair' / 'crosshair.png'
    cursor_img = pygame.image.load(str(cursor_path))
    cursor = pygame.cursors.Cursor((0, 0), cursor_img)
    pygame.mouse.set_cursor(cursor)

    # Crear la pantalla
    display = pygame.display.set_mode((1280, 960), 0, 32)

    # Creamos el objeto reloj para sincronizar el juego
    clock = pygame.time.Clock()

    # Run start screen
    start_screen = StartScreen()
    if not start_screen.run(display):
        pygame.quit()
        sys.exit()

    # Inicializar pantalla de carga
    loading_screen = LoadingScreen()

    # Creamos la fase inicial y el director
    fase11 = Fase11()
    player = fase11.player1
    director = Director()
    
    # Configurar las fases en el director
    level1_fases = [fase11, lambda: Fase12(player), lambda: Fase13(player), lambda: Fase14(player)]
    level2_fases = [lambda: Fase12(player), lambda: Fase12(player), lambda: Fase13(player), lambda: Fase14(player)]
    director.set_fases(level1_fases, level2_fases)

    # El bucle de eventos del juego principal
    while True:
        # Sincronizar el juego a 60 fps
        elapsed_time = clock.tick(60)
        
        # Manejar eventos
        if director.current_fase.handle_events(pygame.event.get()):
            pygame.quit()
            sys.exit()

        # Actualiza la escena si el menú no está visible
        if not director.current_fase.player_menu.visible:
            if director.current_fase.update(elapsed_time):
                pygame.quit()
                sys.exit()
            
            # Check for phase transition
            if director.current_fase.should_change_phase:
                if not director.change_fase(display):
                    pygame.quit()
                    sys.exit()

        # Se dibuja en pantalla
        director.current_fase.draw(display)
        pygame.display.flip()