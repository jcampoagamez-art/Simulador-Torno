import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import pandas as pd
import datetime

class SimuladorTorno:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Operaciones de Torno")
        self.root.geometry("1000x650")
        self.root.configure(bg="#ECECEC")

        # --- Colores y fuentes ---
        self.color_primario = "#2C3E50"
        self.color_secundario = "#34495E"
        self.color_boton = "#1ABC9C"
        self.color_fondo = "#ECECEC"
        self.fuente_titulo = ("Segoe UI", 18, "bold")
        self.fuente_texto = ("Segoe UI", 11)

        # --- Variables ---
        self.tipo_operacion = tk.StringVar()
        self.material = tk.StringVar()
        self.diametro_inicial = tk.DoubleVar()
        self.diametro_final = tk.DoubleVar()
        self.longitud = tk.DoubleVar()
        self.vc = tk.DoubleVar()
        self.f = tk.DoubleVar()
        self.ap = tk.DoubleVar()
        self.resultados = {}

        # Tabla de velocidades automáticas
        self.velocidades = {
            "Desbaste": {"Acero 1020": 28, "Acero inoxidable": 8, "Metal Monel": 15},
            "Acabado": {"Acero 1020": 40, "Acero inoxidable": 14, "Metal Monel": 18},
            "Careado": {"Acero 1020": 28, "Acero inoxidable": 8, "Metal Monel": 18}
        }

        # --- Título ---
        tk.Label(root, text="Simulador de Operaciones de Torno",
                 font=self.fuente_titulo, bg=self.color_primario, fg="white", pady=15).pack(fill="x")

        # --- Frame principal dividido ---
        frame_main = tk.Frame(root, bg=self.color_fondo)
        frame_main.pack(fill="both", expand=True, padx=10, pady=10)

        # --- IZQUIERDA ---
        frame_left = tk.Frame(frame_main, bg=self.color_fondo)
        frame_left.pack(side="left", fill="y", padx=10, pady=10)

        frame_inputs = tk.LabelFrame(frame_left, text="Datos de entrada", bg=self.color_fondo,
                                     font=("Segoe UI", 12, "bold"), fg=self.color_primario, padx=10, pady=10)
        frame_inputs.pack(fill="x")

        etiquetas = [
            "Tipo de operación", "Material", "Diámetro inicial (mm)", "Diámetro final (mm)",
            "Longitud de corte (mm)", "Velocidad de corte Vc (m/min)",
            "Avance por revolución f (mm/rev)", "Profundidad de corte ap (mm)"
        ]

        for i, texto in enumerate(etiquetas):
            tk.Label(frame_inputs, text=texto + ":", bg=self.color_fondo,
                     font=self.fuente_texto).grid(row=i, column=0, sticky="e", pady=5, padx=5)

        # --- Entradas con detección de selección ---
        ttk.Combobox(frame_inputs, textvariable=self.tipo_operacion,
                     values=["Desbaste", "Acabado", "Careado"], width=20,
                     state="readonly").grid(row=0, column=1)
        ttk.Combobox(frame_inputs, textvariable=self.material,
                     values=["Acero 1020", "Acero inoxidable", "Metal Monel"], width=20,
                     state="readonly").grid(row=1, column=1)

        # Detectar cambio para autocompletar velocidad
        self.tipo_operacion.trace("w", self.actualizar_velocidad)
        self.material.trace("w", self.actualizar_velocidad)

        tk.Entry(frame_inputs, textvariable=self.diametro_inicial, width=22).grid(row=2, column=1)
        tk.Entry(frame_inputs, textvariable=self.diametro_final, width=22).grid(row=3, column=1)
        tk.Entry(frame_inputs, textvariable=self.longitud, width=22).grid(row=4, column=1)
        tk.Entry(frame_inputs, textvariable=self.vc, width=22).grid(row=5, column=1)
        tk.Entry(frame_inputs, textvariable=self.f, width=22).grid(row=6, column=1)
        tk.Entry(frame_inputs, textvariable=self.ap, width=22).grid(row=7, column=1)

        # --- Botones ---
        frame_botones = tk.Frame(frame_left, bg=self.color_fondo)
        frame_botones.pack(pady=20)
        estilo_boton = {"font": ("Segoe UI", 11, "bold"), "fg": "white", "width": 15, "height": 1, "relief": "flat"}

        tk.Button(frame_botones, text="Calcular", bg=self.color_boton,
                  command=self.calcular, **estilo_boton).pack(pady=5)
        tk.Button(frame_botones, text="Exportar a Excel", bg=self.color_secundario,
                  command=self.exportar_excel, **estilo_boton).pack(pady=5)

        # --- DERECHA: resultados ---
        frame_right = tk.LabelFrame(frame_main, text="Resultados", bg=self.color_fondo,
                                    font=("Segoe UI", 12, "bold"), fg=self.color_primario, padx=15, pady=10)
        frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.text_result = tk.Text(frame_right, wrap="word", font=("Consolas", 12),
                                   bg="#FAFAFA", height=25, width=55, state="disabled")
        self.text_result.pack(fill="both", expand=True, padx=5, pady=5)

        # Comentario final
        comentario = (
            "Este proyecto está delimitado únicamente para procesos en el torno, "
            "con los tipos de materiales propuestos en la ventana de arriba.\n"
            "Próximamente trabajaremos para agregarles más procesos de mecanizado :)"
        )
        tk.Label(root, text=comentario, font=("Segoe UI", 10, "italic"),
                 bg=self.color_fondo, fg="#555555", wraplength=900, justify="center").pack(pady=5)

    # --- Autocompletar velocidad ---
    def actualizar_velocidad(self, *args):
        operacion = self.tipo_operacion.get()
        material = self.material.get()
        if operacion in self.velocidades and material in self.velocidades[operacion]:
            self.vc.set(self.velocidades[operacion][material])

    # --- Calcular ---
    def calcular(self):
        try:
            Di = self.diametro_inicial.get()
            Df = self.diametro_final.get()
            L = self.longitud.get()
            Vc = self.vc.get()
            f = self.f.get()
            ap = self.ap.get()

            if any(v == 0 for v in [Di, Df, L, Vc, f, ap]):
                messagebox.showwarning("Datos incompletos", "Por favor, ingresa todos los valores numéricos.")
                return

            D_trabajo = (Di + Df) / 2
            N = (1000 * Vc) / (math.pi * D_trabajo)
            Vf = f * N
            T = L / Vf
            np = (Di - Df) / (2 * ap)
            Tt = np * T

            self.resultados = {
                "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Operación": self.tipo_operacion.get(),
                "Material": self.material.get(),
                "Vc (m/min)": Vc,
                "Diámetro inicial (mm)": Di,
                "Diámetro final (mm)": Df,
                "Longitud (mm)": L,
                "f (mm/rev)": f,
                "ap (mm)": ap,
                "N (rpm)": round(N, 2),
                "Vf (mm/min)": round(Vf, 2),
                "T (min)": round(T, 2),
                "n_p": round(np, 2),
                "Tt (min)": round(Tt, 2)
            }

            self.text_result.config(state="normal")
            self.text_result.delete("1.0", tk.END)
            self.text_result.insert(tk.END, f"{'='*45}\n   RESULTADOS DEL MECANIZADO\n{'='*45}\n\n")
            for k, v in self.resultados.items():
                self.text_result.insert(tk.END, f"{k:25}: {v}\n")
            self.text_result.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", f"Error al calcular:\n{e}")

    # --- Exportar a Excel ---
    def exportar_excel(self):
        if not self.resultados:
            messagebox.showwarning("Sin resultados", "Primero debes realizar un cálculo antes de exportar.")
            return
        try:
            ruta = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                filetypes=[("Archivos Excel", "*.xlsx")],
                                                title="Guardar resultados como")
            if not ruta:
                return
            df = pd.DataFrame([self.resultados])
            df.to_excel(ruta, index=False)
            messagebox.showinfo("Éxito", f"Archivo guardado correctamente:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorTorno(root)
    root.mainloop()