include("robot.jl")

using .ModuloRobot
using Genie, Genie.Renderer.Json, Genie.Requests
using UUIDs

const robots = Dict()
const boxes_initialized = Ref(false)  # Verificar si las cajas han sido inicializadas
const packed_boxes = Ref([])  # Almacenar datos de cajas empaquetadas
const robots_initialized = Ref(false)  #variableerificar si los robots han sido inicializados

# Inicializar simulación
route("/simulation", method = POST) do
    id = ""  # Inicializar variable id

    # Verificar si las cajas han sido inicializadas
    if !boxes_initialized[]
        packed_boxes[] = ModuloRobot.boxes()  # Llamar a boxes() solo una vez
        boxes_initialized[] = true  # Establecer la bandera a true
    end

    # Verificar si los robots han sido inicializados
    if !robots_initialized[]
        num_robots = try parse(Int, jsonpayload()["num_robots"]) catch e 5 end
        id = string(UUIDs.uuid1())  # Usar UUIDs.uuid1()
        robots[id] = [ModuloRobot.crearRobot(120.0, 1.0) for _ in 1:num_robots]
        robots_initialized[] = true  # Establecer la bandera a true
    else
        # Si los robots ya están inicializados, obtener el id existente
        id = collect(keys(robots))[1]  # Convertir KeySet a un array y obtener el primer id de robot
    end

    return json(Dict(
        "id" => id,
        "robots" => [ModuloRobot.to_dict(robot) for robot in robots[id]],
        "packed_boxes" => packed_boxes[]  # Incluir datos de cajas empaquetadas en la respuesta
    ))
end

# Actualizar simulación
route("/simulation/:id", method = POST) do
    id = payload(:id)
    println("Solicitud recibida para actualizar simulación con id: ", id)

    if !haskey(robots, id)
        status(404)
        return json(Dict("error" => "Simulación no encontrada"))
    end

    velocidad = try parse(Float64, jsonpayload()["velocidad"]) catch e 1.0 end
    tiempo = try parse(Float64, jsonpayload()["tiempo"]) catch e 1.0 end

    for robot in robots[id]
        ModuloRobot.mover_robot!(robot, velocidad * tiempo, robot.angulo)
        # Esperar respuesta del front-end aquí (pseudo-código)
        # wait_for_frontend_response()
    end

    # Actualizar y devolver el nuevo estado
    updated_robots = [ModuloRobot.to_dict(robot) for robot in robots[id]]
    return json(Dict("robots" => updated_robots))
end

# Eliminar simulación
route("/simulation/:id", method = DELETE) do
    id = payload(:id)
    if haskey(robots, id)
        delete!(robots, id)
        return json(Dict("status" => "eliminado"))
    else
        return json(Dict("error" => "Simulación no encontrada")), 404
    end
end

# Iniciar servidor Genie
Genie.config.run_as_server = true
up(8000)  

# Mantener el servidor en ejecución indefinidamente
wait()
