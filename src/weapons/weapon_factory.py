# weapons/weapon_factory.py
from .pistol import Pistol
from .assault_rifle import AssaultRifle
from .shotgun import Shotgun

class WeaponFactory:
    @staticmethod
    def create_weapon(weapon_type: str, bullet_image: str = "bullets/default_bullet.png"):
        if weapon_type == "pistol":
            return Pistol(bullet_image)
        elif weapon_type == "assault_rifle":
            return AssaultRifle(bullet_image)
        elif weapon_type == "shotgun":
            return Shotgun(bullet_image)
        else:
            raise ValueError(f"Tipo de arma desconocido: {weapon_type}")
