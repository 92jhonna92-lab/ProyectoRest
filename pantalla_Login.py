import tkinter as tk
from tkinter import messagebox
import administrador,usuario,funciones_login
from menu import abrir_menu

# estamos definiendo la ventana principal de la aplicación de login para el restaurante.
ventana = tk.Tk()
ventana.title("Login-Restaurante")
ventana.geometry("1200x760")
ventana.minsize(950, 620)
ventana.configure(bg="snow")


def iniciar_sesion():
    nombre_usuario = entry1.get().strip()
    contraseña = entry2.get()

    if funciones_login.login(nombre_usuario, contraseña):
        ventana_dashboard=administrador.abrir_ventana_principal(nombre_usuario,ventana)
        ventana.withdraw()  # Oculta la ventana de login
    elif funciones_login.loginC(nombre_usuario,contraseña):
        ventana_dashboard=usuario.abrir_ventana_cliente(nombre_usuario,ventana)
        ventana.withdraw()  # Oculta la ventana de login

    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")
        return

    if ventana_dashboard is not None:
        ventana.withdraw()  # Oculta la ventana de login


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