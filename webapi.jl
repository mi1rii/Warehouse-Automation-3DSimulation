# webapi

include("caja.jl")
include("robot.jl")

using .ModuloRobot  
using .ModuloCaja   
using Genie, Genie.Renderer.Json, Genie.Requests
using UUIDs
using Dates  # Para funciones de tiempo
using LinearAlgebra  # Para cálculos de distancia

# Parámetros de la simulación
dim_board = 120.0
zona_descarga = 10.0
margin = 10.0

# Distancia mínima entre cajas 
const MIN_DISTANCE = 5.0 

# Gestión del estado global
instances = Dict()
paquetes = Dict()
simulation_metadata = Dict()  

# Función para verificar la distancia mínima entre una nueva caja y las existentes
function is_far_enough(new_pos::Vector{Float64}, existing_boxes::Vector{ModuloCaja.Caja})
    for box in existing_boxes
        distance = norm(new_pos[1:2] - box.posicion[1:2])  # Calcula la distancia 
        if distance < MIN_DISTANCE
            return false
        end
    end
    return true
end

# Ruta para inicializar la simulación
route("/simulation", method = POST) do
    num_robots = try parse(Int, jsonpayload()["num_robots"]) catch e 5 end
    num_packages = try parse(Int, jsonpayload()["num_packages"]) catch e 100 end

    # Crear ID de simulación
    id = string(uuid1())

    # Crear robots
    robots = [ModuloRobot.crearRobot(dim_board, zona_descarga, 5.0, i + 1, num_robots, margin)
              for i in 1:num_robots]

    # Crear cajas asegurando que no se superpongan
    boxes = ModuloCaja.Caja[]  # Inicializar un arreglo vacío de cajas

    for _ in 1:num_packages
        max_attempts = 100  # Número máximo de intentos para colocar una caja sin superposiciones
        attempt = 0
        success = false

        while attempt < max_attempts && !success
            new_box = ModuloCaja.crearCaja(dim_board, zona_descarga, margin)
            if is_far_enough(new_box.posicion, boxes)
                push!(boxes, new_box)
                success = true
            else
                attempt += 1
            end
        end

        if !success
            println("Warning: No se pudo colocar una caja sin superposición después de $max_attempts intentos.")
            push!(boxes, new_box)
        end
    end

    # Almacenar en instancias
    instances[id] = robots
    paquetes[id] = boxes

    # Almacenar metadatos de simulación
    simulation_metadata[id] = Dict(
        "start_time" => time(),  # Registrar tiempo de inicio
        "end_time" => nothing,
        "completed" => false
    )

    # Devolver ID de simulación y estado inicial
    json(Dict(
        "id" => id,
        "robots" => [ModuloRobot.to_dict(robot) for robot in robots],
        "packages" => [ModuloCaja.to_dict(box) for box in boxes]
    ))
end

# Ruta para actualizar la simulación
route("/simulation/:id", method = POST) do
    id = payload(:id)
    if !haskey(instances, id)
        return json(Dict("error" => "Simulation not found")), 404
    end

    robots = instances[id]
    boxes = paquetes[id]

    # Actualizar cada robot
    for robot in robots
        ModuloRobot.update(robot, boxes)
    end

    # Verificar si todas las cajas están en estado "soltada"
    all_soltadas = all(box -> ModuloCaja.get_estado_caja(box) == "soltada", boxes)

    # Si todas las cajas están soltadas y la simulación no ha sido marcada como completada
    if all_soltadas && !simulation_metadata[id]["completed"]
        simulation_metadata[id]["end_time"] = time()
        simulation_metadata[id]["completed"] = true

        # Calcular la duración de la simulación
        duration = simulation_metadata[id]["end_time"] - simulation_metadata[id]["start_time"]

        # Recopilar los contadores de movimientos de los robots
        movement_counts = [robot.movement_count for robot in robots]
        average_movements = mean(movement_counts)
        std_dev_movements = std(movement_counts)

        # Imprimir las estadísticas en la consola
        println("Simulación completada.")
        println("Tiempo necesario hasta que todas las cajas están en pilas de máximo 5 cajas: ", duration, " segundos.")
        println("Número de movimientos realizados por los robots:")
        println("Promedio: ", average_movements)
        println("Desviación estándar: ", std_dev_movements)
    end

    # Devolver estado actualizado
    json(Dict(
        "robots" => [ModuloRobot.to_dict(robot) for robot in robots],
        "packages" => [ModuloCaja.to_dict(box) for box in boxes]
    ))
end

# Ruta para limpiar la simulación
route("/simulation/:id", method = DELETE) do
    id = payload(:id)
    delete!(instances, id)
    delete!(paquetes, id)
    delete!(simulation_metadata, id)  # Eliminar metadatos de simulación
    json(Dict("status" => "deleted"))
end

# Configurar CORS
Genie.config.run_as_server = true
Genie.config.cors_headers["Access-Control-Allow-Origin"] = "*"
Genie.config.cors_headers["Access-Control-Allow-Headers"] = "Content-Type"
Genie.config.cors_headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
Genie.config.cors_allowed_origins = ["*"]

# Iniciar servidor
up(8000)