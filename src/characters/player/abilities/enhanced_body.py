import pygame
from .base_player import BasePlayer
from .ability_decorator import AbilityDecorator

class EnhancedBody(AbilityDecorator):
    """Concrete Decorator that adds Enhanced Body ability"""
    
    def __init__(self, component: BasePlayer):
        super().__init__(component)
        self.is_active = False
        self.activation_time = 0
        self.duration = 10000
        self.cooldown = 20000
        self.last_use = 0
        self.original_stats = None

    def get_stats(self) -> dict:
        stats = super().get_stats()
        if self.is_active:
            stats["health"] += 50
            stats["speed"] *= 1.2
            stats["damage_reduction"] += 0.2
        return stats

    def activate(self, player) -> bool:
        current_time = pygame.time.get_ticks()
        
        if self.is_active:
            remaining_time = (self.activation_time + self.duration - current_time) / 1000
            print(f"Enhanced Body already active! {remaining_time:.1f}s remaining")
            return False
            
        if current_time - self.last_use < self.cooldown:
            remaining_cooldown = (self.cooldown - (current_time - self.last_use)) / 1000
            print(f"Enhanced Body on cooldown! {remaining_cooldown:.1f}s remaining")
            return False

        # Store current stats before buffing
        self.original_stats = {
            "health": player.health,
            "speed": player.run_speed,
            "damage_reduction": player.damage_reduction
        }

        # Apply buffs
        player.health += 50
        player.run_speed *= 1.2
        player.damage_reduction += 0.2

        self.is_active = True
        self.activation_time = current_time
        self.last_use = current_time
        
        print("\n=== Enhanced Body Activated! ===")
        print(f"Health: {self.original_stats['health']} -> {player.health}")
        print(f"Speed: {self.original_stats['speed']:.2f} -> {player.run_speed:.2f}")
        print(f"Damage Reduction: {self.original_stats['damage_reduction']:.2f} -> {player.damage_reduction:.2f}")
        print("Duration: 10 seconds")
        print("==============================\n")
        return True

    def deactivate(self, player):
        if not self.is_active or not self.original_stats:
            return

        # Restore original stats, except health
        player.run_speed = self.original_stats["speed"]
        player.damage_reduction = self.original_stats["damage_reduction"]
        
        self.is_active = False
        self.original_stats = None
        print("\nEnhanced Body buff has worn off!")

    def check_duration(self, player):
        """Check if ability duration has expired"""
        if not self.is_active:
            return False
            
        current_time = pygame.time.get_ticks()
        if current_time - self.activation_time > self.duration:
            self.deactivate(player)
            return True
        return False