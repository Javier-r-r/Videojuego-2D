# src/weapons/assault_rifle.py
from .weapon import Weapon
from .fire_behavior import AutomaticFire

class AssaultRifle(Weapon):
    def __init__(self, bullet_image):
        super().__init__(30, AutomaticFire(bullet_image))
        self.weapon_type = "assault_rifle"
        self.reload_time = 7  # 7 seconds reload time
