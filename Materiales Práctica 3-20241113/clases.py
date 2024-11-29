# Clase para meter en la cola los nodos, 
# teniendo en cuenta que puede haber claves de distino tipo (str, int, ...)
class Prioridad():
    def __init__(self, prioridad, valor):
        self.prioridad = prioridad
        self.valor = valor

    def __lt__(self, other):
        # Compara las prioridades primero
        if self.prioridad != other.prioridad:
            return self.prioridad < other.prioridad
        # Si las prioridades son iguales, convierte a str para comparar
        return str(self.valor) < str(other.valor)

    def __repr__(self):
        return f"({self.prioridad}, {self.valor})"