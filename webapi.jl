include("caja.jl")
include("robot.jl")

using .ModuloCaja
using .ModuloRobot
using Genie, Genie.Renderer.Json, Genie.Requests
using UUIDs

# Global simulation state
const robots = Dict()
const simulation_state = Dict()

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
    println("Received request to update simulation with id: ", id)

    if !haskey(robots, id)
        status(404)
        return json(Dict("error" => "Simulation not found"))
    end

    velocidad = try parse(Float64, jsonpayload()["velocidad"]) catch e 1.0 end
    tiempo = try parse(Float64, jsonpayload()["tiempo"]) catch e 1.0 end

    for robot in robots[id]
        ModuloRobot.mover_robot!(robot, velocidad * tiempo, robot.angulo)
        # Update boxes based on robot position
        ModuloCaja.update_box_state!(id, [robot.x, robot.y, robot.z])
    end

    # Update and return the new state
    updated_robots = [ModuloRobot.to_dict(robot) for robot in robots[id]]
    return json(Dict("robots" => updated_robots))
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

# Set box targets
route("/simulation/:id/set_box_targets", method = POST) do
    id = payload(:id)
    if !haskey(robots, id)
        return json(Dict("error" => "Simulation not found")), 404
    end
    
    # Receive box target positions from Python
    box_targets = jsonpayload()["box_targets"]
    
    # Store box targets in simulation state
    if !haskey(simulation_state, id)
        simulation_state[id] = Dict()
    end
    simulation_state[id]["box_targets"] = box_targets
    
    return json(Dict("status" => "success"))
end

# Add a route to get current state of all boxes
route("/simulation/:id/boxes", method = GET) do
    id = payload(:id)
    if !haskey(robots, id)
        return json(Dict("error" => "Simulation not found")), 404
    end
    
    # Get current box states from ModuloCaja
    boxes = ModuloCaja.get_all_boxes(id)
    
    return json(Dict("boxes" => boxes))
end

# Add a route to initialize boxes
route("/simulation/:id/init_boxes", method = POST) do
    id = payload(:id)
    if !haskey(robots, id)
        return json(Dict("error" => "Simulation not found")), 404
    end
    
    box_data = jsonpayload()["boxes"]
    for box in box_data
        ModuloCaja.crearCaja(
            id,
            [box["position"]["x"], box["position"]["y"], box["position"]["z"]],
            [box["dimensions"]["x"], box["dimensions"]["y"], box["dimensions"]["z"]]
        )
    end
    
    return json(Dict("status" => "success"))
end

# Start Genie server
Genie.config.run_as_server = true
up(8000)

# Keep the server running indefinitely
wait()
