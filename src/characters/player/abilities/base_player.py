from .component import Component

class BasePlayer(Component):
    """Concrete Component that provides default implementations"""
    
    def __init__(self):
        self.base_stats = {
            "health": 100,
            "speed": 0.2,
            "damage_reduction": 0.0,
            "melee_damage": 0,
            "melee_cooldown": 0,
            "can_melee": False
        }

    def get_stats(self) -> dict:
        """Provides default implementation of stats"""
        return self.base_stats.copy()