import tkinter as tk
from tkinter import messagebox
import administrador,pantalla_usuario,funciones_login
from menu import abrir_menu
from usuarios import abrir_usuarios

# estamos definiendo la ventana principal de la aplicación de login para el restaurante.
ventana = tk.Tk()
ventana.title("Login-Restaurante")
ventana.geometry("1200x760")
ventana.minsize(950, 620)
ventana.configure(bg="snow")


def iniciar_sesion():
    nombre_usuario = entry1.get().strip()
    contraseña = entry2.get()

    cuenta = funciones_login.login(nombre_usuario, contraseña)
    if cuenta is None:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos (o usuario inactivo)")
        return

    if cuenta["categoria"] == "Administrador":
        ventana_dashboard = administrador.abrir_ventana_principal(cuenta["nombre"], ventana)
    elif cuenta["categoria"] == "Mesero":
        ventana_dashboard = pantalla_usuario.abrir_ventana_mesero(cuenta["nombre"], ventana)
    else:
        messagebox.showinfo("Sin acceso", f"La categoría '{cuenta['categoria']}' no tiene acceso al sistema.")
        return

    ventana.withdraw()  # Oculta la ventana de login

    def volver_al_login(evento):
        
        if evento.widget is ventana_dashboard:
            entry1.delete(0, tk.END)
            entry2.delete(0, tk.END)
            ventana.deiconify()  # Muestra otra vez el login

    ventana_dashboard.bind("<Destroy>", volver_al_login)


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


def iniciar_aplicacion():
    ventana.mainloop()