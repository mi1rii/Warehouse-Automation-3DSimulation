import pygame
from OpenGL.GL import *

def draw_rectangle_on_floor():
    rect_color = (0, 0, 0)  # Negro
    rect_width = 30.0  # Ancho del rectángulo (en unidades 3D)
    rect_height = 15.0  # Altura del rectángulo (en unidades 3D)
    rect_depth = 50.0  # Profundidad del rectángulo (en unidades 3D)
    rect_x = 20  # Coordenada X del rectángulo
    rect_y = 0.0  # Coordenada Y del rectángulo

    # Habilitar la mezcla para la transparencia
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Dibujar el prisma rectangular en el plano "Floor"
    glColor4f(1.0, 1.0, 1.0, 0.5)  # Color blanco con transparencia
    glBegin(GL_QUADS)
    # Cara inferior
    glVertex3f(rect_x, 0, rect_y)
    glVertex3f(rect_x + rect_width, 0, rect_y)
    glVertex3f(rect_x + rect_width, 0, rect_y + rect_depth)
    glVertex3f(rect_x, 0, rect_y + rect_depth)
    # Cara superior
    glVertex3f(rect_x, rect_height, rect_y)
    glVertex3f(rect_x + rect_width, rect_height, rect_y)
    glVertex3f(rect_x + rect_width, rect_height, rect_y + rect_depth)
    glVertex3f(rect_x, rect_height, rect_y + rect_depth)
    # Cara frontal
    glVertex3f(rect_x, 0, rect_y)
    glVertex3f(rect_x + rect_width, 0, rect_y)
    glVertex3f(rect_x + rect_width, rect_height, rect_y)
    glVertex3f(rect_x, rect_height, rect_y)
    # Cara trasera
    glVertex3f(rect_x, 0, rect_y + rect_depth)
    glVertex3f(rect_x + rect_width, 0, rect_y + rect_depth)
    glVertex3f(rect_x + rect_width, rect_height, rect_y + rect_depth)
    glVertex3f(rect_x, rect_height, rect_y + rect_depth)
    # Cara izquierda
    glVertex3f(rect_x, 0, rect_y)
    glVertex3f(rect_x, 0, rect_y + rect_depth)
    glVertex3f(rect_x, rect_height, rect_y + rect_depth)
    glVertex3f(rect_x, rect_height, rect_y)
    # Cara derecha
    glVertex3f(rect_x + rect_width, 0, rect_y)
    glVertex3f(rect_x + rect_width, 0, rect_y + rect_depth)
    glVertex3f(rect_x + rect_width, rect_height, rect_y + rect_depth)
    glVertex3f(rect_x + rect_width, rect_height, rect_y)
    glEnd()

    # Dibujar el borde del prisma rectangular
    glColor3f(0.0, 0.0, 0.0)  # Color negro para el borde
    glBegin(GL_LINE_LOOP)
    # Cara inferior
    glVertex3f(rect_x, 0, rect_y)
    glVertex3f(rect_x + rect_width, 0, rect_y)
    glVertex3f(rect_x + rect_width, 0, rect_y + rect_depth)
    glVertex3f(rect_x, 0, rect_y + rect_depth)
    glEnd()
    glBegin(GL_LINE_LOOP)
    # Cara superior
    glVertex3f(rect_x, rect_height, rect_y)
    glVertex3f(rect_x + rect_width, rect_height, rect_y)
    glVertex3f(rect_x + rect_width, rect_height, rect_y + rect_depth)
    glVertex3f(rect_x, rect_height, rect_y + rect_depth)
    glEnd()
    glBegin(GL_LINES)
    # Conectar caras superior e inferior
    glVertex3f(rect_x, 0, rect_y)
    glVertex3f(rect_x, rect_height, rect_y)
    glVertex3f(rect_x + rect_width, 0, rect_y)
    glVertex3f(rect_x + rect_width, rect_height, rect_y)
    glVertex3f(rect_x + rect_width, 0, rect_y + rect_depth)
    glVertex3f(rect_x + rect_width, rect_height, rect_y + rect_depth)
    glVertex3f(rect_x, 0, rect_y + rect_depth)
    glVertex3f(rect_x, rect_height, rect_y + rect_depth)
    glEnd()

    # Deshabilitar la mezcla
    glDisable(GL_BLEND)
