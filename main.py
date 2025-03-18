import numpy as np
import sympy as sp
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import pylatex as pl
from sympy import *

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


    def mostrar_mensaje(self, mensaje):
        """ Muestra el mensaje debajo de los botones """
        self.hover_label.config(text=mensaje)

    def ocultar_mensaje(self, event):
        """ Oculta el mensaje cuando el mouse sale """
        self.hover_label.config(text="")
        
class Pagina1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(width=1000, height=650, bg="#dad2d8", bd=5)
        tk.Label(self, text="Página 1", font=("Times New Roman", 16)).pack(pady=20)
        ttk.Button(self, text="Volver al Inicio", command=lambda: controller.mostrar_frame(Inicio),
                   style="Rounded.TButton").place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

class Pagina2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.configure(width=1000, height=650, bg="#dad2d8", bd=5)
        tk.Label(self, text="Página 2", font=("Times New Roman", 16)).pack(pady=20)
        ttk.Button(self, text="Volver al Inicio", command=lambda: controller.mostrar_frame(Inicio),
                   style="Rounded.TButton").place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

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
        self.label_taylor = tk.Label(self, text="", font=("Times New Roman", 14), fg="black", bg="#dad2d8", wraplength=800, justify="left")
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
        self.configure(width=1000, height=650, bg="#dad2d8", bd=5)
        tk.Label(self, text="Página 4", font=("Times New Roman", 16)).pack(pady=20)
        ttk.Button(self, text="Volver al Inicio", command=lambda: controller.mostrar_frame(Inicio),
                   style="Rounded.TButton").place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)

if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
