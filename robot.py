"""TODO A JULIA"""
from main import(
    rectangulo_ancho,
    rectangulo_posicion,
    rectangulo_profundidad,
    drop_position
)

class Robot:
    def __init__(self, robot_id):
        # Identificador del robot
        self.id = robot_id
        # La posición inicial será la esquina 1: [left, bottom]
        self.position = [rectangulo_posicion[0] - rectangulo_ancho / 2, 0.0, rectangulo_posicion[2] - rectangulo_profundidad / 2]
        self.angle = 0.0  # Ángulo de orientación del robot
        self.state = "waiting"  # Estados: waiting, idle, moving_to_box, picking_box, moving_to_drop, placing_box
        self.target_box = None  # Caja objetivo
        self.speed = 100.0  # Velocidad de movimiento
        self.pickup_distance = 10.0  # Distancia para recoger la caja
        self.radius = 10.0  # Radio del robot para detección de colisiones
        self.path = []  # Camino que seguirá el robot
        self.path_index = 0  # Índice del punto actual en el camino
        self.current_package_index = None  # Índice de la caja actual que se está procesando
        self.start_time = None  # Tiempo de inicio del robot

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
            pending_packages = [p for p in self.packages_state if p.get("assigned_robot_id") == robot.id and p["state"] in ["on_floor", "carried_by_robot"]]

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

    
    
    
    def update(self, current_time):
        if not self.empaquetado_iniciado:
            return

        # Actualizar cada robot
        for robot in self.robots:
            self.update_robot(robot, current_time)

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
