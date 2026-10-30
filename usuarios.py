

import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
from categorias import cargar_categorias, abrir_gestor_categorias

ARCHIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.json")

PROTEGIDAS = ["Administrador", "Mesero"]
ESTADOS = ["Activo", "Inactivo"]
MIN_NOMBRE = 3
MIN_CLAVE = 4


USUARIOS_INICIALES = [
    {"id": 1, "nombre": "admin", "clave": "admin", "estado": "Activo", "categoria": "Administrador"},
]



def guardar_usuarios(usuarios):
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(usuarios, archivo, indent=4, ensure_ascii=False)


def cargar_usuarios():
    if not os.path.exists(ARCHIVO):
        guardar_usuarios(USUARIOS_INICIALES)
        return [dict(u) for u in USUARIOS_INICIALES]
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as archivo:
            usuarios = json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return [dict(u) for u in USUARIOS_INICIALES]
    for u in usuarios:                 
        u.setdefault("clave", "")
    return usuarios


def buscar_cuenta(nombre, clave):
    """Devuelve el usuario si nombre y clave son correctos y está Activo; si no, None."""
    nombre = nombre.strip().lower()
    for u in cargar_usuarios():
        if u["nombre"].lower() == nombre and u["clave"] == clave and u["estado"] == "Activo":
            return u
    return None


def admins_activos(usuarios):
    return [u for u in usuarios
            if u["categoria"] == "Administrador" and u["estado"] == "Activo"]


def validar(nombre, clave, estado, categoria, clave_obligatoria=True):
    nombre = nombre.strip()
    if len(nombre) < MIN_NOMBRE:
        raise ValueError(f"El nombre debe tener al menos {MIN_NOMBRE} letras.")
    if " " in nombre:
        raise ValueError("El nombre no puede tener espacios.")
    if clave_obligatoria or clave:
        if len(clave) < MIN_CLAVE:
            raise ValueError(f"La contraseña debe tener al menos {MIN_CLAVE} caracteres.")
    if estado not in ESTADOS:
        raise ValueError("Elige un estado: Activo o Inactivo.")
    if categoria not in cargar_categorias("usuarios"):
        raise ValueError("Elige una categoría de la lista.")
    return nombre, clave, estado, categoria


def _nombre_repetido(usuarios, nombre, ignorar_id=None):
    return any(u["nombre"].lower() == nombre.lower() and u["id"] != ignorar_id
               for u in usuarios)



def agregar_usuario(nombre, clave, estado, categoria):
    nombre, clave, estado, categoria = validar(nombre, clave, estado, categoria)
    usuarios = cargar_usuarios()
    if _nombre_repetido(usuarios, nombre):
        raise ValueError("Ese nombre de usuario ya existe.")
    nuevo = {
        "id": max((u["id"] for u in usuarios), default=0) + 1,
        "nombre": nombre,
        "clave": clave,
        "estado": estado,
        "categoria": categoria,
    }
    usuarios.append(nuevo)
    guardar_usuarios(usuarios)
    return nuevo


def editar_usuario(id_usuario, nombre, clave, estado, categoria):
    """Si la clave viene vacía se conserva la que ya tenía."""
    nombre, clave, estado, categoria = validar(nombre, clave, estado, categoria,
                                               clave_obligatoria=False)
    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["id"] == id_usuario:
            if _nombre_repetido(usuarios, nombre, ignorar_id=id_usuario):
                raise ValueError("Ese nombre de usuario ya existe.")
            antes = list(admins_activos(usuarios))
            nuevo = dict(u, nombre=nombre, estado=estado, categoria=categoria)
            if clave:
                nuevo["clave"] = clave
            if antes == [u] and not (nuevo["categoria"] == "Administrador"
                                     and nuevo["estado"] == "Activo"):
                raise ValueError("Debe quedar al menos un administrador activo.")
            u.update(nuevo)
            guardar_usuarios(usuarios)
            return u
    raise ValueError("El usuario ya no existe.")


def eliminar_usuario(id_usuario):
    usuarios = cargar_usuarios()
    nuevos = [u for u in usuarios if u["id"] != id_usuario]
    if len(nuevos) == len(usuarios):
        raise ValueError("Ese usuario ya no existe.")
    if not admins_activos(nuevos):
        raise ValueError("No puedes eliminar al único administrador activo.")
    guardar_usuarios(nuevos)



def abrir_usuarios(ventana_padre, es_admin=False):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Usuarios del restaurante")
    ventana.geometry("800x700")
    ventana.minsize(700, 560)
    ventana.configure(bg="snow")

    tk.Label(ventana, text="Usuarios del Restaurante",
             font=("Arial", 24), bg="snow").pack(pady=15)

    barra = tk.Frame(ventana, bg="snow")
    barra.pack(pady=5)
    tk.Label(barra, text="Mostrar:", bg="snow").pack(side=tk.LEFT, padx=5)
    filtro = ttk.Combobox(barra, values=["todos"] + cargar_categorias("usuarios"),
                          state="readonly", width=14)
    filtro.set("todos")
    filtro.pack(side=tk.LEFT)

    marco_tabla = tk.Frame(ventana, bg="snow")

    tabla = ttk.Treeview(marco_tabla, columns=("id", "nombre", "estado", "categoria"),
                         show="headings", height=6)
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
        for u in cargar_usuarios():
            if filtro.get() != "todos" and u["categoria"] != filtro.get():
                continue
            tabla.insert("", tk.END,
                         values=(u["id"], u["nombre"], u["estado"], u["categoria"]))

    filtro.bind("<<ComboboxSelected>>", lambda evento: refrescar())

    
    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(side=tk.BOTTOM, pady=10)
    if es_admin:
        crear_panel_admin(ventana, tabla, refrescar, filtro)
    marco_tabla.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    refrescar()
    return ventana


def crear_panel_admin(ventana, tabla, refrescar, filtro):
   
    panel = tk.LabelFrame(ventana, text="Administrar usuarios", bg="snow", padx=10, pady=10)
    panel.pack(side=tk.BOTTOM, padx=20, pady=5, fill=tk.X)

    tk.Label(panel, text="Nombre", bg="snow").grid(row=0, column=0, padx=5)
    entrada_nombre = tk.Entry(panel, width=18)
    entrada_nombre.grid(row=1, column=0, padx=5, pady=5)

    tk.Label(panel, text="Contraseña", bg="snow").grid(row=0, column=1, padx=5)
    entrada_clave = tk.Entry(panel, width=18, show="*")
    entrada_clave.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(panel, text="Estado", bg="snow").grid(row=0, column=2, padx=5)
    combo_estado = ttk.Combobox(panel, values=ESTADOS, state="readonly", width=10)
    combo_estado.grid(row=1, column=2, padx=5, pady=5)

    tk.Label(panel, text="Categoría", bg="snow").grid(row=0, column=3, padx=5)
    combo_categoria = ttk.Combobox(panel, values=cargar_categorias("usuarios"), state="readonly", width=14)
    combo_categoria.grid(row=1, column=3, padx=5, pady=5)

    

    def limpiar():
        entrada_nombre.delete(0, tk.END)
        entrada_clave.delete(0, tk.END)
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
        id_usuario = int(tabla.item(seleccion[0])["values"][0])
        for u in cargar_usuarios():
            if u["id"] == id_usuario:
                limpiar()
                entrada_nombre.insert(0, u["nombre"])
                combo_estado.set(u["estado"])
                combo_categoria.set(u["categoria"])
                break

    tabla.bind("<<TreeviewSelect>>", al_seleccionar)

    def agregar():
        try:
            agregar_usuario(entrada_nombre.get(), entrada_clave.get(),
                            combo_estado.get(), combo_categoria.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def editar():
        id_usuario = id_seleccionado()
        if id_usuario is None:
            return
        try:
            editar_usuario(id_usuario, entrada_nombre.get(), entrada_clave.get(),
                           combo_estado.get(), combo_categoria.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def eliminar():
        id_usuario = id_seleccionado()
        if id_usuario is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el usuario seleccionado?"):
            return
        try:
            eliminar_usuario(id_usuario)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    botones = tk.Frame(panel, bg="snow")
    botones.grid(row=3, column=0, columnspan=4, pady=5)

    def actualizar_categorias():
       
        nombres = cargar_categorias("usuarios")
        combo_categoria["values"] = nombres
        if combo_categoria.get() not in nombres:
            combo_categoria.set("")
        filtro["values"] = ["todos"] + nombres
        if filtro.get() not in filtro["values"]:
            filtro.set("todos")
        refrescar()

    def abrir_categorias():
        abrir_gestor_categorias(ventana, "usuarios", "Categorías de usuarios",
                                cargar_usuarios, guardar_usuarios,
                                actualizar_categorias, PROTEGIDAS)

    tk.Button(botones, text="Agregar", width=10, command=agregar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Editar", width=10, command=editar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Eliminar", width=10, command=eliminar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Limpiar", width=10, command=limpiar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Categorías", width=10, command=abrir_categorias).pack(side=tk.LEFT, padx=5)
