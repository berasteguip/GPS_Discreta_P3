"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GPxxx
Integrantes:
    - XX
    - XX

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.

Complétese esta descripción según las funcionalidades agregadas por el grupo.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import regex as re
import os
import matplotlib.pyplot as plt
from typing import Tuple
from Levenshtein import distance as string_distance

MAX_DISTANCE = 0.4     # Encontrar distancia máxima ideal

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': '20',
 'residential': '30',
 'primary_link': '40',
 'unclassified': '40',
 'secondary_link': '40',
 'trunk_link': '40',
 'secondary': '50',
 'tertiary': '50',
 'primary': '50',
 'trunk': '50',
 'tertiary_link':'50',
 'busway': '50',
 'motorway_link': '70',
 'motorway': '100',
 'other': '50'}


class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AdressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass


############## Parte 2 ##############

SIGNS = {'W': '-', 'E': '+', 'S': '-', 'N': '+'}

def coord_to_float(coordinate: str) -> float:
    pattern = re.compile(r"([\d]+)°([\d]+)?'?(\d+(?:\.\d+)?)?'' ?([NSEW])")
    match = re.search(pattern, coordinate)
    gra, min, sec = float(match[1]), float(match[2] or 0), float(match[3] or 0)
    min += sec / 60
    gra += min / 60
    dir = match[4]
    gra = float(SIGNS[dir] + str(gra))
    return gra

def carga_callejero() -> pd.DataFrame:
    """ Función que carga el callejero de Madrid, lo procesa y devuelve
    un DataFrame con los datos procesados
    
    Args: None
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice del
            grafo, qué vértice es su padre en el árbol abarcador mínimo.
    Raises:
        FileNotFoundError si el fichero csv con las direcciones no existe
    """
    try:
        print(f'Leyendo el callejero de Madrid...')
        callejero = pd.read_csv('direcciones.csv', encoding='latin1', sep=';')
    except FileNotFoundError:
        raise FileNotFoundError("El fichero csv con las direcciones no existe")
    
    callejero = callejero[['VIA_CLASE', 'VIA_PAR', 'VIA_NOMBRE', 'NUMERO', 'LATITUD', 'LONGITUD']]

    # Coordenadas en float
    callejero['FLOAT_LATITUD'] = callejero['LATITUD'].apply(coord_to_float)
    callejero['FLOAT_LONGITUD'] = callejero['LONGITUD'].apply(coord_to_float)

    # Nombre completo de la calle
    replace_nans = lambda par: "" if str(par).lower() == 'nan' else str(par) + " "

    callejero['VIA_PAR'] = callejero['VIA_PAR'].apply(replace_nans)
    callejero['NOMBRE_COMPLETO'] = callejero['VIA_CLASE'] + " " + callejero['VIA_PAR'] + callejero['VIA_NOMBRE'] + ", " + callejero['NUMERO'].astype(str)
    return callejero


def distancia(calle_pedida, calle_iter):
    VALOR = 0.7 # recortaremos todos los cambios que sean mayores que este valor
    distancia = min(string_distance(calle_pedida.lower(), calle_iter.lower())/len(calle_pedida), VALOR)
    return distancia

def busca_direccion(direccion:str, callejero:pd.DataFrame) -> Tuple[float,float]:
    """ Función que busca una dirección, dada en el formato
        calle, numero
        en el DataFrame callejero de Madrid y devuelve el par (latitud, longitud) en grados de la
        ubicación geográfica de dicha dirección
    
    Args:
        direccion (str): Nombre completo de la calle con número, en formato "Calle, num"
        callejero (DataFrame): DataFrame con la información de las calles
    Returns:
        Tuple[float,float]: Par de float (latitud,longitud) de la dirección buscada, expresados en grados
    Raises:
        AdressNotFoundError: Si la dirección no existe en la base de datos
    Example:
        busca_direccion("Calle de Alberto Aguilera, 23", data)=(40.42998055555555,-3.7112583333333333)
        busca_direccion("Calle de Alberto Aguilera, 25", data)=(40.43013055555555,-3.7126916666666667)
    """

    direccion = direccion.upper()
    if direccion in callejero['NOMBRE_COMPLETO'].unique():
        
        lat = callejero.loc[callejero['NOMBRE_COMPLETO'] == direccion,'FLOAT_LATITUD'].values[0]
        long = callejero.loc[callejero['NOMBRE_COMPLETO'] == direccion,'FLOAT_LONGITUD'].values[0]
        return lat, long

    else:
        callejero_dist = callejero.copy()
        callejero_dist['DISTANCIA'] = callejero_dist['NOMBRE_COMPLETO'].apply( lambda x: distancia(direccion, x))
        callejero_dist = callejero_dist.sort_values(by='DISTANCIA', ascending=True).reset_index()
        
        closest = callejero_dist.iloc[0]
        if closest['DISTANCIA'] > MAX_DISTANCE:
            raise AdressNotFoundError('La dirección proporcionada no es correcta.')
        else:
            lat = closest['FLOAT_LATITUD']
            long = closest['FLOAT_LONGITUD']
            return lat, long



############## Parte 4 ##############


def carga_grafo() -> nx.DiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap y lo convierte en un grafo dirigido sin bucles.
    Args: None
    Returns:
        nx.DiGraph: Grafo dirigido sin bucles de las calles de Madrid.
    Raises:
        ServiceNotAvailableError: Si no es posible recuperar el grafo de OpenStreetMap.
    """

    graph_file = "madrid.graphml"
    
    if os.path.exists(graph_file):
        # Cargar el grafo desde el archivo
        print(f'Cargando grafo de Madrid desde "{graph_file}"...')
        grafo = ox.load_graphml(graph_file)
    else:
        # Descargar el grafo de OpenStreetMap
        print('Descargando grafo de Madrid...')
        grafo = ox.graph_from_place("Madrid, Spain", network_type='drive')

        # Guardar el grafo en un archivo
        ox.save_graphml(grafo, graph_file)
    
    grafo_dirigido = procesa_grafo(grafo)
    
    return grafo_dirigido


def procesa_grafo(multidigrafo:nx.MultiDiGraph) -> nx.DiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args:
        multidigrafo: multidigrafo de las calles de Madrid obtenido de OpenStreetMap.
    Returns:
        nx.DiGraph: Grafo dirigido y sin bucles asociado al multidigrafo dado.
    Raises: None
    """

    # Convertir el multidigrafo en un grafo dirigido
    grafo_dirigido = ox.convert.to_digraph(multidigrafo)
    
    # Eliminar bucles
    loops = list(nx.selfloop_edges(grafo_dirigido))
    grafo_dirigido.remove_edges_from(loops)

    for n0, n1, edge in grafo_dirigido.edges(data=True):
        if 'highway' in edge:
            if type(edge['highway']) == list:
                edge['highway'] = edge['highway'][0]    # Cuando una calle tiene más de un tipo de vía cogemos el primero arbitrariamente.
        else:
            edge['highway'] = 'other'
        if 'maxspeed' in edge:
            if type(edge['maxspeed']) == list:
                edge['maxspeed'] = max(edge['maxspeed'])    # Cogemos el máximo de las velocidades que figuran de manera arbitraria
            elif '|' in edge['maxspeed']:
                edge['maxspeed'] = max(edge['maxspeed'].split('|')) # Cogemos el máximo de las velocidades que figuran de manera arbitraria
        else:
            edge['maxspeed'] = MAX_SPEEDS[edge['highway']]

    return grafo_dirigido

def show_grafo(grafo: nx.DiGraph) -> None:
    pos = {node: (data['x'], data['y']) for node, data in grafo.nodes(data=True)}

    plt.figure(figsize=(12, 12))

    nx.draw_networkx_nodes(grafo, pos, node_size=0.5, node_color='blue')
    nx.draw_networkx_edges(grafo, pos, arrowstyle='->', arrowsize=5, edge_color='gray', width=0.2)

    plt.title('Grafo Dirigido de las Calles de Madrid')
    plt.axis('off')
    plt.show()