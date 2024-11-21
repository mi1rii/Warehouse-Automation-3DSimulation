
# robot_module.py
import pygame
from pygame.locals import *
from Cubo import Cubo

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math

class Robot:
    def __init__(self, dim, vel, textures):
        self.dim = dim
        self.vel = vel
        self.textures = textures
        self.Position = [0, 6, 0]

        dirX = random.randint(-10, 10)
        dirZ = random.randint(-10, 10)
        # Evitar división por cero
        if dirX == 0 and dirZ == 0:
            dirX, dirZ = 1, 1
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]
        self.angle = 0  # Mantendremos este valor fijo

        self.platformHeight = 0  # Inicializar platformHeight

    def draw(self):
        glPushMatrix()
        # Translate to the truck's position (place it slightly above the floor)
        glTranslatef(self.Position[0], 2, self.Position[2])  # Set y = 0.5 to raise the truck

        # Rotate the truck if needed
        glRotatef(self.angle, 0, 1, 0)

        # Scale down the truck
        glScaled(1.5, 1.5, 1.5)  # Reduce the size

        # Set the truck color to red
        glColor3f(1.0, 0.0, 0.0)

        # Draw the main body of the truck
        glBegin(GL_QUADS)
        # Front face
        glVertex3d(1, 1, 1)
        glVertex3d(1, 1, -1)
        glVertex3d(1, -1, -1)
        glVertex3d(1, -1, 1)

        # Back face
        glVertex3d(-2, 1, 1)
        glVertex3d(-2, 1, -1)
        glVertex3d(-2, -1, -1)
        glVertex3d(-2, -1, 1)

        # Top face
        glVertex3d(1, 1, 1)
        glVertex3d(-2, 1, 1)
        glVertex3d(-2, 1, -1)
        glVertex3d(1, 1, -1)

        # Bottom face
        glVertex3d(1, -1, 1)
        glVertex3d(-2, -1, 1)
        glVertex3d(-2, -1, -1)
        glVertex3d(1, -1, -1)

        # Right face
        glVertex3d(1, 1, -1)
        glVertex3d(-2, 1, -1)
        glVertex3d(-2, -1, -1)
        glVertex3d(1, -1, -1)

        # Left face
        glVertex3d(1, 1, 1)
        glVertex3d(-2, 1, 1)
        glVertex3d(-2, -1, 1)
        glVertex3d(1, -1, 1)
        glEnd()

        # Draw the head of the truck
        glPushMatrix()
        glTranslatef(0.0, 1.0, 0)  # Position the head forward and above the body
        glScaled(1.0, 1.0, 1.0)  # Make the head larger
        self.draw_cube()  # Draw the head as a cube
        glPopMatrix()
        
        self.draw_forklift_arms()

        # Draw the wheels of the truck
        glPushMatrix()
        glTranslatef(-1.2, -1, 1)  # Position of the wheel
        glScaled(0.3, 0.3, 0.3)  # Scale down the wheels
        self.draw_wheel()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.5, -1, 1)
        glScaled(0.3, 0.3, 0.3)
        self.draw_wheel()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.5, -1, -1)
        glScaled(0.3, 0.3, 0.3)
        self.draw_wheel()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-1.2, -1, -1)
        glScaled(0.3, 0.3, 0.3)
        self.draw_wheel()
        glPopMatrix()

        glPopMatrix()

        
    def draw_wheel(self):
        glColor3f(0.0, 0.0, 0.0)  # Black color

        glBegin(GL_QUADS)
        # Front face
        glVertex3d(-1, -1, 1)
        glVertex3d(1, -1, 1)
        glVertex3d(1, 1, 1)
        glVertex3d(-1, 1, 1)
        # Back face
        glVertex3d(-1, -1, -1)
        glVertex3d(1, -1, -1)
        glVertex3d(1, 1, -1)
        glVertex3d(-1, 1, -1)
        # Top face
        glVertex3d(-1, 1, -1)
        glVertex3d(1, 1, -1)
        glVertex3d(1, 1, 1)
        glVertex3d(-1, 1, 1)
        # Bottom face
        glVertex3d(-1, -1, -1)
        glVertex3d(1, -1, -1)
        glVertex3d(1, -1, 1)
        glVertex3d(-1, -1, 1)
        # Right face
        glVertex3d(1, -1, -1)
        glVertex3d(1, 1, -1)
        glVertex3d(1, 1, 1)
        glVertex3d(1, -1, 1)
        # Left face
        glVertex3d(-1, -1, -1)
        glVertex3d(-1, 1, -1)
        glVertex3d(-1, 1, 1)
        glVertex3d(-1, -1, 1)
        glEnd()


    def draw_cube(self):
        glBegin(GL_QUADS)
        # Front face
        glVertex3d(-1, -1, 1)
        glVertex3d(1, -1, 1)
        glVertex3d(1, 1, 1)
        glVertex3d(-1, 1, 1)
        # Back face
        glVertex3d(-1, -1, -1)
        glVertex3d(1, -1, -1)
        glVertex3d(1, 1, -1)
        glVertex3d(-1, 1, -1)
        # Top face
        glVertex3d(-1, 1, -1)
        glVertex3d(1, 1, -1)
        glVertex3d(1, 1, 1)
        glVertex3d(-1, 1, 1)
        # Bottom face
        glVertex3d(-1, -1, -1)
        glVertex3d(1, -1, -1)
        glVertex3d(1, -1, 1)
        glVertex3d(-1, -1, 1)
        # Right face
        glVertex3d(1, -1, -1)
        glVertex3d(1, 1, -1)
        glVertex3d(1, 1, 1)
        glVertex3d(1, -1, 1)
        # Left face
        glVertex3d(-1, -1, -1)
        glVertex3d(-1, 1, -1)
        glVertex3d(-1, 1, 1)
        glVertex3d(-1, -1, 1)
        glEnd()

    def draw_forklift_arms(self):
        glColor3f(0.0, 0.0, 0.0)  # Set color to black for the arms

        # Left arm (closer to the robot's front)
        glPushMatrix()
        glTranslatef(1.5, 0.0, 0.6)  # Position the left arm more forward (z = 0.6)
        glScaled(1.0, 0.1, 0.1)  # Shorten the arm length (x-axis scaling = 1.0)
        self.draw_cube()  # Draw the left arm as a cube
        glPopMatrix()

        # Right arm (closer to the robot's back)
        glPushMatrix()
        glTranslatef(1.5, 0.0, -0.6)  # Position the right arm more backward (z = -0.6)
        glScaled(1.0, 0.1, 0.1)  # Shorten the arm length (x-axis scaling = 1.0)
        self.draw_cube()  # Draw the right arm as a cube
        glPopMatrix()

    def update_from_dict(self, data):
        self.position = data["position"]
        self.angle = data["angle"]
        # Update other attributes as needed