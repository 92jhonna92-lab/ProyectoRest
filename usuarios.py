 # Menu del restaurant con tkoonter

import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
 
ARCHIVO_USUARIOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.json")
CATEGORIAS_USUARIOS = ["Administrador", "Mesero", "Mascota"]

USUARIOS_INICIALES = [
    {"id": 1, "nombre": "Jorgito", "contraseña": "12345", "estado": "Activo", "categoria": "Mascota"},
    {"id": 2, "nombre": "Serghiño", "contraseña": "12345", "estado": "Inactivo", "categoria": "Administrador"},
    {"id": 3, "nombre": "Brayan", "contraseña": "12345", "estado": "Activo", "categoria": "Mesero"},
]

def guardar_usuarios(usuarios):
    with open(ARCHIVO_USUARIOS, "w", encoding="utf-8") as archivo:
        json.dump(usuarios, archivo, indent=4, ensure_ascii=False)

def cargar_usuarios():
    if not os.path.exists(ARCHIVO_USUARIOS):
        guardar_usuarios(USUARIOS_INICIALES)
        return [dict(p) for p in USUARIOS_INICIALES]
    try:
        with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []

def validar_usuario(nombre, contraseña, estado_texto, categoria, id_actual=None):
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre no puede estar vacío.")
    
    # Validar que el nombre no esté duplicado
    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["nombre"].lower() == nombre.lower() and (id_actual is None or u["id"] != id_actual):
            raise ValueError("Ya existe un usuario registrado con ese nombre.")

    contraseña = contraseña.strip()
    if len(contraseña) < 5:
        raise ValueError("La contraseña debe tener un mínimo de 5 caracteres.")
        
    estado = estado_texto.strip().capitalize()
    if estado not in ["Activo", "Inactivo"]:
        raise ValueError("El estado debe ser Activo o Inactivo.")
    if categoria not in CATEGORIAS_USUARIOS:
        raise ValueError("Elige una categoría válida.")
    return nombre, contraseña, estado, categoria

def agregar_usuario(nombre, contraseña, estado_texto, categoria):
    nombre, contraseña, estado, categoria = validar_usuario(nombre, contraseña, estado_texto, categoria)
    usuarios = cargar_usuarios()
    nuevo = {
        "id": max((p["id"] for p in usuarios), default=0) + 1,
        "nombre": nombre,
        "contraseña": contraseña,
        "estado": estado,
        "categoria": categoria,
    }
    usuarios.append(nuevo)
    guardar_usuarios(usuarios)
    return nuevo

def editar_usuario(id_producto, nombre, contraseña, estado_texto, categoria):
    nombre, contraseña, estado, categoria = validar_usuario(nombre, contraseña, estado_texto, categoria, id_actual=id_producto)
    usuarios = cargar_usuarios()
    for producto in usuarios:
        if producto["id"] == id_producto:
            producto["nombre"] = nombre
            producto["contraseña"] = contraseña
            producto["estado"] = estado
            producto["categoria"] = categoria
            guardar_usuarios(usuarios)
            return producto
    raise ValueError("El usuario ya no existe.")

def eliminar_usuario(id_producto):
    usuarios = cargar_usuarios()
    nuevo_usuarios = [p for p in usuarios if p["id"] != id_producto]
    if len(nuevo_usuarios) == len(usuarios):
        raise ValueError("Ese usuario ya no existe.")
    guardar_usuarios(nuevo_usuarios)
 
 
def abrir_usuarios(ventana_padre, es_admin=False):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Usuarios del restaurante")
    ventana.geometry("850x600")
    ventana.configure(bg="snow")

    tk.Label(ventana, text="Usuarios del Restaurante", font=("Arial", 24), bg="snow").pack(pady=15)

    barra = tk.Frame(ventana, bg="snow")
    barra.pack(pady=5)
    tk.Label(barra, text="Mostrar:", bg="snow").pack(side=tk.LEFT, padx=5)
    filtro = ttk.Combobox(barra, values=["todos"] + CATEGORIAS_USUARIOS, state="readonly", width=12)
    filtro.set("todos")
    filtro.pack(side=tk.LEFT)

    marco_tabla = tk.Frame(ventana, bg="snow")
    marco_tabla.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    tabla = ttk.Treeview(marco_tabla, columns=("id", "nombre", "estado", "categoria"), show="headings", height=10)
    tabla.heading("id", text="ID")
    tabla.heading("nombre", text="Nombre")
    tabla.heading("estado", text="Estado")
    tabla.heading("categoria", text="Categoría")
    tabla.column("id", width=50, anchor="center")
    tabla.column("nombre", width=300)
    tabla.column("estado", width=120, anchor="center")
    tabla.column("categoria", width=150, anchor="center")

    barra_scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra_scroll.set)
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refrescar():
        tabla.delete(*tabla.get_children())
        for p in cargar_usuarios():
            if filtro.get() != "todos" and p["categoria"] != filtro.get():
                continue
            tabla.insert("", tk.END, values=(p["id"], p["nombre"], p["estado"], p["categoria"].capitalize()))

    filtro.bind("<<ComboboxSelected>>", lambda evento: refrescar())

    if es_admin:
        crear_panel_admin_usuarios(ventana, tabla, refrescar)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
    refrescar()
    return ventana

def crear_panel_admin_usuarios(ventana, tabla, refrescar):
    panel = tk.LabelFrame(ventana, text="Administrar usuarios", bg="snow", padx=10, pady=10)
    panel.pack(padx=20, pady=5, fill=tk.X)

    tk.Label(panel, text="Nombre", bg="snow").grid(row=0, column=0, padx=5)
    entrada_nombre = tk.Entry(panel, width=20)
    entrada_nombre.grid(row=1, column=0, padx=5, pady=5)

    tk.Label(panel, text="Contraseña (mín. 5)", bg="snow").grid(row=0, column=1, padx=5)
    entrada_password = tk.Entry(panel, width=15, show="*")
    entrada_password.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(panel, text="Estado", bg="snow").grid(row=0, column=2, padx=5)
    combo_estado = ttk.Combobox(panel, values=["Activo", "Inactivo"], state="readonly", width=10)
    combo_estado.grid(row=1, column=2, padx=5, pady=5)

    tk.Label(panel, text="Categoría", bg="snow").grid(row=0, column=3, padx=5)
    combo_categoria = ttk.Combobox(panel, values=CATEGORIAS_USUARIOS, state="readonly", width=12)
    combo_categoria.grid(row=1, column=3, padx=5, pady=5)

    def limpiar():
        entrada_nombre.delete(0, tk.END)
        entrada_password.delete(0, tk.END)
        combo_estado.set("")
        combo_categoria.set("")

    def id_seleccionado():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Primero selecciona un usuario de la tabla.")
            return None
        return int(tabla.item(seleccion[0])["values"][0])

    def al_seleccionar(evento):
        seleccion = tabla.selection()
        if not seleccion:
            return
        id_prod = int(tabla.item(seleccion[0])["values"][0])
        for p in cargar_usuarios():
            if p["id"] == id_prod:
                limpiar()
                entrada_nombre.insert(0, p["nombre"])
                entrada_password.insert(0, p.get("contraseña", ""))
                combo_estado.set(p["estado"])
                combo_categoria.set(p["categoria"])
                break

    tabla.bind("<<TreeviewSelect>>", al_seleccionar)

    def agregar():
        try:
            agregar_usuario(entrada_nombre.get(), entrada_password.get(), combo_estado.get(), combo_categoria.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def editar():
        id_prod = id_seleccionado()
        if id_prod is None:
            return
        try:
            editar_usuario(id_prod, entrada_nombre.get(), entrada_password.get(), combo_estado.get(), combo_categoria.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def eliminar():
        id_prod = id_seleccionado()
        if id_prod is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el usuario seleccionado?"):
            return
        try:
            eliminar_usuario(id_prod)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    botones = tk.Frame(panel, bg="snow")
    botones.grid(row=2, column=0, columnspan=4, pady=8)
    tk.Button(botones, text="Agregar", width=10, command=agregar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Editar", width=10, command=editar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Eliminar", width=10, command=eliminar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Limpiar", width=10, command=limpiar).pack(side=tk.LEFT, padx=5)