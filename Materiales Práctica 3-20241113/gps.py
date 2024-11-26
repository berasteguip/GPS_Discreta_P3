import callejero as ca
import grafo_pesado as gp
from typing import Tuple
import math
from shapely.geometry import Point, LineString


def closest_node(coords: Tuple[int, int], G) -> Tuple[int, int]:
    """
    closest_node(coords: Tuple[int, int]) -> Tuple[int, int]
    
    Esta función encuentra el nodo más cercano en un grafo a un punto dado por sus coordenadas.
    
    Args:
        coords (Tuple[int, int]): Un par de coordenadas (latitud, longitud) que representan la ubicación del punto.
        
    Returns:
        Tuple[int, int]: El nodo más cercano al punto dado, representado por su identificador.
    """
    # Convertir las coordenadas a un objeto Point de Shapely
    point = Point(coords)

    # Inicializar la distancia mínima y el nodo más cercano
    min_distance = math.inf
    closest_node_id = None

    # Iterar sobre los nodos del grafo
    for node_id, attributes in G.nodes(data=True):
        # Obtener las coordenadas del nodo
        node_coords = attributes['y'], attributes['x']
        # Calcular la distancia entre el punto y el nodo
        node_point = Point(node_coords)
        distance = point.distance(node_point)
        # Actualizar si encontramos un nodo más cercano
        if distance < min_distance:
            min_distance = distance
            closest_node_id = node_id

    return closest_node_id

def choose():
    options = ['1', '2' ,'3']
    print('''Ruta más corta (1)
    Ruta más rápida (2)
    Ruta más rápida (optimizando semáforos) (3)''')
    select = input('Escoja una opción (1, 2 o 3)')

    while select not in options:
        select = input('Debe escoger una de las tres opciones (1, 2 o 3)')

    if select == '1':
        return gp.peso_longitud
    elif select == '2':
        return gp.peso_velocidad
    elif select == '2':
        return gp.peso_semaforo


if __name__ == "__main__":

    callejero = ca.carga_callejero()
    G = ca.carga_grafo()

    #origin_str = input('¿De dónde quiere salir? ')
    origin_str = 'Calle Río Bullaque, 4'
    try:
        origin = ca.busca_direccion(origin_str, callejero)
        origin = closest_node(origin, G)
    except Exception as error:
        print(error)

    #dest_str = input('¿A dónde quiere ir? ')
    dest_str = "Calle de Alberto Aguilera, 25"
    try:
        dest = ca.busca_direccion(dest_str, callejero)
        dest = closest_node(dest, G)
    except Exception as error:
        print(error)

    peso = choose()

    minimo = gp.camino_minimo(G, peso, origin, dest)
    print(minimo)

