module ModuloRobot

export Robot, get_posicion, get_angulo, mover_robot!, crearRobot, to_dict, update

mutable struct Robot  # Cambiar a mutable struct
    posicion::Tuple{Float64, Float64}
    angulo::Float64
end

# Getter for the robot's position
function get_posicion(robot::Robot)
    return robot.posicion
end

# Getter for the robot's angle
function get_angulo(robot::Robot)
    return robot.angulo
end

# Function to move the robot
function mover_robot!(robot::Robot, distancia::Float64, angulo::Float64)
    x, y = robot.posicion
    nuevo_x = x + distancia * cos(angulo)
    nuevo_y = y + distancia * sin(angulo)
    robot.posicion = (nuevo_x, nuevo_y)
    robot.angulo = angulo
end

# Function to create a new robot
function crearRobot(x::Float64, y::Float64)
    return Robot((x, y), 0.0)
end

# Function to convert a Robot instance to a dictionary
function to_dict(robot::Robot)
    return Dict(
        "position" => robot.posicion,
        "angle" => robot.angulo
    )
end

# Function to update a robot's state
function update(robot::Robot)
    # Mueve el robot en una dirección aleatoria
    robot.angulo += rand() * (π/2) - (π/4)  # Cambia el ángulo aleatoriamente entre -π/4 y π/4
    mover_robot!(robot, 1.0, robot.angulo)
end

end  # End of module ModuloRobot
