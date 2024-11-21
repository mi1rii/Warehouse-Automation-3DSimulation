include("robot.jl")

using .ModuloRobot
using Genie, Genie.Renderer.Json, Genie.Requests

# Global simulation state
const robots = Dict()

# Initialize simulation
route("/simulation", method = POST) do
    num_robots = try parse(Int, jsonpayload()["num_robots"]) catch e 5 end

    id = string(uuid1())
    robots[id] = [ModuloRobot.crearRobot(120.0, 1.0) for _ in 1:num_robots]

    return json(Dict(
        "id" => id,
        "robots" => [ModuloRobot.to_dict(robot) for robot in robots[id]]
    ))
end

# Update simulation
route("/simulation/:id", method = POST) do
    id = payload(:id)
    if !haskey(robots, id)
        return json(Dict("error" => "Simulation not found")), 404
    end

    # Update each robot's state
    for robot in robots[id]
        ModuloRobot.update(robot)
    end

    # Return updated robot states
    updated_robots = [ModuloRobot.to_dict(robot) for robot in robots[id]]
    println("API Response (robots): ", updated_robots)  # Debugging output
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

# Start Genie server
Genie.config.run_as_server = true
up(8000)
