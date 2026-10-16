import tkinter as tk
from tkinter import messagebox
import funciones_login
from menu import abrir_menu


ventana = tk.Tk()
ventana.title("Login-Restaurante")
ventana.geometry("800x600")
ventana.configure(bg="snow")


def iniciar_sesion():
    usuario = entry1.get()
    contraseña = entry2.get()

    if funciones_login.login(usuario, contraseña):
        abrir_ventana_principal(usuario)
    elif funciones_login.loginC(usuario,contraseña):
        abrir_ventana_cliente(usuario)

    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")
def abrir_ventana_principal(usuario):
    ventana_principal = tk.Toplevel(ventana)
    ventana_principal.title("Restaurante")
    ventana_principal.geometry("800x600")
    ventana_principal.configure(bg="snow")

    tk.Label(
        ventana_principal,
        text=f"Bienvenido, {usuario}",
        font=("Arial", 24),
        bg="snow",
    ).pack(pady=30)

    tk.Button(
        ventana_principal,
        text="Ver menú",
        command=lambda: abrir_menu(ventana_principal, es_admin=(usuario == "admin")),
    ).pack(pady=10)

    tk.Button(
        ventana_principal,
        text="Cerrar sesión",
        command=ventana_principal.destroy,
    ).pack(pady=10)

def abrir_ventana_cliente(usuario):
    ventana_principal = tk.Toplevel(ventana)
    ventana_principal.title("Restaurante")
    ventana_principal.geometry("800x600")
    ventana_principal.configure(bg="snow")

    tk.Label(
        ventana_principal,
        text=f"Bienvenido cliente, {usuario}",
        font=("Arial", 24),
        bg="snow",
    ).pack(pady=30)


    tk.Button(
        ventana_principal,
        text="Cerrar sesión",
        command=ventana_principal.destroy,
    ).pack(pady=10)

frame = tk.Frame(master=ventana, bg="snow")
frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

label=tk.Label(
    frame, 
    text=f"Bienvenido al Restaurante",
    font=("Arial", 24),
    bg="snow",)
label.pack(pady=12,padx=10)

tk.Label(frame, text="Usuario", bg="snow").pack(pady=(12, 0))
entry1 = tk.Entry(frame)
entry1.pack(pady=6, padx=10)

tk.Label(frame, text="Contraseña", bg="snow").pack(pady=(12, 0))
entry2 = tk.Entry(frame, show="*")
entry2.pack(pady=6, padx=10)


button=tk.Button(
    frame,
    text="Iniciar Sesión",
    command=iniciar_sesion)
button.pack(pady=12, padx=10)





ventana.mainloop()