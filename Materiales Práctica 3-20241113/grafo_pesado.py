"""
grafo.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPxxx
Integrantes:
    - XX
    - XX

Descripción:
Librería para el análisis de grafos pesados.
"""

from typing import List,Tuple,Dict,Callable,Union
import networkx as nx
import sys
import callejero as ca
import heapq #Librería para la creación de colas de prioridad

WAIT = 30   # Segundos
PROB = 0.8

INFTY=sys.float_info.max #Distincia "infinita" entre nodos de un grafo

def peso_longitud(grafo:nx.Graph, vertice_0: int, vertice_1: int) -> int:
    return grafo[vertice_0][vertice_1]['length']

def peso_velocidad(grafo:nx.Graph, vertice_0: int, vertice_1: int) -> int:

    speed = grafo[vertice_0][vertice_1]['maxspeed']
    distancia = grafo[vertice_0][vertice_1]['length']
    return distancia / speed

def peso_semaforo(grafo:nx.Graph, vertice_0: int, vertice_1: int) -> int:
    
    speed = grafo[vertice_0][vertice_1]['maxspeed']
    distancia = grafo[vertice_0][vertice_1]['length']
    return distancia / speed + PROB*WAIT

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
    heapq.heappush(cola, (0, origen))

    while cola:
        # Extraer el nodo con la distancia mínima
        distancia_actual, nodo_actual = heapq.heappop(cola)

        # Si la distancia actual es mayor que la registrada, continuar
        if distancia_actual > distancias[nodo_actual]:
            continue

        # Iterar sobre los vecinos del nodo actual
        for vecino in G.neighbors(nodo_actual):
            # Calcular el peso de la arista
            peso_arista = peso(G, nodo_actual, vecino)
            nueva_distancia = distancias[nodo_actual] + peso_arista

            # Si se encuentra una distancia más corta
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                padres[vecino] = nodo_actual
                heapq.heappush(cola, (nueva_distancia, vecino))

    return padres


def camino_minimo(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]] ,origen:object,destino:object)->List[object]:
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
    pass
                

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
    pass