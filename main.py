# main.py
import os
import pygame
from pygame.locals import *
import numpy as np
import requests
import json
import math  # Importar la librería math

from OpenGL.GL import *
from OpenGL.GLU import *
from opmat import OpMat
from piramide import Piramide  # Actualizado para 3D

# Parámetros de pantalla y simulación
STACK_TOLERANCE = 1.0
screen_width = 900
screen_height = 700

dimBoard = 150  # Cambiado a entero para evitar errores en range
zonaDescarga = 10.0
margin = 10.0    # Margen en unidades

# Parámetros de proyección perspectiva para 3D
FOVY = 60.0
ZNEAR = 1.0
ZFAR = 500.0

# Posición de la cámara 
EYE_X = 30.0
EYE_Y = 30.0
EYE_Z = 30.0 
CENTER_X = 0.0
CENTER_Y = 0.0
CENTER_Z = 0.0
UP_X = 0.0
UP_Y = 1.0
UP_Z = 0.0

# Variables para dibujar los ejes del sistema
X_MIN = -50
X_MAX = 50
Y_MIN = -50
Y_MAX = 50
Z_MIN = -50
Z_MAX = 50

class SimulationState:
    """Clase para gestionar el estado de la simulación."""
    def __init__(self):
        self.simulation_id = None
        self.robots_state = []
        self.packages_state = []
        self.api_url = "http://localhost:8000"
  
    def initialize_simulation(self, num_robots=5, num_packages=100):
        """Inicializa una nueva simulación con robots y cajas."""
        response = requests.post(
            f"{self.api_url}/simulation",
            json={"num_robots": num_robots, "num_packages": num_packages}
        )
        data = response.json()
        self.simulation_id = data["id"]
        self.robots_state = data["robots"]
        self.packages_state = data["packages"]

        if len(self.robots_state) < num_robots:
            print(f"Warning: Expected {num_robots} robots, but only {len(self.robots_state)} were initialized.")
  
    def update(self):
        """Actualiza el estado de la simulación consultando la API."""
        if not self.simulation_id:
            raise ValueError("Simulation ID not set. Make sure to initialize the simulation first.")
      
        response = requests.post(f"{self.api_url}/simulation/{self.simulation_id}")
      
        print("Response content:", response.content)  # Debug: check raw response content
      
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
    glLineWidth(3.0)
    
    # Eje X en rojo
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(X_MIN, 0.0, 0.0)
    glVertex3f(X_MAX, 0.0, 0.0)
    glEnd()
    
    # Eje Y en verde
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, Y_MIN, 0.0)
    glVertex3f(0.0, Y_MAX, 0.0)
    glEnd()
    
    # Eje Z en azul
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, Z_MIN)
    glVertex3f(0.0, 0.0, Z_MAX)
    glEnd()
    glLineWidth(1.0)

def draw_path(a=20.0, num_points=1000):
    """
    Dibuja el recorrido en forma de símbolo de infinito (lemniscata) en el plano XZ.
    
    Parámetros:
    - a: Escala del símbolo de infinito.
    - num_points: Número de puntos a calcular para la curva.
    """
    glColor3f(1.0, 1.0, 0.0)  # Color amarillo para el recorrido
    glLineWidth(2.0)
    glBegin(GL_LINE_STRIP)
    for i in range(num_points + 1):
        angle = (i / num_points) * 2 * math.pi  # De 0 a 2π
        t = angle
        # Ecuaciones paramétricas de la lemniscata de Bernoulli
        denom = math.sin(t)**2 + 1
        if denom == 0:
            denom = 0.0001  # Evitar división por cero
        x = (a * math.sqrt(2) * math.cos(t)) / denom
        z = (a * math.sqrt(2) * math.cos(t) * math.sin(t)) / denom
        y = 0.0  # Mantener Y constante
        glVertex3f(x, y, z)
    glEnd()
    glLineWidth(1.0)  # Resetear ancho de línea

def dibujarPlano():
    """Dibuja un plano base en el Cuadrante III para referencia."""
    glColor3f(0.5, 0.5, 0.5)  # Color gris para el plano
    glBegin(GL_LINES)
    # Dibujar líneas paralelas al eje X en el Cuadrante III
    for i in range(-dimBoard, 1, 10):
        glVertex3f(i, 0.0, -dimBoard)
        glVertex3f(i, 0.0, 0.0)
    # Dibujar líneas paralelas al eje Z en el Cuadrante III
    for i in range(-dimBoard, 1, 10):
        glVertex3f(-dimBoard, 0.0, i)
        glVertex3f(0.0, 0.0, i)
    glEnd()

def Init(simulation):
    """Inicializa la ventana de Pygame y configura OpenGL."""
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: Robots y Cajas 3D")

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

def dibujar_robot(robot_state):
    """Dibuja un robot como un prisma cuadrangular."""
    opmat = OpMat()
    opmat.push()
    posicion = robot_state["position"]
    angulo = robot_state["angle"]
    
    if len(posicion) == 2:
        x, z = posicion
        y = 0.0
    elif len(posicion) == 3:
        x, y, z = posicion
    else:
        raise ValueError("La posición debe tener 2 o 3 elementos.")
    
    opmat.translate(x, y, z)
    opmat.rotate(np.degrees(angulo), 0, 1, 0)  # Rotar alrededor del eje Y
    opmat.scale(1.0, 1.0, 1.0)  # Ajusta la escala según sea necesario
    dibujar_robot_body(opmat)
    opmat.pop()

def dibujar_robot_body(opmat):
    """Dibuja el cuerpo del robot como un prisma cuadrangular usando glLines."""
    # Definir los vértices del prisma (base y cima)
    vertices = [
        (-1.0, 0.0, -1.0, 1.0),
        (1.0, 0.0, -1.0, 1.0),
        (1.0, 0.0, 1.0, 1.0),
        (-1.0, 0.0, 1.0, 1.0),
        (-1.0, 2.0, -1.0, 1.0),
        (1.0, 2.0, -1.0, 1.0),
        (1.0, 2.0, 1.0, 1.0),
        (-1.0, 2.0, 1.0, 1.0)
    ]

    # Transformar las coordenadas usando OpMat
    transformed_vertices = opmat.mult_Points(vertices)  

    # Definir las aristas del prisma
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
    
    if len(posicion) == 2:
        x, z = posicion
        y = 0.0
    elif len(posicion) == 3:
        x, y, z = posicion
    else:
        raise ValueError("La posición debe tener 2 o 3 elementos.")
    
    opmat.translate(x, y, z)
    opmat.rotate(np.degrees(angulo), 0, 1, 0)  # Rotar alrededor del eje Y
    opmat.scale(1.0, 1.0, 1.0)  # Ajusta la escala según sea necesario
    dibujar_caja_body(opmat, color_override)
    opmat.pop()

def dibujar_caja_body(opmat, color_override=None):
    """Dibuja el cuerpo de la caja como un cubo usando glLines."""
    # Definir los vértices del cubo (base y cima)
    vertices = [
        (-1.0, 0.0, -1.0, 1.0),
        (1.0, 0.0, -1.0, 1.0),
        (1.0, 0.0, 1.0, 1.0),
        (-1.0, 0.0, 1.0, 1.0),
        (-1.0, 2.0, -1.0, 1.0),
        (1.0, 2.0, -1.0, 1.0),
        (1.0, 2.0, 1.0, 1.0),
        (-1.0, 2.0, 1.0, 1.0)
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

def display(simulation):
    """Renderiza la escena de la simulación."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Limpiar buffers
    Axis()
    dibujarPlano()
    draw_path(a=20.0, num_points=1000)  # Dibujar recorrido en forma de infinito
    simulation.update()  # Actualizar estado de la simulación

    # Dibujar todos los robots
    for robot_state in simulation.robots_state:
        dibujar_robot(robot_state)
        
    # Agrupar cajas en pilas según la tolerancia
    stacks = {}
    for package in simulation.packages_state:
        pos = package["position"]
        if len(pos) >= 2:
            x, z = pos[0], pos[1]
        else:
            print("Posición inválida:", pos)
            continue
        # Redondear posiciones para agrupar en pilas
        stack_key = (round(x / STACK_TOLERANCE) * STACK_TOLERANCE,
                    round(z / STACK_TOLERANCE) * STACK_TOLERANCE)
        if stack_key not in stacks:
            stacks[stack_key] = []
        stacks[stack_key].append(package)

    # Determinar el estado de cada pila
    stack_colors = {}
    for key, packages in stacks.items():
        if len(packages) >= 5:
            stack_colors[key] = (1.0, 0.0, 0.0)  # Rojo para pilas llenas
        elif len(packages) > 0:
            stack_colors[key] = (0.0, 1.0, 0.0)  # Verde para pilas disponibles

    # Dibujar cajas con color basado en el estado de la pila
    for key, packages in stacks.items():
        is_full_stack = len(packages) >= 5
        for package in packages:
            if is_full_stack:
                # Dibujar pilas llenas en rojo
                dibujar_caja(package, color_override=(1.0, 0.0, 0.0))  # Rojo
            else:
                # Dibujar pilas disponibles en verde
                dibujar_caja(package, color_override=(0.0, 1.0, 0.0))  # Verde

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

            display(simulation)  # Renderizar la simulación
            pygame.display.flip()  # Actualizar la pantalla
            clock.tick_busy_loop(60)  # Limitar a 60 FPS con mayor precisión

    finally:
        simulation.cleanup()  # Limpiar simulación al finalizar
        pygame.quit()  # Cerrar Pygame

if __name__ == '__main__':
    main()
