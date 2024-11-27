# main.py
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
import numpy as np
import requests
import time
import requests
from decimal import Decimal
import math
import random

import py3dbp

from py3dbp import Bin, Item, Packer

from Caja import Caja

API_BASE_URL = "http://127.0.0.1:8000"  # URL of the Genie server

# Import obj loader
from objloader import *

# Parámetros de pantalla y simulación
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700

# Parámetros de proyección perspectiva para 3D
FOVY = 60.0
ZNEAR = 1.0
ZFAR = 500.0

# Posición inicial de la cámara
CENTER_X = 0.0
CENTER_Y = 0.0
CENTER_Z = 0.0
UP_X = 0.0
UP_Y = 1.0
UP_Z = 0.0

# Variables para dibujar los ejes del sistema
AXIS_LENGTH = 50

objetos = []
objetos2 = []
objetos3 = []
objetos3_2 = []

# CONNECTION
def get_robot_position(simulation_id, robot_index=0):
    try:
        response = requests.get(f"{API_BASE_URL}/simulation/{simulation_id}")
        response.raise_for_status()
        data = response.json()

        robots = data.get("robots", [])
        if robot_index < len(robots):
            robot = robots[robot_index]
            return robot["position"][0], robot["position"][1], robot["position"][2]
        else:
            print(f"Robot index {robot_index} out of range")
            return None, None, None
    except requests.RequestException as e:
        print(f"Error getting robot position: {e}")
        return None, None, None

def convert_decimal(obj):
    """Recursively convert Decimal to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal(v) for v in obj]
    else:
        return obj  # Return other types unchanged

# Clase para manejar la cámara
class Camera:
    def __init__(self):
        self.angle_h = 0.0  # Ángulo horizontal (yaw)
        self.angle_v = 0.0  # Ángulo vertical (pitch)
        self.distance = 30.0  # Distancia desde el centro
        self.mouse_sensitivity = 0.2
        self.move_speed = 1.0

    def handle_mouse_motion(self, dx, dy):
        self.angle_h += dx * self.mouse_sensitivity
        self.angle_v += dy * self.mouse_sensitivity
        self.angle_v = max(-89.0, min(89.0, self.angle_v))  # Limitar el pitch

    def get_position(self):
        rad_h = math.radians(self.angle_h)
        rad_v = math.radians(self.angle_v)
        x = self.distance * math.cos(rad_v) * math.sin(rad_h)
        y = self.distance * math.sin(rad_v)
        z = self.distance * math.cos(rad_v) * math.cos(rad_h)
        return (x, y, z)

    def apply_view(self):
        eye = self.get_position()
        gluLookAt(
            eye[0], eye[1], eye[2],
            CENTER_X, CENTER_Y, CENTER_Z,
            UP_X, UP_Y, UP_Z
        )
        
# Define global variables for position FORKLIFT MOVEMENT
forklift_position_x = 0.0
forklift_position_y = 0.0
forklift_position_z = 0.0

def displayobj():
    global forklift_position_x, forklift_position_y, forklift_position_z

    glPushMatrix()  
    # Apply the corrections to draw the object on the XZ plane
    glRotatef(-90.0, 1.0, 0.0, 0.0)
    
    # Update the translation based on dynamic position values
    glTranslatef(forklift_position_x, forklift_position_y, forklift_position_z)

    glScale(2.0, 2.0, 2.0)
    objetos[0].render()  # Render the first object in the 'objetos' list
    
    glPopMatrix()
    
def displayobj2():
    glPushMatrix()  
    #correcciones para dibujar el objeto en plano XZ
    #esto depende de cada objeto
    glRotatef(-90.0, 270.0, 0.0, 0.0)
    glTranslatef(20.0, 42.5, 0)
    glScale(0.9,0.6, 0.5)
    objetos2[0].render()  
    glPopMatrix()
    
def displayobj3():
    glPushMatrix()  
    # Correcciones para dibujar el objeto en plano XZ
    # Esto depende de cada objeto
    glRotatef(-90.0, 100.0, 0.0, 0.0)
    glTranslatef(0.0, 20.5, 0)
    glScale(0.04, 0.05, 0.03)
    objetos3[0].render()  
    glPopMatrix()

def displayobj4():
    glPushMatrix()  
    # Correcciones para dibujar el objeto en plano XZ
    # Esto depende de cada objeto
    glRotatef(-90.0, 100.0, 0.0, 0.0)
    glTranslatef(-17.0, 20.5, 0)
    glScale(0.04, 0.05, 0.03)
    objetos3_2[0].render()  
    glPopMatrix()

def initialize_boxes(num_cajas, container_dimensions):
    """
    Initialize boxes using the 3dbinpacking algorithm.
    """
    # Get packed box positions
    packed_boxes = empaquetar_cajas(num_cajas, container_dimensions)

    # Generate `Caja` objects for visualization
    cajas = []
    for box in packed_boxes:
        x, y, z = box["position"]
        dimensions = box["dimensions"]
        color = (198/255, 154/255, 101/255)  # Default box color
        cajas.append(Caja(dimensions, color, (x, y, z)))

    return cajas, packed_boxes

# Función para dibujar un cielo en forma de cubo

def draw_corridor_path():
    glPushMatrix()
    
    # Establecer el color blanco para el pasillo
    glColor3f(1.0, 1.0, 1.0)
    
    # Posicionar el pasillo en la cajuela del camión
    glTranslatef(20.0, 5.0, -23.0)  # (x, y, z)
    
    # Definir las dimensiones del pasillo
    corridor_length_start_z = 10.0    # Inicio del pasillo desde la cajuela
    corridor_length_end_z = 65.0     # Extensión del pasillo a lo largo del eje Z
    corridor_x_left = 10.0            # Posición X de la pared izquierda
    corridor_x_right = -10.0          # Posición X de la pared derecha
    
    glDisable(GL_CULL_FACE)  # Deshabilitar face culling para ambas caras
    
    glBegin(GL_QUADS)
    
    # --- Superficie del pasillo (cara superior) ---
    glColor3f(1.0, 1.0, 1.0)  # Color blanco
    glVertex3f(corridor_x_left, -4.99, corridor_length_start_z)  # Esquina superior izquierda
    glVertex3f(corridor_x_right, -4.99, corridor_length_start_z)  # Esquina superior derecha
    glVertex3f(corridor_x_right, -4.99, corridor_length_end_z)  # Esquina inferior derecha
    glVertex3f(corridor_x_left, -4.99, corridor_length_end_z)  # Esquina inferior izquierda
    
    # --- Parte inferior del pasillo (cara inferior) ---
    glColor3f(1.0, 1.0, 1.0)  # Color blanco
    glVertex3f(corridor_x_left, -5.01, corridor_length_start_z)  # Esquina superior izquierda
    glVertex3f(corridor_x_right, -5.01, corridor_length_start_z)  # Esquina superior derecha
    glVertex3f(corridor_x_right, -5.01, corridor_length_end_z)  # Esquina inferior derecha
    glVertex3f(corridor_x_left, -5.01, corridor_length_end_z)  # Esquina inferior izquierda
    
    glEnd()
    
    glEnable(GL_CULL_FACE)  # Rehabilitar face culling
    
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

    size = 50.0  # Tamaño del cubo del cielo

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


def draw_cajuela():
    glPushMatrix()
    
    # Posicionar y escalar la cajuela
    glTranslatef(20.0, 6.0, -23.0)
    glScale(1.0, 0.80, 2.0)
    
    # Habilitar el test de profundidad
    glEnable(GL_DEPTH_TEST)
    
    # Deshabilitar face culling para renderizar ambas caras
    glDisable(GL_CULL_FACE)
    
    size = 6.0  # Tamaño del cubo
    ramp_length = 7.0 
    
    # Dibujar las caras del cubo
    
    # Cara frontal (gris)
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(-size, -size, -size)
    glEnd()
    
    # Cara izquierda (gris)
    glBegin(GL_QUADS)
    glVertex3f(-size, size, size)
    glVertex3f(-size, size, -size)
    glVertex3f(-size, -size, -size)
    glVertex3f(-size, -size, size)
    glEnd()
    
    # Cara derecha (gris)
    glBegin(GL_QUADS)
    glVertex3f(size, size, size)
    glVertex3f(size, size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glEnd()
    
    # Cara superior (gris)
    glBegin(GL_QUADS)
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)
    glEnd()
    
    # Cara inferior (rojo oscuro)
    glColor3f(109/255, 17/255, 10/255)  # Color rojo oscuro
    glBegin(GL_QUADS)
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glVertex3f(-size, -size, size)
    glEnd()
    
    # Dibujar las aristas del cubo en color negro
    glColor3f(0.0, 0.0, 0.0) 
    glLineWidth(1.0) 
    glBegin(GL_LINES)
    
    # Cara frontal (aristas)
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)

    glVertex3f(size, size, -size)
    glVertex3f(size, -size, -size)

    glVertex3f(size, -size, -size)
    glVertex3f(-size, -size, -size)

    glVertex3f(-size, -size, -size)
    glVertex3f(-size, size, -size)

    # Cara trasera (aristas)
    glVertex3f(-size, size, size)
    glVertex3f(size, size, size)

    glVertex3f(size, size, size)
    glVertex3f(size, -size, size)

    glVertex3f(size, -size, size)
    glVertex3f(-size, -size, size)

    glVertex3f(-size, -size, size)
    glVertex3f(-size, size, size)

    # Conectar cara frontal y trasera (aristas)
    glVertex3f(-size, size, -size)
    glVertex3f(-size, size, size)

    glVertex3f(size, size, -size)
    glVertex3f(size, size, size)

    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)

    glVertex3f(-size, -size, -size)
    glVertex3f(-size, -size, size)
    
    glEnd()
    
    # Dibujar la rampa (trasera, inclinada hacia abajo)
    glColor3f(109/255, 17/255, 10/255)  # Color gris para la rampa
    glBegin(GL_TRIANGLES)
    glVertex3f(-size, -size, size)  # Esquina inferior izquierda trasera de la cajuela
    glVertex3f(size, -size, size)   # Esquina inferior derecha trasera de la cajuela
    glVertex3f(0.0, -size - 1.0, size + ramp_length)   # Vértice inferior extendido (más largo)
    glEnd()
    
    # Rehabilitar face culling
    glEnable(GL_CULL_FACE)
    
    glPopMatrix()
    
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

# Función para dibujar los ejes en direcciones positivas y negativas
def draw_axes():
    glLineWidth(3.0)
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
    

# Función para dibujar el piso con textura repetida
def draw_floor(texture_id):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor3f(1.0, 1.0, 1.0)  # Color blanco para mantener la textura original\

    glBegin(GL_QUADS)
    # Definir el tamaño del piso
    size = 50.0
    y = 0.0  # Altura del piso

    # Número de repeticiones de la textura
    repeat = 10.0

    # Coordenadas del piso con texturas repetidas (orden invertido)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-size, y, size)

    glTexCoord2f(repeat, 0.0)
    glVertex3f(size, y, size)

    glTexCoord2f(repeat, repeat)
    glVertex3f(size, y, -size)

    glTexCoord2f(0.0, repeat)
    glVertex3f(-size, y, -size)
    glEnd()

    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
    

# Función para manejar eventos de teclado
def handle_keys(camera, keys):
    if keys[pygame.K_w]:
        camera.distance -= 0.5
        camera.distance = max(5.0, camera.distance)
    if keys[pygame.K_s]:
        camera.distance += 0.5
    if keys[pygame.K_a]:
        camera.angle_h -= 1.0
    if keys[pygame.K_d]:
        camera.angle_h += 1.0

def empaquetar_cajas(num_cajas, container_dimensions):
    """
    Use the 3dbinpacking library to calculate box positions in the container.
    """
    packer = Packer()
    container_name = "truck_container"

    # Set max_weight to a large numeric value instead of infinity
    bin1 = Bin(container_name, *container_dimensions, max_weight=10000.0)  # Replace inf with 10000.0
    packer.add_bin(bin1)

    dimensions_list = [
        (3.0, 3.0, 3.0), 
        (4.2, 4.2, 4.2), 
        (0.6, 0.6, 0.6)
    ]

    # Create boxes
    for i in range(num_cajas):
        dims = random.choice(dimensions_list)
        item = Item(f"box_{i}", *dims, weight=1.0)
        packer.add_item(item)

    for dims in dimensions_list:
        if any(dim <= 0 for dim in dims):
            raise ValueError("Item dimensions must be positive and non-zero.")
    
    # Perform packing
    packer.pack()

    packed_boxes = []
    for b in packer.bins:
        for item in b.items:
            x, y, z = item.position
            dims = (item.width, item.height, item.depth)
            packed_boxes.append({"position": [x, y, z], "dimensions": dims})
            
    packed_boxes.append({
        "position": [float(x), float(y), float(z)],  # Ensure positions are floats
        "dimensions": [float(dim) for dim in dims]  # Ensure dimensions are floats
    })

    return packed_boxes
        
def initialize_simulation():
    try:
        response = requests.post(f"{API_BASE_URL}/simulation", json={"num_robots": 5})
        response.raise_for_status()
        data = response.json()

        simulation_id = data.get("id")
        if not simulation_id:
            raise ValueError("Simulation ID not returned from server")

        robots = data.get("robots", [])
        print(f"Simulation ID: {simulation_id}")
        print(f"Robots initialized: {robots}")

        return simulation_id, robots
    except requests.RequestException as e:
        print(f"Error initializing simulation: {e}")
        return None, []

def update_robot_position(simulation_id):
    """Update the robot's position"""
    global forklift_position_x, forklift_position_y, forklift_position_z
    x, y, z = get_robot_position(simulation_id)
    if x is not None and y is not None and z is not None:
        forklift_position_x = x
        forklift_position_y = y
        forklift_position_z = z
        
        
def send_box_positions_to_julia(packed_boxes):
    
    print("Packed boxes before sending to Julia:", packed_boxes)
    for i, box in enumerate(packed_boxes):
        print(f"Box {i}: Position={box['position']}, Angle={box.get('angle', 0.0)}, State={box.get('state', 'unknown')}")


    """Send packed box positions to the Julia backend."""
    url = f"{API_BASE_URL}/update-boxes"
    
    # Prepare data to send
    data = {
        "boxes": convert_decimal([{
            "position": box["position"],
            "angle": box.get("angle", 0.0),  # Default angle to 0.0 if missing
            "state": box.get("state", "unknown")  # Default state to "unknown" if missing
        } for box in packed_boxes])
    }

    print("Data being sent to Julia:", data)  # Debugging log

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        print("Successfully sent box positions to Julia:", response.json())
    except requests.RequestException as e:
        print(f"Error sending box positions to Julia: {e}")
    
    for i, box in enumerate(packed_boxes):
        if "position" not in box or "angle" not in box or "state" not in box:
            print(f"Invalid box at index {i}: {box}")

        
def interpolate_position(current, target, alpha):
    return current + (target - current) * alpha


def main():
    global forklift_position_x, forklift_position_y, forklift_position_z

    # Initialize variables for position updates
    position_update_interval = 0.1  # Update every 100ms
    last_position_fetch_time = time.time()
    # Initialize Pygame and OpenGL
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Simulación 3D")

    # OpenGL projection and modelview setup
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, SCREEN_WIDTH / SCREEN_HEIGHT, ZNEAR, ZFAR)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    glDisable(GL_CULL_FACE)
    glEnable(GL_TEXTURE_2D)

    # Load textures and models
    floor_texture = load_texture("piso.jpg")
    background_texture = load_texture("back.png")  # Carga la textura de fondo
    camera = Camera()
    objetos.append(OBJ("forklift.obj", swapyz=True))
    objetos[0].generate()
    objetos2.append(OBJ("truck.obj", swapyz=True))
    objetos2[0].generate()
    objetos3.append(OBJ("Catering_Truck.obj", swapyz= True))
    objetos3[0].generate()
    objetos3_2.append(OBJ("Catering_Truck.obj", swapyz= True))
    objetos3_2[0].generate()
    
    # Initialize simulation in Julia and get the simulation ID
    simulation_id, forklift_position_x, forklift_position_y, forklift_position_z, robots = initialize_simulation()
    if simulation_id is None:
        print("Failed to initialize simulation.")
        return

    # Generate packed boxes and visualize them
    num_cajas = 50
    container_dimensions = (320.0, 220.0, 200.0)  # Width, height, depth of container
    cajas, packed_boxes = initialize_boxes(num_cajas, container_dimensions)
    
        # Validate dimensions for Bin and Items
    if any(dim <= 0 for dim in container_dimensions):
        raise ValueError("Container dimensions must be positive and non-zero.")


    # Send packed box positions to Julia
    send_box_positions_to_julia(packed_boxes)

    # Pygame clock for framerate control
    clock = pygame.time.Clock()
    pygame.event.set_grab(True)  # Capture mouse
    pygame.mouse.set_visible(False)

    # Main loop
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
            elif event.type == pygame.MOUSEMOTION:
                dx, dy = event.rel
                camera.handle_mouse_motion(dx, dy)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Rueda del ratón hacia arriba
                    camera.distance -= 1.0
                    camera.distance = max(5.0, camera.distance)
                elif event.button == 5:  # Rueda del ratón hacia abajo
                    camera.distance += 1.0
                    camera.distance = min(100.0, camera.distance)
                    
        # Update robot position from Julia
        update_robot_position(simulation_id)
        
        # Handle key inputs for camera movement
        keys = pygame.key.get_pressed()
        handle_keys(camera, keys)

        # Update camera view
        glLoadIdentity()
        camera.apply_view()

        # Clear screen and render the scene
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_axes()
        draw_floor(floor_texture)
        draw_skybox(background_texture)

        # Render objects and forklift/robot
        displayobj()  # Forklift
        displayobj2()  # Truck
        displayobj3()  # Truck
        displayobj4()
        # Dibujar el pasillo recto
        draw_corridor_path()
        draw_cajuela()

        # Render boxes
        for caja in cajas:
            caja.draw()

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    # Clean up and exit
    pygame.quit()

if __name__ == "__main__":
    main()
