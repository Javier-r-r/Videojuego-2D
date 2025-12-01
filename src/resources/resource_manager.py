# -*- coding: utf-8 -*-

import pygame
import sys
import os

# Initialize pygame
pygame.init()
from pygame.locals import *


# -------------------------------------------------
# Clase GestorRecursos

# En este caso se implementa como una clase vacía, solo con métodos de clase
class ResourceManager(object):
    resources = {}
            
    @classmethod
    def LoadImage(cls, name, colorkey=None):
        # Si el nombre de archivo está entre los recursos ya cargados
        if name in cls.resources:
            return cls.resources[name]
        else:
            fullname = os.path.join('assets', name)
            try:
                image = pygame.image.load(fullname)
            except pygame.error as message:
                print('Cannot load image:', fullname)
                raise SystemExit(message)
                
            # Convertir la imagen con canal alfa en lugar de convert() normal
            image = image.convert_alpha()
            
            # Almacenar y devolver
            cls.resources[name] = image
            return image

    @classmethod
    def LoadCoordinatesFile(cls, name):
        # Si el nombre de archivo está entre los recursos ya cargados
        if name in cls.resources:
            # Se devuelve ese recurso
            return cls.resources[name]
        # Si no ha sido cargado anteriormente
        else:
            # Se carga el recurso indicando el nombre de su carpeta
            fullname = os.path.join('assets', name)
            pfile = open(fullname, 'r')
            # Read only numbers and ignore letters
            data = ''.join(c for c in pfile.read() if c.isdigit() or c in '., \n')
            pfile.close()
            # Se almacena
            cls.resources[name] = data
            # Se devuelve
            return data
