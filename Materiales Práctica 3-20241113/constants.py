import sys

# Para callejero
WAIT = 30   # Segundos
PROB = 0.8
INFTY=sys.float_info.max #Distincia "infinita" entre nodos de un grafo


# Para gps
MARGIN = 3    # Margen para considerar como dirección "recto" entre dos calles

# Para callejero
MIN_SIMILITUD = 60     # Estimamos esta similitud mínima

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

SIGNS = {'W': '-', 'E': '+', 'S': '-', 'N': '+'}