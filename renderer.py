import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from opmat import OpMat

# Importar constantes necesarias
from main import (
    screen_width, screen_height, FOVY, ZNEAR, ZFAR,
    EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z,
    X_MIN, X_MAX, Y_MIN, Y_MAX, Z_MIN, Z_MAX,
    dimBoard, area_offset_x, area_offset_z,
    contenedor_ancho, contenedor_altura, contenedor_profundidad,
    rectangulo_ancho, rectangulo_profundidad, rectangulo_posicion
)

def init_gl():
    """Inicializa la ventana de Pygame y configura OpenGL."""
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: Simulación de Robots en Pasarela")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width / screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)
    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

def draw_axis():
    """Dibuja los ejes X, Y, Z."""
    glBegin(GL_LINES)
    # Eje X en rojo
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(X_MIN, 0.0, 0.0)
    glVertex3f(X_MAX, 0.0, 0.0)
    # Eje Y en verde
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, Y_MIN, 0.0)
    glVertex3f(0.0, Y_MAX, 0.0)
    # Eje Z en azul
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, Z_MIN)
    glVertex3f(0.0, 0.0, Z_MAX)
    glEnd()

def draw_floor():
    """Dibuja el plano base."""
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    for i in range(-int(dimBoard/2), int(dimBoard/2), 50):
        glVertex3f(i + area_offset_x, 0.0, -dimBoard/2 + area_offset_z)
        glVertex3f(i + area_offset_x, 0.0, dimBoard/2 + area_offset_z)
        glVertex3f(-dimBoard/2 + area_offset_x, 0.0, i + area_offset_z)
        glVertex3f(dimBoard/2 + area_offset_x, 0.0, i + area_offset_z)
    glEnd()

def draw_cube(width, height, depth, color=(1.0, 1.0, 1.0)):
    """Dibuja un cubo con las dimensiones especificadas."""
    glColor3f(*color)
    vertices = [
        [-width/2, -height/2, -depth/2],
        [width/2, -height/2, -depth/2],
        [width/2, height/2, -depth/2],
        [-width/2, height/2, -depth/2],
        [-width/2, -height/2, depth/2],
        [width/2, -height/2, depth/2],
        [width/2, height/2, depth/2],
        [-width/2, height/2, depth/2]
    ]
    
    edges = [
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    ]
    
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3f(*vertices[vertex])
    glEnd()

def draw_base_plane():
    """Dibuja el plano base debajo del contenedor."""
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex3f(-contenedor_ancho/2, 0, -contenedor_profundidad/2)
    glVertex3f(contenedor_ancho/2, 0, -contenedor_profundidad/2)
    glVertex3f(contenedor_ancho/2, 0, contenedor_profundidad/2)
    glVertex3f(-contenedor_ancho/2, 0, contenedor_profundidad/2)
    glEnd()

def draw_walkway():
    """Dibuja la pasarela."""
    glPushMatrix()
    glTranslatef(rectangulo_posicion[0], rectangulo_posicion[1], rectangulo_posicion[2])
    glColor3f(0.7, 0.7, 0.7)
    draw_cube(rectangulo_ancho, 1.0, rectangulo_profundidad)
    glPopMatrix()

def draw_box(package_state, color_override=None):
    """Dibuja una caja."""
    glPushMatrix()
    pos = package_state["position"]
    dim = package_state["dimensions"]
    glTranslatef(pos[0], pos[1], pos[2])
    glRotatef(package_state["angle"] * 180.0 / np.pi, 0, 1, 0)
    
    if color_override:
        color = color_override
    else:
        color = (1.0, 1.0, 1.0)
    
    draw_cube(dim[0], dim[1], dim[2], color)
    glPopMatrix()

def draw_container():
    """Dibuja el contenedor."""
    glPushMatrix()
    glColor3f(0.5, 0.5, 1.0)
    draw_cube(contenedor_ancho, contenedor_altura, contenedor_profundidad)
    glPopMatrix()

def draw_robot(robot):
    """Dibuja un robot."""
    glPushMatrix()
    glTranslatef(robot.position[0], robot.position[1], robot.position[2])
    glRotatef(robot.angle * 180.0 / np.pi, 0, 1, 0)
    glColor3f(1.0, 0.0, 0.0)
    draw_cube(20.0, 20.0, 20.0)  # Tamaño del robot
    glPopMatrix()

def render_scene(simulation):
    """Renderiza la escena completa."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    draw_axis()
    draw_floor()
    draw_base_plane()
    draw_walkway()
    draw_container()

    # Dibujar cajas
    for package in simulation.packages_state:
        if package["state"] == "on_floor":
            draw_box(package, color_override=(0.73, 0.61, 0.43))
        elif package["state"] == "carried_by_robot":
            assigned_robot = next((r for r in simulation.robots if r.id == package.get("assigned_robot_id")), None)
            if assigned_robot:
                package["position"] = [assigned_robot.position[0], 0.0, assigned_robot.position[2]]
                package["angle"] = assigned_robot.angle
                draw_box(package, color_override=(1.0, 1.0, 0.0))
        elif package["state"] == "in_container":
            draw_box(package, color_override=(0.0, 1.0, 0.0))

    # Dibujar robots
    for robot in simulation.robots:
        draw_robot(robot) 