# Ventana del mesero: toma pedidos, ve el menú y actualiza el estado de sus pedidos.
import tkinter as tk

from menu import abrir_menu
from ventana_mesero import abrir_nuevo_pedido, abrir_mis_pedidos


def abrir_ventana_mesero(nombre_usuario, ventana):
    ventana_principal = tk.Toplevel(ventana)
    ventana_principal.title("Restaurante")
    ventana_principal.geometry("800x600")
    ventana_principal.configure(bg="snow")

    tk.Label(
        ventana_principal,
        text=f"Bienvenido mesero, {nombre_usuario}",
        font=("Arial", 24),
        bg="snow",
    ).pack(pady=30)

    tk.Label(
        ventana_principal,
        text="¿Qué quieres hacer?",
        font=("Arial", 14),
        bg="snow",
    ).pack(pady=10)

    # Cada botón abre una ventana hija. Con lambda le pasamos los datos que necesita.
    tk.Button(
        ventana_principal, text="Nuevo pedido", font=("Arial", 12), width=22,
        command=lambda: abrir_nuevo_pedido(ventana_principal, nombre_usuario),
    ).pack(pady=8)

    tk.Button(
        ventana_principal, text="Mis pedidos", font=("Arial", 12), width=22,
        command=lambda: abrir_mis_pedidos(ventana_principal, nombre_usuario),
    ).pack(pady=8)

    tk.Button(
        ventana_principal, text="Ver menú", font=("Arial", 12), width=22,
        command=lambda: abrir_menu(ventana_principal, es_admin=False),
    ).pack(pady=8)

    tk.Button(
        ventana_principal,
        text="Cerrar sesión",
        command=ventana_principal.destroy,
    ).pack(pady=20)

    return ventana_principal
