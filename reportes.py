import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


ARCHIVO_VENTAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ventas.json")

def cargar_datos_ventas():
    """Carga exclusivamente las ventas en un DataFrame de Pandas."""
    if os.path.exists(ARCHIVO_VENTAS):
        try:
            with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as f:
                ventas_raw = json.load(f)
        except Exception:
            ventas_raw = []
    else:
        ventas_raw = [
            {"id": 1, "hora": "12:30", "vendedor": "Brayan", "origen": "Salón", "total": 140.00, "pago": "Efectivo"},
            {"id": 2, "hora": "13:10", "vendedor": "Serghiño", "origen": "Delivery", "total": 65.00, "pago": "QR"},
        ]

    return pd.DataFrame(ventas_raw)


def abrir_reportes_financieros(ventana_padre):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Análisis de Rendimiento de Ventas")
    ventana.geometry("980x620")
    ventana.configure(bg="snow")

    tk.Label(ventana, text="Panel Estadístico de Ventas", font=("Arial", 20, "bold"), bg="snow").pack(pady=12)

    df_ventas = cargar_datos_ventas()

    if df_ventas.empty:
        tk.Label(ventana, text="No hay registros de ventas para generar análisis.", font=("Arial", 12), bg="snow").pack(pady=40)
        return ventana


    vendedor_top = df_ventas["vendedor"].mode()[0] if not df_ventas["vendedor"].empty else "N/A"
    total_vendedor = df_ventas[df_ventas["vendedor"] == vendedor_top]["total"].sum()

    pago_top = df_ventas["pago"].mode()[0] if not df_ventas["pago"].empty else "N/A"
    origen_top = df_ventas["origen"].mode()[0] if not df_ventas["origen"].empty else "N/A"


    marco_kpis = tk.Frame(ventana, bg="snow")
    marco_kpis.pack(fill=tk.X, padx=20, pady=5)

    def crear_tarjeta(parent, titulo, valor, subtitulo):
        card = tk.LabelFrame(parent, text=titulo, font=("Arial", 10, "bold"), bg="#f8f9fa", padx=10, pady=8)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(card, text=valor, font=("Arial", 14, "bold"), fg="#2c3e50", bg="#f8f9fa").pack(anchor="w")
        tk.Label(card, text=subtitulo, font=("Arial", 9), fg="#7f8c8d", bg="#f8f9fa").pack(anchor="w", pady=(2, 0))

    crear_tarjeta(marco_kpis, "VENDEDOR LÍDER", vendedor_top, f"Recaudado: Bs {total_vendedor:,.2f}")
    crear_tarjeta(marco_kpis, "MÉTODO DE PAGO TOP", pago_top, "Frecuencia más alta")
    crear_tarjeta(marco_kpis, "ORIGEN PRINCIPAL", origen_top, "Canal más seleccionado")

    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.8), dpi=100)
    fig.patch.set_facecolor("#fffafa")

    #Grafico 1:Barras
    conteo_pagos = df_ventas["pago"].value_counts()
    conteo_pagos.plot(kind="bar", ax=ax1, color=["#4e79a7", "#f28e2b", "#59a14f"], rot=0)
    ax1.set_title("Transacciones por Método de Pago", fontsize=10, fontweight="bold")
    ax1.set_xlabel("")
    ax1.set_ylabel("Cantidad")
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    #Grfico 2:Pastel
    conteo_origen = df_ventas["origen"].value_counts()
    conteo_origen.plot(
        kind="pie",
        ax=ax2,
        autopct="%1.1f%%",
        startangle=140,
        colors=["#76b7b2", "#edc948", "#b07aa1"],
        textprops={"fontsize": 9}
    )
    ax2.set_title("Distribución por Origen de Venta", fontsize=10, fontweight="bold")
    ax2.set_ylabel("")

    plt.tight_layout()

    #Acoplar en Tkinter
    marco_grafico = tk.Frame(ventana, bg="snow")
    marco_grafico.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    canvas = FigureCanvasTkAgg(fig, master=marco_grafico)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    #Botones de exportación con Pandas
    def exportar_csv():
        try:
            df_ventas.to_csv("reporte_ventas_puro.csv", index=False, encoding="utf-8-sig")
            messagebox.showinfo("Exportado", "Reporte de ventas exportado exitosamente como 'reporte_ventas_puro.csv'.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

    barra_botones = tk.Frame(ventana, bg="snow")
    barra_botones.pack(pady=10)
    tk.Button(barra_botones, text="Exportar reporte a CSV (Pandas)", command=exportar_csv, width=28).pack(side=tk.LEFT, padx=10)
    tk.Button(barra_botones, text="Cerrar", command=ventana.destroy, width=12).pack(side=tk.LEFT, padx=10)

    return ventana






