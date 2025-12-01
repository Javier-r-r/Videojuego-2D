# src/weapons/pistol.py
from .weapon import Weapon
from .fire_behavior import SingleShot

class Pistol(Weapon):
    def __init__(self, bullet_image):
        super().__init__(12, SingleShot(bullet_image))
        self.weapon_type = "pistol"
        self.reload_time = 3  # 3 seconds reload time
