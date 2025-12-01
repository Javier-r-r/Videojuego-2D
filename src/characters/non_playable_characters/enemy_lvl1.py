import pygame
from src.characters.character import Character
from src.characters.non_playable_characters.enemy import Enemy
from src.characters.constants import *
from src.resources.sound_manager import SoundManager  # Add this import

# NonPlayerCharacter Class

class Enemy_lvl1(Enemy):
    def __init__(self, walls, items_image, items_coord, damage):
        super().__init__(
            walls,
            items_image, 
            items_coord,
            'enemies/Slime2/Slime2.png',
            'enemies/Slime2/coordSlime.txt',
            [8, 8, 8, 8, 6, 6, 6, 6, 10, 10, 10, 10, 11, 11, 11, 11, 5, 5, 5, 5],
            (ANIMATION_SPEED * 1.5),
        )
        # Specific attributes for Enemy_lvl1
        self.attack_range = 25
        self.perception_range = 150
        self.max_health = 25
        self.current_health = self.max_health
        self.damage = damage
        self.sound_manager = SoundManager()

    def attack(self, player):
        current_time = pygame.time.get_ticks()
        self.velocity = (0, 0)
        self.last_attack_time = current_time
        self.attacking = True
        self.attack_frame = 0
        player.take_damage(self.damage)
        self.sound_manager.play_sound('slime_attack')
        print(f"Enemy_lvl1 attacked player! Player health: {player.health}")  # Debug print