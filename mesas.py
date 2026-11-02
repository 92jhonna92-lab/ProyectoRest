import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

ARCHIVO_MESAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mesas.json")
AREAS_MESAS = ["Salón", "Terraza", "VIP"]
ESTADOS_MESAS = ["Disponible", "Ocupada", "Reservada"]

MESAS_INICIALES = [
    {"id": 1, "nombre": "Mesa 01", "capacidad": 2, "area": "Salón", "estado": "Disponible", "detalle": "—"},
    {"id": 2, "nombre": "Mesa 02", "capacidad": 4, "area": "Salón", "estado": "Ocupada", "detalle": "P-1047"},
    {"id": 3, "nombre": "Mesa 03", "capacidad": 2, "area": "Terraza", "estado": "Disponible", "detalle": "—"},
    {"id": 4, "nombre": "Mesa 04", "capacidad": 4, "area": "Terraza", "estado": "Ocupada", "detalle": "P-1048"},
]

def guardar_mesas(mesas):
    with open(ARCHIVO_MESAS, "w", encoding="utf-8") as archivo:
        json.dump(mesas, archivo, indent=4, ensure_ascii=False)

def cargar_mesas():
    if not os.path.exists(ARCHIVO_MESAS):
        guardar_mesas(MESAS_INICIALES)
        return [dict(m) for m in MESAS_INICIALES]
    try:
        with open(ARCHIVO_MESAS, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []

def validar_mesa(nombre, capacidad_texto, area, estado, detalle):
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre de la mesa no puede estar vacío.")
    try:
        capacidad = int(capacidad_texto)
        if capacidad <= 0:
            raise ValueError()
    except ValueError:
        raise ValueError("La capacidad debe ser un número entero mayor a 0.")
    if area not in AREAS_MESAS:
        raise ValueError("Selecciona un área válida (Salón, Terraza, VIP).")
    if estado not in ESTADOS_MESAS:
        raise ValueError("Selecciona un estado válido.")
    detalle = detalle.strip() if detalle else "—"
    return nombre, capacidad, area, estado, detalle

def agregar_mesa(nombre, capacidad_texto, area, estado, detalle):
    nombre, capacidad, area, estado, detalle = validar_mesa(nombre, capacidad_texto, area, estado, detalle)
    mesas = cargar_mesas()
    nueva = {
        "id": max((m["id"] for m in mesas), default=0) + 1,
        "nombre": nombre,
        "capacidad": capacidad,
        "area": area,
        "estado": estado,
        "detalle": detalle,
    }
    mesas.append(nueva)
    guardar_mesas(mesas)
    return nueva

def editar_mesa(id_mesa, nombre, capacidad_texto, area, estado, detalle):
    nombre, capacidad, area, estado, detalle = validar_mesa(nombre, capacidad_texto, area, estado, detalle)
    mesas = cargar_mesas()
    for mesa in mesas:
        if mesa["id"] == id_mesa:
            mesa["nombre"] = nombre
            mesa["capacidad"] = capacidad
            mesa["area"] = area
            mesa["estado"] = estado
            mesa["detalle"] = detalle
            guardar_mesas(mesas)
            return mesa
    raise ValueError("La mesa ya no existe.")

def eliminar_mesa(id_mesa):
    mesas = cargar_mesas()
    nuevas_mesas = [m for m in mesas if m["id"] != id_mesa]
    if len(nuevas_mesas) == len(mesas):
        raise ValueError("Esa mesa ya no existe.")
    guardar_mesas(nuevas_mesas)


# --- VENTANA DE GESTIÓN DE MESAS ---
def abrir_mesas(ventana_padre, es_admin=False):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Gestión de Mesas y Áreas")
    ventana.geometry("900x630")
    ventana.configure(bg="snow")

    tk.Label(ventana, text="Gestión de Mesas por Área", font=("Arial", 24), bg="snow").pack(pady=15)

    barra = tk.Frame(ventana, bg="snow")
    barra.pack(pady=5)
    tk.Label(barra, text="Filtrar por Área:", bg="snow").pack(side=tk.LEFT, padx=5)
    filtro_area = ttk.Combobox(barra, values=["todas"] + AREAS_MESAS, state="readonly", width=14)
    filtro_area.set("todas")
    filtro_area.pack(side=tk.LEFT, padx=(0, 15))

    tk.Label(barra, text="Filtrar por Estado:", bg="snow").pack(side=tk.LEFT, padx=5)
    filtro_estado = ttk.Combobox(barra, values=["todos"] + ESTADOS_MESAS, state="readonly", width=14)
    filtro_estado.set("todos")
    filtro_estado.pack(side=tk.LEFT)

    marco_tabla = tk.Frame(ventana, bg="snow")
    marco_tabla.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    tabla = ttk.Treeview(
        marco_tabla,
        columns=("id", "nombre", "capacidad", "area", "estado", "detalle"),
        show="headings",
        height=10,
    )
    tabla.heading("id", text="ID")
    tabla.heading("nombre", text="Mesa")
    tabla.heading("capacidad", text="Capacidad")
    tabla.heading("area", text="Área")
    tabla.heading("estado", text="Estado")
    tabla.heading("detalle", text="Pedido o Reserva")

    tabla.column("id", width=50, anchor="center")
    tabla.column("nombre", width=140)
    tabla.column("capacidad", width=100, anchor="center")
    tabla.column("area", width=120, anchor="center")
    tabla.column("estado", width=120, anchor="center")
    tabla.column("detalle", width=160, anchor="center")

    barra_scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra_scroll.set)
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refrescar():
        tabla.delete(*tabla.get_children())
        for m in cargar_mesas():
            if filtro_area.get() != "todas" and m["area"] != filtro_area.get():
                continue
            if filtro_estado.get() != "todos" and m["estado"] != filtro_estado.get():
                continue
            tabla.insert(
                "",
                tk.END,
                values=(m["id"], m["nombre"], f"{m['capacidad']} personas", m["area"], m["estado"], m["detalle"]),
            )

    filtro_area.bind("<<ComboboxSelected>>", lambda evento: refrescar())
    filtro_estado.bind("<<ComboboxSelected>>", lambda evento: refrescar())

    if es_admin:
        crear_panel_admin_mesas(ventana, tabla, refrescar)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
    refrescar()
    return ventana

def crear_panel_admin_mesas(ventana, tabla, refrescar):
    panel = tk.LabelFrame(ventana, text="Administrar mesas", bg="snow", padx=10, pady=10)
    panel.pack(padx=20, pady=5, fill=tk.X)

    tk.Label(panel, text="Nombre Mesa", bg="snow").grid(row=0, column=0, padx=5)
    entrada_nombre = tk.Entry(panel, width=15)
    entrada_nombre.grid(row=1, column=0, padx=5, pady=5)

    tk.Label(panel, text="Capacidad", bg="snow").grid(row=0, column=1, padx=5)
    entrada_capacidad = tk.Entry(panel, width=10)
    entrada_capacidad.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(panel, text="Área", bg="snow").grid(row=0, column=2, padx=5)
    combo_area = ttk.Combobox(panel, values=AREAS_MESAS, state="readonly", width=12)
    combo_area.grid(row=1, column=2, padx=5, pady=5)

    tk.Label(panel, text="Estado", bg="snow").grid(row=0, column=3, padx=5)
    combo_estado = ttk.Combobox(panel, values=ESTADOS_MESAS, state="readonly", width=12)
    combo_estado.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(panel, text="Pedido / Reserva", bg="snow").grid(row=0, column=4, padx=5)
    entrada_detalle = tk.Entry(panel, width=15)
    entrada_detalle.grid(row=1, column=4, padx=5, pady=5)

    def limpiar():
        entrada_nombre.delete(0, tk.END)
        entrada_capacidad.delete(0, tk.END)
        combo_area.set("")
        combo_estado.set("")
        entrada_detalle.delete(0, tk.END)

    def id_seleccionado():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Primero selecciona una mesa de la tabla.")
            return None
        return int(tabla.item(seleccion[0])["values"][0])

    def al_seleccionar(evento):
        seleccion = tabla.selection()
        if not seleccion:
            return
        id_m = int(tabla.item(seleccion[0])["values"][0])
        for m in cargar_mesas():
            if m["id"] == id_m:
                limpiar()
                entrada_nombre.insert(0, m["nombre"])
                entrada_capacidad.insert(0, str(m["capacidad"]))
                combo_area.set(m["area"])
                combo_estado.set(m["estado"])
                entrada_detalle.insert(0, m["detalle"])
                break

    tabla.bind("<<TreeviewSelect>>", al_seleccionar)

    def agregar():
        try:
            agregar_mesa(entrada_nombre.get(), entrada_capacidad.get(), combo_area.get(), combo_estado.get(), entrada_detalle.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def editar():
        id_m = id_seleccionado()
        if id_m is None:
            return
        try:
            editar_mesa(id_m, entrada_nombre.get(), entrada_capacidad.get(), combo_area.get(), combo_estado.get(), entrada_detalle.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def eliminar():
        id_m = id_seleccionado()
        if id_m is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar la mesa seleccionada?"):
            return
        try:
            eliminar_mesa(id_m)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    botones = tk.Frame(panel, bg="snow")
    botones.grid(row=2, column=0, columnspan=5, pady=8)
    tk.Button(botones, text="Agregar", width=10, command=agregar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Editar", width=10, command=editar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Eliminar", width=10, command=eliminar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Limpiar", width=10, command=limpiar).pack(side=tk.LEFT, padx=5)
    