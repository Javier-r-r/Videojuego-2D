import pygame
from pathlib import Path
from src.resources.resource_manager import ResourceManager
from src.resources.music_manager import MusicManager

class ShopScreen:
    def __init__(self, player):
        self.player = player
        self.music_manager = MusicManager()
        self.font_path = Path('assets') / 'fonts' / 'Cyberphont-2' / 'Cyberphont2.0.ttf'
        self.font = pygame.font.Font(self.font_path, 36)
        self.small_font = pygame.font.Font(self.font_path, 24)
        
        # Shop items: [name, cost, description, effect_function]
        self.items = [
            ["Health Upgrade", 1, "Increases max health by 20", self.upgrade_health],
            ["Speed Boost", 1, "Increases movement speed by 10%", self.upgrade_speed],
            ["Damage Reduction", 4, "Increases damage reduction by 5%", self.upgrade_defense]
        ]
        self.selected_item = 0

    def draw(self, screen):
        screen.fill((0, 0, 0))
        
        # Draw title
        title = self.font.render("SHOP", True, (255, 255, 255))
        screen.blit(title, (640 - title.get_width()//2, 100))
        
        # Draw coins
        coins_text = self.font.render(f"Coins: {self.player.coins_collected}", True, (255, 215, 0))
        screen.blit(coins_text, (50, 50))
        
        # Draw items with more spacing between title and description
        item_vertical_spacing = 180  # Increased from 150
        for i, (name, cost, desc, _) in enumerate(self.items):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            
            # Calculate base Y position for this item
            base_y = 250 + i * item_vertical_spacing
            
            # Draw item name and cost with larger font
            item_text = self.font.render(f"{name} - {cost} coins", True, color)
            screen.blit(item_text, (400, base_y))
            
            # Draw description with more padding and smaller font
            desc_text = self.small_font.render(desc, True, color)
            screen.blit(desc_text, (400, base_y + 75))  # Increased gap between title and description
        
        # Draw instructions at bottom
        instructions = self.small_font.render("Use UP/DOWN to select, ENTER to buy, ESC to continue", True, (255, 255, 255))
        screen.blit(instructions, (640 - instructions.get_width()//2, 850))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_item = (self.selected_item - 1) % len(self.items)
                elif event.key == pygame.K_DOWN:
                    self.selected_item = (self.selected_item + 1) % len(self.items)
                elif event.key == pygame.K_RETURN:
                    self.buy_item()
                elif event.key == pygame.K_ESCAPE:
                    return True
        return False

    def buy_item(self):
        item = self.items[self.selected_item]
        if self.player.coins_collected >= item[1]:
            self.player.coins_collected -= item[1]
            item[3]()  # Call the effect function
            
    def upgrade_health(self):
        stats = self.player.player_component.get_stats()
        # Incrementar la salud máxima en los stats
        stats["health"] += 20
        # Actualizar la salud actual del jugador al nuevo máximo
        self.player.health = stats["health"]
        # Actualizar los stats en el componente del jugador
        self.player.player_component.stats = stats
        self.player.notify_health_observers()

    def upgrade_speed(self):
        self.player.run_speed *= 1.1

    def upgrade_defense(self):
        self.player.damage_reduction = min(0.95, self.player.damage_reduction + 0.05)

    def run(self, display):
        running = True
        clock = pygame.time.Clock()
        continue_to_next_level = False
        
        # Cambiar a la música de la tienda
        self.music_manager.play_music('Amb_Loop-Extra_Strong.wav')
        
        while running:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return (None, False)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_item = (self.selected_item - 1) % len(self.items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_item = (self.selected_item + 1) % len(self.items)
                    elif event.key == pygame.K_RETURN:
                        self.buy_item()
                    elif event.key == pygame.K_ESCAPE:
                        continue_to_next_level = True
                        running = False
            
            self.draw(display)
            pygame.display.flip()
        
        # Detener la música al salir
        return (self.player, continue_to_next_level)
