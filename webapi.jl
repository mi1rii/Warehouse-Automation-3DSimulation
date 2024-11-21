include("robot.jl")

using .ModuloRobot  # Cambiar a importación relativa
using Genie, Genie.Renderer.Json, Genie.Requests
using UUIDs  # Import UUIDs module

# Global simulation state
const robots = Dict()

# Initialize simulation
route("/simulation", method = POST) do
    num_robots = try parse(Int, jsonpayload()["num_robots"]) catch e 5 end

    id = string(UUIDs.uuid1())  # Use UUIDs.uuid1()
    robots[id] = [ModuloRobot.crearRobot(120.0, 1.0) for _ in 1:num_robots]

    return json(Dict(
        "id" => id,
        "robots" => [ModuloRobot.to_dict(robot) for robot in robots[id]]
    ))
end

# Update simulation
route("/simulation/:id", method = POST) do
    id = payload(:id)
    println("Received request to update simulation with id: ", id)  # Depuración

    if !haskey(robots, id)
        status(404)
        return json(Dict("error" => "Simulation not found"))
    end

    try
        println("Current robots: ", robots)  # Depuración
        # Update each robot's state
        for robot in robots[id]
            println("Before update, robot: ", robot)  # Depuración
            ModuloRobot.update(robot)  # Llamada directa a la función exportada
            println("After update, robot: ", robot)  # Depuración
        end

        # Return updated robot states
        updated_robots = [ModuloRobot.to_dict(robot) for robot in robots[id]]
        println("API Response (robots): ", updated_robots)  # Depuración
        return json(Dict("robots" => updated_robots))
    catch e
        println("Error updating simulation: ", e)
        println("Stacktrace: ", catch_backtrace())  # Depuración de stacktrace
        return halt(500, json(Dict("error" => "Internal Server Error")))  # Usar halt para devolver el error
    end
end

# Delete simulation
route("/simulation/:id", method = DELETE) do
    id = payload(:id)
    if haskey(robots, id)
        delete!(robots, id)
        return json(Dict("status" => "deleted"))
    else
        return json(Dict("error" => "Simulation not found")), 404
    end
end

# Start Genie server
Genie.config.run_as_server = true
up(8000)

# Keep the server running indefinitely
wait()
