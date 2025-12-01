import pygame
from src.characters.my_sprite import MySprite
from src.resources.resource_manager import ResourceManager

class AbilityIndicator(MySprite):
    def __init__(self):
        super().__init__()
        self.fixed_position = True
        
        # Load ability icons and scale them down
        original_melee = ResourceManager.LoadImage('abilities/melee_active.png')
        original_melee_cd = ResourceManager.LoadImage('abilities/melee_cooldown.png')
        original_enhanced = ResourceManager.LoadImage('abilities/enhanced_active.png')
        original_enhanced_cd = ResourceManager.LoadImage('abilities/enhanced_cooldown.png')
        
        # Scale icons to 20x20 pixels
        self.melee_icon = pygame.transform.scale(original_melee, (24, 24))
        self.melee_cooldown_icon = pygame.transform.scale(original_melee_cd, (24, 24))
        self.enhanced_icon = pygame.transform.scale(original_enhanced, (24, 24))
        self.enhanced_cooldown_icon = pygame.transform.scale(original_enhanced_cd, (24, 24))
        
        # Create smaller surface for both icons side by side
        self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # Initial state
        self.melee_ready = True
        self.enhanced_ready = True
        self.update_surface()
        
        # Set initial position (will be updated in fase12.py)
        self.position = (0, 0)
        self.rect.topleft = self.position

    def update_surface(self):
        """Update the indicator surface with current ability states"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Draw melee icon
        melee_icon = self.melee_icon if self.melee_ready else self.melee_cooldown_icon
        self.image.blit(melee_icon, (0, 0))
        
        # Draw enhanced body icon with small spacing
        enhanced_icon = self.enhanced_icon if self.enhanced_ready else self.enhanced_cooldown_icon
        self.image.blit(enhanced_icon, (25, 0))  # 5px spacing between icons

    def update_melee_status(self, is_ready):
        """Update melee ability status"""
        if self.melee_ready != is_ready:
            self.melee_ready = is_ready
            self.update_surface()

    def update_enhanced_status(self, is_ready):
        """Update enhanced body ability status"""
        if self.enhanced_ready != is_ready:
            self.enhanced_ready = is_ready
            self.update_surface()

    def set_position(self, pos):
        """Set the position of the ability indicator"""
        self.position = pos
        self.rect.topleft = pos