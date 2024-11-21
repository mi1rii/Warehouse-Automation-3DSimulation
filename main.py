import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import requests
import numpy as np
import json
import random

from Caja import Caja
from Cubo import Cubo
from Robot import Robot  # Importar la clase Robot en lugar de Lifter
from Camion import draw_rectangle_on_floor

API_BASE_URL = "http://127.0.0.1:8000"  # URL of the Genie server

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

# Función para cargar texturas
def load_texture(texture_path):
    try:
        texture_surface = pygame.image.load(texture_path)
    except pygame.error as e:
        print(f"Unable to load texture image: {texture_path}")
        raise SystemExit(e)
    
    # Detectar si la textura tiene un canal alfa
    texture_format = GL_RGBA if texture_surface.get_bitsize() == 32 else GL_RGB
    texture_data = pygame.image.tostring(texture_surface, "RGBA" if texture_format == GL_RGBA else "RGB", True)
    width = texture_surface.get_width()
    height = texture_surface.get_height()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexImage2D(GL_TEXTURE_2D, 0, texture_format, width, height, 0, texture_format, GL_UNSIGNED_BYTE, texture_data)
    glBindTexture(GL_TEXTURE_2D, 0)  # Liberar textura

    print(f"Textura cargada correctamente: {texture_path}, ID: {texture_id}, Formato: {'GL_RGBA' if texture_format == GL_RGBA else 'GL_RGB'}")
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
    glColor3f(1.0, 1.0, 1.0)  # Color blanco para mantener la textura original

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
    try:
        response = requests.post(f"{API_BASE_URL}/simulation", json={"num_robots": 1})
        response.raise_for_status()
        data = response.json()
        return data["id"], data["robots"]
    except requests.RequestException as e:
        print(f"Error initializing simulation: {e}")
        return None, []

def update_simulation(simulation_id):
    try:
        response = requests.post(f"{API_BASE_URL}/simulation/{simulation_id}")
        response.raise_for_status()
        data = response.json()
        return data["robots"]
    except requests.RequestException as e:
        print(f"Error updating simulation: {e}")
        if response is not None:
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.content}")
        return []

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Simulación 3D: Piso Texturizado, Ejes 3D y Robot")

    # Configuración de la proyección
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, SCREEN_WIDTH / SCREEN_HEIGHT, ZNEAR, ZFAR)

    # Configuración de la vista
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Habilitar el test de profundidad
    # Configuración de OpenGL en main.py
    glEnable(GL_DEPTH_TEST)  # Habilitar el test de profundidad
    
    glClearColor(135/255, 206/255, 250/255, 1.0)  # Fondo azul claro (135, 206, 250)
    
    glEnable(GL_CULL_FACE)  # (Normalmente habilitado, pero lo deshabilitaremos para probar)
    glDisable(GL_CULL_FACE)  # <--- Aquí deshabilitamos el culling
    glCullFace(GL_BACK)  # Opcional, define qué caras cull (no tendrá efecto con el culling deshabilitado)

    # Habilitar suavizado de caras
    glEnable(GL_CULL_FACE)
    glDisable(GL_CULL_FACE)

    # Habilitar texturas
    glEnable(GL_TEXTURE_2D)

    # Cargar las texturas
    floor_texture = load_texture("textures/Floor.jpg")
    wheel_texture = load_texture("textures/Wheel.jpg")         # Textura para las ruedas
    body_texture = load_texture("textures/RobotBody.jpg")      # Textura para el cuerpo del robot
    head_texture = load_texture("textures/Head.jpg")           # Textura para la cabeza del robot

    # Arreglo de texturas para Robot
    robot_textures = [floor_texture, wheel_texture, body_texture, head_texture]

    # Crear instancia de la cámara
    camera = Camera()

    # Initialize simulation
    simulation_id, robots_data = initialize_simulation()
    if not simulation_id:
        print("Failed to initialize simulation. Exiting.")
        return

    # Crear instancia de Robot con datos iniciales
    robot = Robot(dim=1, vel=1, textures=[])  # No need to pass textures anymore

    # Crear 5 cajas en el tercer cuadrante con diferentes dimensiones
    cajas = [
        Caja((1, 1, 1), (198/255, 154/255, 101/255), (-10.0, 0.5, -10.0)),  # Caja 1
        Caja((0.6, 0.4, 0.6), (198/255, 154/255, 101/255), (-12.0, 0.2, -12.0)),  # Caja 2
        Caja((2, 1, 2), (198/255, 154/255, 101/255), (-14.0, 0.5, -14.0)),  # Caja 3
        Caja((3, 3, 3), (198/255, 154/255, 101/255), (-16.0, 1.5, -16.0)),  # Caja 4
        Caja((3, 4, 3), (198/255, 154/255, 101/255), (-18.0, 2.0, -18.0))   # Caja 5
    ]

    clock = pygame.time.Clock()
    done = False  # Initialize the done variable

    # Variables para el movimiento del ratón
    pygame.event.set_grab(True)  # Capturar el ratón
    pygame.mouse.set_visible(False)  # Ocultar el cursor del ratón

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

        # Obtener el estado de las teclas
        keys = pygame.key.get_pressed()
        handle_keys(camera, keys)

        # Aplicar la transformación de la cámara
        glLoadIdentity()
        camera.apply_view()

        # Limpiar buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Dibujar los ejes
        draw_axes()

        # Dibujar el piso con textura
        draw_floor(floor_texture)
        glBindTexture(GL_TEXTURE_2D, 0)  # Liberar la textura del piso

        # Dibujar las cajas
        for caja in cajas:
            caja.draw()

        # Update simulation and get updated robot states
        robots_data = update_simulation(simulation_id)
        if not robots_data:
            print("Failed to update simulation. Exiting.")
            break

        # Ensure robots_data is not empty before accessing its elements
        if robots_data:
            robot_data = robots_data[0]
            robot.update_from_dict(robot_data)
        else:
            print("No robot data received. Exiting.")
            break

        # Dibujar el robot montacargas (Robot)
        robot.draw()

        # Dibujar el rectángulo en el plano "Floor"
        draw_rectangle_on_floor()

        # Actualizar la pantalla
        pygame.display.flip()
        clock.tick(60)  # Limitar a 60 FPS

    # Limpiar y salir
    pygame.quit()

if __name__ == "__main__":
    main()