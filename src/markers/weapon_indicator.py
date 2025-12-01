import pygame
from src.characters.my_sprite import MySprite
from src.resources.resource_manager import ResourceManager


class WeaponIndicator(MySprite):
    def __init__(self, player_weapons):
        super().__init__()
        self.fixed_position = True  # Marcar como posición fija
        self.weapons_icons = {}
        self.weapons_reload_icons = {}
        
        # Map weapon objects to their respective icons
        for weapon in player_weapons:
            self.weapons_icons[weapon] = ResourceManager.LoadImage(f'weapons/{weapon.weapon_type}.png')
            self.weapons_reload_icons[weapon] = ResourceManager.LoadImage(f'weapons/{weapon.weapon_type}_reload.png')
        
        self.current_weapon = player_weapons[0]
        self.image = self.weapons_icons[self.current_weapon]
        self.rect = self.image.get_rect()
        
        # Position in the HUD (bottom right corner)
        self.rect.bottomleft = self.position

    def update(self, Subject):
        weapon = Subject.current_weapon
        # Update the weapon indicator when player switches weapons 
        if weapon in self.weapons_icons:
            self.current_weapon = weapon
            # Check if weapon is reloading to show appropriate icon
            if weapon.is_reloading:
                self.image = self.weapons_reload_icons[weapon]
            else:
                self.image = self.weapons_icons[weapon]
