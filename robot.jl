module ModuloRobot

export Robot, get_posicion, get_angulo, mover_robot!

struct Robot
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

end  # End of module ModuloRobot
