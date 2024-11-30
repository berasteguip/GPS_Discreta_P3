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

Funciones adicionales:
- coord_to_float(): Convierte una coordenada en formato de grados, minutos y segundos a un valor decimal en formato de punto flotante.
- calcular_similitud(): Calcula la similitud entre dos cadenas de texto utilizando una métrica de similitud.
- distancia(): Calcula la distancia entre dos puntos geográficos dados por sus coordenadas.
"""

from constants import *
import pandas as pd
import re
from rapidfuzz.fuzz import ratio
from typing import Tuple
import osmnx as ox
import os
import networkx as nx

class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AdressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass


############## Parte 2 ##############

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
        print('· Leyendo el callejero de Madrid...')
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

def distancia(calle_pedida: str, calle_iter: str) -> float:
    """
    Calcula la distancia de edición normalizada entre dos nombres de calles.

    Args:
        calle_pedida (str): Nombre de la calle que se está buscando.
        calle_iter (str): Nombre de la calle con la que se compara.

    Returns:
        float: Distancia de edición normalizada entre las dos cadenas, truncada a un valor máximo de 0.7.
               Un valor más bajo indica mayor similitud entre las cadenas.
    """
    entrada_normalizada = calle_pedida.strip().lower()
    valor_normalizado = calle_iter.strip().lower()
    # Calcula la similitud con la métrica que prefieras (ejemplo: ratio simple)
    return ratio(entrada_normalizada, valor_normalizado)

def capitalize_custom(word: str, particulas: pd.Series) -> str:
    """
    Capitaliza una palabra, excepto si es una partícula que debe ir en minúsculas.

    Args:
        word (str): La palabra a capitalizar.
        callejero (pd.DataFrame): DataFrame con la información de las calles.

    Returns:
        str: La palabra capitalizada o en minúsculas si es una partícula.
    """
    if word.upper() in particulas:
        return word.lower()
    else:
        return word.capitalize()

def busca_direccion(direccion: str, callejero: pd.DataFrame) -> Tuple[float,float]:
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


    else:
        callejero_sim = callejero.copy()
        callejero_sim['SIMILITUD'] = callejero_sim['NOMBRE_COMPLETO'].apply( lambda x: distancia(direccion, x))
        callejero_sim = callejero_sim.sort_values(by='SIMILITUD', ascending=False).reset_index()
        
        closest = callejero_sim.iloc[0]
        if closest['SIMILITUD'] < MIN_SIMILITUD:
            raise AdressNotFoundError('La dirección proporcionada no es correcta.')
        else:
            lat = closest['FLOAT_LATITUD']
            long = closest['FLOAT_LONGITUD']
        direccion = closest['NOMBRE_COMPLETO']

    particulas = callejero['VIA_PAR'].str.strip().unique()
    direccion = ' '.join(capitalize_custom(word, particulas) for word in direccion.split(' '))
    print(f'Dirección encontrada --> {direccion}')
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
        try:
            # Cargar el grafo desde el archivo
            print(f'· Cargando grafo de Madrid desde "{graph_file}"...')
            grafo = ox.load_graphml(graph_file)
        except Exception:
            raise ServiceNotAvailableError("No se pudo cargar el grafo desde el archivo")
    else:
        try:
            # Descargar el grafo de OpenStreetMap
            print('· Descargando grafo de Madrid...')
            grafo = ox.graph_from_place("Madrid, Spain", network_type='drive')

            # Guardar el grafo en un archivo
            ox.save_graphml(grafo, graph_file)
        except Exception:
            raise ServiceNotAvailableError("No se pudo descargar el grafo de OpenStreetMap")
    
    grafo_dirigido = procesa_grafo(grafo)
    
    return grafo_dirigido


def procesa_grafo(multidigrafo:nx.MultiDiGraph) -> nx.DiGraph:
    """ Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    Args:
        multidigrafo: multidigrafo de las calles de Madrid obtenido de OpenStreetMap.
    Returns:
        nx.DiGraph: Grafo con valores limpios, dirigido y sin bucles asociado al multidigrafo dado.
    Raises: None
    """
    # Convertir el multidigrafo en un grafo dirigido
    grafo_dirigido = ox.convert.to_digraph(multidigrafo)
    
    # Eliminar bucles
    loops = list(nx.selfloop_edges(grafo_dirigido))
    grafo_dirigido.remove_edges_from(loops)

    for n0, n1, edge in grafo_dirigido.edges(data=True):
        
        # Corrección del tipo de vía
        if 'highway' in edge:
            if type(edge['highway']) == list:
                edge['highway'] = edge['highway'][0]    # Cuando una calle tiene más de un tipo de vía cogemos el primero arbitrariamente.
        else:
            edge['highway'] = 'other'

        # Corrección de la velocidad de la vía
        if 'maxspeed' in edge:
            if type(edge['maxspeed']) == list:
                edge['maxspeed'] = max(edge['maxspeed'])    # Cogemos el máximo de las velocidades que figuran de manera arbitraria
            elif '|' in edge['maxspeed']:
                edge['maxspeed'] = max(edge['maxspeed'].split('|')) # Cogemos el máximo de las velocidades que figuran de manera arbitraria
        else:
            edge['maxspeed'] = MAX_SPEEDS[edge['highway']]
        edge['maxspeed'] = float(edge['maxspeed']) / 3.6   # De km/h a m/s

        # Corrección del nombre de la calle
        if 'name' in edge:
            if type(edge['name']) == list:
                edge['name'] = edge['name'][0]  # De manera arbitraria cogemos el primer elemento, ya que la calle se puede llamar de ambas formas
        else:
            edge['name'] = 'Calle sin nombre'
        edge['length'] = round(edge['length'])

    return grafo_dirigido