#Caja.jl
import numpy as np
from OpenGL.GL import *

class Caja:
    def __init__(self, dimensions, color, position):
        """
        Inicializa una caja.
        :param dimensions: Dimensiones de la caja (ancho, alto, profundidad).
        :param color: Color de la caja (RGB).
        :param position: Posición de la caja (X, Y, Z).
        """
        self.dimensions = dimensions
        self.color = color
        self.position = position

    def draw(self):
        """
        Dibuja la caja utilizando OpenGL.
        """
        width, height, depth = self.dimensions
        x, y, z = self.position

        # Vértices de la caja
        vertices = [
            [x - width / 2, y - height / 2, z - depth / 2],  # Inferior trasero izquierdo
            [x + width / 2, y - height / 2, z - depth / 2],  # Inferior trasero derecho
            [x + width / 2, y + height / 2, z - depth / 2],  # Superior trasero derecho
            [x - width / 2, y + height / 2, z - depth / 2],  # Superior trasero izquierdo
            [x - width / 2, y - height / 2, z + depth / 2],  # Inferior frontal izquierdo
            [x + width / 2, y - height / 2, z + depth / 2],  # Inferior frontal derecho
            [x + width / 2, y + height / 2, z + depth / 2],  # Superior frontal derecho
            [x - width / 2, y + height / 2, z + depth / 2],  # Superior frontal izquierdo
        ]

        # Caras de la caja (quads)
        faces = [
            [0, 1, 2, 3],  # Cara trasera
            [4, 5, 6, 7],  # Cara frontal
            [0, 1, 5, 4],  # Cara inferior
            [2, 3, 7, 6],  # Cara superior
            [0, 3, 7, 4],  # Cara izquierda
            [1, 2, 6, 5],  # Cara derecha
        ]

        # Normales para cada cara
        normals = [
            [0, 0, -1],  # Trasera
            [0, 0, 1],   # Frontal
            [0, -1, 0],  # Inferior
            [0, 1, 0],   # Superior
            [-1, 0, 0],  # Izquierda
            [1, 0, 0],   # Derecha
        ]

        # Dibujar las caras de la caja
        glColor3f(*self.color)
        glBegin(GL_QUADS)
        for i, face in enumerate(faces):
            glNormal3f(*normals[i])  # Normal para cada cara
            for vertex in face:
                glVertex3f(*vertices[vertex])
        glEnd()

        # Dibujar bordes de la caja
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_LINES)
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        for edge in edges:
            glVertex3f(*vertices[edge[0]])
            glVertex3f(*vertices[edge[1]])
        glEnd()

    def update_position(self, new_position):
        """
        Actualiza la posición de la caja.
        :param new_position: Nueva posición de la caja (X, Y, Z).
        """
        self.position = new_position
