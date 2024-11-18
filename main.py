# main.py
import os
import pygame
from pygame.locals import *
import numpy as np
import requests
import json
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from opmat import OpMat

# Parámetros de pantalla y simulación
STACK_TOLERANCE = 1.0
screen_width = 900
screen_height = 700

dimBoard = 150  # Dimensión del tablero
zonaDescarga = 10.0
margin = 10.0    # Margen en unidades

# Parámetros de proyección perspectiva para 3D
FOVY = 60.0
ZNEAR = 1.0
ZFAR = 1000.0

# Posición de la cámara (ajustada para que Y sea altura)
EYE_X = 0.0
EYE_Y = 50.0
EYE_Z = 150.0
CENTER_X = 0.0
CENTER_Y = 0.0
CENTER_Z = 0.0
UP_X = 0.0
UP_Y = 1.0
UP_Z = 0.0

# Variables para dibujar los ejes del sistema
AXIS_LENGTH = 100.0

class SimulationState:
    """Clase para gestionar el estado de la simulación."""
    def __init__(self):
        self.simulation_id = None
        self.robots_state = []
        self.packages_state = []
        self.api_url = "http://localhost:8000"
      
    def initialize_simulation(self, num_robots=5, num_packages=200):
        """Inicializa una nueva simulación con robots y cajas."""
        response = requests.post(
            f"{self.api_url}/simulation",
            json={"num_robots": num_robots, "num_packages": num_packages}
        )
        data = response.json()
        self.simulation_id = data["id"]
        self.robots_state = data["robots"]
        self.packages_state = data["packages"]
      
    def update(self):
        """Actualiza el estado de la simulación consultando la API."""
        if not self.simulation_id:
            raise ValueError("Simulation ID not set. Make sure to initialize the simulation first.")
          
        response = requests.post(f"{self.api_url}/simulation/{self.simulation_id}")
      
        try:
            data = response.json()
            self.robots_state = data["robots"]
            self.packages_state = data["packages"]
        except json.JSONDecodeError:
            print("Failed to parse JSON. Response content:", response.content)
            data = None
      
        return data
      
    def cleanup(self):
        """Limpia la simulación eliminándola de la API."""
        if self.simulation_id:
            requests.delete(f"{self.api_url}/simulation/{self.simulation_id}")

def Axis():
    """Dibuja los ejes X, Y, Z en colores rojo, verde y azul respectivamente."""
    glShadeModel(GL_FLAT)
    glLineWidth(2.0)
    
    glBegin(GL_LINES)
    # Eje X en rojo
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-AXIS_LENGTH, 0.0, 0.0)
    glVertex3f(AXIS_LENGTH, 0.0, 0.0)
    
    # Eje Y en verde
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -AXIS_LENGTH, 0.0)
    glVertex3f(0.0, AXIS_LENGTH, 0.0)
    
    # Eje Z en azul
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -AXIS_LENGTH)
    glVertex3f(0.0, 0.0, AXIS_LENGTH)
    glEnd()
    
    glLineWidth(1.0)

def dibujarPlano():
    """Dibuja un plano base en el plano XZ para referencia."""
    glColor3f(0.5, 0.5, 0.5)  # Color gris para el plano
    glBegin(GL_LINES)
    # Dibujar líneas paralelas al eje X
    for z in range(-int(dimBoard), int(dimBoard)+1, 10):
        glVertex3f(-dimBoard, 0.0, z)
        glVertex3f(dimBoard, 0.0, z)
    # Dibujar líneas paralelas al eje Z
    for x in range(-int(dimBoard), int(dimBoard)+1, 10):
        glVertex3f(x, 0.0, -dimBoard)
        glVertex3f(x, 0.0, dimBoard)
    glEnd()

def dibujar_robot(robot_state):
    """Dibuja un robot como un prisma cuadrangular."""
    opmat = OpMat()
    opmat.push()
    posicion = robot_state["position"]
    angulo = robot_state["angle"]
    
    if len(posicion) == 3:
        x, y, z = posicion
    else:
        raise ValueError("La posición debe tener 3 elementos.")
    
    opmat.translate(x, y, z)
    opmat.rotate(np.degrees(angulo), 0, 0, 1)  # Rotar alrededor del eje Y (altura)
    opmat.scale(2.0, 2.0, 2.0)  # Ajusta la escala según sea necesario
    dibujar_robot_body(opmat)
    opmat.pop()

def dibujar_robot_body(opmat):
    """Dibuja el cuerpo del robot como un cubo cuadrado usando glLines."""
    # Definir los vértices del cubo (base y cima)
    vertices = [
        (-1.0, 0.0, -1.0, 1.0),  # Robot cuadrado
        (1.0, 0.0, -1.0, 1.0),   # Robot cuadrado
        (1.0, 0.0, 1.0, 1.0),    # Robot cuadrado
        (-1.0, 0.0, 1.0, 1.0),   # Robot cuadrado
        (-1.0, 2.0, -1.0, 1.0),  # Mantener altura razonable
        (1.0, 2.0, -1.0, 1.0),   # Mantener altura razonable
        (1.0, 2.0, 1.0, 1.0),    # Mantener altura razonable
        (-1.0, 2.0, 1.0, 1.0)    # Mantener altura razonable
    ]

    # Transformar las coordenadas usando OpMat
    transformed_vertices = opmat.mult_Points(vertices)

    # Definir las aristas del cubo
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Base
        (4, 5), (5, 6), (6, 7), (7, 4),  # Cima
        (0, 4), (1, 5), (2, 6), (3, 7)   # Conectores
    ]

    glColor3f(0.0, 0.0, 1.0)  # Color azul para los robots

    glBegin(GL_LINES)
    for edge in edges:
        start = transformed_vertices[edge[0]]
        end = transformed_vertices[edge[1]]
        glVertex3f(start[0], start[1], start[2])
        glVertex3f(end[0], end[1], end[2])
    glEnd()


def dibujar_caja(package_state, color_override=None):
    """Dibuja una caja como un cubo usando glLines."""
    opmat = OpMat()
    opmat.push()
    posicion = package_state["position"]
    angulo = package_state["angle"]
    
    if len(posicion) == 3:
        x, y, z = posicion
    else:
        raise ValueError("La posición debe tener 3 elementos.")
    
    opmat.translate(x, y, z)
    opmat.rotate(np.degrees(angulo), 0, 0, 1)  # Rotar alrededor del eje Y (altura)
    opmat.scale(2.0, 2.0, 2.0)  # Ajusta la escala según sea necesario
    dibujar_caja_body(opmat, color_override)
    opmat.pop()

def dibujar_caja_body(opmat, color_override=None):
    """Dibuja el cuerpo de la caja como un cubo pequeño usando glLines."""
    # Definir los vértices del cubo (base y cima) con tamaño reducido
    vertices = [
        (-0.5, 0.0, -0.5, 1.0),  # Más pequeño
        (0.5, 0.0, -0.5, 1.0),   # Más pequeño
        (0.5, 0.0, 0.5, 1.0),    # Más pequeño
        (-0.5, 0.0, 0.5, 1.0),   # Más pequeño
        (-0.5, 1.0, -0.5, 1.0),  # Mantener altura pequeña
        (0.5, 1.0, -0.5, 1.0),   # Mantener altura pequeña
        (0.5, 1.0, 0.5, 1.0),    # Mantener altura pequeña
        (-0.5, 1.0, 0.5, 1.0)    # Mantener altura pequeña
    ]

    # Transformar las coordenadas usando OpMat
    transformed_vertices = opmat.mult_Points(vertices)

    # Definir las aristas del cubo
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Base
        (4, 5), (5, 6), (6, 7), (7, 4),  # Cima
        (0, 4), (1, 5), (2, 6), (3, 7)   # Conectores
    ]

    # Establecer el color de la caja
    if color_override:
        glColor3f(*color_override)
    else:
        glColor3f(0.73, 0.61, 0.43)  # Color marrón para las cajas

    glBegin(GL_LINES)
    for edge in edges:
        start = transformed_vertices[edge[0]]
        end = transformed_vertices[edge[1]]
        glVertex3f(start[0], start[1], start[2])
        glVertex3f(end[0], end[1], end[2])
    glEnd()


def dibujar_autobus():
    """Dibuja un autobús muy ancho y largo en el cuadrante (-X, +Y, +Z)."""
    opmat = OpMat()
    opmat.push()
    # Posicionar el autobús en el cuadrante (-X, +Y, +Z)
    opmat.translate(-50.0, 0.0, 50.0)

    # Definir los vértices del autobús
    vertices = [
        (-10.0, 0.0, -20.0, 1.0),  # Muy ancho y largo
        (10.0, 0.0, -20.0, 1.0),   # Muy ancho y largo
        (10.0, 0.0, 20.0, 1.0),    # Muy ancho y largo
        (-10.0, 0.0, 20.0, 1.0),   # Muy ancho y largo
        (-10.0, 5.0, -20.0, 1.0),  # Mantener altura razonable
        (10.0, 5.0, -20.0, 1.0),   # Mantener altura razonable
        (10.0, 5.0, 20.0, 1.0),    # Mantener altura razonable
        (-10.0, 5.0, 20.0, 1.0)    # Mantener altura razonable
    ]

    # Transformar los vértices
    transformed_vertices = opmat.mult_Points(vertices)

    # Definir las aristas
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Base
        (4, 5), (5, 6), (6, 7), (7, 4),  # Techo
        (0, 4), (1, 5), (2, 6), (3, 7)   # Conexión entre base y techo
    ]

    glColor3f(1.0, 1.0, 0.0)  # Color amarillo para el autobús

    glBegin(GL_LINES)
    for edge in edges:
        start = transformed_vertices[edge[0]]
        end = transformed_vertices[edge[1]]
        glVertex3f(start[0], start[1], start[2])
        glVertex3f(end[0], end[1], end[2])
    glEnd()
    opmat.pop()


# Variables globales para el desplazamiento del mapa
camera_offset_x = 0.0
camera_offset_y = 0.0
mouse_dragging = False
last_mouse_x = 0
last_mouse_y = 0

def Init(simulation):
    """Inicializa la ventana de Pygame y configura OpenGL."""
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Simulación de Robots y Cajas 3D")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width / screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)
    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    simulation.initialize_simulation()  # Iniciar simulación


def handle_mouse_motion(event):
    """Maneja el movimiento del mouse para mover el mapa."""
    global camera_offset_x, camera_offset_y, last_mouse_x, last_mouse_y, mouse_dragging

    if mouse_dragging:
        dx = event.pos[0] - last_mouse_x
        dy = event.pos[1] - last_mouse_y
        camera_offset_x += dx * 0.1  # Ajusta la sensibilidad
        camera_offset_y -= dy * 0.1  # Ajusta la sensibilidad
        last_mouse_x, last_mouse_y = event.pos


def handle_mouse_button(event):
    """Maneja los clics del mouse para iniciar o detener el arrastre."""
    global mouse_dragging, last_mouse_x, last_mouse_y

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Botón izquierdo
        mouse_dragging = True
        last_mouse_x, last_mouse_y = event.pos
    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Botón izquierdo
        mouse_dragging = False


def update_camera():
    """Actualiza la posición de la cámara según los desplazamientos."""
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        EYE_X + camera_offset_x,  # Aplicar desplazamiento en X
        EYE_Y,
        EYE_Z + camera_offset_y,  # Aplicar desplazamiento en Y
        CENTER_X + camera_offset_x,
        CENTER_Y,
        CENTER_Z + camera_offset_y,
        UP_X,
        UP_Y,
        UP_Z
    )


def display(simulation):
    """Renderiza la escena de la simulación."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Limpiar buffers

    update_camera()  # Actualizar la cámara según el desplazamiento
    Axis()
    dibujarPlano()
    simulation.update()  # Actualizar estado de la simulación

    # Dibujar todos los robots
    for robot_state in simulation.robots_state:
        dibujar_robot(robot_state)

    # Dibujar todas las cajas
    for package_state in simulation.packages_state:
        dibujar_caja(package_state)

    # Dibujar el autobús
    dibujar_autobus()


def main():
    """Función principal que ejecuta la simulación."""
    pygame.init()  # Inicializar Pygame
    simulation = SimulationState()
    done = False
    Init(simulation)  # Configurar la simulación

    clock = pygame.time.Clock()  # Control de FPS

    try:
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # Salir del bucle principal
                elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    handle_mouse_button(event)
                elif event.type == pygame.MOUSEMOTION:
                    handle_mouse_motion(event)

            display(simulation)  # Renderizar la simulación
            pygame.display.flip()  # Actualizar la pantalla
            clock.tick(60)  # Limitar a 60 FPS

    finally:
        simulation.cleanup()  # Limpiar simulación al finalizar
        pygame.quit()  # Cerrar Pygame


if __name__ == '__main__':
    main()
