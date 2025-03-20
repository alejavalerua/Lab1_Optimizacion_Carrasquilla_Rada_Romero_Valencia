from itertools import zip_longest
import random

# Implementación propia de matrices dispersas
class MatrizDispersaCSC:
    """ Implementación de matrices dispersas según formato CSC. """
    def __init__(self, matriz=None, forma=None):
        self.elementos = []
        self.filas = []
        self.indices_columnas = []
        self.forma = forma if not forma is None else (len(matriz), len(matriz[0]))

        if matriz is not None:
          current_index = 1
          for fil in zip_longest(*matriz, fillvalue=None):
            fil = [(col + 1, x) for col, x in enumerate(fil) if x != 0]
            if len(fil) == 0:
              continue
            self.indices_columnas.append(current_index)
            current_index += len(fil)
            for col, elem in fil:
              self.elementos.append(elem)
              self.filas.append(col)
          self.indices_columnas.append(self.indices_columnas[0] + len(self.filas))

    def __str__(self):
      return f"Matriz dispersa CSC\nElementos: {self.elementos}\nFilas: {self.filas}\nÍndices de columnas: {self.indices_columnas}\n"

    def sumar(self, otra):
        """ Suma dos matrices CSC """
        assert self.forma == otra.forma, "Las matrices deben tener la misma forma."

        elementos_res, filas_res, indices_res = [], [], [1]
        num_columnas = self.forma[1]
        indice_actual = 1

        for col in range(num_columnas):
            col_inicio_A, col_fin_A = self.indices_columnas[col] - 1, self.indices_columnas[col + 1] - 1
            col_inicio_B, col_fin_B = otra.indices_columnas[col] - 1, otra.indices_columnas[col + 1] - 1

            valores_A = {self.filas[i]: self.elementos[i] for i in range(col_inicio_A, col_fin_A)}
            valores_B = {otra.filas[i]: otra.elementos[i] for i in range(col_inicio_B, col_fin_B)}

            suma_columna = {}
            for fila in set(valores_A.keys()).union(valores_B.keys()):
                suma_columna[fila] = valores_A.get(fila, 0) + valores_B.get(fila, 0)

            for fila, valor in sorted(suma_columna.items()):
                if valor != 0:
                    elementos_res.append(valor)
                    filas_res.append(fila)

            indices_res.append(indice_actual + len(suma_columna))
            indice_actual += len(suma_columna)

        return MatrizDispersaCSC(forma=self.forma)._cargar_datos(elementos_res, filas_res, indices_res)

    def multiplicar_vector(self, vector):
      assert len(vector) == self.forma[1], "El vector no posee la dimensión adecuada."
      resultado = [0] * self.forma[0]

      for col in range(len(self.indices_columnas) - 1):
          col_inicio = self.indices_columnas[col] - 1
          col_fin = self.indices_columnas[col + 1] - 1
          valor_vector = vector[col]

          for i in range(col_inicio, col_fin):
              fila = self.filas[i] - 1  # Ajustar el índice
              resultado[fila] += self.elementos[i] * valor_vector

      return resultado

    def _cargar_datos(self, elementos, filas, indices):
        """ Permite rellenar la data de la matriz manualmente """
        self.elementos = elementos
        self.filas = filas
        self.indices_columnas = indices
        return self

    def a_matriz_normal(self):
        """ Convierte la matriz CSC a formato denso (numpy) """
        matriz = [[0] * self.forma[1] for _ in range(self.forma[0])]
        for col in range(len(self.indices_columnas) - 1):
            for i in range(self.indices_columnas[col] - 1, self.indices_columnas[col + 1] - 1):
                fila = self.filas[i] - 1  # Ajuste de índice
                matriz[fila][col] = self.elementos[i]
        return matriz

def generar_matriz_dispersa(n, m, densidad=0.2, min_val=1, max_val=10):
        matriz = [[0] * m for _ in range(n)]
        tot_elems = int(n * m * densidad)  # Calcula cuántos elementos no nulos habrá

        for _ in range(tot_elems):
            i = random.randint(0, n - 1)  # Fila aleatoria
            j = random.randint(0, m - 1)  # Columna aleatoria
            matriz[i][j] = random.randint(min_val, max_val)

        return matriz

def suma_matriz(m1, m2):
    if len(m1) != len(m2) or len(m1[0]) != len(m2[0]):
        raise ValueError("Las matrices deben tener la misma forma.")
    return [[m1[i][j] + m2[i][j] for j in range(len(m1[0]))] for i in range(len(m1))]

def matriz_por_vector(matriz, vector):
    if len(matriz[0]) != len(vector):
        raise ValueError("El número de columnas de la matriz debe ser igual al tamaño del vector.")
    return [sum(matriz[i][j] * vector[j] for j in range(len(matriz[0]))) for i in range(len(matriz))]