 # Menu del restaurant con tkoonter

import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
 
ARCHIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "menu.json")
CATEGORIAS = ["plato", "bebida", "postre"]
 
PRODUCTOS_INICIALES = [
    {"id": 1, "nombre": "Silpancho", "precio": 35.0, "categoria": "plato"},
    {"id": 2, "nombre": "Pique macho", "precio": 45.0, "categoria": "plato"},
    {"id": 3, "nombre": "Pollo a la plancha", "precio": 32.0, "categoria": "plato"},
    {"id": 4, "nombre": "Sopa de maní", "precio": 25.0, "categoria": "plato"},
    {"id": 5, "nombre": "Refresco", "precio": 10.0, "categoria": "bebida"},
    {"id": 6, "nombre": "Jugo de naranja", "precio": 12.0, "categoria": "bebida"},
    {"id": 7, "nombre": "Agua ", "precio": 7.0, "categoria": "bebida"},
    {"id": 8, "nombre": "Cerveza", "precio": 20.0, "categoria": "bebida"},
    {"id": 9, "nombre": "Gelatina", "precio": 15.0, "categoria": "postre"},
    {"id": 10, "nombre": "Flan", "precio": 14.0, "categoria": "postre"},
    {"id": 11, "nombre": "Torta de chocolate", "precio": 18.0, "categoria": "postre"},
]
 
def guardar_menu(menu):
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(menu, archivo, indent=4, ensure_ascii=False)
 
 
def cargar_menu():
    
    if not os.path.exists(ARCHIVO):
        guardar_menu(PRODUCTOS_INICIALES)
        return [dict(p) for p in PRODUCTOS_INICIALES]
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []
 
 
def validar(nombre, precio_texto, categoria):
    
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre no puede estar vacío.")
    try:
        precio = float(precio_texto.strip().replace(",", "."))
    except ValueError:
        raise ValueError("El precio debe ser un número (ejemplo: 25.50).")
    if precio <= 0:
        raise ValueError("El precio debe ser mayor que cero.")
    if categoria not in CATEGORIAS:
        raise ValueError("Elige una categoría: plato, bebida o postre.")
    return nombre, round(precio, 2), categoria
 
 
def agregar_producto(nombre, precio_texto, categoria):
    nombre, precio, categoria = validar(nombre, precio_texto, categoria)
    menu = cargar_menu()
    nuevo = {
        "id": max((p["id"] for p in menu), default=0) + 1,
        "nombre": nombre,
        "precio": precio,
        "categoria": categoria,
    }
    menu.append(nuevo)
    guardar_menu(menu)
    return nuevo
 
 
def editar_producto(id_producto, nombre, precio_texto, categoria):
    nombre, precio, categoria = validar(nombre, precio_texto, categoria)
    menu = cargar_menu()
    for producto in menu:
        if producto["id"] == id_producto:
            producto["nombre"] = nombre
            producto["precio"] = precio
            producto["categoria"] = categoria
            guardar_menu(menu)
            return producto
    raise ValueError("Ese producto ya no existe.")
 
 
def eliminar_producto(id_producto):
    menu = cargar_menu()
    nuevo_menu = [p for p in menu if p["id"] != id_producto]
    if len(nuevo_menu) == len(menu):
        raise ValueError("Ese producto ya no existe.")
    guardar_menu(nuevo_menu)
 
 
def abrir_menu(ventana_padre, es_admin=False):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Menú del restaurante")
    ventana.geometry("800x600")
    ventana.configure(bg="snow")
 
    tk.Label(
        ventana, text="Menú del Restaurante", font=("Arial", 24), bg="snow"
    ).pack(pady=15)
 
 
    barra = tk.Frame(ventana, bg="snow")
    barra.pack(pady=5)
    tk.Label(barra, text="Mostrar:", bg="snow").pack(side=tk.LEFT, padx=5)
    filtro = ttk.Combobox(
        barra, values=["todos"] + CATEGORIAS, state="readonly", width=12
    )
    filtro.set("todos")
    filtro.pack(side=tk.LEFT)
 
    
    marco_tabla = tk.Frame(ventana, bg="snow")
    marco_tabla.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
 
    tabla = ttk.Treeview(
        marco_tabla,
        columns=("id", "nombre", "precio", "categoria"),
        show="headings",
        height=10,
    )
    tabla.heading("id", text="ID")
    tabla.heading("nombre", text="Nombre")
    tabla.heading("precio", text="Precio")
    tabla.heading("categoria", text="Categoría")
    tabla.column("id", width=50, anchor="center")
    tabla.column("nombre", width=300)
    tabla.column("precio", width=120, anchor="center")
    tabla.column("categoria", width=150, anchor="center")
 
    barra_scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra_scroll.set)
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)
 
    def refrescar():
        """Vuelve a llenar la tabla con lo que hay en menu.json."""
        tabla.delete(*tabla.get_children())
        for p in cargar_menu():
            if filtro.get() != "todos" and p["categoria"] != filtro.get():
                continue
            tabla.insert(
                "",
                tk.END,
                values=(p["id"], p["nombre"], f"Bs {p['precio']:.2f}",
                        p["categoria"].capitalize()),
            )
 
    filtro.bind("<<ComboboxSelected>>", lambda evento: refrescar())
 
    if es_admin:
        crear_panel_admin(ventana, tabla, refrescar)
 
    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
    refrescar()
    return ventana
 
 
def crear_panel_admin(ventana, tabla, refrescar):
    """Formulario y botones para agregar, editar y eliminar productos."""
    panel = tk.LabelFrame(ventana, text="Administrar productos", bg="snow", padx=10, pady=10)
    panel.pack(padx=20, pady=5, fill=tk.X)
 
    tk.Label(panel, text="Nombre", bg="snow").grid(row=0, column=0, padx=5)
    entrada_nombre = tk.Entry(panel, width=25)
    entrada_nombre.grid(row=1, column=0, padx=5, pady=5)
 
    tk.Label(panel, text="Precio (Bs)", bg="snow").grid(row=0, column=1, padx=5)
    entrada_precio = tk.Entry(panel, width=10)
    entrada_precio.grid(row=1, column=1, padx=5, pady=5)
 
    tk.Label(panel, text="Categoría", bg="snow").grid(row=0, column=2, padx=5)
    combo_categoria = ttk.Combobox(panel, values=CATEGORIAS, state="readonly", width=10)
    combo_categoria.grid(row=1, column=2, padx=5, pady=5)
 
    def limpiar():
        entrada_nombre.delete(0, tk.END)
        entrada_precio.delete(0, tk.END)
        combo_categoria.set("")
 
    def id_seleccionado():
        
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Primero selecciona un producto de la tabla.")
            return None
        return int(tabla.item(seleccion[0])["values"][0])
 
    def al_seleccionar(evento):
        
        seleccion = tabla.selection()
        if not seleccion:
            return
        id_producto = int(tabla.item(seleccion[0])["values"][0])
        for p in cargar_menu():
            if p["id"] == id_producto:
                limpiar()
                entrada_nombre.insert(0, p["nombre"])
                entrada_precio.insert(0, str(p["precio"]))
                combo_categoria.set(p["categoria"])
                break
 
    tabla.bind("<<TreeviewSelect>>", al_seleccionar)
 
    def agregar():
        try:
            agregar_producto(entrada_nombre.get(), entrada_precio.get(), combo_categoria.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()
 
    def editar():
        id_producto = id_seleccionado()
        if id_producto is None:
            return
        try:
            editar_producto(id_producto, entrada_nombre.get(),
                            entrada_precio.get(), combo_categoria.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()
 
    def eliminar():
        id_producto = id_seleccionado()
        if id_producto is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el producto seleccionado?"):
            return
        try:
            eliminar_producto(id_producto)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()
 
    botones = tk.Frame(panel, bg="snow")
    botones.grid(row=2, column=0, columnspan=3, pady=5)
    tk.Button(botones, text="Agregar", width=10, command=agregar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Editar", width=10, command=editar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Eliminar", width=10, command=eliminar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Limpiar", width=10, command=limpiar).pack(side=tk.LEFT, padx=5)
 