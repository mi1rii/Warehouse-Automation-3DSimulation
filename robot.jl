module ModuloRobot

include("caja.jl")

export Robot, crearRobot, mover_robot!, to_dict

mutable struct Robot
    x::Float64
    y::Float64
    z::Float64
    angulo::Float64
    velocidad::Float64
    target_x::Float64
    target_y::Float64
    estado::Symbol
    last_target_time::Float64
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
        time()         # Current time
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

function mover_robot!(robot::Robot, tiempo::Float64, target_pos::Vector{Float64})
    dx = target_pos[1] - robot.x
    dy = target_pos[2] - robot.y
    distancia = sqrt(dx^2 + dy^2)

    if distancia > 0.5  # Movement threshold
        # Normalize movement direction
        step = robot.velocidad * tiempo
        direction = [dx, dy] ./ distancia
        robot.x += step * direction[1]
        robot.y += step * direction[2]
    else
        # Target reached
        println("Robot reached position: $target_pos")
        robot.estado = :idle
    end

    println("Robot State: ", robot.estado)
    println("Robot Position: x=$(robot.x), y=$(robot.y), z=$(robot.z)")

end

function execute_task!(robot::Robot, cajas::Vector{ModuloCaja.Caja})
    if robot.estado == :idle && !isempty(cajas)
        target_caja = popfirst!(cajas)  # Get the next box
        robot.target_x, robot.target_y = target_caja.posicion[1], target_caja.posicion[2]
        robot.estado = :moving_to_box
    elseif robot.estado == :moving_to_box
        mover_robot!(robot, 1.0 / 60.0, [robot.target_x, robot.target_y])  # 60 FPS assumption
        if ha_llegado_objetivo(robot)
            println("Picking up box...")
            robot.estado = :moving_to_dropoff
        end
    elseif robot.estado == :moving_to_dropoff
        dropoff_position = [0.0, 0.0]  # Define drop-off position
        mover_robot!(robot, 1.0 / 60.0, dropoff_position)
        if ha_llegado_objetivo(robot)
            println("Box dropped off!")
            robot.estado = :idle
        end
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