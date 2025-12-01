import pygame

class MySprite(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.position = (0, 0)
        self.velocity = (0, 0)
        self.scroll = [0, 0]
        self.fixed_position = False  # Nueva bandera

    def set_position(self, position):
        self.position = position

    def set_screen_position(self, scroll):
        self.scroll = scroll
        if not self.fixed_position:  # Solo actualizar con scroll si no es posición fija
            self.rect.x = self.position[0] - self.scroll[0]
            self.rect.y = self.position[1] - self.scroll[1]
        else:
            self.rect.x = self.position[0]
            self.rect.y = self.position[1]

    def increment_position(self, increment):
        (posx, posy) = self.position
        (incrementx, incrementy) = increment
        self.set_position((posx+incrementx, posy+incrementy))

    def update(self, time):
        incrementx = self.velocity[0]*time
        incrementy = self.velocity[1]*time
        self.increment_position((incrementx, incrementy))