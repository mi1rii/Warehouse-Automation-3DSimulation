module ModuloRobot

export Robot, crearRobot, mover_robot!, to_dict

# Define the Robot type with necessary properties
mutable struct Robot
    x::Float64       # Position X
    y::Float64       # Position Y (height)
    z::Float64       # Position Z
    angulo::Float64  # Orientation angle
    velocidad::Float64
    target_x::Float64
    target_y::Float64
    estado::Symbol   # :idle, :moving, :picking, :dropping
    last_target_time::Float64
end

# Constructor for creating a new robot
function crearRobot(pos_inicial::Float64, vel_inicial::Float64)
    Robot(
        0.0,            # Initial X position
        0.0,            # Initial Y position
        0.0,            # Initial Z position
        0.0,            # Initial angle
        vel_inicial,    # Initial velocity
        0.0,           # Initial target X
        0.0,           # Initial target Z
        :idle,         # Initial state
        time()         # Current time
    )
end

# Convert robot state to dictionary for JSON serialization
function to_dict(robot::Robot)
    Dict(
        "x" => robot.x,
        "y" => robot.y,
        "z" => robot.z,
        "angulo" => robot.angulo,
        "velocidad" => robot.velocidad,
        "estado" => string(robot.estado)
    )
end

# Generate a new random target within bounds
function generar_nuevo_objetivo!(robot::Robot)
    # Define boundaries (matching your Python frontend)
    max_bound = 45.0
    min_bound = -45.0
    
    # Generate new target position
    robot.target_x = 0
    robot.target_y = 10
    robot.last_target_time = time()
    robot.estado = :moving
    
    # Calculate new angle towards target
    dx = robot.target_x - robot.x
    dy = robot.target_y - robot.y
    robot.angulo = atan(dx, dy)
end

# Check if robot has reached its target
function ha_llegado_objetivo(robot::Robot)
    dx = robot.target_x - robot.x
    dy = robot.target_y - robot.y
    distancia = sqrt(dx^2 + dy^2)
    return distancia < 0.1
end

# Main movement function
function mover_robot!(robot::Robot, tiempo::Float64, angulo::Float64)
    # If idle, potentially generate new target
    if robot.estado == :idle
        if time() - robot.last_target_time > 2.0  # Wait 2 seconds between movements
            generar_nuevo_objetivo!(robot)
        end
        return
    end

    # If moving, update position
    if robot.estado == :moving
        # Calculate direction vector
        dx = robot.target_x - robot.x
        dy = robot.target_y - robot.y
        distancia = sqrt(dx^2 + dy^2)
        
        if distancia < 0.1
            robot.estado = :idle
            robot.last_target_time = time()
            return
        end
        
        # Normalize direction and apply velocity
        velocidad_actual = robot.velocidad * tiempo
        robot.x += (dx / distancia) * velocidad_actual
        robot.y += (dy / distancia) * velocidad_actual
        
        # Update angle towards movement direction
        robot.angulo = atan(dx, dy)
        
        # Optional: Add smooth height variations
        robot.y = 0.1 * sin(time()) # Small up/down movement
        
        # Boundary checking
        max_bound = 45.0
        robot.x = clamp(robot.x, -max_bound, max_bound)
        robot.y = clamp(robot.y, -max_bound, max_bound)
    end
end

# Optional: Add functions for more complex behaviors
function iniciar_recogida!(robot::Robot)
    robot.estado = :picking
    robot.z = 1.0  # Raise forklift
end

function finalizar_recogida!(robot::Robot)
    robot.estado = :moving
    robot.z = 0.0  # Lower forklift
end

function pausar_robot!(robot::Robot)
    robot.estado = :idle
end

function reanudar_robot!(robot::Robot)
    robot.estado = :moving
end

# Optional: Add collision avoidance
function verificar_colision(robot::Robot, otros_robots::Vector{Robot})
    for otro in otros_robots
        if otro !== robot  # Don't check against self
            dx = robot.x - otro.x
            dy = robot.y - otro.y
            distancia = sqrt(dx^2 + dy^2)
            if distancia < 2.0  # Minimum safe distance
                return true
            end
        end
    end
    return false
end

end # module