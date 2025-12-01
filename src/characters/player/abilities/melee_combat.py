from .base_player import BasePlayer
from .ability_decorator import AbilityDecorator

class MeleeCombat(AbilityDecorator):
    """Concrete Decorator that adds Melee Combat ability"""
    
    def __init__(self, component: BasePlayer):
        super().__init__(component)

    def get_stats(self) -> dict:
        stats = super().get_stats()
        stats["melee_damage"] = 50
        stats["melee_cooldown"] = 5.0
        stats["can_melee"] = True
        return stats