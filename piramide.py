# piramide.py
# Autor: Ivan Olmos Pineda

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from opmat import OpMat
import random
import math
import numpy as np

class Piramide:
    
    def __init__(self, op):
        # Coordenadas de los vértices del prisma cuadrangular (base y cima)
        self.points = np.array([
            (-1.0, 0.0, -1.0, 1.0),
            (1.0, 0.0, -1.0, 1.0),
            (1.0, 0.0, 1.0, 1.0),
            (-1.0, 0.0, 1.0, 1.0),
            (-1.0, 2.0, -1.0, 1.0),
            (1.0, 2.0, -1.0, 1.0),
            (1.0, 2.0, 1.0, 1.0),
            (-1.0, 2.0, 1.0, 1.0)
        ])
        self.op3D = op
        self.dir = [0, 0, 0]
        self.prev_pos = [0,0,0]
        self.deg = 0.0
        self.x = 0
        self.y = 0
        self.z = 0
        self.a = 20.0  # Escala del recorrido

    def update(self):
        """Actualiza la posición de la pirámide siguiendo una trayectoria de infinito."""
        # Ecuaciones paramétricas de la lemniscata de Bernoulli en el plano XZ
        t = math.radians(self.deg)
        a = self.a  

        denom = math.sin(t)**2 + 1
        if denom == 0:
            denom = 0.0001  # Evitar el 0

        # Coordenadas X, Y y Z
        self.x = (a * math.sqrt(2) * math.cos(t)) / denom
        self.y = 0.0  
        self.z = (a * math.sqrt(2) * math.cos(t) * math.sin(t)) / denom

        # Actualizar theta para la rotación
        self.deg = (self.deg + 1) % 360

    def draw(self):
        """Dibuja el prisma cuadrangular usando glLines."""
        glBegin(GL_LINES)
        # Base
        glVertex3f(self.points[0][0], self.points[0][1], self.points[0][2])
        glVertex3f(self.points[1][0], self.points[1][1], self.points[1][2])
        
        glVertex3f(self.points[1][0], self.points[1][1], self.points[1][2])
        glVertex3f(self.points[2][0], self.points[2][1], self.points[2][2])
        
        glVertex3f(self.points[2][0], self.points[2][1], self.points[2][2])
        glVertex3f(self.points[3][0], self.points[3][1], self.points[3][2])
        
        glVertex3f(self.points[3][0], self.points[3][1], self.points[3][2])
        glVertex3f(self.points[0][0], self.points[0][1], self.points[0][2])
        
        # Cima
        glVertex3f(self.points[4][0], self.points[4][1], self.points[4][2])
        glVertex3f(self.points[5][0], self.points[5][1], self.points[5][2])
        
        glVertex3f(self.points[5][0], self.points[5][1], self.points[5][2])
        glVertex3f(self.points[6][0], self.points[6][1], self.points[6][2])
        
        glVertex3f(self.points[6][0], self.points[6][1], self.points[6][2])
        glVertex3f(self.points[7][0], self.points[7][1], self.points[7][2])
        
        glVertex3f(self.points[7][0], self.points[7][1], self.points[7][2])
        glVertex3f(self.points[4][0], self.points[4][1], self.points[4][2])
        
        # Conectores
        glVertex3f(self.points[0][0], self.points[0][1], self.points[0][2])
        glVertex3f(self.points[4][0], self.points[4][1], self.points[4][2])
        
        glVertex3f(self.points[1][0], self.points[1][1], self.points[1][2])
        glVertex3f(self.points[5][0], self.points[5][1], self.points[5][2])
        
        glVertex3f(self.points[2][0], self.points[2][1], self.points[2][2])
        glVertex3f(self.points[6][0], self.points[6][1], self.points[6][2])
        
        glVertex3f(self.points[3][0], self.points[3][1], self.points[3][2])
        glVertex3f(self.points[7][0], self.points[7][1], self.points[7][2])
        glEnd()    

    def render(self):
        """Aplica transformaciones y renderiza el prisma cuadrangular."""
        self.op3D.push()
        self.op3D.translate(self.x, self.y, self.z)
        self.op3D.rotate(self.deg, 1, 1, 1)  # Rotar alrededor de un eje arbitrario
        self.op3D.scale(1.0, 1.0, 1.0)  # Escala uniforme
        pointsR = self.points.copy()
        pointsR = self.op3D.mult_Points(pointsR)
        glColor3f(1.0, 1.0, 1.0)  # Color blanco para el prisma

        glBegin(GL_LINES)
        # Base
        glVertex3f(pointsR[0][0], pointsR[0][1], pointsR[0][2])
        glVertex3f(pointsR[1][0], pointsR[1][1], pointsR[1][2])
        
        glVertex3f(pointsR[1][0], pointsR[1][1], pointsR[1][2])
        glVertex3f(pointsR[2][0], pointsR[2][1], pointsR[2][2])
        
        glVertex3f(pointsR[2][0], pointsR[2][1], pointsR[2][2])
        glVertex3f(pointsR[3][0], pointsR[3][1], pointsR[3][2])
        
        glVertex3f(pointsR[3][0], pointsR[3][1], pointsR[3][2])
        glVertex3f(pointsR[0][0], pointsR[0][1], pointsR[0][2])
        
        # Cima
        glVertex3f(pointsR[4][0], pointsR[4][1], pointsR[4][2])
        glVertex3f(pointsR[5][0], pointsR[5][1], pointsR[5][2])
        
        glVertex3f(pointsR[5][0], pointsR[5][1], pointsR[5][2])
        glVertex3f(pointsR[6][0], pointsR[6][1], pointsR[6][2])
        
        glVertex3f(pointsR[6][0], pointsR[6][1], pointsR[6][2])
        glVertex3f(pointsR[7][0], pointsR[7][1], pointsR[7][2])
        
        glVertex3f(pointsR[7][0], pointsR[7][1], pointsR[7][2])
        glVertex3f(pointsR[4][0], pointsR[4][1], pointsR[4][2])
        
        # Conectores
        glVertex3f(pointsR[0][0], pointsR[0][1], pointsR[0][2])
        glVertex3f(pointsR[4][0], pointsR[4][1], pointsR[4][2])
        
        glVertex3f(pointsR[1][0], pointsR[1][1], pointsR[1][2])
        glVertex3f(pointsR[5][0], pointsR[5][1], pointsR[5][2])
        
        glVertex3f(pointsR[2][0], pointsR[2][1], pointsR[2][2])
        glVertex3f(pointsR[6][0], pointsR[6][1], pointsR[6][2])
        
        glVertex3f(pointsR[3][0], pointsR[3][1], pointsR[3][2])
        glVertex3f(pointsR[7][0], pointsR[7][1], pointsR[7][2])
        glEnd()

        self.op3D.pop()
        self.update()