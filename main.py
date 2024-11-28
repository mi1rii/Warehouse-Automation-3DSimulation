
# main.py
import os
import pygame
from pygame.locals import *
import numpy as np
import math
import random
import time  # Importar para manejar tiempos
import requests

from OpenGL.GL import *
from OpenGL.GLU import *
from opmat import OpMat

from py3dbp import Bin, Item, Packer

# Import obj loader
from objloader import * #CAMBIO

API_BASE_URL = "http://127.0.0.1:8000"  # URL of the Genie server

# Parámetros de pantalla y simulación
screen_width = 900
screen_height = 700

dimBoard = 500.0  # Tamaño del área del piso donde se colocarán las cajas
margin = 10.0

# Desplazamiento del área de aparición de las cajas
area_offset_x = 400.0  # Ajustado para posicionar el robot dentro del rectángulo
area_offset_z = 0.0     # Mantiene el desplazamiento en Z

# Parámetros de proyección perspectiva para 3D
FOVY = 90.0
ZNEAR = 1.0
ZFAR = 4000.0  # Mantener ZFAR para ver objetos lejanos

# Posición de la cámara
EYE_X = 400.0
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

objetos = [] #CAMBIO
objetos2 = [] #CAMBIO
objetos3 = []

contenedor_ancho = 320.0
contenedor_altura = 220.0
contenedor_profundidad = 200.0

# Dimensiones del rectángulo adicional (pasarela)
rectangulo_ancho = 400.0  # Ancho aumentado para mejor disposición
rectangulo_profundidad = 200.0
rectangulo_posicion = [dimBoard / 2 + rectangulo_ancho / 2, 0.0, 0.0]  # [250 + 200, 0, 0] = [450, 0, 0]

# Definir la posición de descarga (drop_position) en la esquina 4
# Esquina 4: [left, top]
drop_position = [
    rectangulo_posicion[0] - rectangulo_ancho / 2,
    0.0,
    rectangulo_posicion[2] + rectangulo_profundidad / 2
]


def get_robot_position(sim, robot_index=0):
    """Get robot position from the simulation"""
    try:
        # Make a GET request to fetch the current state of the simulation
        response = requests.post(f"{API_BASE_URL}/simulation/{sim}")
        print(f"Request URL: {API_BASE_URL}/simulation/{sim}")  # Debugging line
        print(f"Response Status Code: {response.status_code}")  # Debugging line
        response.raise_for_status()
        data = response.json()
        print(f"Response Data: {data}")  # Debugging line
        
        # Get the robot data from the response
        if "robots" in data and len(data["robots"]) > robot_index:
            robot = data["robots"][robot_index]
            return robot["x"], robot["y"], robot["z"]
        return None, None, None
    except requests.RequestException as e:
        print(f"Error getting robot position: {e}")
        return None, None, None

def initialize_simulation():
    """Initialize the simulation and get the simulation ID"""
    try:
        response = requests.post(f"{API_BASE_URL}/simulation", json={"num_robots": 1})
        response.raise_for_status()
        data = response.json()
        sim = data["id"]
        
        # Get initial position
        x, y, z = get_robot_position(sim)
        if x is None:
            x, y, z = 0.0, 0.0, 0.0
            
        return sim, x, y, z, data.get("robots", [])
    except requests.RequestException as e:
        print(f"Error initializing simulation: {e}")
        return None, 0.0, 0.0, 0.0, []

def update_robot_position(sim):
    """Update the robot's position and wait for confirmation."""
    global forklift_position_x, forklift_position_y, forklift_position_z
    target_x, target_y, target_z = forklift_position_x, forklift_position_y, forklift_position_z  # Store the current position as target
    x, y, z = get_robot_position(sim)
    
    if x is not None and y is not None and z is not None:
        forklift_position_x = x
        forklift_position_y = y
        forklift_position_z = z
        
        # Wait for the robot to reach the target position
        while not (math.isclose(forklift_position_x, target_x, abs_tol=0.1) and
                   math.isclose(forklift_position_y, target_y, abs_tol=0.1) and
                   math.isclose(forklift_position_z, target_z, abs_tol=0.1)):
            time.sleep(0.1)  # Wait for a short period before checking again
            x, y, z = get_robot_position(sim)
            if x is not None and y is not None and z is not None:
                forklift_position_x = x
                forklift_position_y = y
                forklift_position_z = z

def displayobj():

    glPushMatrix()  
    # Rotar en el eje Y para que el objeto mire hacia la izquierda
    glRotatef(90.0, 0.0, 1.0, 0.0)
    
    # Mantener la rotación en el eje X para la orientación correcta en el plano XZ
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    
    # Update the translation based on dynamic position values
    glTranslatef(0, 260, 0)
    # Establecer el color blanco
    glColor3f(1.0, 1.0, 1.0)

    glScale(12.0, 8.0, 12.0)
    objetos[0].render()  # Render the first object in the 'objetos' list
    
    glPopMatrix()

def displayobj2():

    glPushMatrix()  
    # Rotar en el eje Y para que el objeto mire hacia la izquierda
    glRotatef(90.0, 0.0, 1.0, 0.0)
    # Mantener la rotación en el eje X para la orientación correcta en el plano XZ
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    
    # Update the translation based on dynamic position values
    glTranslatef(-400, 50, 0)
    # Establecer el color blanco
    glColor3f(1.0, 1.0, 1.0)
    glScale(0.7, 0.7, 0.7)
    objetos2[0].render()  # Render the first object in the 'objetos' list
    
    glPopMatrix()

def displayobj3():

    glPushMatrix()  
    # Rotar en el eje Y para que el objeto mire hacia la izquierda
    glRotatef(90.0, 0.0, 1.0, 0.0)
    # Mantener la rotación en el eje X para la orientación correcta en el plano XZ
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    
    # Update the translation based on dynamic position values
    glTranslatef(-700, 50, 0)
    # Establecer el color blanco
    glColor3f(1.0, 1.0, 1.0)
    glScale(0.7, 0.7, 0.7)
    objetos3[0].render()  # Render the first object in the 'objetos' list
    
    glPopMatrix()
    
class Robot:
    def __init__(self, robot_id):
        # Identificador del robot
        self.id = robot_id
        # La posición inicial será la esquina 1: [left, bottom]
        self.position = [
            rectangulo_posicion[0] - rectangulo_ancho / 2,
            0.0,
            rectangulo_posicion[2] - rectangulo_profundidad / 2
        ]
        self.angle = 0.0  # Ángulo de orientación del robot
        self.state = "waiting"  # Estados: waiting, idle, moving_to_box, picking_box, moving_to_drop, placing_box
        self.target_box = None  # Caja objetivo
        self.speed = 3000.0  # Velocidad de movimiento
        self.pickup_distance = 10.0  # Distancia para recoger la caja
        self.radius = 10.0  # Radio del robot para detección de colisiones
        self.path = []  # Camino que seguirá el robot
        self.path_index = 0  # Índice del punto actual en el camino
        self.current_package_index = None  # Índice de la caja actual que se está procesando
        self.start_time = None  # Tiempo de inicio del robot

class SimulationState:
    def __init__(self):
        self.packages_state = []
        self.robots = []
        self.empaquetado_iniciado = False  # Indica si ya se inició el proceso de empaquetado
        self.empaquetado_inicio = None     # Tiempo de inicio del empaquetado

        # Coordenadas de las orillas de la pasarela
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

        # Crear tres robots
        self.num_robots = 3  # Número de robots
        for i in range(self.num_robots):
            robot = Robot(robot_id=i+1)
            self.robots.append(robot)

        # Actualizar la posición inicial de los robots a la esquina 1
        for robot in self.robots:
            robot.position = self.waypoints[0].copy()

    def initialize_simulation(self, num_packages=15):
        """Inicializa la simulación con cajas alrededor de la pasarela en tres lados."""
        dimensions_options = [
            (50.0, 50.0, 50.0),  # Tamaño más grande primero
            (40.0, 40.0, 40.0),
            (30.0, 30.0, 30.0)
        ]

        self.packages_state = []
        margin = 20.0  # Espacio entre las cajas y la pasarela
        occupied_positions = []  # Lista para mantener posiciones ocupadas y evitar superposición

        for i in range(num_packages):
            dimensiones = random.choice(dimensions_options)
            max_attempts = 100  # Máximo de intentos para colocar una caja sin superposición
            for attempt in range(max_attempts):
                position = self.generate_position_around_pasarela(dimensiones, margin)
                if not self.check_overlap(position, dimensiones, occupied_positions):
                    occupied_positions.append((position, dimensiones))
                    package = {
                        "position": position.copy(),
                        "angle": 0.0,  # Inicialmente sin rotación
                        "dimensions": dimensiones,
                        "state": "on_floor",
                        "start_position": position.copy(),
                        "end_position": None,
                        "order": None,  # Se asignará después del empaquetado
                        "assigned_robot_id": None  # Se asignará después del empaquetado
                    }
                    self.packages_state.append(package)
                    break
            else:
                print(f"Advertencia: No se pudo colocar la caja {i} sin superposición después de {max_attempts} intentos.")

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

        y = 10.0  # Las cajas están en el piso
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

    def empaquetar_cajas(self, contenedor_dimensiones):
        """Utiliza py3dbp para determinar el orden de las cajas."""
        packer = Packer()

        # Asignar un peso máximo alto para que no sea una limitación
        max_weight = 10000  # Puedes ajustar este valor según tus necesidades

        # Crear el contenedor con el peso máximo
        bin1 = Bin('contenedor', *contenedor_dimensiones, max_weight)
        packer.add_bin(bin1)

        # Crear los ítems (cajas)
        for idx, package in enumerate(self.packages_state):
            dimensiones = package["dimensions"]
            weight = 1  # Puedes asignar pesos reales si lo deseas
            # No permitir rotaciones de las cajas
            item = Item(f'caja_{idx}', *dimensiones, weight)
            item.rotation_type = 0  # No permitir rotaciones
            packer.add_item(item)

        # Realizar el empaquetado
        packer.pack(bigger_first=True, distribute_items=False, number_of_decimals=2)

        # Obtener el orden de las cajas
        order = []
        for b in packer.bins:
            for item in b.items:
                package_index = int(item.name.split('_')[1])
                package = self.packages_state[package_index]
                package["order"] = len(order)
                order.append(package)

                # Posición del ítem dentro del contenedor
                x, y, z = item.position

                # Convertir x, y, z a float para evitar errores de tipo
                x = float(x)
                y = float(y)
                z = float(z)
                # Convertir dimensiones a float
                item_width = float(item.width)
                item_height = float(item.height)
                item_depth = float(item.depth)
                # Ajustar la posición para centrar el contenedor en la escena
                x += -contenedor_ancho / 2.0 + item_width / 2.0
                z += -contenedor_profundidad / 2.0 + item_depth / 2.0
                # Ajustar y para apilar correctamente
                y += item_height / 2.0  # Centrar la caja verticalmente

                # Guardar la posición final
                package["end_position"] = [x, y, z]
                package["angle"] = 0.0  # Establecer ángulo a 0.0 ya que no hay rotación
                print(f"Caja {package_index} posicionada en el contenedor en {package['end_position']}.")

        # Ordenar las cajas según el empaquetado
        self.packages_state.sort(key=lambda p: p["order"])

        # Opcional: Manejar los ítems no empaquetados
        if packer.unfit_items:
            print("Las siguientes cajas no pudieron ser empaquetadas:")
            for item in packer.unfit_items:
                print(f"- {item.name} con dimensiones {item.width}x{item.height}x{item.depth}")

        # Asignar paquetes a los robots
        self.assign_packages_to_robots()

    def assign_packages_to_robots(self):
        """Asigna las cajas a los robots alternadamente."""
        num_packages = len(self.packages_state)
        num_robots = len(self.robots)
        for idx, package in enumerate(self.packages_state):
            robot = self.robots[idx % num_robots]
            package["assigned_robot_id"] = robot.id

    def update(self, current_time):
        if not self.empaquetado_iniciado:
            return

        # Actualizar cada robot
        for robot in self.robots:
            self.update_robot(robot, current_time)

    def update_robot(self, robot, current_time):
        # Inicializar el tiempo de inicio del robot
        if robot.start_time is None:
            robot.start_time = self.empaquetado_inicio + (robot.id - 1) * 5000  # 5000 ms = 5 segundos

        # Esperar hasta que hayan pasado 5 segundos desde el inicio del robot anterior
        if current_time < robot.start_time:
            return

        if robot.state == "waiting":
            robot.state = "idle"  # Cambiar a idle para comenzar su operación

        # Obtener las cajas asignadas a este robot que aún no han sido procesadas
        pending_packages = [
            p for p in self.packages_state
            if p.get("assigned_robot_id") == robot.id and p["state"] in ["on_floor", "carried_by_robot"]
        ]

        if robot.current_package_index is None:
            if pending_packages:
                # Asignar la siguiente caja al robot
                package = pending_packages[0]
                robot.current_package_index = self.packages_state.index(package)
            else:
                robot.state = "idle"
                print(f"Robot {robot.id} está en estado idle. Todas sus cajas han sido procesadas.")
                return
        else:
            package = self.packages_state[robot.current_package_index]

        if robot.state == "idle":
            robot.target_box = package
            # Generar camino desde la posición actual hasta el punto del contorno más cercano a la caja
            robot.path = self.generate_path_to_closest_perimeter_point(robot.position, package["position"])
            robot.path_index = 0  # Reiniciar el índice del camino
            robot.state = "moving_to_box"
            print(f"Robot {robot.id} moviéndose hacia la caja {robot.current_package_index} en posición {package['position']}.")

        elif robot.state == "moving_to_box":
            if robot.path_index < len(robot.path):
                self.move_robot_along_path(robot)
            else:
                # Moverse desde el punto del contorno hasta la caja
                self.move_robot_towards(robot, package["position"])
                if self.is_close(robot.position, package["position"], robot.pickup_distance):
                    robot.state = "picking_box"
                    print(f"Robot {robot.id} ha llegado a la caja {robot.current_package_index}.")

        elif robot.state == "picking_box":
            package["state"] = "carried_by_robot"
            # Generar camino desde la posición actual hasta el punto del contorno más cercano al punto de entrega
            robot.path = self.generate_path_to_closest_perimeter_point(robot.position, drop_position)
            robot.path_index = 0  # Reiniciar el índice del camino
            robot.state = "moving_to_drop"
            print(f"Robot {robot.id} ha recogido la caja {robot.current_package_index} y se dirige a la posición de entrega.")

        elif robot.state == "moving_to_drop":
            if robot.path_index < len(robot.path):
                self.move_robot_along_path(robot)
            else:
                # Moverse desde el punto del contorno hasta el punto de entrega
                self.move_robot_towards(robot, drop_position)
                if self.is_close(robot.position, drop_position):
                    robot.state = "placing_box"
                    print(f"Robot {robot.id} ha llegado a la posición de entrega para colocar la caja {robot.current_package_index}.")

        elif robot.state == "placing_box":
            # Colocar la caja en su posición final dentro del contenedor
            package["state"] = "in_container"
            package["position"] = package["end_position"].copy()  # Mover la caja a end_position dentro del contenedor
            package["angle"] = 0.0  # Establecer ángulo a 0.0 ya que no hay rotación
            robot.target_box = None
            robot.current_package_index = None
            robot.state = "idle"
            print(f"Robot {robot.id} ha colocado la caja {self.packages_state.index(package)} en el contenedor y está en estado idle.")

    def generate_path_to_closest_perimeter_point(self, start_position, target_position):
        """Genera un camino en sentido horario desde start_position hasta el punto del contorno más cercano al destino."""
        # Encontrar el punto del contorno más cercano al destino
        closest_point = self.get_closest_point_on_perimeter(target_position)
        # Generar camino en sentido horario desde la posición actual hasta el punto más cercano en el contorno
        path = self.generate_clockwise_path(start_position, closest_point)
        return path

    def get_closest_point_on_perimeter(self, position):
        """Encuentra el punto más cercano en el contorno (perímetro de la pasarela) a una posición dada."""
        x, y, z = position
        left = self.pasarela['left']
        right = self.pasarela['right']
        top = self.pasarela['top']
        bottom = self.pasarela['bottom']

        # Proyectar la posición al contorno de la pasarela
        if x < left:
            x_closest = left
        elif x > right:
            x_closest = right
        else:
            x_closest = x

        if z < bottom:
            z_closest = bottom
        elif z > top:
            z_closest = top
        else:
            z_closest = z

        # Determinar si la posición está más cerca de una esquina
        distances = []
        corners = [
            [left, 0.0, bottom],  # Esquina 1
            [right, 0.0, bottom],  # Esquina 2
            [right, 0.0, top],     # Esquina 3
            [left, 0.0, top],      # Esquina 4
        ]
        for corner in corners:
            distances.append(np.linalg.norm(np.array(position) - np.array(corner)))

        min_distance = min(distances)
        if min_distance < np.linalg.norm(np.array([x_closest, y, z_closest]) - np.array(position)):
            # Más cercano a una esquina
            closest_point = corners[distances.index(min_distance)]
        else:
            # Más cercano a un punto en los lados
            closest_point = [x_closest, 0.0, z_closest]

        return closest_point

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

    def find_closest_waypoint_index(self, position):
        """Encuentra el índice del waypoint más cercano a una posición dada."""
        distances = []
        for waypoint in self.waypoints:
            distances.append(np.linalg.norm(np.array(position) - np.array(waypoint)))
        return distances.index(min(distances))

    def move_robot_along_path(self, robot):
        if robot.path_index < len(robot.path):
            next_point = robot.path[robot.path_index]
            self.move_robot_towards(robot, next_point)
            if self.is_close(robot.position, next_point):
                robot.path_index += 1  # Avanzar al siguiente punto

    def move_robot_towards(self, robot, target_pos, ignore_orientation=False):
        current_pos = np.array(robot.position)
        target_pos = np.array(target_pos)
        direction = target_pos - current_pos
        distance = np.linalg.norm(direction)
        if distance > 0:
            direction_normalized = direction / distance
            step = direction_normalized * robot.speed * (1 / 60.0)  # Asumiendo 60 FPS

            # No exceder el objetivo
            if np.linalg.norm(step) > distance:
                step = direction

            # Calcular nueva posición tentativa
            new_position = current_pos + step

            # Mantener Y fijo en 0.0 para movimiento en XZ
            new_position[1] = 0.0

            # Actualización de posición
            robot.position = new_position.tolist()
            if not ignore_orientation:
                robot.angle = math.atan2(direction[2], direction[0])

    def is_close(self, pos1, pos2, threshold=1.0):
        """Verifica si dos posiciones están cerca dentro de un umbral dado."""
        return np.linalg.norm(np.array(pos1) - np.array(pos2)) <= threshold

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

class Camera:
    def __init__(self):
        self.position = np.array([EYE_X, EYE_Y, EYE_Z])
        self.center = np.array([CENTER_X, CENTER_Y, CENTER_Z])
        self.up = np.array([UP_X, UP_Y, UP_Z])
        self.zoom_speed = 1.0
        self.move_speed = 1.0

    def apply(self):
        gluLookAt(*self.position, *self.center, *self.up)

    def zoom_in(self):
        direction = self.center - self.position
        self.position += direction * self.zoom_speed * 0.1

    def zoom_out(self):
        direction = self.center - self.position
        self.position -= direction * self.zoom_speed * 0.1

    def move(self, dx, dy):
        right = np.cross(self.center - self.position, self.up)
        right = right / np.linalg.norm(right)
        up = np.cross(right, self.center - self.position)
        up = up / np.linalg.norm(up)

        self.position += right * dx * self.move_speed
        self.center += right * dx * self.move_speed
        self.position += up * dy * self.move_speed
        self.center += up * dy * self.move_speed

def dibujarPlano():
    """Dibuja un plano base sólido de color negro de 4000x4000 centrado en (0, 0, 0) en el plano y=0."""
    # Asegurar que OpenGL renderiza caras visibles correctamente
    glDisable(GL_CULL_FACE)  # Deshabilitar culling para que ambas caras sean visibles
    glDisable(GL_TEXTURE_2D)  # Desactivar texturas para evitar interferencias
    glColor3f(1.0, 1.0, 1.0)  # Establecer el color negro para el plano

    # Dibujar un cuadrado grande
    glBegin(GL_QUADS)
    glVertex3f(200.0, -18.0, -200.0)  # Esquina inferior izquierda
    glVertex3f(800.0, -18.0, -200.0)   # Esquina inferior derecha
    glVertex3f(800.0, -18.0, 200.0)    # Esquina superior derecha
    glVertex3f(200.0, -18.0, 200.0)   # Esquina superior izquierda
    glEnd()

    # Restaurar configuraciones globales para otros objetos
    glEnable(GL_CULL_FACE)
    glEnable(GL_TEXTURE_2D)
    
def dibujarPlano2():
    """Dibuja un plano base sólido de color negro de 4000x4000 centrado en (0, 0, 0) en el plano y=0."""
    # Asegurar que OpenGL renderiza caras visibles correctamente
    glDisable(GL_CULL_FACE)  # Deshabilitar culling para que ambas caras sean visibles
    glDisable(GL_TEXTURE_2D)  # Desactivar texturas para evitar interferencias
    glColor3f(0.0, 0.0, 0.0)  # Establecer el color negro para el plano

    # Dibujar un cuadrado grande
    glBegin(GL_QUADS)
    glVertex3f(-2000.0, -20.0, -2000.0)  # Esquina inferior izquierda
    glVertex3f(2000.0, -20.0, -2000.0)   # Esquina inferior derecha
    glVertex3f(2000.0, -20.0, 2000.0)    # Esquina superior derecha
    glVertex3f(-2000.0, -20.0, 2000.0)   # Esquina superior izquierda
    glEnd()

    # Restaurar configuraciones globales para otros objetos
    glEnable(GL_CULL_FACE)
    glEnable(GL_TEXTURE_2D)

def Init(simulation):
    """Inicializa la ventana de Pygame y configura OpenGL."""
    global camera
    camera = Camera()  # Crear instancia de la cámara
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: Simulación de Robots en Pasarela")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width / screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    camera.apply()  # Aplicar la cámara
    #glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    simulation.initialize_simulation()  # Iniciar simulación

def dibujar_caja(package_state, color_override=None):
    """Dibuja una caja como un cubo usando glLines."""
    opmat = OpMat()
    opmat.push()
    posicion = package_state["position"]
    angulo = package_state["angle"]
    dimensiones = package_state.get("dimensions")

    x, y, z = posicion

    opmat.translate(x, y, z)  # y ya está ajustado correctamente
    opmat.rotate(np.degrees(angulo), 0, 1, 0)  # Rotar alrededor del eje Y
    opmat.scale(*[dim / 2.0 for dim in dimensiones])  # Escalar según las dimensiones
    dibujar_caja_body(opmat, color_override)
    opmat.pop()

def dibujar_caja_body(opmat, color_override=None):
    """Dibuja el cuerpo de la caja como un cubo sólido con caras visibles desde dentro y fuera."""
    # Vértices del cubo unitario
    vertices = [
        (-1.0, -1.0, -1.0, 1.0),  # Vértice 0
        (1.0, -1.0, -1.0, 1.0),   # Vértice 1
        (1.0, -1.0, 1.0, 1.0),    # Vértice 2
        (-1.0, -1.0, 1.0, 1.0),   # Vértice 3
        (-1.0, 1.0, -1.0, 1.0),   # Vértice 4
        (1.0, 1.0, -1.0, 1.0),    # Vértice 5
        (1.0, 1.0, 1.0, 1.0),     # Vértice 6
        (-1.0, 1.0, 1.0, 1.0)     # Vértice 7
    ]

    # Transformar las coordenadas usando OpMat
    transformed_vertices = opmat.mult_Points(vertices)

    # Definir las caras del cubo (cada cara tiene 4 vértices)
    faces = [
        (0, 1, 2, 3),  # Base
        (4, 5, 6, 7),  # Cima
        (0, 1, 5, 4),  # Lado frontal
        (1, 2, 6, 5),  # Lado derecho
        (2, 3, 7, 6),  # Lado trasero
        (3, 0, 4, 7)   # Lado izquierdo
    ]

    # Establecer el color de las caras (café)
    if color_override:
        glColor3f(*color_override)
    else:
        glColor3f(0.73, 0.61, 0.43)  # Marrón

    # Configurar OpenGL para dibujar caras sólidas
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Dibujar polígonos llenos
    glDisable(GL_CULL_FACE)  # Deshabilitar culling para dibujar ambas caras

    # Dibujar cada cara del cubo
    glBegin(GL_QUADS)
    for face in faces:
        for vertex_index in face:
            vertex = transformed_vertices[vertex_index]
            glVertex3f(vertex[0], vertex[1], vertex[2])
    glEnd()

    # Dibujar los bordes en negro
    glColor3f(0.0, 0.0, 0.0)  # Color negro para los bordes
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)  # Cambiar a modo de líneas
    glBegin(GL_QUADS)
    for face in faces:
        for vertex_index in face:
            vertex = transformed_vertices[vertex_index]
            glVertex3f(vertex[0], vertex[1], vertex[2])
    glEnd()

    # Restaurar configuraciones
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Volver al modo relleno
    # glEnable(GL_CULL_FACE)  # Habilitar culling si lo necesitas para otros objetos


def dibujar_contenedor(texture_id):
    """Dibuja un contenedor texturizado con las dimensiones especificadas."""
    glPushMatrix()

    # Activar la textura y enlazarla
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Establecer el color a blanco para que no altere la textura
    glColor3f(1.0, 1.0, 1.0)

    # Desactivar face culling para renderizar las caras internas
    glDisable(GL_CULL_FACE)

    # Variables de dimensiones del contenedor
    ancho = contenedor_ancho / 2.0  # Dividir entre 2 para que esté centrado
    altura = contenedor_altura 
    profundidad = contenedor_profundidad / 2.0

    glBegin(GL_QUADS)

    # Cara Frontal (Z negativo)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-ancho, 0, -profundidad)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(ancho, 0, -profundidad)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(ancho, altura, -profundidad)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-ancho, altura, -profundidad)


    # Cara Izquierda (X negativo)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-ancho, 0, -profundidad)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(-ancho, 0, profundidad)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(-ancho, altura, profundidad)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-ancho, altura, -profundidad)



    # Cara Superior (Y positivo)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-ancho, altura, -profundidad)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(ancho, altura, -profundidad)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(ancho, altura, profundidad)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-ancho, altura, profundidad)

    # Cara Inferior (Y negativo)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-ancho, 0, -profundidad)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(ancho, 0, -profundidad)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(ancho, 0, profundidad)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-ancho, 0, profundidad)

    glEnd()

    # Restaurar configuraciones globales
    glEnable(GL_CULL_FACE)  # Rehabilitar culling
    glBindTexture(GL_TEXTURE_2D, 0)  # Desenlazar la textura
    glDisable(GL_TEXTURE_2D)  # Desactivar texturas

    glPopMatrix()
    
def draw_skybox(texture_id):
    glPushMatrix()

    # Activar la textura y enlazarla
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Establecer el color a blanco para que no altere la textura
    glColor3f(1.0, 1.0, 1.0)

    # Desactivar face culling para renderizar las caras internas
    glDisable(GL_CULL_FACE)

    size = 1000.0  # Tamaño del cubo del cielo

    glBegin(GL_QUADS)

    # **Cara Frontal (Mirando hacia dentro, Z negativo)**
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-size, size, -size)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(size, size, -size)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(size, -size, -size)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-size, -size, -size)

    # **Cara Trasera (Mirando hacia dentro, Z positivo)**
    glTexCoord2f(0.0, 0.0)
    glVertex3f(size, size, size)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(-size, size, size)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(-size, -size, size)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(size, -size, size)

    # **Cara Izquierda (Mirando hacia dentro, X negativo)**
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-size, size, size)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(-size, size, -size)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(-size, -size, -size)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-size, -size, size)

    # **Cara Derecha (Mirando hacia dentro, X positivo)**
    glTexCoord2f(0.0, 0.0)
    glVertex3f(size, size, -size)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(size, size, size)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(size, -size, size)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(size, -size, -size)

    # **Cara Superior (Mirando hacia dentro, Y positivo)**
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-size, size, size)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(size, size, size)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(size, size, -size)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-size, size, -size)

    # **Cara Inferior (Mirando hacia dentro, Y negativo)**
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-size, -size, -size)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(size, -size, -size)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(size, -size, size)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-size, -size, size)

    glEnd()

    # Rehabilitar face culling si estaba habilitado previamente
    glEnable(GL_CULL_FACE)

    # Desactivar la textura
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)

    glPopMatrix()

def dibujar_robot(robot):
    """Dibuja el robot como un cubo simple."""
    opmat = OpMat()
    opmat.push()
    x, y, z = robot.position
    angle = robot.angle

    # Posicionar y orientar el robot
    opmat.translate(x, y, z)  # Posicionar el robot en su ubicación
    opmat.rotate(np.degrees(-angle), 0, 1, 0)  # Rotar según la orientación del robot

    # Dibujar el cubo grande (base)
    opmat.push()  # Guardar estado actual
    opmat.scale(20.0, 20.0, 20.0)  # Escalar para que sea la base (cubo grande)
    dibujar_cubo2(opmat, color=(0.5, 0.5, 0.5))  # Dibujar cubo gris
    opmat.pop()  # Restaurar estado

    # Dibujar el cubo pequeño (cabeza)
    opmat.push()  # Guardar estado actual
    opmat.translate(0.0, 20.0, 0.0)  # Mover hacia arriba para colocar encima del cubo grande
    opmat.scale(12.0, 12.0, 12.0)  # Escalar para que sea la cabeza (cubo pequeño)
    dibujar_cubo2(opmat, color=(0.5, 0.5, 0.5))  # Dibujar cubo gris
    opmat.pop()  # Restaurar estado

    opmat.pop()  # Restaurar el estado principal

def dibujar_cubo2(opmat, color):
    """Dibuja un cubo sólido con el color especificado."""
    vertices = [
        (-1.0, -1.0, -1.0, 1.0),
        (1.0, -1.0, -1.0, 1.0),
        (1.0, -1.0, 1.0, 1.0),
        (-1.0, -1.0, 1.0, 1.0),
        (-1.0, 1.0, -1.0, 1.0),
        (1.0, 1.0, -1.0, 1.0),
        (1.0, 1.0, 1.0, 1.0),
        (-1.0, 1.0, 1.0, 1.0)
    ]

    transformed_vertices = opmat.mult_Points(vertices)

    # Definir las caras del cubo
    faces = [
        (0, 1, 2, 3),  # Base
        (4, 5, 6, 7),  # Cima
        (0, 1, 5, 4),  # Lado frontal
        (1, 2, 6, 5),  # Lado derecho
        (2, 3, 7, 6),  # Lado trasero
        (3, 0, 4, 7)   # Lado izquierdo
    ]

    glColor3f(*color)  # Establecer el color del cubo
    glBegin(GL_QUADS)  # Dibujar caras del cubo
    for face in faces:
        for vertex_index in face:
            vertex = transformed_vertices[vertex_index]
            glVertex3f(vertex[0], vertex[1], vertex[2])
    glEnd()

def dibujar_cubo(opmat, color):
    vertices = [
        (-1.0, -1.0, -1.0, 1.0),
        (1.0, -1.0, -1.0, 1.0),
        (1.0, -1.0, 1.0, 1.0),
        (-1.0, -1.0, 1.0, 1.0),
        (-1.0, 1.0, -1.0, 1.0),
        (1.0, 1.0, -1.0, 1.0),
        (1.0, 1.0, 1.0, 1.0),
        (-1.0, 1.0, 1.0, 1.0)
    ]

    transformed_vertices = opmat.mult_Points(vertices)

    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    glColor3f(*color)
    glBegin(GL_LINES)
    for edge in edges:
        start = transformed_vertices[edge[0]]
        end = transformed_vertices[edge[1]]
        glVertex3f(start[0], start[1], start[2])
        glVertex3f(end[0], end[1], end[2])
    glEnd()
    
# Función para cargar texturas
def load_texture(texture_path):
    try:
        texture_surface = pygame.image.load(texture_path)
    except pygame.error as e:
        print(f"Unable to load texture image: {texture_path}")
        raise SystemExit(e)
    
    texture_data = pygame.image.tostring(texture_surface, "RGB", True)
    width = texture_surface.get_width()
    height = texture_surface.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # Configurar los parámetros de la textura para repetir
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)  # Repetir en el eje S (X)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)  # Repetir en el eje T (Z)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glBindTexture(GL_TEXTURE_2D, 0)
    return texture_id

def display(simulation):
    """Renderiza la escena de la simulación."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Limpiar buffers
    glLoadIdentity()
    camera.apply()  # Aplicar la cámara
    Axis()
    dibujarPlano()
    dibujarPlano2()
    cont_texture = load_texture("cont.jpg")
    dibujar_contenedor(cont_texture)
    

    # Dibujar cajas
    for package in simulation.packages_state:
        if package["state"] == "on_floor":
            # Dibujar cajas en el piso
            dibujar_caja(package, color_override=(0.73, 0.61, 0.43))  # Marrón
        elif package["state"] == "carried_by_robot":
            # La caja se mueve con el robot correspondiente
            assigned_robot = next(
                (r for r in simulation.robots if r.id == package.get("assigned_robot_id")),
                None
            )
            if assigned_robot:
                package["position"] = [
                    assigned_robot.position[0],
                    50.0,
                    assigned_robot.position[2]
                ]
                package["angle"] = assigned_robot.angle
                dibujar_caja(package, color_override=(1.0, 1.0, 0.0))  # Amarillo
        elif package["state"] == "in_container":
            # Dibujar cajas dentro del contenedor
            dibujar_caja(package, color_override=(0.0, 1.0, 0.0))  # Verde

    # Dibujar robots
    for robot in simulation.robots:
        dibujar_robot(robot)

def main():
    """Función principal que ejecuta la simulación."""
    pygame.init()  # Inicializar Pygame
    simulation = SimulationState()
    done = False
    Init(simulation)  # Configurar la simulación
    background_texture = load_texture("back.png") 

     
    
    objetos.append(OBJ("truck.obj", swapyz=True))
    objetos[0].generate()
    
    objetos2.append(OBJ("Catering_Truck.obj", swapyz=True))
    objetos2[0].generate()
    
    objetos3.append(OBJ("Catering_Truck.obj", swapyz=True))
    objetos2[0].generate()
    
    global forklift_position_x, forklift_position_y, forklift_position_z

    # Initialize variables for position updates
    position_update_interval = 0.1  # Update every 100ms
    last_position_fetch_time = time.time()
    
    sim, forklift_position_x, forklift_position_y, forklift_position_z, robots = initialize_simulation()
    if sim is None:
        print("Failed to initialize simulation.")
        return

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
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up
                        camera.zoom_in()
                    elif event.button == 5:  # Scroll down
                        camera.zoom_out()
                elif event.type == pygame.MOUSEMOTION:
                    if pygame.mouse.get_pressed()[0]:  # Left button is held down
                        dx, dy = event.rel
                        camera.move(dx * 1, -dy * 1)

            if not simulation.empaquetado_iniciado and current_time - tiempo_inicio > tiempo_espera:
                # Realizar el empaquetado
                simulation.empaquetar_cajas((contenedor_ancho, contenedor_altura, contenedor_profundidad))
                simulation.empaquetado_iniciado = True

            current_time = time.time()
            try:
                requests.post(f"{API_BASE_URL}/simulation/{sim}", 
                                json={"velocidad": 1.0, "tiempo": position_update_interval})
            except requests.RequestException as e:
                print(f"Error updating simulation: {e}")


            simulation.update(current_time)  # Actualizar estado de la simulación
            display(simulation)  # Renderizar la simulación
            displayobj()  # Forklift
            displayobj2()  # Forklift
            displayobj3()
            
            draw_skybox(background_texture)
            pygame.display.flip()  # Actualizar la pantalla
            clock.tick(60)  # Limitar a 60 FPS

    finally:
        pygame.quit()  # Cerrar Pygame

if __name__ == '__main__':
    main()
