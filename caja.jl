# caja

module ModuloCaja
    export Caja, crearCaja, update_box_state!, get_all_boxes

    mutable struct Caja
        posicion::Vector{Float64}
        target_position::Vector{Float64}
        estado_caja::String  # "waiting", "being_moved", "placed"
        dimensions::Vector{Float64}
    end

    # Global dictionary to store boxes for each simulation
    const simulation_boxes = Dict()

    function crearCaja(sim_id::String, posicion::Vector{Float64}, dimensions::Vector{Float64})
        caja = Caja(posicion, [0.0, 0.0, 0.0], "waiting", dimensions)
        if !haskey(simulation_boxes, sim_id)
            simulation_boxes[sim_id] = []
        end
        push!(simulation_boxes[sim_id], caja)
        return caja
    end

    function update_box_state!(sim_id::String, robot_position::Vector{Float64})
        if !haskey(simulation_boxes, sim_id)
            return
        end
        
        for caja in simulation_boxes[sim_id]
            # Calculate distance to robot
            distance_to_robot = sqrt(sum((caja.posicion - robot_position).^2))
            
            if caja.estado_caja == "waiting" && distance_to_robot < 2.0  # Increased pickup range
                caja.estado_caja = "being_moved"
                println("Box picked up at position: ", caja.posicion)
            elseif caja.estado_caja == "being_moved"
                # Update box position to follow robot
                caja.posicion = copy(robot_position)  # Use copy to avoid reference issues
                
                # Check if we're at target position
                distance_to_target = sqrt(sum((caja.posicion - caja.target_position).^2))
                if distance_to_target < 1.0
                    caja.estado_caja = "placed"
                    caja.posicion = copy(caja.target_position)
                    println("Box placed at target position: ", caja.target_position)
                end
            end
        end
    end

    function get_all_boxes(sim_id::String)
        if !haskey(simulation_boxes, sim_id)
            return []
        end
        return [Dict(
            "posicion" => box.posicion,
            "target_position" => box.target_position,
            "estado_caja" => box.estado_caja,
            "dimensions" => box.dimensions
        ) for box in simulation_boxes[sim_id]]
    end
end