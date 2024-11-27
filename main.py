# main.py
import os
import pygame
from pygame.locals import *
import numpy as np
import math
import random
import time  # Importar para manejar tiempos
import requests
import json

from renderer import *
from caja import *
from robot import Robot
from OpenGL.GL import *
from OpenGL.GLU import *
from opmat import OpMat

from py3dbp import Bin, Item, Packer

import renderer

# Parámetros de pantalla y simulación
screen_width = 900
screen_height = 700

dimBoard = 500.0  # Tamaño del área del piso donde se colocarán las cajas
margin = 10.0

# Definir parámetros de proyección ortográfica para 2D
ORTHO_LEFT = -dimBoard
ORTHO_RIGHT = dimBoard
ORTHO_BOTTOM = -dimBoard
ORTHO_TOP = dimBoard
ORTHO_NEAR = -1.0
ORTHO_FAR = 1.0

# Desplazamiento del área de aparición de las cajas
area_offset_x = 400.0  # Ajustado para posicionar el robot dentro del rectángulo
area_offset_z = 0.0     # Mantiene el desplazamiento en Z

# Parámetros de proyección perspectiva para 3D
FOVY = 40.0
ZNEAR = 1.0
ZFAR = 2000.0  # Mantener ZFAR para ver objetos lejanos

# Posición de la cámara
EYE_X = 0.0
EYE_Y = 800.0  # Mantener la altura de la cámara para ver mejor las cajas
EYE_Z = 800.0
CENTER_X = 200.0
CENTER_Y = 0.0
CENTER_Z = 0.0
UP_X = 0.0
UP_Y = 1.0
UP_Z = 0.0

# Variables para dibujar los ejes del sistema
X_MIN = -1000
X_MAX = 1000
Y_MIN = -1000
Y_MAX = 1000
Z_MIN = -1000
Z_MAX = 1000

STACK_TOLERANCE = 1

# Dimensiones del contenedor
contenedor_ancho = 320.0
contenedor_altura = 220.0
contenedor_profundidad = 200.0

"""JULIA Y PYTHON"""
# Dimensiones del rectángulo adicional (pasarela)
rectangulo_ancho = 400.0  # Ancho aumentado para mejor disposición
rectangulo_profundidad = 200.0
rectangulo_posicion = [dimBoard / 2 + rectangulo_ancho / 2, 0.0, 0.0]  # [250 + 200, 0, 0] = [450, 0, 0]
""

"""JULIA"""
# Definir la posición de descarga (drop_position) en la esquina 4
# Esquina 4: [left, top]
drop_position = [rectangulo_posicion[0] - rectangulo_ancho / 2, 0.0, rectangulo_posicion[2] + rectangulo_profundidad / 2]
""

class SimulationState:
    """Clase para gestionar el estado de la simulación."""
    def __init__(self):
        self.simulation_id = None
        self.robots_state = []
        self.packages_state = []
        self.api_url = "http://localhost:8000"

    def initialize_simulation(self, num_robots=3, num_packages=15):
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


    """JULIA"""
    def generate_position_around_pasarela(self, dimensions, margin):
        """Genera posiciones alrededor de la pasarela en tres lados."""
        side = random.choice(['top', 'bottom', 'right'])
        buffer = margin

        if side == 'top':
            x = random.uniform(
                rectangulo_posicion[0] - rectangulo_ancho / 2 - buffer - dimensions[0] / 2,
                rectangulo_posicion[0] + rectangulo_ancho / 2 + buffer + dimensions[0] / 2)
            z = rectangulo_posicion[2] + rectangulo_profundidad / 2 + buffer + dimensions[2] / 2
        elif side == 'bottom':
            x = random.uniform(
                rectangulo_posicion[0] - rectangulo_ancho / 2 - buffer - dimensions[0] / 2,
                rectangulo_posicion[0] + rectangulo_ancho / 2 + buffer + dimensions[0] / 2)
            z = rectangulo_posicion[2] - rectangulo_profundidad / 2 - buffer - dimensions[2] / 2
        elif side == 'right':
            x = rectangulo_posicion[0] + rectangulo_ancho / 2 + buffer + dimensions[0] / 2
            z = random.uniform(
                rectangulo_posicion[2] - rectangulo_profundidad / 2 - buffer - dimensions[2] / 2,
                rectangulo_posicion[2] + rectangulo_profundidad / 2 + buffer + dimensions[2] / 2)

        y = 0.0  # Las cajas están en el piso
        return [x, y, z]
    def check_overlap(self, position, dimensions, occupied_positions):
        """Verifica si una nueva caja se superpone con cajas existentes."""
        new_min_x = position[0] - dimensions[0] / 2.0
        new_max_x = position[0] + dimensions[0] / 2.0
        new_min_z = position[2] - dimensions[2] / 2.0
        new_max_z = position[2] + dimensions[2] / 2.0

        for (pos, dims) in occupied_positions:
            existing_min_x = pos[0] - dims[0] / 2.0
            existing_max_x = pos[0] + dims[0] / 2.0
            existing_min_z = pos[2] - dims[2] / 2.0
            existing_max_z = pos[2] + dims[2] / 2.0

            # Verificar superposición en el plano XZ
            overlap_x = not (new_max_x < existing_min_x or new_min_x > existing_max_x)
            overlap_z = not (new_max_z < existing_min_z or new_min_z > existing_max_z)

            if overlap_x and overlap_z:
                return True  # Hay superposición

        return False  # No hay superposición
    ""


    def empaquetar_cajas(self, contenedor_dimensiones):
        """Utiliza py3dbp para determinar el orden de las cajas con impresión detallada."""
        print("\n--- INICIO DEL PROCESO DE EMPAQUETADO ---")
        print(f"Dimensiones del contenedor: {contenedor_dimensiones}")

        # Crear el empaquetador
        packer = Packer()

        # Definir peso máximo
        max_weight = 10000
        print(f"Peso máximo del contenedor: {max_weight}")

        # Crear el contenedor
        bin1 = Bin('contenedor', *contenedor_dimensiones, max_weight)
        print(f"Contenedor creado: {bin1}")
        packer.add_bin(bin1)

        # Imprimir detalles de las cajas
        print("\n--- DETALLES DE LAS CAJAS ---")
        for idx, package in enumerate(self.packages_state):
            dimensiones = package["dimensions"]
            print(f"Caja {idx}:")
            print(f"  Dimensiones: {dimensiones}")
            
            """JULIA"""
            print(f"  Posición inicial: {package['position']}")
            ""

            # Crear ítem para empaquetado
            weight = 1  # Peso arbitrario
            item = Item(f'caja_{idx}', *dimensiones, weight)
            
            # Configuración de rotación
            item.rotation_type = 0  # No permitir rotaciones
            print(f"  Tipo de rotación: {item.rotation_type}")

            packer.add_item(item)

        # Realizar el empaquetado
        print("\n--- CRITERIOS DE ACOMODO ---")
        packer.pack(
            bigger_first=True,  # Empaquetar cajas más grandes primero
            distribute_items=False,  # No distribuir ítems entre múltiples contenedores
            number_of_decimals=2
        )

        # Imprimir resultados del empaquetado
        print("\n--- RESULTADOS DEL EMPAQUETADO ---")
        for b in packer.bins:
            print(f"Contenedor: {b}")
            print(f"Volumen total: {b.width}x{b.height}x{b.depth}")
            print("Ítems empaquetados:")
            for item in b.items:
                print(f"  - {item.name}")
                print(f"    Dimensiones: {item.width}x{item.height}x{item.depth}")
                print(f"    Posición en contenedor: {item.position}")

        # Manejar cajas no empaquetadas
        if packer.unfit_items:
            print("\n--- CAJAS NO EMPAQUETADAS ---")
            for item in packer.unfit_items:
                print(f"- {item.name} con dimensiones {item.width}x{item.height}x{item.depth}")

        """PROCESO DE ACOMODO"""
        # Procesar cajas empaquetadas
        order = []
        for b in packer.bins:
            for item in b.items:
                package_index = int(item.name.split('_')[1])
                package = self.packages_state[package_index]
                package["order"] = len(order)
                order.append(package)

                # Convertir coordenadas a float
                x, y, z = map(float, item.position)
                item_width = float(item.width)
                item_height = float(item.height)
                item_depth = float(item.depth)

                # Ajustar posición para centrar el contenedor
                x += -contenedor_dimensiones[0] / 2.0 + item_width / 2.0
                y = 0.0  # Mantener y fijo
                z += -contenedor_dimensiones[2] / 2.0 + item_depth / 2.0

                # Guardar posición final
                package["end_position"] = [x, y, z]
                package["angle"] = 0.0

                print(f"\nCaja {package_index}:")
                print(f"  Posición inicial: {package['position']}")
                print(f"  Posición final en contenedor: {package['end_position']}")
                
        ""

        # Ordenar cajas según el empaquetado
        self.packages_state.sort(key=lambda p: p["order"])

        # Asignar paquetes a robots
        self.assign_packages_to_robots()

        print("\n--- FIN DEL PROCESO DE EMPAQUETADO ---")
        
    """VER SI SE PUEDE PASAR A JULIA"""        
    def assign_packages_to_robots(self):
        """Asigna las cajas a los robots alternadamente."""
        num_packages = len(self.packages_state)
        num_robots = len(self.robots)
        for idx, package in enumerate(self.packages_state):
            robot = self.robots[idx % num_robots]
            package["assigned_robot_id"] = robot.id
    ""

    def generate_clockwise_path(self, start_pos, end_pos):
        """Genera una lista de waypoints en sentido horario desde start_pos hasta end_pos alrededor de la pasarela."""
        waypoints = self.waypoints.copy()

        # Encontrar el índice del waypoint más cercano al punto de inicio y al punto final
        start_index = self.find_closest_waypoint_index(start_pos)
        end_index = self.find_closest_waypoint_index(end_pos)

        # Generar camino en sentido horario desde start_index hasta end_index
        path = []
        index = start_index
        while True:
            path.append(waypoints[index])
            if index == end_index:
                break
            index = (index + 1) % len(waypoints)

        return path
    
def Init(simulation):
    """Inicializa la ventana de Pygame y configura OpenGL."""
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: Robots")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Configurar proyección ortográfica para 2D
    gluOrtho2D(ORTHO_LEFT, ORTHO_RIGHT, ORTHO_BOTTOM, ORTHO_TOP)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()  # Cargar la identidad para 2D
    
    glClearColor(0, 0, 0, 0)  # Color de fondo negro
    glDisable(GL_DEPTH_TEST)  # Deshabilitar test de profundidad para 2D
    glEnable(GL_BLEND) 
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Modo de polígono relleno

    # Configurar tamaño de los puntos para visibilidad
    glPointSize(2.0)  # Puedes ajustar este valor según tus necesidades

    renderer.init_gl()
    simulation.initialize_simulation()

def display(simulation):
    """Renderiza la escena de la simulación."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Limpiar buffers
    renderer.render_scene(simulation)
    simulation.update()  # Actualizar estado de la simulación

    # # Dibujar todos los robots
    # for robot_state in simulation.robots_state:
    #     dibujar_robot(robot_state)
        
    # Agrupar cajas en pilas según la tolerancia
    stacks = {}
    for package in simulation.packages_state:
        pos = package["position"]
        if len(pos) >= 2:
            x, y = pos[0], pos[1]
        else:
            print("Posición inválida:", pos)
            continue
        # Redondear posiciones para agrupar en pilas
        stack_key = (round(x / STACK_TOLERANCE) * STACK_TOLERANCE,
                    round(y / STACK_TOLERANCE) * STACK_TOLERANCE)
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

    # Variables para control del inicio de la simulación
    tiempo_inicio = pygame.time.get_ticks()
    tiempo_espera = 2000  # Esperar 2 segundos antes de iniciar el movimiento

    simulation.empaquetado_iniciado = tiempo_inicio + tiempo_espera  # Tiempo en que inicia el empaquetado

    try:
        while not done:
            current_time = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True  # Salir del bucle principal

            if not simulation.empaquetado_iniciado and current_time - tiempo_inicio > tiempo_espera:
                # Realizar el empaquetado
                simulation.empaquetar_cajas((contenedor_ancho, contenedor_altura, contenedor_profundidad))
                simulation.empaquetado_iniciado = True

            simulation.update()  # Actualizar estado de la simulación
            display(simulation)  # Renderizar la simulación
            pygame.display.flip()  # Actualizar la pantalla
            clock.tick(60)  # Limitar a 60 FPS

    finally:
        pygame.quit()  # Cerrar Pygame

if __name__ == '__main__':
    main()
