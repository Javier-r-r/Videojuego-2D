import pygame

class Weapon():

    # Clase base para todas las armas.
    def __init__(self, ammo, fire_behavior):
        self.fire_behavior = fire_behavior
        self.ammo = ammo
        self.max_ammo = ammo
        self.reload_time = 3  # Default reload time
        self.is_reloading = False
        self.reload_start_time = 0

    def get_max_ammo(self):
        return self.max_ammo

    def get_ammo(self):
        return self.ammo
    
    def set_ammo(self, ammo):
        self.ammo = ammo   

    def fire(self, bullets, x, y, target_x, target_y, can_shoot):
        if self.ammo > 0 and not self.is_reloading:  # Añadir comprobación de recarga
            if self.fire_behavior.fire(bullets, x, y, target_x, target_y, can_shoot):
                print("Disparo realizado!")
                self.ammo = self.ammo - 1
                print("Munición restante: ", self.ammo)

    def start_reload(self):
        if not self.is_reloading and self.ammo < self.max_ammo:
            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()
            return True
        return False

    def update_reload(self):
        if self.is_reloading:
            current_time = pygame.time.get_ticks()
            if current_time - self.reload_start_time >= self.reload_time * 1000:
                self.ammo = self.max_ammo
                self.is_reloading = False
                return True
        return False
