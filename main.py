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

# CONNECTION
# Function to get the robot's position from the server
def get_robot_position(simulation_id, robot_index=0):
    """Get robot position from the simulation"""
    try:
        # Make a GET request to fetch the current state of the simulation
        response = requests.post(f"{API_BASE_URL}/simulation/{simulation_id}")
        response.raise_for_status()
        data = response.json()
        
        # Get the robot data from the response
        if "robots" in data and len(data["robots"]) > robot_index:
            robot = data["robots"][robot_index]
            return robot["x"], robot["y"], robot["z"]
        return None, None, None
    except requests.RequestException as e:
        print(f"Error getting robot position: {e}")
        return None, None, None


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
    
def generate_box_positions(num_cajas):
    colors = [
        (198/255, 154/255, 101/255),  # Rojo
        (198/255, 154/255, 101/255),  # Verde
        (198/255, 154/255, 101/255),  # Azul
        (198/255, 154/255, 101/255),  # Amarillo
        (198/255, 154/255, 101/255),  # Magenta
    ]

    dimensions_list = [
        (1, 1, 1), 
        (0.6, 0.4, 0.6), 
        (2, 2, 2),  
        (3, 3, 3),
        (3, 1, 3,)
    ]

    box_positions = []
    min_distance = 4  # Distancia mínima entre cajas

    for _ in range(num_cajas):
        while True:
            # Seleccionar un tipo de dimensiones aleatorio
            dimensions = random.choice(dimensions_list)
            x = random.uniform(-50.0, -1.0)  # X en el tercer cuadrante
            z = random.uniform(50.0, -1.0)  # Z en el tercer cuadrante
            y = dimensions[1] / 2.0 # Fijo para que la caja esté encima del piso

            color = random.choice(colors)
            # Verificar colisiones en el plano X-Z
            collision = False
            for pos in box_positions:
                distance = math.sqrt((x - pos[0]) ** 2 + (z - pos[2]) ** 2)  # Comparar X e Z
                if distance < min_distance:
                    collision = True
                    break

            if not collision:
                box_positions.append((x, y, z, dimensions, color))
                break

    return box_positions

# Función para dibujar un cielo en forma de cubo

def draw_skybox():
    glPushMatrix()
    glEnable(GL_DEPTH_TEST)  
    glColor3f(0.53, 0.81, 0.98)  # Color azul cielo
    
    size = 50.0  # Tamaño del cubo del cielo, basado en el tamaño del piso

    # Dibujar las caras internas del cubo
    glBegin(GL_QUADS)

    # Cara frontal
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(-size, -size, -size)

    # Cara trasera
    glVertex3f(-size, size, size)
    glVertex3f(size, size, size)
    glVertex3f(size, -size, size)
    glVertex3f(-size, -size, size)

    # Cara izquierda
    glVertex3f(-size, size, size)
    glVertex3f(-size, size, -size)
    glVertex3f(-size, -size, -size)
    glVertex3f(-size, -size, size)

    # Cara derecha
    glVertex3f(size, size, size)
    glVertex3f(size, size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)

    # Cara superior
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)

    # Cara inferior (opcional para el cielo, usualmente no visible)
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glVertex3f(-size, -size, size)

    glEnd()

    glEnable(GL_DEPTH_TEST)  # Restaurar el test de profundidad
    glPopMatrix()
    
def draw_cajuela():
    glPushMatrix()
    glTranslatef(20.0, 6.0, -23.0)
    glScale(1.0, 0.99, 2.0)

    # Habilitar el test de profundidad
    glEnable(GL_DEPTH_TEST)

    size = 6.0  # Tamaño del cubo

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
    glColor3f(109/255, 17/255, 10/255)
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
        
def initialize_simulation():
    """Initialize the simulation and get the simulation ID"""
    try:
        response = requests.post(f"{API_BASE_URL}/simulation", json={"num_robots": 1})
        response.raise_for_status()
        data = response.json()
        simulation_id = data["id"]
        
        # Get initial position
        x, y, z = get_robot_position(simulation_id)
        if x is None:
            x, y, z = 0.0, 0.0, 0.0
            
        return simulation_id, x, y, z, data.get("robots", [])
    except requests.RequestException as e:
        print(f"Error initializing simulation: {e}")
        return None, 0.0, 0.0, 0.0, []

def update_robot_position(simulation_id):
    """Update the robot's position"""
    global forklift_position_x, forklift_position_y, forklift_position_z
    x, y, z = get_robot_position(simulation_id)
    if x is not None and y is not None and z is not None:
        forklift_position_x = x
        forklift_position_y = y
        forklift_position_z = z
        
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
    floor_texture = load_texture("floor.jpg")
    camera = Camera()
    objetos.append(OBJ("forklift.obj", swapyz=True))
    objetos[0].generate()
    objetos2.append(OBJ("truck.obj", swapyz=True))
    objetos2[0].generate()

    # Generate boxes
    num_cajas = 50
    box_positions = generate_box_positions(num_cajas)
    cajas = [
        Caja(dimensions, color, (x, y, z))
        for x, y, z, dimensions, color in box_positions
    ]

    # Initialize simulation and get robot id
    robot_id, forklift_position_x, forklift_position_y, forklift_position_z, robots = initialize_simulation()
    if robot_id is None:
        print("Failed to initialize simulation.")
        return

    # Pygame clock for framerate control
    clock = pygame.time.Clock()
    pygame.event.set_grab(True)  # Capture mouse
    pygame.mouse.set_visible(False)
    
    simulation_id, forklift_position_x, forklift_position_y, forklift_position_z, robots = initialize_simulation()
    if simulation_id is None:
        print("Failed to initialize simulation.")
        return

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
                    
        # Update robot position periodically
        current_time = time.time()
        if current_time - last_position_fetch_time > position_update_interval:
            update_robot_position(simulation_id)
            last_position_fetch_time = current_time
        # Handle key inputs for camera movement
        keys = pygame.key.get_pressed()
        handle_keys(camera, keys)

        # Periodically update the robot's position
        current_time = time.time()
        if current_time - last_position_fetch_time > position_update_interval:
            robot_x, robot_y, robot_z = get_robot_position(1)  # Assuming robot_id = 1
            if robot_x is not None and robot_y is not None and robot_z is not None:
                forklift_position_x, forklift_position_y, forklift_position_z = robot_x, robot_y, robot_z
            last_position_fetch_time = current_time  # Update the time of last position fetch
            
        try:
            requests.post(f"{API_BASE_URL}/simulation/{simulation_id}", 
                        json={"velocidad": 1.0, "tiempo": position_update_interval})
        except requests.RequestException as e:
            print(f"Error updating simulation: {e}")

        # Update camera view
        glLoadIdentity()
        camera.apply_view()

        # Clear screen and render the scene
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_axes()
        draw_floor(floor_texture)
        draw_skybox()

        # Render objects and forklift/robot
        displayobj()  # Forklift
        displayobj2()  # Truck
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
