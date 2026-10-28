import funciones_login
import tkinter as tk
from tkinter import messagebox
from menu import abrir_menu

def abrir_ventana_cliente(nombre_usuario,ventana):
    ventana_principal = tk.Toplevel(ventana)
    ventana_principal.title("Restaurante")
    ventana_principal.geometry("800x600")
    ventana_principal.configure(bg="snow")

    tk.Label(
        ventana_principal,
        text=f"Bienvenido cliente, {nombre_usuario}",
        font=("Arial", 24),
        bg="snow",
    ).pack(pady=30)

    tk.Label(
        ventana_principal,
        text="Consulta nuestro menú",
        font=("Arial", 14),
        bg="snow",
    ).pack(pady=15)

    tk.Button(
        ventana_principal,
        text="Ver menú",
        font=("Arial", 12),
        width=20,
        command=lambda: abrir_menu(
            ventana_principal,
            es_admin=False

        ),
    ).pack(pady=15)
    
 

    tk.Button(
        ventana_principal,
        text="Cerrar sesión",
        command=ventana_principal.destroy,
    ).pack(pady=10)

    return ventana_principal
