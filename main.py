import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
from Caja import Caja
import random

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

def generate_box_positions(num_cajas):
    colors = [
        (1.0, 0.0, 0.0),  # Rojo
        (0.0, 1.0, 0.0),  # Verde
        (0.0, 0.0, 1.0),  # Azul
        (1.0, 1.0, 0.0),  # Amarillo
        (1.0, 0.0, 1.0),  # Magenta
    ]

    dimensions_list = [
        (1, 1, 1),  # Tipo 1
        (0.6, 0.4, 0.6),  # Tipo 2
        (2, 1, 2),  # Tipo 3
        (3, 3, 3),  # Tipo 4
        (3, 4, 3),  # Tipo 5
    ]

    box_positions = []
    min_distance = 4  # Distancia mínima entre cajas

    for _ in range(num_cajas):
        while True:
            x = random.uniform(-50.0, -1.0)  # X en el tercer cuadrante
            z = random.uniform(-50.0, -1.0)  # Z en el tercer cuadrante
            y = dimensions_list[0][1] / 2.0 + 0.1  # Fijo para que la caja esté encima del piso

            # Seleccionar un tipo de dimensiones aleatorio
            dimensions = random.choice(dimensions_list)
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

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Simulación 3D: Piso Texturizado y Ejes 3D")

    # Configuración de la proyección
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, SCREEN_WIDTH / SCREEN_HEIGHT, ZNEAR, ZFAR)

    # Configuración de la vista
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Habilitar el test de profundidad
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)

    # Habilitar suavizado de caras
    glCullFace(GL_BACK)

    # Habilitar texturas
    glEnable(GL_TEXTURE_2D)

    # Cargar la textura del piso
    floor_texture = load_texture("Floor.jpg")

    # Crear instancia de la cámara
    camera = Camera()

    num_cajas = 50
    box_positions = generate_box_positions(num_cajas)

    # Crear las cajas con las posiciones, dimensiones y colores generados
    cajas = [
        Caja(dimensions, color, (x, y, z))
        for x, y, z, dimensions, color in box_positions
    ]

    clock = pygame.time.Clock()
    done = False

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

        # Dibujar las cajas
        for caja in cajas:
            caja.draw()

        # Actualizar la pantalla
        pygame.display.flip()
        clock.tick(60)  # Limitar a 60 FPS

    # Limpiar y salir
    pygame.quit()

if __name__ == "__main__":
    main()