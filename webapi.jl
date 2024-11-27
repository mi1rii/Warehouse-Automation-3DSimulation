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

route("/boxes", method = POST) do
    global cajas  # Global state for boxes
    box_data = jsonpayload()["boxes"]

    # Parse incoming box positions
    cajas = [ModuloCaja.Caja(box["position"], 0.0, "esperando") for box in box_data]

    return json(Dict("status" => "Box positions received"))
end

route("/simulation/:id", method = POST) do
    id = payload(:id)
    println("Received update request for Simulation ID: ", id)

    if !haskey(robots, id)
        println("Simulation ID not found: ", id)
        status(404)
        return json(Dict("error" => "Simulation not found"))
    end

    # Update robots based on tasks or movements
    for robot in robots[id]
        execute_task!(robot, cajas)  # Ensure this function updates robot.x, y, z
    end

    return json(Dict("robots" => [ModuloRobot.to_dict(robot) for robot in robots[id]]))
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