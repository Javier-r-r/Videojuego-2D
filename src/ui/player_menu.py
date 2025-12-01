import pygame
from pygame.locals import *
from ..resources.resource_manager import ResourceManager
from ..resources.sound_manager import SoundManager
from ..resources.music_manager import MusicManager
from pathlib import Path

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        font_path = Path('assets') / 'fonts' / 'Cyberphont-2' / 'Cyberphont2.0.ttf'
        self.font = pygame.font.Font(str(font_path), 16)
        
        # Cargar imagen y coordenadas
        button_sheet = ResourceManager.LoadImage('image/menu_button01.png')
        coord_data = ResourceManager.LoadCoordinatesFile('image/coordButton.txt')
        
        # Procesar coordenadas
        coords = []
        for line in coord_data.split('\n'):
            if line.strip():
                x, y, w, h = map(int, line.split())
                coords.append((x, y, w, h))
                
        # Crear las imágenes recortadas
        self.normal_image = button_sheet.subsurface(pygame.Rect(*coords[0]))
        self.hover_image = button_sheet.subsurface(pygame.Rect(*coords[1]))
        
        # Escalar las imágenes
        self.normal_image = pygame.transform.scale(self.normal_image, (width, height))
        self.hover_image = pygame.transform.scale(self.hover_image, (width, height))
        
    def draw(self, surface):
        # Seleccionar la imagen según el estado
        current_image = self.hover_image if self.is_hovered else self.normal_image
        surface.blit(current_image, self.rect)
        # Renderizar el texto
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        # Convertir la posición del mouse considerando la posición real del menú
        if event.type == MOUSEMOTION:
            mouse_pos = event.pos
            # Ajustar la posición del mouse relativa al menú
            relative_pos = (
                mouse_pos[0] - self.rect.x,
                mouse_pos[1] - self.rect.y
            )
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                mouse_pos = event.pos
                if self.rect.collidepoint(mouse_pos):
                    return True
        return False

class VolumeSlider:
    def __init__(self, x, y, width, height, label="Volume"):
        self.rect = pygame.Rect(x, y, width, height)
        self.slider_rect = pygame.Rect(x, y, 20, height)
        self.value = 0.5  # 50% volume by default
        self.dragging = False
        self.label = label
        font_path = Path('assets') / 'fonts' / 'Cyberphont-2' / 'Cyberphont2.0.ttf'
        self.font = pygame.font.Font(str(font_path), 16)
        self.update_slider_position()
        self.on_value_changed = None  # Callback para cuando cambia el valor

    def update_slider_position(self):
        self.slider_rect.centerx = self.rect.left + (self.rect.width * self.value)

    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.dragging = True
                # Update value based on click position
                self.value = (event.pos[0] - self.rect.left) / self.rect.width
                self.value = max(0, min(1, self.value))
                self.update_slider_position()
                if self.on_value_changed:
                    self.on_value_changed(self.value)
                return True
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == MOUSEMOTION and self.dragging:
            # Update value based on drag position
            self.value = (event.pos[0] - self.rect.left) / self.rect.width
            self.value = max(0, min(1, self.value))
            self.update_slider_position()
            if self.on_value_changed:
                self.on_value_changed(self.value)
            return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, (34, 140, 148), self.rect)
        pygame.draw.rect(surface, (51, 224, 235), self.slider_rect)
        text = self.font.render(f"{self.label}: {int(self.value * 100)}%", True, (255, 255, 255))
        text_rect = text.get_rect(bottomleft=(self.rect.left, self.rect.top - 5))
        surface.blit(text, text_rect)

class PlayerMenu:
    def __init__(self, screen_width, screen_height):
        self.visible = False
        menu_width = 400
        menu_height = 300
        
        # Centrar el menú en la pantalla
        menu_x = (screen_width - menu_width) // 2
        menu_y = (screen_height - menu_height) // 2
        
        # Eliminamos la surface del menú ya que no la necesitaremos
        self.rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        
        # Crear botones con posiciones relativas al menú
        button_width = 200
        button_height = 50
        spacing = 30
        
        # Centrar los botones horizontalmente
        button_x = menu_x + (menu_width - button_width) // 2
        
        # Crear botón continuar (primero)
        self.continue_button = Button(
            button_x, menu_y + 50,
            button_width, button_height,
            "Continuar", (100, 100, 100), (150, 150, 150)
        )
        
        # Crear botón reiniciar (segundo)
        self.restart_button = Button(
            button_x, menu_y + 50 + (button_height + spacing),
            button_width, button_height,
            "Reiniciar", (100, 100, 100), (150, 150, 150)
        )

        # Crear botón salir (tercero)
        self.exit_button = Button(
            button_x, menu_y + 50 + (button_height + spacing) * 2,
            button_width, button_height,
            "Salir", (100, 100, 100), (150, 150, 150)
        )
        
        # Crear sliders de volumen
        slider_width = 200
        slider_height = 20
        slider_spacing = spacing  # Changed from spacing // 2 to spacing
        
        self.music_slider = VolumeSlider(
            button_x,
            menu_y + 50 + (button_height + spacing) * 3 + spacing,
            slider_width,
            slider_height,
            "Música"
        )
        
        self.effects_slider = VolumeSlider(
            button_x,
            menu_y + 50 + (button_height + spacing) * 3 + spacing * 3 + slider_height,  # Added more spacing
            slider_width,
            slider_height,
            "Efectos"
        )
        
        # Reemplazar la línea anterior de volume_slider con esto:
        self.volume_slider = self.music_slider
        
        self.callbacks = {
            'continue': None,
            'restart': None,
            'exit': None
        }
        self.last_continue_click = 0  # Añadir timestamp del último click

        # Configurar los callbacks de los sliders
        self.music_slider.on_value_changed = lambda value: MusicManager().set_volume(value)
        self.effects_slider.on_value_changed = lambda value: SoundManager().set_volume(value)

    def set_callback(self, button_type, callback):
        self.callbacks[button_type] = callback

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def handle_events(self, events):
        if not self.visible:
            return
            
        current_time = pygame.time.get_ticks()
        for event in events:
            if self.music_slider.handle_event(event):
                continue
            if self.effects_slider.handle_event(event):
                continue
            if self.continue_button.handle_event(event):
                if self.callbacks['continue']:
                    self.last_continue_click = current_time
                    self.callbacks['continue']()
                return True  # Consumir el evento
            elif self.restart_button.handle_event(event):
                if self.callbacks['restart']:
                    self.callbacks['restart']()
                return True
            elif self.exit_button.handle_event(event):
                if self.callbacks['exit']:
                    self.callbacks['exit']()

    def is_click_blocked(self):
        return pygame.time.get_ticks() - self.last_continue_click < 200  # 200ms de delay

    def draw(self, screen):
        if not self.visible:
            return
        
        # Dibujar solo el overlay semi-transparente de la pantalla completa
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Dibujar botones y slider directamente en la pantalla
        self.continue_button.draw(screen)
        self.restart_button.draw(screen)
        self.exit_button.draw(screen)
        self.music_slider.draw(screen)
        self.effects_slider.draw(screen)
