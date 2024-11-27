import random

def initialize_simulation(self, num_packages=15):
    """Inicializa la simulación con cajas alrededor de la pasarela en tres lados."""
    dimensions_options = [
        (10.0, 10.0, 10.0),
        (50.0, 50.0, 50.0),
        (70.0, 70.0, 70.0)
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
                }
                self.packages_state.append(package)
                break
        else:
            print(f"Advertencia: No se pudo colocar la caja {i} sin superposición después de {max_attempts} intentos.")