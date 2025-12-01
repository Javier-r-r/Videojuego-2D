# src/weapons/shotgun.py
from .weapon import Weapon
from .fire_behavior import ShotgunFire

class Shotgun(Weapon):
    def __init__(self, bullet_image):
        super().__init__(6, ShotgunFire(bullet_image))
        self.weapon_type = "shotgun"
        self.reload_time = 5  # 5 seconds reload time
