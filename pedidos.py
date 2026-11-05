import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

ARCHIVO_MENU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "menu.json")
ARCHIVO_PEDIDOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pedidos.json")

ESTADOS_PEDIDOS = ["Pendiente", "En preparación", "Listo", "Entregado"]
CANALES_PEDIDO = ["Mesa 01", "Mesa 02", "Mesa 03", "Mesa 04", "Para llevar", "Delivery"]

MENU_INICIALES = [
    {"id": 1, "nombre": "Milanesa con papas", "precio": 35.00, "categoria": "Platos"},
    {"id": 2, "nombre": "Pizza Familiar", "precio": 80.00, "categoria": "Comidas"},
    {"id": 3, "nombre": "Soda 2L", "precio": 14.00, "categoria": "Bebidas"},
]

PEDIDOS_INICIALES = [
    {"id": "P-1048", "mesa": "Mesa 04", "articulos": "2x Milanesa con papas", "total": 70.00, "estado": "En preparación"},
    {"id": "P-1047", "mesa": "Mesa 02", "articulos": "1x Pizza Familiar, 1x Soda 2L", "total": 94.00, "estado": "Pendiente"},
    {"id": "P-1046", "mesa": "Para llevar", "articulos": "1x Soda 2L", "total": 14.00, "estado": "Listo"},
]

def guardar_menu(menu):
    with open(ARCHIVO_MENU, "w", encoding="utf-8") as archivo:
        json.dump(menu, archivo, indent=4, ensure_ascii=False)

def cargar_menu():
    if not os.path.exists(ARCHIVO_MENU):
        guardar_menu(MENU_INICIALES)
        return [dict(m) for m in MENU_INICIALES]
    try:
        with open(ARCHIVO_MENU, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []

def guardar_pedidos(pedidos):
    with open(ARCHIVO_PEDIDOS, "w", encoding="utf-8") as archivo:
        json.dump(pedidos, archivo, indent=4, ensure_ascii=False)

def cargar_pedidos():
    if not os.path.exists(ARCHIVO_PEDIDOS):
        guardar_pedidos(PEDIDOS_INICIALES)
        return [dict(p) for p in PEDIDOS_INICIALES]
    try:
        with open(ARCHIVO_PEDIDOS, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []

def validar_pedido(id_pedido, mesa, articulos, total_texto, estado):
    id_pedido = id_pedido.strip()
    if not id_pedido:
        raise ValueError("El código del pedido no puede estar vacío.")
    if mesa not in CANALES_PEDIDO:
        raise ValueError("Selecciona una mesa o canal válido.")
    articulos = articulos.strip()
    if not articulos:
        raise ValueError("Los artículos no pueden estar vacíos.")
    try:
        total = float(total_texto)
        if total < 0:
            raise ValueError()
    except ValueError:
        raise ValueError("El total debe ser un número válido mayor o igual a 0.")
    if estado not in ESTADOS_PEDIDOS:
        raise ValueError("Selecciona un estado de pedido válido.")
    return id_pedido, mesa, articulos, total, estado

def agregar_pedido(id_pedido, mesa, articulos, total_texto, estado):
    id_pedido, mesa, articulos, total, estado = validar_pedido(id_pedido, mesa, articulos, total_texto, estado)
    pedidos = cargar_pedidos()
    if any(p["id"] == id_pedido for p in pedidos):
        raise ValueError("Ya existe un pedido con ese código.")
    nueva = {
        "id": id_pedido,
        "mesa": mesa,
        "articulos": articulos,
        "total": total,
        "estado": estado,
    }
    pedidos.append(nueva)
    guardar_pedidos(pedidos)
    return nueva

def editar_pedido(id_original, id_nuevo, mesa, articulos, total_texto, estado):
    id_nuevo, mesa, articulos, total, estado = validar_pedido(id_nuevo, mesa, articulos, total_texto, estado)
    pedidos = cargar_pedidos()
    for pedido in pedidos:
        if pedido["id"] == id_original:
            pedido["id"] = id_nuevo
            pedido["mesa"] = mesa
            pedido["articulos"] = articulos
            pedido["total"] = total
            pedido["estado"] = estado
            guardar_pedidos(pedidos)
            return pedido
    raise ValueError("El pedido ya no existe.")

def eliminar_pedido(id_pedido):
    pedidos = cargar_pedidos()
    nuevos_pedidos = [p for p in pedidos if p["id"] != id_pedido]
    if len(nuevos_pedidos) == len(pedidos):
        raise ValueError("Ese pedido ya no existe.")
    guardar_pedidos(nuevos_pedidos)

def abrir_pedidos(ventana_padre, es_admin=False):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Gestión de Pedidos")
    ventana.geometry("950x630")
    ventana.configure(bg="snow")

    tk.Label(ventana, text="Administración de Pedidos", font=("Arial", 24), bg="snow").pack(pady=15)

    barra = tk.Frame(ventana, bg="snow")
    barra.pack(pady=5)
    tk.Label(barra, text="Filtrar por Estado:", bg="snow").pack(side=tk.LEFT, padx=5)
    filtro_estado = ttk.Combobox(barra, values=["todos"] + ESTADOS_PEDIDOS, state="readonly", width=16)
    filtro_estado.set("todos")
    filtro_estado.pack(side=tk.LEFT, padx=(0, 15))

    tk.Label(barra, text="Buscar:", bg="snow").pack(side=tk.LEFT, padx=5)
    entrada_buscar = tk.Entry(barra, width=20)
    entrada_buscar.pack(side=tk.LEFT, padx=(0, 10), ipady=2)

    marco_tabla = tk.Frame(ventana, bg="snow")
    marco_tabla.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    tabla = ttk.Treeview(
        marco_tabla,
        columns=("id", "mesa", "articulos", "total", "estado"),
        show="headings",
        height=10,
    )
    tabla.heading("id", text="Pedido")
    tabla.heading("mesa", text="Mesa o canal")
    tabla.heading("articulos", text="Artículos")
    tabla.heading("total", text="Total")
    tabla.heading("estado", text="Estado")

    tabla.column("id", width=90, anchor="center")
    tabla.column("mesa", width=140, anchor="center")
    tabla.column("articulos", width=320)
    tabla.column("total", width=110, anchor="e")
    tabla.column("estado", width=140, anchor="center")

    barra_scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra_scroll.set)
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refrescar(evento=None):
        tabla.delete(*tabla.get_children())
        texto_busqueda = entrada_buscar.get().strip().lower()
        for p in cargar_pedidos():
            if filtro_estado.get() != "todos" and p["estado"] != filtro_estado.get():
                continue
            if texto_busqueda and texto_busqueda not in p["id"].lower() and texto_busqueda not in p["mesa"].lower() and texto_busqueda not in p["articulos"].lower():
                continue
            tabla.insert(
                "",
                tk.END,
                values=(p["id"], p["mesa"], p["articulos"], f"Bs {p['total']:.2f}", p["estado"]),
            )

    filtro_estado.bind("<<ComboboxSelected>>", refrescar)
    entrada_buscar.bind("<KeyRelease>", refrescar)

    if es_admin:
        crear_panel_admin_pedidos(ventana, tabla, refrescar)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
    refrescar()
    return ventana

def crear_panel_admin_pedidos(ventana, tabla, refrescar):
    panel = tk.LabelFrame(ventana, text="Administrar pedidos", bg="snow", padx=10, pady=10)
    panel.pack(padx=20, pady=5, fill=tk.X)

    tk.Label(panel, text="Cod. Pedido", bg="snow").grid(row=0, column=0, padx=5)
    entrada_id = tk.Entry(panel, width=12)
    entrada_id.grid(row=1, column=0, padx=5, pady=5)
    entrada_id.insert(0, "P-1049")

    tk.Label(panel, text="Mesa / Canal", bg="snow").grid(row=0, column=1, padx=5)
    combo_mesa = ttk.Combobox(panel, values=CANALES_PEDIDO, state="readonly", width=14)
    combo_mesa.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(panel, text="Seleccionar del Menú", bg="snow").grid(row=0, column=2, padx=5)

    menu_disponible = cargar_menu()
    opciones_menu = [f"{m['nombre']} (Bs {m['precio']:.2f})" for m in menu_disponible]
    combo_menu = ttk.Combobox(panel, values=opciones_menu, state="readonly", width=24)
    combo_menu.grid(row=1, column=2, padx=5, pady=5)

    tk.Label(panel, text="Artículos", bg="snow").grid(row=2, column=0, padx=5)
    entrada_articulos = tk.Entry(panel, width=32)
    entrada_articulos.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    tk.Label(panel, text="Total (Bs)", bg="snow").grid(row=2, column=2, padx=5)
    entrada_total = tk.Entry(panel, width=12)
    entrada_total.grid(row=3, column=2, padx=5, pady=5)

    tk.Label(panel, text="Estado", bg="snow").grid(row=2, column=3, padx=5)
    combo_estado = ttk.Combobox(panel, values=ESTADOS_PEDIDOS, state="readonly", width=14)
    combo_estado.grid(row=3, column=3, padx=5, pady=5)


    def al_elegir_menu(evento):
        seleccion = combo_menu.get()
        if not seleccion:
            return
        for m in menu_disponible:
            if f"{m['nombre']} (Bs {m['precio']:.2f})" == seleccion:
                actual_art = entrada_articulos.get().strip()
                nuevo_art = f"1x {m['nombre']}" if not actual_art else f"{actual_art}, 1x {m['nombre']}"
                entrada_articulos.delete(0, tk.END)
                entrada_articulos.insert(0, nuevo_art)

                try:
                    actual_tot = float(entrada_total.get()) if entrada_total.get().strip() else 0.0
                except ValueError:
                    actual_tot = 0.0
                
                nuevo_tot = actual_tot + m["precio"]
                entrada_total.delete(0, tk.END)
                entrada_total.insert(0, f"{nuevo_tot:.2f}")
                break

    combo_menu.bind("<<ComboboxSelected>>", al_elegir_menu)

    def limpiar():
        entrada_id.delete(0, tk.END)
        entrada_id.insert(0, "P-1050")
        combo_mesa.set("")
        combo_menu.set("")
        entrada_articulos.delete(0, tk.END)
        entrada_total.delete(0, tk.END)
        combo_estado.set("")

    def id_seleccionado():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Primero selecciona un pedido de la tabla.")
            return None
        return tabla.item(seleccion[0])["values"][0]

    def al_seleccionar(evento):
        seleccion = tabla.selection()
        if not seleccion:
            return
        id_p = tabla.item(seleccion[0])["values"][0]
        for p in cargar_pedidos():
            if str(p["id"]) == str(id_p):
                limpiar()
                entrada_id.delete(0, tk.END)
                entrada_id.insert(0, p["id"])
                combo_mesa.set(p["mesa"])
                entrada_articulos.delete(0, tk.END)
                entrada_articulos.insert(0, p["articulos"])
                entrada_total.delete(0, tk.END)
                entrada_total.insert(0, str(p["total"]))
                combo_estado.set(p["estado"])
                break

    tabla.bind("<<TreeviewSelect>>", al_seleccionar)

    def agregar():
        try:
            agregar_pedido(entrada_id.get(), combo_mesa.get(), entrada_articulos.get(), entrada_total.get(), combo_estado.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def editar():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona un pedido para editar.")
            return
        id_original = tabla.item(seleccion[0])["values"][0]
        try:
            editar_pedido(id_original, entrada_id.get(), combo_mesa.get(), entrada_articulos.get(), entrada_total.get(), combo_estado.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def eliminar():
        id_p = id_seleccionado()
        if id_p is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el pedido seleccionado?"):
            return
        try:
            eliminar_pedido(id_p)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    botones = tk.Frame(panel, bg="snow")
    botones.grid(row=4, column=0, columnspan=4, pady=10)
    tk.Button(botones, text="Agregar", width=10, command=agregar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Editar", width=10, command=editar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Eliminar", width=10, command=eliminar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Limpiar", width=10, command=limpiar).pack(side=tk.LEFT, padx=5)