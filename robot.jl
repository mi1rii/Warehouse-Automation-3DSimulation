# robot.jl

include("caja.jl")
using .ModuloCaja
using Statistics  # Importar el módulo Statistics para mean y std

module ModuloRobot
    export Robot, crearRobot, update, transportar, soltar
    export get_estado_robot, get_posicion, get_angulo, asignar_zona_descarga
    export imprimir_estadisticas
    using Random
    using LinearAlgebra  # Para operaciones vectoriales

    mutable struct Robot
        dimBoard::Float64
        zonaDescarga::Float64
        posicion::Vector{Float64}            # [x, y, z] posición del robot
        estado_robot::String                 # Estado actual del robot
        contador::Int                         # Contador de eventos
        puntoCarga::Vector{Float64}          # Punto de carga asociado al robot
        caja_recogida::Union{Nothing, Main.ModuloCaja.Caja}  # Caja actualmente recogida
        angulo::Float64                       # Ángulo de orientación del robot
        rotando::Bool                        # Indica si el robot está rotando
        angulo_objetivo::Float64              # Ángulo objetivo para rotar
        velocidad_rotacion::Float64           # Velocidad de rotación
        velocidad::Float64                    # Velocidad de movimiento
        zona_descarga_robot::Tuple{Float64, Float64, Float64, Float64}  # Zona de descarga asignada
        posiciones_pilas::Vector{Vector{Float64}}  # Posiciones de las pilas en la zona de descarga
        indice_pila_actual::Int               # Índice de la pila actual
        altura_pila_actual::Int               # Altura actual de la pila
        margin::Float64                       # Margen para límites del tablero
        seccionAlmacen::Int                   # Sección de almacenamiento asignada
        movement_count::Int                   # Contador de movimientos realizados
        boxes_carried::Int                    # Contador de cajas transportadas
    end

    function to_dict(robot::Robot)
        return Dict(
            "position" => robot.posicion,
            "angle" => robot.angulo,
            "state" => robot.estado_robot,
            "movement_count" => robot.movement_count,  # Contador de movimientos
            "boxes_carried" => robot.boxes_carried       # Contador de cajas transportadas
        )
    end

    function crearRobot(dimBoard::Float64, zonaDescarga::Float64, vel::Float64, num_robot::Int, total_robots::Int, margin::Float64)
        # Definir límites de posición inicial evitando márgenes y zona de descarga
        x_min = margin
        x_max = dimBoard - margin
        y_min = margin
        y_max = dimBoard - margin
        x = rand() * (x_max - x_min) + x_min
        y = rand() * (y_max - y_min) + y_min
        posicion = [x, y, 0.0]  # Mantener z en el piso (0.0)

        # Asignar ángulo inicial
        angulo = pi/2  # Orientación inicial hacia el eje Z negativo
        estado_robot = "buscar"       # Estado inicial
        contador = 0
        puntoCarga = zeros(3)         # Punto de carga inicializado en (0,0,0)
        caja_recogida = nothing        # No hay caja recogida inicialmente
        rotando = false
        angulo_objetivo = angulo
        velocidad_rotacion = pi / 4    # Velocidad de rotación
        velocidad = vel                 # Velocidad de movimiento

        # Asignar sección de almacenamiento única a cada robot
        seccionAlmacen = num_robot

        # Crear instancia del robot
        robot = Robot(dimBoard, zonaDescarga, posicion, estado_robot, contador, puntoCarga, caja_recogida,
                      angulo, rotando, angulo_objetivo, velocidad_rotacion, velocidad,
                      (0.0, 0.0, 0.0, 0.0), [], 1, 0,
                      margin, seccionAlmacen, 0, 0)
        updatePuntoCarga!(robot)  # Actualizar punto de carga
        return robot
    end

    # (El resto del código permanece igual)

end  # Fin del módulo ModuloRobot
