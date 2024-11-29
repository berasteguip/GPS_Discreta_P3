"""
grafo_pesado.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPxxx
Integrantes:
    - XX
    - XX

Descripción:
Librería para el análisis de grafos pesados.
"""

from clases import Prioridad
from constants import *
import networkx as nx
import heapq
from typing import Union, Callable, List, Tuple, Dict

def peso_longitud(grafo: nx.Graph, vertice_0: int, vertice_1: int) -> int:
    """
    Calcula el peso de una arista basado en su longitud.

    Args:
        grafo (nx.Graph): El grafo que contiene la arista.
        vertice_0 (int): El primer vértice de la arista.
        vertice_1 (int): El segundo vértice de la arista.

    Returns:
        int: La longitud de la arista entre vertice_0 y vertice_1.
    """
    return grafo[vertice_0][vertice_1]['length']

def peso_velocidad(grafo: nx.Graph, vertice_0: int, vertice_1: int) -> float:
    """
    Calcula el peso de una arista basado en el tiempo de viaje sin considerar semáforos.

    Args:
        grafo (nx.Graph): El grafo que contiene la arista.
        vertice_0 (int): El primer vértice de la arista.
        vertice_1 (int): El segundo vértice de la arista.

    Returns:
        float: El tiempo de viaje entre vertice_0 y vertice_1 en segundos.
    """
    speed = grafo[vertice_0][vertice_1]['maxspeed']
    distancia = grafo[vertice_0][vertice_1]['length']
    return distancia / speed

def peso_semaforo(grafo: nx.Graph, vertice_0: int, vertice_1: int) -> float:
    """
    Calcula el peso de una arista considerando el tiempo de viaje y la probabilidad de encontrar un semáforo.

    Args:
        grafo (nx.Graph): El grafo que contiene la arista.
        vertice_0 (int): El primer vértice de la arista.
        vertice_1 (int): El segundo vértice de la arista.

    Returns:
        float: El tiempo de viaje estimado entre vertice_0 y vertice_1 en segundos, incluyendo posibles paradas en semáforos.
    """
    speed = grafo[vertice_0][vertice_1]['maxspeed']
    distancia = grafo[vertice_0][vertice_1]['length']
    return distancia / speed + PROB * WAIT

def dijkstra(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]], origen:object)-> Dict[object,object]:
    """ Calcula un Árbol de Caminos Mínimos para el grafo pesado partiendo
    del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
    el árbol de la componente conexa que contiene a "origen".
    Args:
        origen (object): vértice del grafo de origen
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice alcanzable
            desde "origen", qué vértice es su padre en el árbol de caminos mínimos.
    Raises:
        TypeError: Si origen no es "hashable".
    Example:
        Si G.dijksra(1)={2:1, 3:2, 4:1} entonces 1 es padre de 2 y de 4 y 2 es padre de 3.
        En particular, un camino mínimo desde 1 hasta 3 sería 1->2->3.
    """

    # Inicializar la cola de prioridad y el diccionario de padres
    cola = []
    padres = {nodo: None for nodo in G.nodes}
    distancias = {nodo: INFTY for nodo in G.nodes}
    distancias[origen] = 0
    # Agregar el nodo de origen a la cola
    heapq.heappush(cola, Prioridad(0, origen))
    while cola:
        # Extraer el nodo con la distancia mínima
        nodo = heapq.heappop(cola)
        distancia_actual = nodo.prioridad
        nodo_actual = nodo.valor
        # Si la distancia actual es mayor que la registrada, continuar
        if distancia_actual <= distancias[nodo_actual]:    
            # Iterar sobre los vecinos del nodo actual
            for vecino in G.neighbors(nodo_actual):
                # Calcular el peso de la arista
                peso_arista = peso(G, nodo_actual, vecino)
                nueva_distancia = distancias[nodo_actual] + peso_arista

                # Si se encuentra una distancia más corta
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    padres[vecino] = nodo_actual
                    heapq.heappush(cola, Prioridad(nueva_distancia, vecino))

    return padres


def camino_minimo(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]] , origen:object, destino:object)->List[object]:
    """ Calcula el camino mínimo desde el vértice origen hasta el vértice
    destino utilizando el algoritmo de Dijkstra.
    
    Args:
        G (nx.Graph o nx.Digraph): grafo a grado dirigido
        peso (función): función que recibe un grafo o grafo dirigido y dos vértices del mismo y devuelve el peso de la arista que los conecta
        origen (object): vértice del grafo de origen
        destino (object): vértice del grafo de destino
    Returns:
        List[object]: Devuelve una lista con los vértices del grafo por los que pasa
            el camino más corto entre el origen y el destino. El primer elemento de
            la lista es origen y el último destino.
    Example:
        Si dijksra(G,peso,1,4)=[1,5,2,4] entonces el camino más corto en G entre 1 y 4 es 1->5->2->4.
    Raises:
        TypeError: Si origen o destino no son "hashable".
    """
    padres = dijkstra(G, peso, origen)

    camino = []
    nodo_actual = destino
    while nodo_actual is not None:
        camino.append(nodo_actual)
        nodo_actual = padres[nodo_actual]
    
    camino.reverse()  # Invertir el camino para que vaya de origen a destino
    return camino

def prim(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> Dict[object,object]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo pesado
    usando el algoritmo de Prim.
    
    Args: None
    Returns:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises: None
    Example:
        Si prim(G,peso)={1: None, 2:1, 3:2, 4:1} entonces en un árbol abarcador mínimo tenemos que:
            1 es una raíz (no tiene padre)
            1 es padre de 2 y de 4
            2 es padre de 3
    """
    nodo_inicial = next(iter(G.nodes))  # Seleccionar un nodo arbitrario como inicial
    visitados = set()
    padres = {nodo: None for nodo in G.nodes}

    # Cola de prioridad para aristas (peso, nodo_origen, nodo_destino)
    cola = []
    for vecino in G.neighbors(nodo_inicial):
        peso_arista = peso(G, nodo_inicial, vecino)
        heapq.heappush(cola, Prioridad(peso_arista, (nodo_inicial, vecino)))

    visitados.add(nodo_inicial)

    while cola:
        arista_min = heapq.heappop(cola)
        peso_arista, (origen, destino) = arista_min.prioridad, arista_min.valor

        if destino in visitados:
            continue

        visitados.add(destino)
        padres[destino] = origen

        for vecino in G.neighbors(destino):
            if vecino not in visitados:
                peso_arista = peso(G, destino, vecino)
                heapq.heappush(cola, Prioridad(peso_arista, (destino, vecino)))

    return padres

                

def kruskal(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> List[Tuple[object,object]]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo
    usando el algoritmo de Kruskal.
    
    Args:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
    Returns:
        List[Tuple[object,object]]: Devuelve una lista [(s1,t1),(s2,t2),...,(sn,tn)]
            de los pares de vértices del grafo que forman las aristas
            del arbol abarcador mínimo.
    Raises: None
    Example:
        En el ejemplo anterior en que prim(G,peso)={1:None, 2:1, 3:2, 4:1} podríamos tener, por ejemplo,
        kruskal(G,peso)=[(1,2),(1,4),(3,2)]
    """
    # Crear una lista de aristas con sus pesos
    aristas = [
        (peso(G, u, v), u, v)
        for u, v in G.edges
    ]
    aristas.sort()  # Ordenar las aristas por peso

    # Inicializar la estructura de conjuntos disjuntos
    parent = {nodo: nodo for nodo in G.nodes}
    rank = {nodo: 0 for nodo in G.nodes}

    def find(nodo):
        if parent[nodo] != nodo:
            parent[nodo] = find(parent[nodo])  # Compresión de caminos
        return parent[nodo]

    def union(nodo1, nodo2):
        raiz1, raiz2 = find(nodo1), find(nodo2)
        if raiz1 != raiz2:
            if rank[raiz1] > rank[raiz2]:
                parent[raiz2] = raiz1
            elif rank[raiz1] < rank[raiz2]:
                parent[raiz1] = raiz2
            else:
                parent[raiz2] = raiz1
                rank[raiz1] += 1

    # Construir el MST
    mst = []
    for peso_arista, u, v in aristas:
        if find(u) != find(v):  # Si no forman un ciclo
            union(u, v)
            mst.append((u, v))

    return mst
