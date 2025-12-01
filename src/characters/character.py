import pygame
from src.characters.constants import *
from src.characters.my_sprite import MySprite
from src.resources.resource_manager import ResourceManager


class Character(MySprite):
    "Cualquier personaje del juego"

    # Parametros pasados al constructor de esta clase:
    #  Archivo con la hoja de Sprites
    #  Archivo con las coordenadoas dentro de la hoja
    #  Numero de imagenes en cada postura
    #  Velocidad de caminar y de salto
    #  Retardo para mostrar la animacion del personaje
    def __init__(self, image_file, coordinates_file, num_images, animation_delay):

        # Primero invocamos al constructor de la clase padre
        MySprite.__init__(self)
        self.alive = True
        self.death_timer = 0

        # Cargamos las hojas de sprites
        self.sprite_sheet = ResourceManager.LoadImage(image_file, -1)
        
        self.sprite_sheet = self.sprite_sheet.convert_alpha()
        
        # Inicializamos con idle mirando hacia abajo
        self.movement = IDLE
        self.facing = DOWN
        self.numPosture = DOWN_ROW
        self.numImagePosture = 0

        # Leemos las coordenadas de un archivo de texto
        data = ResourceManager.LoadCoordinatesFile(coordinates_file)
        data = data.split()
        self.numPosture = 1
        self.numImagePosture = 0
        count = 0
        self.sheet_coordinates = []
        
        # Cargar las coordenadas usando num_images para saber el número de frames por línea
        for line in range(0, len(num_images)):
            self.sheet_coordinates.append([])
            tmp = self.sheet_coordinates[line]
            frames_in_line = num_images[line]
            
            for frame in range(frames_in_line):
                if count + 3 < len(data):
                    tmp.append(pygame.Rect((int(data[count]), int(data[count+1])), 
                                         (int(data[count+2]), int(data[count+3]))))
                    count += 4

        # El retardo a la hora de cambiar la imagen del Sprite (para que no se mueva demasiado rápido)
        self.movement_delay = 0

        # En que postura esta inicialmente
        self.numPosture = IDLE

        # El rectangulo del Sprite
        self.rect = pygame.Rect(100,100,self.sheet_coordinates[self.numPosture][self.numImagePosture][2],self.sheet_coordinates[self.numPosture][self.numImagePosture][3])

        # Las velocidades de caminar y salto
        self.run_speed = 0.2

        # El retardo en la animacion del personaje (podria y deberia ser distinto para cada postura)
        self.animation_delay = animation_delay

        # Y actualizamos la postura del Sprite inicial, llamando al metodo correspondiente
        self.update_posture()

        # Establecemos la imagen inicial con idle
        self.image = self.sprite_sheet.subsurface(self.sheet_coordinates[self.numPosture][self.numImagePosture])


    # Metodo base para realizar el movimiento: simplemente se le indica cual va a hacer, y lo almacena
    def move(self, movement):
        self.movement = movement


    def update_posture(self):
        self.movement_delay -= 1
        if self.movement_delay < 0:
            self.movement_delay = self.animation_delay

            if not self.alive:
                self._handle_death_animation()
            elif hasattr(self, 'is_shooting') and self.is_shooting:
                self._handle_shoot_animation()
            elif hasattr(self, 'is_melee_attacking') and self.is_melee_attacking:
                self._handle_melee_animation()
            elif hasattr(self, 'is_hurt') and self.is_hurt:
                self._handle_hurt_animation()
            elif hasattr(self, 'attacking') and self.attacking:
                self._handle_attack_animation()
            else:
                self._handle_movement_animation()

            # Actualizar sprite con comprobación de seguridad
            if (0 <= self.numPosture < len(self.sheet_coordinates) and 
                0 <= self.numImagePosture < len(self.sheet_coordinates[self.numPosture])):
                self.image = self.sprite_sheet.subsurface(self.sheet_coordinates[self.numPosture][self.numImagePosture])

    def _handle_death_animation(self):
        death_base_row = DEATH_SPRITE + 1
        if self.facing == DOWN:
            self.numPosture = death_base_row 
        elif self.facing == LEFT_DOWN:
            self.numPosture = death_base_row + 1
        elif self.facing == RIGHT_DOWN:
            self.numPosture = death_base_row + 2
        elif self.facing == UP:
            self.numPosture = death_base_row + 3

        if self.numImagePosture < len(self.sheet_coordinates[self.numPosture]) - 1:
            self.numImagePosture += 1
        elif hasattr(self, 'death_animation_completed') and not self.death_animation_completed:
            self.death_animation_completed = True
            if hasattr(self, 'handle_death'):
                self.handle_death()
            else:
                self.kill()

    def _handle_movement_animation(self):
        self.numImagePosture += 1
        if self.velocity[0] == 0 and self.velocity[1] == 0:
            base_row = 4  # Animaciones idle
        else:
            base_row = 0  # Animaciones de movimiento

        # Ajustar postura según dirección
        if self.facing == DOWN:
            self.numPosture = base_row + DOWN_ROW
        elif self.facing == LEFT_DOWN:
            self.numPosture = base_row + LEFT_ROW
        elif self.facing == RIGHT_DOWN:
            self.numPosture = base_row + RIGHT_ROW
        elif self.facing == UP:
            self.numPosture = base_row + UP_ROW

        # Loop de animación
        if self.numImagePosture >= len(self.sheet_coordinates[self.numPosture]):
            self.numImagePosture = 0

    def _handle_attack_animation(self):
        # Manejar animación de ataque
        if self.facing == DOWN:
            self.numPosture = ATTACK_SPRITE
        elif self.facing == LEFT_DOWN:
            self.numPosture = ATTACK_SPRITE + 1
        elif self.facing == RIGHT_DOWN:
            self.numPosture = ATTACK_SPRITE + 2
        elif self.facing == UP:
            self.numPosture = ATTACK_SPRITE + 3

        self.numImagePosture += 1
        if self.numImagePosture >= len(self.sheet_coordinates[self.numPosture]):
            self.numImagePosture = 0
            self.attacking = False

    def _handle_melee_animation(self):
        """Maneja la animación del ataque cuerpo a cuerpo"""
        if self.facing == DOWN:
            self.numPosture = MELEE_DOWN_ROW
        elif self.facing == LEFT_DOWN:
            self.numPosture = MELEE_LEFT_ROW
        elif self.facing == RIGHT_DOWN:
            self.numPosture = MELEE_RIGHT_ROW
        elif self.facing == UP:
            self.numPosture = MELEE_UP_ROW

        if self.numImagePosture < len(self.sheet_coordinates[self.numPosture]) - 1:
            self.numImagePosture += 1
        else:
            # Reset cuando termina la animación
            self.numImagePosture = 0
            if hasattr(self, 'is_melee_attacking'):
                self.is_melee_attacking = False

    def _handle_shoot_animation(self):
        """Maneja la animación de disparo"""
        shoot_base = SHOOT_SPRITE
        if self.facing == DOWN:
            self.numPosture = shoot_base
        elif self.facing == LEFT_DOWN:
            self.numPosture = shoot_base + 1
        elif self.facing == RIGHT_DOWN:
            self.numPosture = shoot_base + 2
        elif self.facing == UP:
            self.numPosture = shoot_base + 3

        if self.numImagePosture < len(self.sheet_coordinates[self.numPosture]) - 1:
            self.numImagePosture += 1
        else:
            # Reset cuando termina la animación
            self.numImagePosture = 0
            if hasattr(self, 'is_shooting'):
                self.is_shooting = False

    def _handle_hurt_animation(self):
        hurt_base = HURT_SPRITE
        if self.facing == DOWN:
            self.numPosture = hurt_base
        elif self.facing == LEFT_DOWN:
            self.numPosture = hurt_base + 1
        elif self.facing == RIGHT_DOWN:
            self.numPosture = hurt_base + 2
        elif self.facing == UP:
            self.numPosture = hurt_base + 3

        # Continuar la animación sin reiniciarla
        self.numImagePosture = (self.numImagePosture + 1) % len(self.sheet_coordinates[self.numPosture])
        
        # Solo marcar como completada cuando pase el tiempo
        current_time = pygame.time.get_ticks()
        if current_time - self.hurt_timer >= self.hurt_duration:
            self.is_hurt = False
            self.hurt_animation_completed = True

    def update(self, time):
        if not self.alive:
            # Solo actualizar animación si está muerto
            self.update_posture()
            return
            
        # Actualización normal para personaje vivo
        if self.velocity[0] != 0 or self.velocity[1] != 0:
            self.numPosture = WALK_SPRITE
        else:
            self.numPosture = IDLE_SPRITE
            
        self.update_posture()
        MySprite.update(self, time)
        
        return