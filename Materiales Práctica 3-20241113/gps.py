"""
gps.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPxxx
Integrantes:
    - XX
    - XX

Descripción:
Librería para la gestión y cálculo de rutas en un sistema de navegación GPS.
"""

import callejero as ca
import grafo_pesado as gp
from constants import *
import networkx as nx
from typing import Callable, Tuple, List
import math
from shapely.geometry import Point
import matplotlib.pyplot as plt



def closest_node(G: nx.DiGraph, coords: Tuple[int, int]) -> Tuple[int, int]:
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

def choose() -> Callable[[nx.Graph,object,object],float]:
    """
    choose() -> Callable[[nx.Graph,object,object],float]
    
    Esta función permite al usuario seleccionar el tipo de ruta que desea calcular.
    
    Returns:
        Callable[[nx.Graph,object,object],float]: Una función de peso que será utilizada
        para calcular la ruta. Las opciones son:
            - peso_longitud: Calcula la ruta más corta en distancia
            - peso_velocidad: Calcula la ruta más rápida sin considerar semáforos
            - peso_semaforo: Calcula la ruta más rápida considerando semáforos
    """
    options = ['1', '2' ,'3']
    print('''
· Ruta más corta (1)
· Ruta más rápida (2)
· Ruta más rápida (optimizando semáforos) (3)''')
    select = input('Escoja una opción (1, 2 o 3)')

    while select not in options:
        select = input('Debe escoger una de las tres opciones (1, 2 o 3)')

    if select == '1':
        return gp.peso_longitud
    elif select == '2':
        return gp.peso_velocidad
    elif select == '3':
        return gp.peso_semaforo

def convert(n: int) -> str:
    """
    Convierte un número de metros a un formato legible, ya sea en kilómetros o metros.

    Args:
        n (int): La distancia en metros que se desea convertir.

    Returns:
        str: La distancia convertida a un formato legible, ya sea en kilómetros (km) o metros (m).
    """
    if n >= 1000:
        return f"{round(n / 1000, 1):.1f} km"
    else:
        return f"{round(n / 10) * 10} m"

def instrucciones(G: nx.DiGraph, caminos: List[List[int]]) -> List[str]:
    """
    Genera una lista de instrucciones de navegación basadas en un camino y un grafo.

    Args:
        camino (List[int]): Lista de identificadores de nodos que forman el camino.
        G (nx.DiGraph): Grafo dirigido que representa la red de calles.

    Returns:
        List[str]: Lista de instrucciones de navegación en formato texto, incluyendo
                  giros, distancias y nombres de calles.
    """
    total_time = 0
    instrucc = []
    for camino in caminos:
        edge_actual = G[camino[0]][camino[1]]
        total_time += round(edge_actual['length'] / edge_actual['maxspeed'])
        vector_actual = (G.nodes[camino[0]]['y'] - G.nodes[camino[1]]['y'], 
                        G.nodes[camino[0]]['x'] - G.nodes[camino[1]]['x'])
        nombre_actual = edge_actual['name']
        distancia_acumulada = edge_actual['length']
        instrucc.append(f'Sal por calle {nombre_actual}.')
        for i in range(len(camino) - 2):

            edge_next = G[camino[i + 1]][camino[i + 2]]
            vector_next = (G.nodes[camino[i + 1]]['y'] - G.nodes[camino[i + 2]]['y'], 
                                G.nodes[camino[i + 1]]['x'] - G.nodes[camino[i + 2]]['x'])

            # Calcular el ángulo entre los dos vectores
            dot_product = vector_actual[0] * vector_next[0] + vector_actual[1] * vector_next[1]
            magnitude_actual = math.sqrt(vector_actual[0]**2 + vector_actual[1]**2)
            magnitude_next = math.sqrt(vector_next[0]**2 + vector_next[1]**2)
            angle = math.acos(dot_product / (magnitude_actual * magnitude_next)) * (180 / math.pi)  # Esto último para pasar a grados

            determinante = vector_actual[0] * vector_next[1] - vector_actual[1] * vector_next[0]

            if angle < MARGIN:
                giro = None
            elif determinante < 0:
                giro = 'izquierda'
            elif determinante > 0:
                giro = 'derecha'
            # Si determinante = 0, ya habrá entrado en angle < MARGIN (los dos vectores son combinación lineal)

            nombre_next = edge_next['name']
            if nombre_actual != nombre_next:
                if giro:
                    instrucc.append(f'En {distancia_acumulada} metros, gira a la {giro} en {nombre_next}')
                else:
                    instrucc.append(f'En {distancia_acumulada} metros, continúa por {nombre_next}')
                distancia_acumulada = edge_next['length']
            else:
                distancia_acumulada += edge_next['length']
            
            vector_actual = vector_next
            edge_actual = edge_next
            total_time += round(edge_actual['length'] / edge_actual['maxspeed'])
            nombre_actual = nombre_next

    total_time = round(total_time / 60) # Pasar segundos a minutos
    print(f'Tiempo estimado de la ruta: {total_time}')
    return instrucc

def show_instrucciones(instrucc: list[str]) -> None:
    """
    Muestra las instrucciones de navegación en un formato legible.

    Args:
        instrucc (list[str]): Lista de instrucciones de navegación en formato texto.
    
    Returns:
        None: Imprime las instrucciones en la consola precedidas por una flecha.
    """
    for chain in instrucc:
        print(f'--> {chain}')

def dibuja_camino(G: nx.DiGraph, camino:list):
    """
    Dibuja el grafo dirigido utilizando las posiciones geográficas de los nodos.
    
    Args:
        grafo (nx.DiGraph): Grafo dirigido a dibujar.
    """
    # Extraer las posiciones de los nodos
    pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}
    
    # Dibujar el grafo
    plt.figure(figsize=(12, 12))
    camino_edges = list(zip(camino[:-1], camino[1:]))
    nx.draw_networkx_nodes(G, pos, nodelist=camino, node_size=0.1, node_color='red')
    nx.draw_networkx_edges(G, pos, edgelist=camino_edges, edge_color='red', width=2)
    
    plt.title("Grafo dirigido de calles de Madrid")
    plt.show()

def dibuja_caminos_ciudad(G: nx.DiGraph, caminos: List[List[int]]) -> None:
    """
    Dibuja el grafo completo de la ciudad y resalta el camino especificado.

    Args:
        grafo (nx.DiGraph): Grafo dirigido que representa la ciudad.
        camino (List[int]): Lista de nodos que forman el camino a resaltar.

    Returns:
        None: Muestra el gráfico usando matplotlib.

    La función dibuja todo el grafo de la ciudad en gris claro y superpone
    el camino especificado en rojo para destacarlo visualmente.
    """
    pos = {node: (data['x'], data['y']) for node, data in G.nodes(data=True)}

    plt.figure(figsize=(12, 12))

    # Dibujo de la ciudad
    nx.draw_networkx_nodes(G, pos, node_size=0.1, node_color='gray')
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=5, edge_color='gray', width=0.2)

    nx.draw_networkx_nodes(G, pos, nodelist=[caminos[0][0]], node_size=20, node_color='green', label='Origen')

    for camino in caminos:
        # Dibujo del camino
        camino_edges = list(zip(camino[:-1], camino[1:]))
        nx.draw_networkx_nodes(G, pos, nodelist=camino, node_size=0.7, node_color='black')
        nx.draw_networkx_edges(G, pos, edgelist=camino_edges, edge_color='black', width=2, style='solid')
        # Dibujar puntos de origen y destino
        if camino != caminos[-1]:
            nx.draw_networkx_nodes(G, pos, nodelist=[camino[-1]], node_size=20, node_color='Blue', label='Parada')
    
    nx.draw_networkx_nodes(G, pos, nodelist=[caminos[-1][-1]], node_size=20, node_color='Red', label='Destino')
    
    plt.legend()
    plt.title('Tu ruta')
    plt.axis('off')

    caminos_combined = []
    for camino in caminos:
        caminos_combined.extend(camino)
    # Ajustar los límites del gráfico para ampliar la vista de la ruta
    x_values, y_values = zip(*[pos[node] for node in caminos_combined])
    plt.xlim(min(x_values) - 0.01, max(x_values) + 0.01)
    plt.ylim(min(y_values) - 0.01, max(y_values) + 0.01)

    plt.show()

if __name__ == "__main__":

    # Inicialización del dataset y grafo de las calles de Madrid
    print('· Inicializando GPS...')
    callejero = ca.carga_callejero()
    G = ca.carga_grafo()



    while True:     # Bucle de viajes completos

        peso = choose()
        
        while True:     # Bucle de paradas
            entrada = input('Va a comenzar su viaje. ¿Cuántas paradas intermedias quiere hacer? ([enter] para 0 paradas), ([s] para salir)\n')
            if entrada.lower() == "s":
                break
            elif entrada == "":
                entrada = "0"
            if entrada.isdigit() and int(entrada) >= 0:
                break
            else:
                print("Por favor, introduzca 's' para salir o un número entero positivo.")
        if entrada.lower() == "s":
            print('· Cerrando GPS...')
            break
        stops = int(entrada)

        
        origin_str = input('¿De dónde quiere salir?')
        #origin_str = 'Calle de la Princesa, 25'
        try:
            origin = ca.busca_direccion(origin_str, callejero)
            origin = closest_node(G, origin)
        except Exception as error:
            print(error)
        caminos = []
        for i in range(stops):
            stop_str = input(f'Introduzca la parada nº{i + 1}: ')
            stop = ca.busca_direccion(stop_str, callejero)
            stop = closest_node(G, stop)
            caminos.append(gp.camino_minimo(G, peso, origin, stop))
            origin = stop

        dest_str = input('¿A dónde quiere ir? ')
        #dest_str = 'Calle de Río Bullaque, 4'
        try:
            dest = ca.busca_direccion(dest_str, callejero)
            dest = closest_node(G, dest)
        except Exception as error:
            print(error)

        minimo = gp.camino_minimo(G, peso, origin, dest)
        caminos.append(minimo)
        instrucc = instrucciones(G, caminos)    # Hacer para múltiples caminos

        # Mostramos los resultados en formato mapa y texto
        show_instrucciones(instrucc)
        dibuja_caminos_ciudad(G, caminos)

        # Datos de interés
        print(f'Número de cruces: {len(minimo)}')
        print(f'Número de instrucciones: {len(instrucc)}')