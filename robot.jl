module ModuloRobot

using ..ModuloCaja  # Import ModuloCaja module

export Robot, crearRobot, mover_robot!, to_dict

mutable struct Robot
    x::Float64
    y::Float64
    z::Float64
    angulo::Float64
    velocidad::Float64
    target_x::Float64
    target_y::Float64
    estado::Symbol  # :idle, :moving_to_box, :carrying_box, :moving_to_target
    current_box::Union{Nothing, Int64}  # ID of the box being carried
    last_target_time::Float64  # Store the last target time as Float64
end

function crearRobot(pos_inicial::Float64, vel_inicial::Float64)
    Robot(
        0.0,            # Initial X position
        0.0,            # Initial Y position
        0.0,            # Initial Z position
        0.0,            # Initial angle
        vel_inicial,    # Initial velocity
        0.0,           # Initial target X
        0.0,           # Initial target Y
        :idle,         # Initial state
        nothing,       # No box being carried initially
        time()         # Current time as Float64
    )
end

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

function generar_nuevo_objetivo!(robot::Robot)
    # Define boundaries
    max_bound = 45.0
    min_bound = -45.0
    
    # Generate random target positions for both X and Y
    robot.target_x = rand() * (max_bound - min_bound) + min_bound
    robot.target_y = rand() * (max_bound - min_bound) + min_bound
    robot.last_target_time = time()
    robot.estado = :moving
    
    # Calculate new angle towards target
    dx = robot.target_x - robot.x
    dy = robot.target_y - robot.y
    robot.angulo = atan(dy, dx)
end

function ha_llegado_objetivo(robot::Robot)
    dx = robot.target_x - robot.x
    dy = robot.target_y - robot.y
    distancia = sqrt(dx^2 + dy^2)
    return distancia < 0.5  # Increased threshold slightly
end

function mover_robot!(robot::Robot, tiempo::Float64, angulo::Float64)
    if robot.estado == :idle
        if time() - robot.last_target_time > 2.0
            generar_nuevo_objetivo!(robot)
        end
        return
    end

    if robot.estado == :moving
        dx = robot.target_x - robot.x
        dy = robot.target_y - robot.y
        distancia = sqrt(dx^2 + dy^2)
        
        # Check if we've reached the target with a slightly larger threshold
        if distancia < 0.5
            # Snap to exact position when very close
            robot.x = robot.target_x
            robot.y = robot.target_y
            robot.estado = :idle
            robot.last_target_time = time()
            println("Target reached: x=$(robot.x), y=$(robot.y)")
            return
        end
        
        # Calculate movement with smoothing
        velocidad_actual = min(robot.velocidad * tiempo, distancia)  # Don't overshoot
        
        # Normalize direction and apply velocity
        if distancia > 0
            # Calculate movement vector
            move_x = (dx / distancia) * velocidad_actual
            move_y = (dy / distancia) * velocidad_actual
            
            # Apply movement
            robot.x += move_x
            robot.y += move_y
            
            # Update angle smoothly
            target_angle = atan(dy, dx)
            angle_diff = target_angle - robot.angulo
            
            # Normalize angle difference to [-π, π]
            while angle_diff > π
                angle_diff -= 2π
            end
            while angle_diff < -π
                angle_diff += 2π
            end
            
            # Smooth angle update
            robot.angulo += angle_diff * min(1.0, tiempo * 5.0)
        end
        
        # Boundary checking
        max_bound = 45.0
        robot.x = clamp(robot.x, -max_bound, max_bound)
        robot.y = clamp(robot.y, -max_bound, max_bound)
    end
    println("Sending position: x=$(robot.x), y=$(robot.y)")

    # Update box positions if robot is carrying any
    if robot.estado == :carrying_box
        ModuloCaja.update_box_state!(simulation_id, [robot.x, robot.y, robot.z])
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

function update_robot_state!(robot::Robot, boxes::Vector{ModuloCaja.Caja})
    if robot.estado == :idle
        # Find closest unplaced box
        closest_box = find_closest_unplaced_box(robot, boxes)
        if closest_box !== nothing
            robot.estado = :moving_to_box
            set_target_position!(robot, boxes[closest_box].posicion)
        end
    elseif robot.estado == :moving_to_box
        # Check if we've reached the box
        if has_reached_target(robot)
            robot.estado = :carrying_box
            robot.current_box = closest_box
            set_target_position!(robot, boxes[closest_box].target_position)
        end
    elseif robot.estado == :carrying_box
        # Check if we've reached the target position
        if has_reached_target(robot)
            robot.estado = :idle
            robot.current_box = nothing
        end
    end
end

end # module
