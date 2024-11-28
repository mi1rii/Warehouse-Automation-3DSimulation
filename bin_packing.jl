# bin_packing.jl

module BinPackingModule

using Random

export empaquetar_cajas, Caja

struct Caja
    id::Int
    ancho::Float64
    alto::Float64
    profundidad::Float64
end

function empaquetar_cajas(cajas::Vector{Caja}, contenedor_ancho::Float64, contenedor_alto::Float64, contenedor_profundidad::Float64)
    # Ejemplo simplificado: asignar posiciones sin superposición
    Random.seed!(123)
    posiciones = []
    ocupados = []
    for caja in cajas
        colocado = false
        attempts = 0
        while !colocado && attempts < 100
            x = rand() * (contenedor_ancho - caja.ancho)
            y = rand() * (contenedor_altura - caja.alto)
            z = rand() * (contenedor_profundidad - caja.profundidad)
            nueva_pos = (x, y, z)
            if !superpone(nueva_pos, caja, ocupados)
                push!(ocupados, (nueva_pos, caja))
                push!(posiciones, nueva_pos)
                colocado = true
            end
            attempts += 1
        end
        if !colocado
            push!(posiciones, (0.0, 0.0, 0.0))  # Posición por defecto si no se puede colocar
            println("Advertencia: No se pudo colocar la caja $(caja.id)")
        end
    end
    return posiciones
end

function superpone(pos::Tuple{Float64, Float64, Float64}, caja::Caja, ocupados::Vector{Tuple{Tuple{Float64, Float64, Float64}, Caja}})
    for (otra_pos, otra_caja) in ocupados
        if (abs(pos[1] - otra_pos[1]) < (caja.ancho + otra_caja.ancho) / 2) &&
           (abs(pos[3] - otra_pos[3]) < (caja.profundidad + otra_caja.profundidad) / 2)
            return true
        end
    end
    return false
end

end  # module
