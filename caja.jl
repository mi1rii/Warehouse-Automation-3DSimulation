

module ModuloCaja
    export Caja, crearCaja, setPos, setPosYEstado!, get_estado_caja, set_estado_caja, get_posicion_caja, get_angulo_caja, to_dict
    using Random
    using JSON  

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

    # Dimensiones del rectángulo más pequeño
    const SMALL_RECT_X_MIN = -50.0  # Límite izquierdo
    const SMALL_RECT_X_MAX = 50.0   # Límite derecho
    const SMALL_RECT_Y_MIN = -50.0  # Límite inferior
    const SMALL_RECT_Y_MAX = 50.0   # Límite superior

    # Función para crear una nueva caja en una de las tres caras del rectángulo más pequeño
    function crearCaja(dimBoard::Float64, zonaDescarga::Float64, margin::Float64)
        # Seleccionar aleatoriamente una de las tres caras
        cara = CARAS[rand(1:length(CARAS))]

        # Definir posición basada en la cara seleccionada
        if cara == :arriba
            # Cara superior del rectángulo más pequeño
            y = SMALL_RECT_Y_MIN
            x = rand(SMALL_RECT_X_MIN:SMALL_RECT_X_MAX)  # Entre SMALL_RECT_X_MIN y SMALL_RECT_X_MAX
        elseif cara == :izquierda
            # Cara izquierda del rectángulo más pequeño
            x = SMALL_RECT_X_MIN
            y = rand(SMALL_RECT_Y_MIN:SMALL_RECT_Y_MAX)  # Entre SMALL_RECT_Y_MIN y SMALL_RECT_Y_MAX
        elseif cara == :derecha
            # Cara derecha del rectángulo más pequeño
            x = SMALL_RECT_X_MAX
            y = rand(SMALL_RECT_Y_MIN:SMALL_RECT_Y_MAX)  # Entre SMALL_RECT_Y_MIN y SMALL_RECT_Y_MAX
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
