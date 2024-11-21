# main.py
import os
import pygame
from pygame.locals import *
import numpy as np
import requests
import json

from OpenGL.GL import *
from OpenGL.GLU import *
from opmat import OpMat

# Parámetros de pantalla y simulación
STACK_TOLERANCE = 1.0
screen_width = 700
screen_height = 700

dimBoard = 200.0  # Aumentamos el tamaño del tablero
margin = 10.0  # Margen en unidades

# Definir parámetros de proyección perspectiva para 3D
FOVY = 45.0  # Ajustado a un valor estándar
ZNEAR = 0.1
ZFAR = 1000.0

# Posición de la cámara 
EYE_X = dimBoard
EYE_Y = dimBoard
EYE_Z = dimBoard
CENTER_X = 0.0
CENTER_Y = 0.0
CENTER_Z = 0.0
UP_X = 0.0
UP_Y = 1.0
UP_Z = 0.0

# Definir área de almacenamiento en la esquina inferior izquierda
storage_area_size = 100.0  # Tamaño del área de almacenamiento (más grande)
storage_area_position = (-dimBoard + storage_area_size / 2 + margin, 0, -dimBoard + storage_area_size / 2 + margin)  # Posición en esquina

# Calcular los límites del área de almacenamiento
x_center, y_center, z_center = storage_area_position
s = storage_area_size / 2
x_min_storage = x_center - s
x_max_storage = x_center + s
z_min_storage = z_center - s
z_max_storage = z_center + s

# Convertir los límites del área de almacenamiento a una tupla
storage_area = (x_min_storage, x_max_storage, z_min_storage, z_max_storage)

class SimulationState:
    """Clase para gestionar el estado de la simulación."""
    def __init__(self):
        self.simulation_id = None
        self.robots_state = []
        self.packages_state = []
        self.api_url = "http://localhost:8000"
        self.package_sizes = {}  # Almacena los tamaños de las cajas

    def initialize_simulation(self, num_robots=2, num_packages=10):
        """Inicializa una nueva simulación con robots y cajas."""
        # Enviar información del área de almacenamiento al servidor
        response = requests.post(
            f"{self.api_url}/simulation",
            json={
                "num_robots": num_robots,
                "num_packages": num_packages,
                "storage_area": storage_area  # Enviar el área de almacenamiento
            }
        )
        data = response.json()
        self.simulation_id = data["id"]
        self.robots_state = data["robots"]
        self.packages_state = data["packages"]

        if len(self.robots_state) < num_robots:
            print(f"Warning: Expected {num_robots} robots, but only {len(self.robots_state)} were initialized.")

        # Asignar tamaños aleatorios a las cajas iniciales
        for package in self.packages_state:
            package_id = package.get("id")
            if package_id and package_id not in self.package_sizes:
                # Generar tamaño aleatorio entre 5 y 15 unidades para cada dimensión
                size = {
                    "width": np.random.uniform(5, 15),
                    "height": np.random.uniform(5, 15),
                    "depth": np.random.uniform(5, 15)
                }
                self.package_sizes[package_id] = size
            package["size"] = self.package_sizes.get(package_id, {"width": 10, "height": 10, "depth": 10})

    def update(self):
        """Actualiza el estado de la simulación consultando la API."""
        if not self.simulation_id:
            raise ValueError("Simulation ID not set. Make sure to initialize the simulation first.")

        response = requests.post(f"{self.api_url}/simulation/{self.simulation_id}")

        try:
            data = response.json()
            self.robots_state = data["robots"]
            self.packages_state = data["packages"]

            # Asignar tamaños fijos a las cajas
            for package in self.packages_state:
                package_id = package.get("id")
                if package_id and package_id not in self.package_sizes:
                    # Generar tamaño aleatorio entre 5 y 15 unidades para cada dimensión
                    size = {
                        "width": np.random.uniform(5, 15),
                        "height": np.random.uniform(5, 15),
                        "depth": np.random.uniform(5, 15)
                    }
                    self.package_sizes[package_id] = size
                package["size"] = self.package_sizes.get(package_id, {"width": 10, "height": 10, "depth": 10})

        except json.JSONDecodeError:
            print("Failed to parse JSON. Response content:", response.content)
            data = None

        return data

    def cleanup(self):
        """Limpia la simulación eliminándola de la API."""
        if self.simulation_id:
            requests.delete(f"{self.api_url}/simulation/{self.simulation_id}")

def dibujarPlano():
    """Dibuja un grid simple en el plano XZ."""
    glColor3f(0.7, 0.7, 0.7)  # Color gris claro para el grid
    glBegin(GL_LINES)
    # Dibujar líneas paralelas al eje X (variando Z)
    for z in np.arange(-dimBoard, dimBoard + 1, 10):
        glVertex3f(-dimBoard, 0, z)
        glVertex3f(dimBoard, 0, z)
    # Dibujar líneas paralelas al eje Z (variando X)
    for x in np.arange(-dimBoard, dimBoard + 1, 10):
        glVertex3f(x, 0, -dimBoard)
        glVertex3f(x, 0, dimBoard)
    glEnd()

def dibujarEjes():
    """Dibuja los ejes X, Y, Z."""
    glLineWidth(2.0)  # Ancho de línea para mayor visibilidad
    glBegin(GL_LINES)
    # Eje X en rojo
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-dimBoard, 0.0, 0.0)
    glVertex3f(dimBoard, 0.0, 0.0)
    # Eje Y en verde
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -dimBoard, 0.0)
    glVertex3f(0.0, dimBoard, 0.0)
    # Eje Z en azul
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -dimBoard)
    glVertex3f(0.0, 0.0, dimBoard)
    glEnd()
    glLineWidth(1.0)  # Restaurar ancho de línea predeterminado

def dibujar_area_almacenamiento():
    """Dibuja el área de almacenamiento como un cubo 3D en una esquina."""
    x, y, z = storage_area_position
    s = storage_area_size / 2

    # Definir los vértices del cubo
    vertices = [
        (x - s, y, z - s),
        (x + s, y, z - s),
        (x + s, y, z + s),
        (x - s, y, z + s),
        (x - s, y + storage_area_size, z - s),
        (x + s, y + storage_area_size, z - s),
        (x + s, y + storage_area_size, z + s),
        (x - s, y + storage_area_size, z + s)
    ]

    # Definir las aristas del cubo
    edges = [
        (0,1),(1,2),(2,3),(3,0),  # Base
        (4,5),(5,6),(6,7),(7,4),  # Tapa
        (0,4),(1,5),(2,6),(3,7)   # Lados
    ]

    glColor3f(0.0, 1.0, 0.0)  # Color verde para el área de almacenamiento
    glLineWidth(3.0)  # Ancho de línea para resaltar el área

    glBegin(GL_LINES)
    for edge in edges:
        glVertex3f(*vertices[edge[0]])
        glVertex3f(*vertices[edge[1]])
    glEnd()

    glLineWidth(1.0)  # Restaurar el ancho de línea predeterminado

def dibujar_robot(robot_state):
    """Dibuja un robot en la posición y orientación especificadas."""
    opmat = OpMat()
    opmat.push()
    posicion = robot_state["position"]
    angulo = robot_state["angle"]

    if len(posicion) == 2:
        x, y = posicion
        z = 0.0
    elif len(posicion) == 3:
        x, y, z = posicion
    else:
        raise ValueError("La posición debe tener 2 o 3 elementos.")

    opmat.translate(x, y, z)
    opmat.rotate(np.degrees(angulo), 0, 1, 0)  # Rotar alrededor del eje Y para 3D
    opmat.scale(1.0, 1.0, 1.0)  # Escalar en X, Y, Z
    dibujar_robot_body(opmat)
    opmat.pop()

def dibujar_robot_body(opmat):
    """Dibuja el cuerpo del robot como un cubo 3D de color azul."""
    # Definir los vértices de la caja (un cubo)
    size = 10
    vertices = [
        (-size, -size, -size),
        (size, -size, -size),
        (size, size, -size),
        (-size, size, -size),
        (-size, -size, size),
        (size, -size, size),
        (size, size, size),
        (-size, size, size)
    ]

    # Transformar las coordenadas usando OpMat
    transformed_vertices = opmat.mult_points(vertices)  

    # Definir las aristas del cubo
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Base
        (4, 5), (5, 6), (6, 7), (7, 4),  # Top
        (0, 4), (1, 5), (2, 6), (3, 7)   # Lados
    ]

    glColor3f(0.0, 0.0, 1.0)  # Color azul para los robots
    glLineWidth(2.0)  # Ancho de línea para los robots

    glBegin(GL_LINES)
    for edge in edges:
        start = transformed_vertices[edge[0]]
        end = transformed_vertices[edge[1]]
        glVertex3f(start[0], start[1], start[2])
        glVertex3f(end[0], end[1], end[2])
    glEnd()
    glLineWidth(1.0)  # Restaurar el ancho de línea predeterminado

def dibujar_caja(package_state):
    """Dibuja una caja en la posición y orientación especificadas con tamaño fijo."""
    opmat = OpMat()
    opmat.push()
    posicion = package_state["position"]
    angulo = package_state["angle"]
    size = package_state.get("size", {"width": 10, "height": 10, "depth": 10})

    width = size.get("width", 10)
    height = size.get("height", 10)
    depth = size.get("depth", 10)

    if len(posicion) == 2:
        x, y = posicion
        z = 0.0
    elif len(posicion) == 3:
        x, y, z = posicion
    else:
        raise ValueError("La posición debe tener 2 o 3 elementos.")

    opmat.translate(x, y, z)
    opmat.rotate(np.degrees(angulo), 0, 1, 0)  # Rotar alrededor del eje Y para 3D
    opmat.scale(width, height, depth)  # Escalar en X, Y y Z
    dibujar_caja_body(opmat)
    opmat.pop()

def dibujar_caja_body(opmat):
    """Dibuja el contorno de una caja como un cubo 3D de color rojo."""
    # Definir los vértices de la caja (un cubo unitario centrado en el origen)
    vertices = [
        (-0.5, -0.5, -0.5),
        (0.5, -0.5, -0.5),
        (0.5, 0.5, -0.5),
        (-0.5, 0.5, -0.5),
        (-0.5, -0.5, 0.5),
        (0.5, -0.5, 0.5),
        (0.5, 0.5, 0.5),
        (-0.5, 0.5, 0.5)
    ]

    # Transformar las coordenadas usando OpMat
    transformed_vertices = opmat.mult_points(vertices) 

    # Definir las aristas del cubo
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Base
        (4, 5), (5, 6), (6, 7), (7, 4),  # Top
        (0, 4), (1, 5), (2, 6), (3, 7)   # Lados
    ]

    glColor3f(1.0, 0.0, 0.0)  # Color rojo para las cajas
    glLineWidth(2.0)  # Ancho de línea para las cajas

    glBegin(GL_LINES)
    for edge in edges:
        start = transformed_vertices[edge[0]]
        end = transformed_vertices[edge[1]]
        glVertex3f(start[0], start[1], start[2])
        glVertex3f(end[0], end[1], end[2])
    glEnd()
    glLineWidth(1.0)  # Restaurar el ancho de línea predeterminado

def Init(simulation):
    """Inicializa la ventana de Pygame y configura OpenGL para 3D."""
    pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Simulación 3D de Almacén")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Configurar proyección perspectiva para 3D
    gluPerspective(FOVY, screen_width / screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # Configurar la cámara usando gluLookAt
    gluLookAt(
        EYE_X, EYE_Y, EYE_Z,    # Posición de la cámara (eye)
        CENTER_X, CENTER_Y, CENTER_Z,  # Punto de referencia (center)
        UP_X, UP_Y, UP_Z       # Vector up
    )

    glClearColor(0, 0, 0, 1)  # Color de fondo negro
    glEnable(GL_DEPTH_TEST)    # Habilitar test de profundidad
    glEnable(GL_BLEND) 
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Modo de polígono relleno

    # Configurar iluminación básica (opcional)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [0, -dimBoard, dimBoard * 2, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])

    # Habilitar el uso de colores con iluminación
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Configurar tamaño de los puntos para visibilidad
    glPointSize(2.0)  # Puedes ajustar este valor según tus necesidades

    simulation.initialize_simulation(num_robots=2, num_packages=10)  # Iniciar simulación con 2 robots y 10 cajas

def display(simulation):
    """Renderiza la escena de la simulación."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        EYE_X, EYE_Y, EYE_Z,
        CENTER_X, CENTER_Y, CENTER_Z,
        UP_X, UP_Y, UP_Z
    )
    dibujarPlano()
    dibujarEjes()
    dibujar_area_almacenamiento()

    simulation.update()

    # Dibujar todos los robots
    for robot_state in simulation.robots_state:
        dibujar_robot(robot_state)

    # Dibujar todas las cajas en rojo
    for package in simulation.packages_state:
        dibujar_caja(package)

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
