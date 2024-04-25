import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# Valores para actualizar la dirección de pacman
    # (incremento/decremento, qué eje se actualiza, qué eje se hace 0)
direcciones = {
    "right": (1, 0, 2),
    "left": (-1, 0, 2),
    "up": (-1, 2, 0),
    "down": (1, 2, 0)
}

# Valores de grados necesarios de rotación para pacman al cambiar de dirección
# ("na" no se usa)
rotar = {
    "right": 0,
    "left": 180,
    "up": 90,
    "down": 270,
    "na": -1
}

size = 8.5
class Pacman:
    
    def __init__(self, dim, dim2, dim3, vel):

        #Limites de movimiento del pacman
        self.Limit1 = dim
        self.Limit2 = dim2
        self.Limit3 = dim3
        
        self.Position = [201, 2.5, 231]
        
        self.Direction = []
        self.Direction.append(0)
        self.Direction.append(0)
        self.Direction.append(0)
        
        self.Direction[0] *= vel
        self.Direction[2] *= vel
    
        self.vel = vel

    def drawPac(self, texture, dir, prev):
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        if rotar[dir] != -1:
            glRotatef(rotar[dir], 0, 1, 0)
        else:
            glRotate(rotar[prev], 0, 1, 0)
        glColor3f(255,255,255)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)    
        glBegin(GL_QUADS)
        # Dimensiones del pacman: 17 x 17
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-size, 0, -size)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-size, 0, size)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(size, 0, size)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(size, 0, -size)
        glEnd()              
        glPopMatrix()
        glDisable(GL_TEXTURE_2D)
        
    def update(self, dir):
        if dir == "na":
            self.Direction[0] = 0
            self.Direction[2] = 0
        else:
            valPos = direcciones[dir]
            self.Direction[valPos[1]] = valPos[0] * self.vel
            self.Direction[valPos[2]] = 0
            new_x = self.Position[valPos[1]] + self.Direction[valPos[1]]
            self.Position[valPos[1]] = new_x