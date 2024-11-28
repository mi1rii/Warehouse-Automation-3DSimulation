module ModuloRobot

# Exportar las funciones y tipos que estarán disponibles fuera del módulo
export Robot, crearRobot, mover_robot!, to_dict, boxes, generar_nuevo_objetivo!

# Definición de la estructura mutable Robot
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

# Definición de la estructura BoxData
struct BoxData
    boxId::String
    dimensions::Tuple{Float64, Float64, Float64}
    weight::Float64
    volume::Float64
    dropOff::Tuple{Float64, Float64, Float64}
end

# Declarar pyCallBoxes como una variable global
global pyCallBoxes = []

# Definir max_bound
const max_bound = 50.0  # Establecer este valor según sea apropiado para tu simulación

# Función para crear un nuevo robot
function crearRobot(pos_inicial::Float64, vel_inicial::Float64)
    Robot(
        0.0,            # Posición inicial en X
        0.0,            # Posición inicial en Y
        0.0,            # Posición inicial en Z
        0.0,            # Ángulo inicial
        vel_inicial,    # Velocidad inicial
        0.0,            # Objetivo inicial en X
        0.0,            # Objetivo inicial en Y
        :idle,          # Estado inicial
        time()          # Tiempo actual
    )
end

# Función para convertir un robot a un diccionario
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

# Importar PyCall y los módulos necesarios de py3dbp
using PyCall
Packer = pyimport("py3dbp").Packer
Bin = pyimport("py3dbp").Bin
Item = pyimport("py3dbp").Item

# Función para empaquetar cajas
function boxes()
    println("Iniciando el proceso de empaquetado...")  # Iniciar el proceso de empaquetado
    packer = Packer()
    packer.add_bin(Bin("Boxes", 22, 20, 32, 70.0))
    
    # Añadir ítems (cajas)
    packer.add_item(Item("box1", 7, 7, 7, 0))
    packer.add_item(Item("box2", 1, 1, 1, 0))
    packer.add_item(Item("box3", 1, 1, 1, 0))
    packer.add_item(Item("box4", 7, 7, 7, 0))
    packer.add_item(Item("box5", 5, 5, 5, 0))
    packer.add_item(Item("box6", 5, 5, 5, 0))
    packer.add_item(Item("box7", 7, 7, 7, 0))
    packer.add_item(Item("box8", 7, 7, 7, 0))
    packer.add_item(Item("box9", 7, 7, 7, 0))
    packer.add_item(Item("box10", 5, 5, 5, 0))
    packer.add_item(Item("box11", 7, 7, 7, 0))
    packer.add_item(Item("box12", 5, 5, 5, 0))
    packer.add_item(Item("box13", 7, 7, 7, 0))
    packer.add_item(Item("box14", 7, 7, 7, 0))
    packer.add_item(Item("box15", 5, 5, 5, 0))

    println("Empaquetando las cajas...")  # Iniciar el empaquetado
    packer.pack()

    global pyCallBoxes = []  # Reiniciar la variable global

    println("Proceso de empaquetado completado, extrayendo datos de las cajas...")  # Extracción de datos de las cajas

    for bin in packer[:bins]
        for item in bin[:items]
            boxId = item[:name]
            width = item[:width]
            height = item[:height]
            depth = item[:depth]
            weight = item[:weight]
            vol = width * height * depth
            x, y, z = item[:position][1], item[:position][2], item[:position][3]
            push!(pyCallBoxes, BoxData(boxId, (width, height, depth), weight, vol, (x, y, z)))
        end
    end

    sort!(pyCallBoxes, by = x -> (x.dropOff[2], x.dropOff[1], x.dropOff[3]))  # Ordenar por coordenadas de entrega
    println(pyCallBoxes)
    return pyCallBoxes
end

# Función para generar un nuevo objetivo para el robot
function generar_nuevo_objetivo!(robot::Robot)
    global pyCallBoxes  # Acceder a la variable global
    if isempty(pyCallBoxes)
        println("Proceso terminado: Todas las cajas han sido procesadas.")
        return  # Salir de la función si no hay cajas
    end
    println("CREANDO NUEVO OBJETIVO")

    current_box = popfirst!(pyCallBoxes)  # Obtener la siguiente caja
    println("Procesando caja: ", current_box.boxId)

    x, y, z = current_box.dropOff  # Extraer solo las coordenadas

    robot.target_x = 20
    robot.target_y = 20
    robot.last_target_time = time()
    robot.estado = :pickingBox
    
    # Calcular nuevo ángulo hacia el objetivo
    dx = robot.target_x - robot.x
    dy = robot.target_y - robot.y
    robot.angulo = atan(dy, dx)
end

# Función para mover el robot
function mover_robot!(robot::Robot, tiempo::Float64, angulo::Float64)
    if robot.estado == :idle
        if time() - robot.last_target_time > 2.0
            generar_nuevo_objetivo!(robot)
        end
        return
    end

    # Rastrear la posición actual del robot
    robot.x = clamp(robot.x, -max_bound, max_bound)
    robot.y = clamp(robot.y, -max_bound, max_bound)

    # Actualizar la posición del robot progresivamente
    if robot.estado == :pickingBox || robot.estado == :movingToDropOff
        # Calcular la distancia al objetivo
        dx = robot.target_x - robot.x
        dy = robot.target_y - robot.y
        distancia = sqrt(dx^2 + dy^2)

        # Actualizar la posición solo si el robot no está en el objetivo
        if distancia > 0.5  # Umbral para considerar que el robot ha alcanzado el objetivo
            velocidad_actual = min(robot.velocidad * tiempo, distancia)  # No sobrepasar el objetivo
            # Calcular el vector de movimiento
            move_x = (dx / distancia) * velocidad_actual
            move_y = (dy / distancia) * velocidad_actual
            
            # Aplicar movimiento
            robot.x += move_x
            robot.y += move_y
            
            # Actualizar el ángulo suavemente
            target_angle = atan(dy, dx)
            angle_diff = target_angle - robot.angulo
            
            # Normalizar la diferencia de ángulo a [-π, π]
            while angle_diff > π
                angle_diff -= 2π
            end
            while angle_diff < -π
                angle_diff += 2π
            end
            
            # Actualización suave del ángulo
            robot.angulo += angle_diff * min(1.0, tiempo * 5.0)
            
            # Introducir un retraso para ralentizar el movimiento
            sleep(0.5)  # Esperar 0.5 segundos después de cada paso de movimiento
        end
    end

    println("Enviando posición: x=$(robot.x), y=$(robot.y)")
end

end # módulo
