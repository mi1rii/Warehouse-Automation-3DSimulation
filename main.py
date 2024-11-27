# main.py
import os
import pygame
from pygame.locals import *
import numpy as np
import math
import random
import time  # Importar para manejar tiempos

from caja import *
from robot import *
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

# Desplazamiento del área de aparición de las cajas
area_offset_x = 400.0  # Ajustado para posicionar el robot dentro del rectángulo
area_offset_z = 0.0     # Mantiene el desplazamiento en Z

# Parámetros de proyección perspectiva para 3D
FOVY = 60.0
ZNEAR = 1.0
ZFAR = 2000.0  # Mantener ZFAR para ver objetos lejanos

# Posición de la cámara
EYE_X = 0.0
EYE_Y = 800.0  # Mantener la altura de la cámara para ver mejor las cajas
EYE_Z = 800.0
CENTER_X = 0.0
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
    def __init__(self):
        self.packages_state = []
        self.robots = []
        self.empaquetado_iniciado = False  # Indica si ya se inició el proceso de empaquetado

        # Coordenadas de las orillas de la pasarela
        """PASAR A JULIA"""
        self.pasarela = {
            'left': rectangulo_posicion[0] - rectangulo_ancho / 2,
            'right': rectangulo_posicion[0] + rectangulo_ancho / 2,
            'top': rectangulo_posicion[2] + rectangulo_profundidad / 2,
            'bottom': rectangulo_posicion[2] - rectangulo_profundidad / 2
        }
        # Definir las esquinas (waypoints) en sentido horario
        self.waypoints = [
            [self.pasarela['left'], 0.0, self.pasarela['bottom']],  # Esquina 1
            [self.pasarela['right'], 0.0, self.pasarela['bottom']],  # Esquina 2
            [self.pasarela['right'], 0.0, self.pasarela['top']],     # Esquina 3
            [self.pasarela['left'], 0.0, self.pasarela['top']],      # Esquina 4
        ]
        ""

        # Crear tres robots
        self.num_robots = 3  # Número de robots
        for i in range(self.num_robots):
            robot = Robot(robot_id=i+1)
            self.robots.append(robot)

        """JULIA"""
        # Actualizar la posición inicial de los robots a la esquina 1
        for robot in self.robots:
            robot.position = self.waypoints[0].copy()
        ""


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
    """Inicializa la simulación."""
    renderer.init_gl()
    simulation.initialize_simulation()

def display(simulation):
    """Renderiza la escena de la simulación."""
    renderer.render_scene(simulation)

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

    simulation.empaquetado_inicio = tiempo_inicio + tiempo_espera  # Tiempo en que inicia el empaquetado

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

            simulation.update(current_time)  # Actualizar estado de la simulación
            display(simulation)  # Renderizar la simulación
            pygame.display.flip()  # Actualizar la pantalla
            clock.tick(60)  # Limitar a 60 FPS

    finally:
        pygame.quit()  # Cerrar Pygame

if __name__ == '__main__':
    main()
