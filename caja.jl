# caja.jl

module ModuloCaja
    export Caja, crearCaja, setPos, setPosYEstado!, get_estado_caja, set_estado_caja, get_posicion_caja, get_angulo_caja, to_dict
    using Random
    using JSON  
    mutable struct Caja
        posicion::Vector{Float64}  # Posición [x, y, z] de la caja
        angulo::Float64            # Ángulo de orientación de la caja
        estado_caja::String        # Estado actual de la caja 
    end

    function Base.Dict(caja::Caja)
        Dict(
            "posicion" => caja.posicion,
            "angulo" => caja.angulo,
            "estado_caja" => caja.estado_caja
        )
    end

    function crearCaja(dimBoard::Float64, zonaDescarga::Float64, margin::Float64)
        x_min = margin
        x_max = dimBoard - margin
        y_min = margin
        y_max = dimBoard - margin
        x = rand() * (x_max - x_min) + x_min
        y = rand() * (y_max - y_min) + y_min
        z = 0.0  # Altura fija

        posicion = [x, y, z]               # Posición inicial
        angulo = rand() * 2π                  # Ángulo aleatorio entre 0 y 2π
        estado_caja = "esperando"             # Estado inicial de la caja
        return Caja(posicion, angulo, estado_caja)
    end

    # (El resto del código permanece igual)

end  # Fin del módulo ModuloCaja
