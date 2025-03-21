# All imports
import numpy as np
import sympy as sp
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from sympy import *
from scipy.optimize import minimize
from centrar_ventanas import center_window_method
import time
from time import perf_counter
import scipy.sparse as scp
from matrizdispersa import MatrizDispersaCSC, generar_matriz_dispersa, suma_matriz, matriz_por_vector

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.title("Lösung")
        self.geometry("1000x650+120-10") 
        self.resizable(False, False)
        self.iconphoto(True, tk.PhotoImage(file="data/Lab.png"))
        self.configure(bg="#dad2d8")

        # Crear estilo para botones redondeados
        style = ttk.Style()
        style.configure("Rounded.TButton",
                        font=("Times New Roman", 14, "bold"),
                        padding=8,
                        relief="GROOVE",
                        background="#dad2d8",
                        foreground="black",
                        borderwidth=1)
        
        style.map("Rounded.TButton",
                  background=[("active", "#dad2d8")],  # Cambio de color al pasar el mouse
                  foreground=[("active", "blue")])

        # Contenedor de los frames
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(fill="both", expand=True)

        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

        # Diccionario de frames
        self.frames = {}
        for F in (Inicio, Pagina1, Pagina2, Pagina3, Pagina4):
            frame = F(self.contenedor, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.mostrar_frame(Inicio)

    def mostrar_frame(self, contenedor):
        frame = self.frames[contenedor]
        frame.tkraise()

class Inicio(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(width=1000, height=650, bg="#dad2d8", bd=5)

        titulo = tk.Label(self, text="¡Bienvenido a Lösung!", font=("Montserrat", 50, "bold"),
                          fg="black", bg="#dad2d8", padx=20, pady=10, bd=5)
        titulo.pack(pady=20)

        # === Cargar una imagen en el frame ===
        imagen_path = "data/Lab.png"  # Cambia esto al nombre de tu imagen
        imagen = Image.open(imagen_path)
        imagen = imagen.resize((100, 100))  # Ajusta el tamaño si es necesario
        self.imagen_tk = ImageTk.PhotoImage(imagen)

        # Crear un Label con la imagen
        label_imagen = tk.Label(self, image=self.imagen_tk, bg="#dad2d8")
        label_imagen.place(x=1000-20, y=650-20)
        label_imagen.pack()

        texto_hover1 = '''Escoge un problema de optimización de dos variables (o puedes crear uno también). Plantea su función de costo y las restricciones. Grafica la región factible con ayuda de Python. Desarrolla un programa que le permita al usuario:\n
        a.	tener el valor de la función de costo a partir de un punto (x,y)\n
        b.	ver gráficamente cómo cambia la región factible ante un cambio en las restricciones.\n'''
        texto_hover2 = '''Selecciona un método de representación de matrices sparse e impleméntalo en Python desde cero. Compara tus resultados con la función de las librerías de Python. La comparación debe incluir el tiempo de ejecución para una matriz sparse con los 2 métodos (propio vs Python) y el tiempo de ejecución de una operación con la matriz densa. Para la interfaz el usuario debe poder escoger entre 3 métodos de representación de matrices sparse (pueden ser librerías de Python), realizar al menos dos operaciones con matrices y visualizar el tiempo de ejecución.'''
        texto_hover3 = '''Crea un programa para implementar la expansión en series de Taylor. El usuario debe ingresar la cantidad de términos de la expansión, el punto de expansión y la función a representar (debe tener al menos 5 funciones diferentes para escoger). Se debe mostrar en una gráfica la función original y la aproximación.'''
        texto_hover4 = '''Escoge 3 algoritmos de optimización sin restricciones. El usuario debe poder realizar cambios sobre sus parámetros y sobre el punto inicial. ¿Cómo afectan estos cambios los resultados? ¿Cómo afecta el tiempo de convergencia o cantidad de iteraciones? Nota: Puedes utilizar las librerías de Python y alguna ayuda gráfica o tabulaciones si lo necesitan para soportar sus conclusiones.'''

        # Contenedor para los botones alineados en una fila
        boton_frame = tk.Frame(self, bg="#dad2d8")
        boton_frame.pack(pady=30)

        botones = [
            ("Punto 1", Pagina1, texto_hover1),
            ("Punto 2", Pagina2, texto_hover2),
            ("Punto 3", Pagina3, texto_hover3),
            ("Punto 4", Pagina4, texto_hover4)
        ]

        # Etiqueta para mostrar el mensaje hover
        self.hover_label = tk.Label(self, text="", font=("Times New Roman", 13),
                                    fg="black", bg="#dad2d8", wraplength=700, justify= "left")
        self.hover_label.pack(pady=10)  # Se coloca debajo de los botones

        for i, (texto, pagina, mensaje) in enumerate(botones):
            boton = ttk.Button(boton_frame, text=texto, command=lambda p=pagina: controller.mostrar_frame(p),
                               style="Rounded.TButton")
            boton.grid(row=0, column=i, padx=10, pady=10)

            # Asignar eventos de hover
            boton.bind("<Enter>", lambda event, msg=mensaje: self.mostrar_mensaje(msg))
            boton.bind("<Leave>", self.ocultar_mensaje)

        ttk.Button(self, text="Salir", command=self.quit, style="Rounded.TButton").place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    def mostrar_mensaje(self, mensaje):
        """ Muestra el mensaje debajo de los botones """
        self.hover_label.config(text=mensaje)

    def ocultar_mensaje(self, event):
        """ Oculta el mensaje cuando el mouse sale """
        self.hover_label.config(text="")
        
class Pagina1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(bg="#dad2d8")
        # 🔹 Contenedor principal con Canvas y Scrollbar
        self.canvas = tk.Canvas(self, bg="#dad2d8")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        
        # 🔹 Frame dentro del Canvas donde irá el contenido
        self.frame_contenido = tk.Frame(self.canvas, bg="#dad2d8")
        # 🔹 Vinculación del Frame con el Canvas
        self.frame_contenido.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # 🔹 Crear una ventana dentro del Canvas para el contenido
        self.window = self.canvas.create_window((0, 0), window=self.frame_contenido, anchor="nw")
        # 🔹 Configurar el canvas con la scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        # 🔹 Posicionar elementos en la interfaz
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        # ------------------------- 🔹 CONTENIDO DE LA VENTANA -------------------------
        title_P1 = tk.Label(self.frame_contenido, text="Región Factible", fg="black", bg="#dad2d8",
                            font=("Times New Roman", 20, "bold", "underline"))
        title_P1.pack(pady=10)
        descripcion = """Una empresa fabrica dos tipos de productos: A y B. Cada unidad del producto A genera una ganancia de $5 y cada unidad del producto B genera una ganancia de $8. La empresa tiene 120 horas de trabajo disponibles y 100 unidades de materia prima."""
        
        tk.Label(self.frame_contenido, text="Problema de optimización:", font=("Times New Roman", 13, "bold"),
                 fg="black", bg="#dad2d8").pack(pady=2, anchor="w", padx=40)
        tk.Label(self.frame_contenido, text=descripcion, font=("Times New Roman", 12),
                 fg="black", bg="#dad2d8", wraplength=890, justify="left").pack(pady=2, anchor="w", padx=40)
        # Función objetivo
        tk.Label(self.frame_contenido, text="Función de costo (Objetivo):", font=("Times New Roman", 13, "bold"),
                 fg="black", bg="#dad2d8").pack(anchor="w", pady=2, padx=40)
        tk.Label(self.frame_contenido, text="Maximizar Z = 5x + 8y", font=("Times New Roman", 12),
                 fg="black", bg="#dad2d8").pack(pady=2, anchor="w", padx=40)
        tk.Label(self.frame_contenido, text="Sujeto a:", font=("Times New Roman", 13, "bold"), fg="black", bg="#dad2d8").pack(pady=2, anchor="w", padx=40)
        tk.Label(self.frame_contenido, text="✍ cx + dy <= 120          ✍ gx + hy <= 100          ✍ x, y >= 0", font=("Times New Roman", 12), fg="black", bg="#dad2d8").pack(pady=2, anchor="w", padx=40)
        
        # Contenedor principal que tendrá ambos frames lado a lado
        main_container = tk.Frame(self.frame_contenido, bg="#dad2d8")
        main_container.pack(fill="both", expand=True, padx=40, pady=5)
        
        # Frame para restricciones (izquierda)
        frame_restricciones = tk.Frame(main_container, bg="#dad2d8")
        frame_restricciones.pack(side="left", anchor="nw", pady=5)
        
        # Frame para la evaluación de la función de costo (derecha)
        frame_evaluacion = tk.Frame(main_container, bg="#dad2d8")
        frame_evaluacion.pack(side="right", anchor="ne", pady=5, padx=20)
        
        # Contenido del frame de restricciones
        labels = ["c:", "d:", "r1:", "g:", "h:", "r2:"]
        self.entries = {}
        for i, label in enumerate(labels):
            tk.Label(frame_restricciones, text=label, font=("Times New Roman", 12, "bold"), bg="#dad2d8").grid(row=i, column=0, padx=5, pady=2, sticky="w")
            entry = tk.Entry(frame_restricciones, width=10)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry.insert(0, "0")
            self.entries[label] = entry
            
        # Contenido del frame de evaluación de función de costo
        tk.Label(frame_evaluacion, text="Evaluación de la función de costo:", font=("Times New Roman", 12, "bold"), bg="#dad2d8").grid(row=0, column=0, columnspan=4, pady=10, sticky="w")
        
        # Entradas para X e Y
        self.entry_x = tk.Entry(frame_evaluacion, width=10)
        self.entry_y = tk.Entry(frame_evaluacion, width=10)
        
        tk.Label(frame_evaluacion, text="X:", font=("Times New Roman", 12, "bold"), bg="#dad2d8").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_x.grid(row=1, column=1, padx=5, pady=5)
        self.entry_x.insert(0, "0")
        
        tk.Label(frame_evaluacion, text="Y:", font=("Times New Roman", 12, "bold"), bg="#dad2d8").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.entry_y.grid(row=1, column=3, padx=5, pady=5)
        self.entry_y.insert(0, "0")
        
        # Label para mostrar el resultado
        self.label_resultado = tk.Label(frame_evaluacion, text="Z = 5x + 8y = 0", font=("Times New Roman", 12), bg="#dad2d8")
        self.label_resultado.grid(row=2, column=0, columnspan=4, padx=5, pady=10)
        
        # Botón para calcular la función de costo
        ttk.Button(frame_evaluacion, text="Evaluar función", 
                   command=self.calcular_funcion_costo, 
                   style="Rounded.TButton").grid(row=3, column=0, columnspan=4, pady=10)
        
        # Botón para graficar
        ttk.Button(self.frame_contenido, text="Graficar", 
                   command=self.calcular_optimizacion,
                   style="Rounded.TButton").pack(pady=10)
        
        # Frame para la gráfica
        self.frame_grafica = tk.Frame(self.frame_contenido, bg="#dad2d8")
        self.frame_grafica.pack(pady=20)
        
        # Frame para los valores de solución
        frame_valores = tk.Frame(self.frame_contenido, bg="#dad2d8")
        frame_valores.pack(pady=10)
        
        # Crear los Labels para X, Y, Z (resultados de la optimización)
        self.labels_resultado = {}
        for i, text in enumerate(["X = ", "Y = ", "Z = "]):
            tk.Label(frame_valores, text=text, font=("Times New Roman", 12, "bold"), bg="#dad2d8").grid(row=0, column=i*2, padx=5, pady=2)
            label_valor = tk.Label(frame_valores, text="--", font=("Times New Roman", 12), bg="#dad2d8")
            label_valor.grid(row=0, column=i*2+1, padx=5, pady=2)
            self.labels_resultado[text[0].lower()] = label_valor

        ttk.Button(self, text="Volver al Inicio", command=lambda: controller.mostrar_frame(Inicio),
                   style="Rounded.TButton").place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    def calcular_funcion_costo(self):
        """Calcular el valor de la función de costo con los valores de X e Y ingresados"""
        try:
            x = float(self.entry_x.get())
            y = float(self.entry_y.get())
            z = 5 * x + 8 * y
            self.label_resultado.config(text=f"Z = 5x + 8y = {z:.2f}")
        except ValueError:
            self.label_resultado.config(text="Error: Ingrese valores numéricos")
        
    def calcular_optimizacion(self):
        try:
            # Obtener valores desde la interfaz
            c, d, r1 = float(self.entries["c:"].get()), float(self.entries["d:"].get()), float(self.entries["r1:"].get())
            g, h, r2 = float(self.entries["g:"].get()), float(self.entries["h:"].get()), float(self.entries["r2:"].get())

            # Resolver la intersección
            A = np.array([[c, d], [g, h]])
            B = np.array([r1, r2])
            x_inter, y_inter = np.linalg.solve(A, B)

            # Crear valores de x
            x_vals = np.linspace(0, 40, 100)
            y1 = (r1 - c*x_vals) / d
            y2 = (r2 - g*x_vals) / h

            # Graficar
            fig, ax = plt.subplots(figsize=(6, 5))
            ax.plot(x_vals, y1, label=f'{c}x + {d}y = {r1}', color='blue')
            ax.plot(x_vals, y2, label=f'{g}x + {h}y = {r2}', color='green')

            # Sombrear la región factible
            ax.fill_between(x_vals, np.minimum(y1, y2), 0, where=(np.minimum(y1, y2) >= 0), color='gray', alpha=0.3)

            # Marcar la intersección
            ax.scatter(x_inter, y_inter, color='red', zorder=5, label="Intersección")

            # Configuración del gráfico
            ax.set_xlim(0, 40)
            ax.set_ylim(0, 40)
            ax.set_xlabel('Unidades de A (x)')
            ax.set_ylabel('Unidades de B (y)')
            ax.legend()
            ax.set_title('Región Factible')
            ax.grid(True)

            # Mostrar la gráfica en la interfaz
            for widget in self.frame_grafica.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
            canvas.draw()
            canvas.get_tk_widget().pack()

            # Mostrar resultados
            self.labels_resultado['x'].config(text=round(x_inter, 2))
            self.labels_resultado['y'].config(text=round(y_inter, 2))
            self.labels_resultado['z'].config(text=round(5*x_inter + 8*y_inter, 2))

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error: {e}")

class Pagina2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(width=1000, height=650, bg="#dad2d8", bd=5)

        # Título de la página
        tk.Label(self, text="Matrices Sparse", font=("Times New Roman", 20, "bold", "underline"), bg="#dad2d8").pack(pady=20)

        # Selección de método de representación
        tk.Label(self, text="Seleccione un método de representación:", font=("Times New Roman", 12), bg="#dad2d8").pack(pady=10)
        self.metodos = ["Implementación propia", "Estándar, CSC, CSR (NP)"]
        self.combo_metodos = ttk.Combobox(self, values=self.metodos, state="readonly", font=("Times New Roman", 12))
        self.combo_metodos.pack(pady=10)
        self.combo_metodos.current(0)
        self.combo_metodos.bind("<<ComboboxSelected>>", self.mostrar_entradas)

        # Frame para las entradas
        self.frame_entradas = tk.Frame(self, bg="#dad2d8")
        self.frame_entradas.pack(pady=10)

        # Botón para volver al inicio
        ttk.Button(self, text="Volver al Inicio", command=lambda: controller.mostrar_frame(Inicio),
                   style="Rounded.TButton").place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
    
        # Frame para resultado
        self.frame_result = tk.Frame(self, bg="#dad2d8")
        self.frame_result.pack(pady=10)

    def Respuesta1(self, nn=1000, mm=1000, den=0.3):

        for widget in self.frame_result.winfo_children():
            widget.destroy()

        def metodoPropio(n=nn, m=mm, densidad=den):
            matriz_aleatoria = generar_matriz_dispersa(n, m, densidad)
            matriz_aleatoriaCSC = MatrizDispersaCSC(matriz_aleatoria, forma=(n, m))
            tiempos = {}

            t_ini = perf_counter()
            suma_matriz(matriz_aleatoria, matriz_aleatoria)
            t_fin = perf_counter()
            tiempos["Suma"] = t_fin - t_ini

            t_ini = perf_counter()
            matriz_por_vector(matriz_aleatoria, [2] * m)
            t_fin = perf_counter()
            tiempos["Multiplicacion"] = t_fin - t_ini

            t_ini = perf_counter()
            matriz_aleatoriaCSC.sumar(matriz_aleatoriaCSC)
            t_fin = perf_counter()
            tiempos["SumaCSC"] = t_fin - t_ini

            t_ini = perf_counter()
            matriz_aleatoriaCSC.multiplicar_vector([2] * m)
            t_fin = perf_counter()
            tiempos["MultiplicacionCSC"] = t_fin - t_ini

            resultado_string = "Tiempos de ejecuión:\n"
            for op, t in tiempos.items():
                resultado_string += f"{op}: {t:.6f} seconds\n"
            return resultado_string

        respuesta = metodoPropio(nn, mm, den)
        texto_new = tk.Label(self.frame_result, text=respuesta, font=("Times New Roman", 13), bg="#dad2d8")
        texto_new.pack(pady=10)
            
    def Respuesta2(self, n, m, densidad):
        for widget in self.frame_result.winfo_children():
            widget.destroy()

        def benchmark(nn=n, mm=m, densidad=0.2):

            def generate_sparse_matrix(n=nn, m=mm, density=densidad, min_val=1, max_val=10):
                """Genera una matriz sparse con una densidad cualquiera."""
                size = int(n * m * density)
                rows = np.random.randint(0, n, size)
                cols = np.random.randint(0, m, size)
                values = np.random.randint(min_val, max_val, size)

                dense_matrix = np.zeros((n, m), dtype=int)
                dense_matrix[rows, cols] = values

                csc_matrix = scp.csc_matrix(dense_matrix)
                csr_matrix = scp.csr_matrix(dense_matrix)

                return dense_matrix, csc_matrix, csr_matrix

            def add_normal(A, B):
                return A + B

            def add_csc(A, B):
                return A + B

            def add_csr(A, B):
                return A + B

            def multiply_normal(A, B):
                return np.dot(A, B)

            def multiply_csc(A, B):
                return (A @ B).tocsc()

            def multiply_csr(A, B):
                return (A @ B).tocsr()
            
            A_dense, A_csc, A_csr = generate_sparse_matrix(nn, mm, densidad)
            B_dense, B_csc, B_csr = generate_sparse_matrix(nn, mm, densidad)

            tiempos = {}  # Diccionario de tiempos

            tiempos['dense_add'] = perf_counter()
            add_normal(A_dense, B_dense)
            tiempos['dense_add'] = perf_counter() - tiempos['dense_add']

            tiempos['csc_add'] = perf_counter()
            add_csc(A_csc, B_csc)
            tiempos['csc_add'] = perf_counter() - tiempos['csc_add']

            tiempos['csr_add'] = perf_counter()
            add_csr(A_csr, B_csr)
            tiempos['csr_add'] = perf_counter() - tiempos['csr_add']

            tiempos['dense_mult'] = perf_counter()
            multiply_normal(A_dense, B_dense)
            tiempos['dense_mult'] = perf_counter() - tiempos['dense_mult']

            tiempos['csc_mult'] = perf_counter()
            multiply_csc(A_csc, B_csc)
            tiempos['csc_mult'] = perf_counter() - tiempos['csc_mult']

            tiempos['csr_mult'] = perf_counter()
            multiply_csr(A_csr, B_csr)
            tiempos['csr_mult'] = perf_counter() - tiempos['csr_mult']

            resultado_string = ""
            for op, t in tiempos.items():
                resultado_string += f"{op}: {t:.6f} seconds\n"
            return resultado_string

        respuesta = benchmark(n, m, densidad)
        texto2 = tk.Label(self.frame_result, text=respuesta, font=("Times New Roman", 13), bg="#dad2d8")
        texto2.pack(pady=10)

    def mostrar_entradas(self, event):
        # Limpiar el frame de entradas
        for widget in self.frame_entradas.winfo_children():
            widget.destroy()

        for widget in self.frame_result.winfo_children():
            widget.destroy()

        metodo_seleccionado = self.combo_metodos.get()

        if metodo_seleccionado == "Implementación propia":
           # Entrada para el valor de n
            tk.Label(self.frame_entradas, text="➡︎ Ingrese el valor de n (< 30000):", font=("Times New Roman", 13), bg="#dad2d8").pack(pady=10)
            self.entry_n = tk.Entry(self.frame_entradas, width=10)
            self.entry_n.pack(pady=10, padx=10)

            # Entrada para el valor de m
            tk.Label(self.frame_entradas, text="➡︎ Ingrese el valor de m (< 30000):", font=("Times New Roman", 13), bg="#dad2d8").pack(pady=10)
            self.entry_m = tk.Entry(self.frame_entradas, width=10)
            self.entry_m.pack(pady=10, padx=10)

            # Entrada para la densidad
            tk.Label(self.frame_entradas, text="➡︎ Ingrese la densidad (0.1 - 0.8):", font=("Times New Roman", 13), bg="#dad2d8").pack(pady=10)
            self.entry_densidad = tk.Entry(self.frame_entradas, width=10)
            self.entry_densidad.pack(pady=10, padx=10)

            ttk.Button(self.frame_entradas, text="Ejecutar", command=lambda: self.Respuesta1(int(self.entry_n.get()), int(self.entry_m.get()), float(self.entry_densidad.get())), style="Rounded.TButton").pack(pady=5)

        elif metodo_seleccionado == "Estándar, CSC, CSR (NP)":
           # Entrada para el valor de n
            tk.Label(self.frame_entradas, text="➡︎ Ingrese el valor de n (< 30000):", font=("Times New Roman", 13), bg="#dad2d8").pack(pady=10)
            self.entry_n = tk.Entry(self.frame_entradas, width=10)
            self.entry_n.pack(pady=10, padx=10)

            # Entrada para el valor de m
            tk.Label(self.frame_entradas, text="➡︎ Ingrese el valor de m (< 30000):", font=("Times New Roman", 13), bg="#dad2d8").pack(pady=10)
            self.entry_m = tk.Entry(self.frame_entradas, width=10)
            self.entry_m.pack(pady=10, padx=10)

            # Entrada para la densidad
            tk.Label(self.frame_entradas, text="➡︎ Ingrese la densidad (0.1 - 0.8):", font=("Times New Roman", 13), bg="#dad2d8").pack(pady=10)
            self.entry_densidad = tk.Entry(self.frame_entradas, width=10)
            self.entry_densidad.pack(pady=10, padx=10)
            
            ttk.Button(self.frame_entradas, text="Ejecutar", command=lambda: self.Respuesta2(int(self.entry_n.get()), int(self.entry_m.get()), float(self.entry_densidad.get())), style="Rounded.TButton").pack(pady=5)

class Pagina3(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(width=1000, height=650, bg="#dad2d8", bd=5)
        title_P3 = tk.Label(self, text="Expansión en Series de Taylor")
        title_P3.config(fg="black", bg="#dad2d8", font=("Times New Roman", 20, "bold", "underline"))
        title_P3.pack(pady=20)

        # Definición de las funciones disponibles
        self.funciones = {
            "sin(x)": sp.sin(sp.Symbol('x')),
            "cos(x)": sp.cos(sp.Symbol('x')),
            "e^x": sp.exp(sp.Symbol('x')),
            "ln(x+1)": sp.ln(sp.Symbol('x')+1),
            "x^2": sp.Symbol('x')**2
        }

        self.funcion_seleccionada = tk.StringVar(value="sin(x)")

        # Frame para los controles
        frame_controles = tk.Frame(self, bg="#dad2d8")
        frame_controles.pack(pady=10)

        # Radiobuttons para seleccionar la función
        tk.Label(frame_controles, text="Seleccione una función:", font=("Times New Roman", 14, "bold"), bg="#dad2d8").grid(row=0, column=0, columnspan=2)
        for i, (nombre, _) in enumerate(self.funciones.items()):
            tk.Radiobutton(frame_controles, text=nombre, variable=self.funcion_seleccionada, value=nombre, font=("Times New Roman", 14), bg="#dad2d8").grid(row=i+1, column=0, sticky="w")

        # Entradas para la cantidad de términos y el punto de expansión
        tk.Label(frame_controles, text="Cantidad de términos:", font=("Times New Roman", 13, "bold"), bg="#dad2d8").grid(row=0, column=3, padx=10)
        self.entrada_terminos = tk.Entry(frame_controles, width=5)
        self.entrada_terminos.grid(row=0, column=4, padx=10)

        tk.Label(frame_controles, text="Punto de expansión (a):", font=("Times New Roman", 13, "bold"), bg="#dad2d8").grid(row=1, column=3, padx=10)
        self.entrada_punto = tk.Entry(frame_controles, width=5)
        self.entrada_punto.grid(row=1, column=4, padx=10)

        # Botón para generar la gráfica
        ttk.Button(frame_controles, text="Generar Gráfica", command=self.generar_grafica, style="Rounded.TButton").grid(row=0, column=6, rowspan=2, padx=10, pady=5, sticky="w")

        # Label para mostrar el polinomio de Taylor
        self.label_taylor = tk.Label(self, text="", font=("Times New Roman", 14), fg="black", bg="#dad2d8", wraplength=650, justify="left")
        self.label_taylor.pack(pady=5)

        # Frame para la gráfica
        self.frame_grafica = tk.Frame(self, bg="#dad2d8")
        self.frame_grafica.pack(pady=10)

        ttk.Button(self, text="Volver al Inicio", command=lambda: controller.mostrar_frame(Inicio),
                   style="Rounded.TButton").place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

    def generar_grafica(self):
        """ Genera la gráfica de la función original y su aproximación de Taylor """
        try:
            n = int(self.entrada_terminos.get())
            a = float(self.entrada_punto.get())
            x = sp.Symbol('x')

            # Obtener la función seleccionada
            funcion_str = self.funcion_seleccionada.get()
            funcion = self.funciones[funcion_str]

            f = sp.sympify(funcion)
            
            # Expansión en Series de Taylor
            taylor = f.subs(x, a)       # Primer término
            for i in range(1, n):
                taylor += f.diff(x, i).subs(x, a) * (x - a)**i / sp.factorial(i)

            # Mostrar el polinomio de Taylor
            # taylor_simple = str(taylor_str)
            self.label_taylor.config(text=f"Polinomio de Taylor de grado {n}:\n{taylor}")
            
            # Convertir a función numérica
            f_taylor = sp.lambdify(x, taylor, modules=["numpy"])
            f_original = sp.lambdify(x, f, modules=["numpy"])

            # Crear el rango de valores de x
            x_vals = np.linspace(a-3, a+3, 400)
            y_vals_original = f_original(x_vals)
            y_vals_taylor = f_taylor(x_vals)

            # Limpiar el frame de la gráfica si ya existe
            for widget in self.frame_grafica.winfo_children():
                widget.destroy()

            # Crear la figura de Matplotlib
            fig = Figure(figsize=(5, 4), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(x_vals, y_vals_original, label=f"Función Original: {funcion_str}", color="blue")
            ax.plot(x_vals, y_vals_taylor, label=f"Aproximación de Taylor (n={n})", color="red", linestyle="dashed")
            ax.axvline(a, color="gray", linestyle="dotted", label="Punto de Expansión a")
            ax.legend()
            ax.set_title("Expansión en Series de Taylor")

            # Mostrar la gráfica en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.frame_grafica)
            canvas.draw()
            canvas.get_tk_widget().pack()

        except Exception as e:
            print(f"Error: {e}")
            tk.messagebox.showerror("Error", "Ocurrió un error al generar la gráfica. Verifica los datos ingresados.")
            return

class Pagina4(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(width=1000, height=650, bg="#dad2d8", bd=5)
        
        self.crear_interfaz_principal()

    def crear_interfaz_principal(self):
        """Crea la interfaz de la página 4 con sus botones."""
        for widget in self.winfo_children():
            widget.destroy()

        tk.Label(self, text="Optimización sin Restricciones", font=("Times New Roman", 20, "bold", "underline"), bg="#dad2d8").pack(pady=10)
        ttk.Button(self, text="Algoritmo de Newton", command=self.abrir_ventana_newton, style="Rounded.TButton").pack(pady=20)
        ttk.Button(self, text="Gradiente Descendente", command=self.abrir_ventana_gradiente, style="Rounded.TButton").pack(pady=20)
        ttk.Button(self, text="Nelder-Mead", command=self.abrir_ventana_nelder_mead, style="Rounded.TButton").pack(pady=20)

        ttk.Button(self, text="Volver al Inicio", command=lambda: self.controller.mostrar_frame(Inicio),
            style="Rounded.TButton").place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)


    def abrir_ventana_newton(self):
        # Destruir elementos anteriores de la ventana
        for widget in self.winfo_children():
            widget.destroy()

        # Crear nuevo frame
        nuevo_frame = tk.Frame(self, bg="#dad2d8")
        nuevo_frame.pack(fill="both", expand=True)

        tk.Label(nuevo_frame, text="Algoritmo de Newton", font=("Times New Roman", 16, "bold"), bg="#dad2d8").pack(pady=20)

        # Entrada para la función f(x)
        tk.Label(nuevo_frame, text="Función f(x):", bg="#dad2d8").pack(pady=5)
        entry_func = tk.Entry(nuevo_frame, width=30)
        entry_func.pack(pady=5)

        # Entrada para la derivada f'(x)
        tk.Label(nuevo_frame, text="Derivada f'(x):", bg="#dad2d8").pack(pady=5)
        entry_deriv = tk.Entry(nuevo_frame, width=30)
        entry_deriv.pack(pady=5)

        # Entrada para x0 (valor inicial)
        tk.Label(nuevo_frame, text="Valor inicial x0:", bg="#dad2d8").pack(pady=5)
        entry_x0 = tk.Entry(nuevo_frame, width=15)
        entry_x0.pack(pady=5)

        # Entrada para epsilon (criterio de parada)
        tk.Label(nuevo_frame, text="Epsilon (criterio de parada):", bg="#dad2d8").pack(pady=5)
        entry_epsilon = tk.Entry(nuevo_frame, width=15)
        entry_epsilon.pack(pady=5)

        # Entrada para el número máximo de iteraciones
        tk.Label(nuevo_frame, text="Máximo de iteraciones:", bg="#dad2d8").pack(pady=5)
        entry_max_iter = tk.Entry(nuevo_frame, width=15)
        entry_max_iter.pack(pady=5)

        # Función para ejecutar el algoritmo de Newton
        def ejecutar_newton():
            try:
                # Obtener valores de los widgets
                func_str = entry_func.get()
                deriv_str = entry_deriv.get()
                x0 = float(entry_x0.get())
                epsilon = float(entry_epsilon.get())
                max_iter = int(entry_max_iter.get())

                # Convertir las funciones a expresiones ejecutables
                f = lambda x: eval(func_str, {"np": np, "x": x})
                Df = lambda x: eval(deriv_str, {"np": np, "x": x})

            except Exception as e:
                tk.messagebox.showerror("Error", f"Entrada inválida: {e}")
                return

            # Ejecutar el método de Newton
            def newton(f, Df, x0, epsilon, max_iter):
                xn = x0
                iter_data = []
                start_time = time.time()

                for n in range(max_iter):
                    fxn = f(xn)
                    if abs(fxn) < epsilon:
                        end_time = time.time()
                        return xn, n, iter_data, end_time - start_time

                    Dfxn = Df(xn)
                    if Dfxn == 0:
                        return None, n, iter_data, time.time() - start_time

                    correction = fxn / Dfxn
                    iter_data.append((n, xn, fxn, -correction))
                    xn = xn - correction

                return None, max_iter, iter_data, time.time() - start_time

            # Ejecutar el algoritmo de Newton
            raiz, iteraciones, iter_data, tiempo_ejecucion = newton(f, Df, x0, epsilon, max_iter)

            # Ocultar el frame de entrada y mostrar los resultados
            nuevo_frame.pack_forget()

            resultado_frame = tk.Frame(self, bg="#dad2d8")
            resultado_frame.pack(fill="both", expand=True)

            tk.Label(resultado_frame, text="Resultados del Algoritmo de Newton", font=("Times New Roman", 16), bg="#dad2d8").pack(pady=20)

            # Tabla para mostrar iteraciones
            tree = ttk.Treeview(resultado_frame, columns=("Iteración", "x_n", "f(x_n)", "Corrección"), show="headings")
            tree.heading("Iteración", text="Iteración")
            tree.heading("x_n", text="x_n")
            tree.heading("f(x_n)", text="f(x_n)")
            tree.heading("Corrección", text="Corrección")
            tree.pack(pady=10)

            for row in iter_data:
                tree.insert("", "end", values=row)

            # Mostrar resultados finales
            tk.Label(resultado_frame, text=f"Raíz aproximada: {raiz:.6f}" if raiz is not None else "No se encontró solución", bg="#dad2d8", font=("Arial", 12)).pack(pady=5)
            tk.Label(resultado_frame, text=f"Iteraciones realizadas: {iteraciones}", bg="#dad2d8", font=("Arial", 12)).pack(pady=5)
            tk.Label(resultado_frame, text=f"Tiempo de ejecución: {tiempo_ejecucion:.6f} segundos", bg="#dad2d8", font=("Arial", 12)).pack(pady=5)

            # Botón para volver a la entrada
            ttk.Button(resultado_frame, text="Volver", command=self.crear_interfaz_principal, style="Rounded.TButton").pack(pady=10)

        # Botón para ejecutar el algoritmo
        ttk.Button(nuevo_frame, text="Ejecutar", command=ejecutar_newton, style="Rounded.TButton").pack(pady=20)

        # Botón para volver al menú principal
        ttk.Button(nuevo_frame, text="Volver", command=self.crear_interfaz_principal, style="Rounded.TButton").pack(pady=10)


    def abrir_ventana_gradiente(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        nuevo_frame = tk.Frame(self, bg="#dad2d8")
        nuevo_frame.pack(fill="both", expand=True)
        
        tk.Label(nuevo_frame, text="Gradiente Descendente", font=("Times New Roman", 16, "bold"), bg="#dad2d8").pack(pady=20)
        
        # Frame para los valores de entrada
        frame_entrada = tk.Frame(nuevo_frame, bg="#dad2d8")
        frame_entrada.pack(pady=10)

        tk.Label(frame_entrada, text="Ingrese la función f(x):", bg="#dad2d8").pack()
        entry_funcion = tk.Entry(frame_entrada)
        entry_funcion.pack()

        tk.Label(frame_entrada, text="Ingrese la derivada f'(x):", bg="#dad2d8").pack()
        entry_gradiente = tk.Entry(frame_entrada)
        entry_gradiente.pack()

        tk.Label(frame_entrada, text="Ingrese la tasa de aprendizaje:", bg="#dad2d8").pack()
        entry_learning_rate = tk.Entry(frame_entrada)
        entry_learning_rate.pack()

        tk.Label(frame_entrada, text="Ingrese el valor inicial x:", bg="#dad2d8").pack()
        entry_x_inicial = tk.Entry(frame_entrada)
        entry_x_inicial.pack()

        tk.Label(frame_entrada, text="Ingrese el número de iteraciones:", bg="#dad2d8").pack()
        entry_epochs = tk.Entry(frame_entrada)
        entry_epochs.pack()

        # Función para ejecutar el algoritmo y mostrar las gráficas
        def ejecutar_gradiente():
            # Obtener los valores ingresados
            learning_rate = float(entry_learning_rate.get())
            x = float(entry_x_inicial.get())
            epochs = int(entry_epochs.get())

            # Eliminar el frame de entrada
            frame_entrada.destroy()

            # Definir la función y su gradiente de forma estática (por ahora)
            def f(x):
                return x**2 + 2*x + 1

            def gradient(x):
                return 2*x + 2

            # Listas para almacenar valores
            x_values = [x]
            y_values = [f(x)]

            # Algoritmo de gradiente descendente
            for _ in range(epochs):
                x = x - learning_rate * gradient(x)
                x_values.append(x)
                y_values.append(f(x))

            # Rango para graficar la función
            x_range = np.linspace(-6, 4, 100)
            y_range = f(x_range)

            # Mínimo encontrado
            x_min = x_values[-1]
            y_min = f(x_min)

            # Crear la figura para Matplotlib
            fig = Figure(figsize=(12, 5))

            # Primera gráfica: Variación de f(x)
            ax1 = fig.add_subplot(121)
            ax1.plot(range(len(y_values)), y_values, marker='o', linestyle='-', color='b', label='Valor de f(x)')
            ax1.set_xlabel('Iteraciones')
            ax1.set_ylabel('f(x)')
            ax1.set_title('Variación de y en el Gradiente Descendente')
            ax1.legend()
            ax1.grid()

            # Segunda gráfica: Función y mínimo encontrado
            ax2 = fig.add_subplot(122)
            ax2.plot(x_range, y_range, label='f(x) = x² + 2x + 1', color='g')
            ax2.scatter(x_min, y_min, color='r', zorder=3, label=f'Mínimo ({x_min:.2f}, {y_min:.2f})')
            ax2.set_xlabel('x')
            ax2.set_ylabel('f(x)')
            ax2.set_title('Función y Mínimo Encontrado')
            ax2.legend()
            ax2.grid()

            # Frame para las gráficas
            frame_graficas = tk.Frame(nuevo_frame, bg="#dad2d8")
            frame_graficas.pack(fill="both", expand=True, pady=10)

            # Integrar la figura en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=frame_graficas)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Botón para volver a la interfaz principal
            ttk.Button(nuevo_frame, text="Volver", command=self.crear_interfaz_principal, style="Rounded.TButton").pack(pady=20)

        # Botón para ejecutar el algoritmo
        ttk.Button(frame_entrada, text="Ejecutar", command=ejecutar_gradiente, style="Rounded.TButton").pack(pady=10)

        # Botón para volver a la interfaz principal
        ttk.Button(nuevo_frame, text="Volver", command=self.crear_interfaz_principal, style="Rounded.TButton").pack(pady=20)





    def abrir_ventana_nelder_mead(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        nuevo_frame = tk.Frame(self, bg="#dad2d8")
        nuevo_frame.pack(fill="both", expand=True)
        
        tk.Label(nuevo_frame, text="Nelder-Mead", font=("Times New Roman", 16, "bold"), bg="#dad2d8").pack(pady=20)

        # Entrada para los valores iniciales
        tk.Label(nuevo_frame, text="Valores iniciales (separados por comas):", bg="#dad2d8").pack(pady=5)
        entry_x0 = ttk.Entry(nuevo_frame, width=30)
        entry_x0.pack(pady=5)

        # Entrada para la función a minimizar
        tk.Label(nuevo_frame, text="Función f(x):", bg="#dad2d8").pack(pady=5)
        entry_func = ttk.Entry(nuevo_frame, width=30)
        entry_func.pack(pady=5)

        # Botón para ejecutar el algoritmo
        ttk.Button(nuevo_frame, text="Ejecutar", command=lambda: ejecutar_nelder_mead(entry_x0, entry_func, nuevo_frame), style="Rounded.TButton").pack(pady=10)

        # Botón para volver
        ttk.Button(nuevo_frame, text="Volver", command=self.crear_interfaz_principal, style="Rounded.TButton").pack(pady=20)

        def ejecutar_nelder_mead(entry_x0, entry_func, frame_actual):
            """Ejecuta el algoritmo de Nelder-Mead, oculta los widgets y muestra las gráficas."""
            # Obtener valores antes de destruir el frame
            valores_x0 = entry_x0.get()
            funcion_texto = entry_func.get()

            # Validación de los valores ingresados
            try:
                x0 = [float(val) for val in valores_x0.split(',')]
            except ValueError:
                tk.Label(frame_actual, text="Error: Ingrese valores iniciales válidos.", fg="red", bg="#dad2d8").pack()
                return

            # Evaluar la función ingresada
            try:
                func = lambda x: eval(funcion_texto, {"np": np, "x": x})
            except Exception:
                tk.Label(frame_actual, text="Error: Ingrese una función válida.", fg="red", bg="#dad2d8").pack()
                return

            # Ocultar frame actual
            for widget in frame_actual.winfo_children():
                widget.destroy()

            # Crear el rango de valores para graficar
            x = np.arange(-2, 2, 0.01)
            y = np.vectorize(func)(x)

            # Ejecutar el algoritmo para cada punto inicial
            resultados = []
            for x_start in x0:
                result = minimize(func, x_start, method="nelder-mead")
                resultados.append((result.x[0], result.fun))

            # Crear nueva figura de Matplotlib
            fig, ax = plt.subplots(len(x0), figsize=(4, 2 * len(x0)))
            if len(x0) == 1:
                ax = [ax]  # Asegurar que ax sea iterable

            for i, (x_start, (x_min, y_min)) in enumerate(zip(x0, resultados)):
                ax[i].plot(x, y, label="f(x)")
                ax[i].plot(x_min, y_min, 'sr', label="Mínimo encontrado")
                ax[i].set_title(f"Inicio en {x_start}")
                ax[i].legend(loc='best', fancybox=True, shadow=True)
                ax[i].grid()

            plt.tight_layout()

            # Mostrar la gráfica en Tkinter
            canvas = FigureCanvasTkAgg(fig, master=frame_actual)
            canvas.draw()
            canvas.get_tk_widget().pack()

            # Mostrar resultados numéricos en Tkinter
            for i, x_start in enumerate(x0):
                result = minimize(func, x_start, method="nelder-mead")
                resultado_texto = f"Inicio en {x_start}: mínimo en x = {result.x[0]:.6f}, f(x) = {result.fun:.6f}"
                tk.Label(frame_actual, text=resultado_texto, font=("Times New Roman", 12), bg="#dad2d8").pack(pady=5)

            # Botón para volver
            ttk.Button(frame_actual, text="Volver", command=self.crear_interfaz_principal, style="Rounded.TButton").pack(pady=20)


if __name__ == "__main__":
    app = Aplicacion()
    center_window_method(app, 1000, 650)
    app.mainloop()
