# opmat.py
import numpy as np

class OpMat:
    def __init__(self):
        self.init_matrix = np.identity(4)  # Matriz 4x4 para transformaciones 3D
        self.pila = []

    def translate(self, tx, ty, tz):
        """Aplica una traslación en los ejes x, y, z."""
        T =  np.array(
            [[1., 0., 0., tx],
             [0., 1., 0., ty],
             [0., 0., 1., tz],
             [0., 0., 0., 1.]]
        )
        self.init_matrix = self.init_matrix @ T

    def scale(self, sx, sy, sz):
        """Aplica un escalado en los ejes x, y, z."""
        S =  np.array(
            [[sx, 0., 0., 0.],
             [0., sy, 0., 0.],
             [0., 0., sz, 0.],
             [0., 0., 0., 1.]]
        )
        self.init_matrix = self.init_matrix @ S

    def rotateZ(self, deg):
        """Aplica una rotación alrededor del eje Z."""
        rad = np.radians(deg)
        R = np.array([
            [np.cos(rad), -np.sin(rad), 0.0, 0.0],
            [np.sin(rad),  np.cos(rad), 0.0, 0.0],
            [0.0,          0.0,         1.0, 0.0],
            [0.0,          0.0,         0.0, 1.0]
        ])
        self.init_matrix = self.init_matrix @ R

    def rotateX(self, deg):
        """Aplica una rotación alrededor del eje X."""
        rad = np.radians(deg)
        R = np.array([
            [1.0, 0.0,          0.0,         0.0],
            [0.0, np.cos(rad), -np.sin(rad), 0.0],
            [0.0, np.sin(rad),  np.cos(rad), 0.0],
            [0.0, 0.0,          0.0,         1.0]
        ])
        self.init_matrix = self.init_matrix @ R

    def rotateY(self, deg):
        """Aplica una rotación alrededor del eje Y."""
        rad = np.radians(deg)
        R = np.array([
            [ np.cos(rad), 0.0, np.sin(rad), 0.0],
            [ 0.0,         1.0, 0.0,         0.0],
            [-np.sin(rad), 0.0, np.cos(rad), 0.0],
            [ 0.0,         0.0, 0.0,         1.0]
        ])
        self.init_matrix = self.init_matrix @ R

    def rotate(self, deg, x, y, z): 
        """Aplica una rotación alrededor de un eje arbitrario (x, y, z)."""
        if x == 1 and y == 0 and z == 0:
            self.rotateX(deg)
        elif x == 0 and y == 1 and z == 0:
            self.rotateY(deg)
        elif x == 0 and y == 0 and z == 1:
            self.rotateZ(deg)
        else:
            # Normalizar el vector de rotación
            norm = np.sqrt(x**2 + y**2 + z**2)
            if norm == 0:
                raise ValueError("El vector de rotación no puede ser cero.")
            x /= norm
            y /= norm
            z /= norm
            rad = np.radians(deg)
            c = np.cos(rad)
            s = np.sin(rad)
            t = 1 - c

            # Matriz de rotación utilizando la fórmula de Rodrigues
            R = np.array([
                [t*x*x + c,    t*x*y - s*z,  t*x*z + s*y, 0.0],
                [t*x*y + s*z,  t*y*y + c,    t*y*z - s*x, 0.0],
                [t*x*z - s*y,  t*y*z + s*x,  t*z*z + c,   0.0],
                [0.0,          0.0,          0.0,         1.0]
            ])
            self.init_matrix = self.init_matrix @ R

    def loadIdentity(self):
        """Carga la matriz identidad."""
        self.init_matrix = np.identity(4)

    def push(self):
        """Guarda la matriz actual en la pila."""
        self.pila.append(self.init_matrix.copy())

    def pop(self):
        """Recupera la última matriz de la pila."""
        if self.pila:
            self.init_matrix = self.pila.pop()
        else:
            print("Stack is empty")

    def mult_Points(self, points):
        """Multiplica una lista de puntos por la matriz de transformación actual."""
        transformed_points = []
        for x, y, z, w in points:
            vec = np.array([x, y, z, w])
            transformed_vec = self.init_matrix @ vec
            transformed_points.append(
                (transformed_vec[0], transformed_vec[1], transformed_vec[2])
            )
        return transformed_points
