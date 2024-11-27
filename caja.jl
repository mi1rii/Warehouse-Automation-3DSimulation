module ModuloCaja
    export Caja, crearCaja, setPos, setPosYEstado!, get_estado_caja, set_estado_caja, get_posicion_caja, get_angulo_caja, to_dict
    using Random
    using JSON  

    const dimBoard = 500
    const rectangulo_ancho = 400.0  # Ancho aumentado para mejor disposición
    const rectangulo_profundidad = 200.0
    const rectangulo_posicion = [dimBoard / 2 + rectangulo_ancho / 2, 0.0, 0.0]
    
    # Estructura mutable para representar una caja
    mutable struct Caja
        posicion::Vector{Float64}  # Posición [x, y, z] de la caja
        angulo::Float64            # Ángulo de orientación de la caja
        estado_caja::String        # Estado actual de la caja 
    end

    # Extensión de la función Dict para serializar Caja a JSON
    function Base.Dict(caja::Caja)
        Dict(
            "posicion" => caja.posicion,
            "angulo" => caja.angulo,
            "estado_caja" => caja.estado_caja
        )
    end

    # Definir las tres caras donde aparecerán las cajas
    const CARAS = [:arriba, :izquierda, :derecha]

    # Función para crear una nueva caja en una de las tres caras del rectángulo
    function crearCaja(dimBoard::Float64, zonaDescarga::Float64, margin::Float64)
        # Seleccionar aleatoriamente una de las tres caras
        cara = CARAS[rand(1:length(CARAS))]

        # Definir posición basada en la cara seleccionada
        if cara == :arriba
            # Cara superior
            y = dimBoard - zonaDescarga - margin
            x = rand() * (2 * (dimBoard - margin)) - (dimBoard - margin) + 500 # Entre -dimBoard + margin y +dimBoard - margin
        elseif cara == :izquierda
            y = -dimBoard + zonaDescarga + margin 
            x = rand() * (2 * (dimBoard - margin)) - (dimBoard - margin) + 500 # Entre -dimBoard + margin y +dimBoard - margin
            # Cara izquierda
        elseif cara == :derecha
            # Cara derecha
            x = dimBoard - margin + 500
            y = rand() * (dimBoard - zonaDescarga - 2 * margin) - (dimBoard - zonaDescarga - margin)
        else
            error("Cara no válida seleccionada para la creación de la caja.")
        end

        # Posición fija en z (puede ajustarse según necesidad)
        z = 1.0

        posicion = [x, y, z]
        angulo = rand() * 2π  # Ángulo aleatorio entre 0 y 2π
        estado_caja = "esperando"  # Estado inicial de la caja

        return Caja(posicion, angulo, estado_caja)
    end

    # Función para establecer la posición y ángulo de una caja
    function setPos(caja::Caja, pos::Vector{Float64}, an::Float64)
        caja.posicion = pos
        caja.angulo = an
    end

    # Función para establecer posición, ángulo y estado de una caja
    function setPosYEstado!(caja::Caja, pos::Vector{Float64}, an::Float64, estado::String)
        caja.posicion = pos
        caja.angulo = an
        caja.estado_caja = estado
    end

    # Getter para el estado de la caja
    function get_estado_caja(caja::Caja)
        return caja.estado_caja
    end

    # Setter para el estado de la caja
    function set_estado_caja(caja::Caja, estado::String)
        caja.estado_caja = estado
    end

    # Getter para la posición de la caja
    function get_posicion_caja(caja::Caja)
        return caja.posicion
    end

    # Getter para el ángulo de la caja
    function get_angulo_caja(caja::Caja)
        return caja.angulo
    end

    # Función para crear una representación serializable de la caja
    function to_dict(caja::Caja)
       return Dict(
           "position" => caja.posicion,
           "angle" => caja.angulo,
           "state" => caja.estado_caja
       )
    end

end  # Fin del módulo ModuloCaja
