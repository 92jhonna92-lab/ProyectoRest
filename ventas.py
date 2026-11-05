import json
import os
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

ARCHIVO_VENTAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ventas.json")
ARCHIVO_USUARIOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "usuarios.json")
ARCHIVO_MENU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "menu.json")

METODOS_PAGO = ["Efectivo", "Tarjeta", "QR"]
ORIGENES_VENTA = ["Salón", "Delivery", "Para llevar"]

VENTAS_INICIALES = [
    {"id": 1, "hora": "12:30", "vendedor": "Brayan", "origen": "Salón", "total": 140.00, "pago": "Efectivo"},
    {"id": 2, "hora": "13:10", "vendedor": "Serghiño", "origen": "Delivery", "total": 65.00, "pago": "QR"},
]

def guardar_ventas(ventas):
    with open(ARCHIVO_VENTAS, "w", encoding="utf-8") as archivo:
        json.dump(ventas, archivo, indent=4, ensure_ascii=False)

def cargar_ventas():
    if not os.path.exists(ARCHIVO_VENTAS):
        guardar_ventas(VENTAS_INICIALES)
        return [dict(v) for v in VENTAS_INICIALES]
    try:
        with open(ARCHIVO_VENTAS, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []

def cargar_nombres_vendedores():
    """Carga los nombres de usuarios registrados que estén activos o sean de categorías válidas."""
    if not os.path.exists(ARCHIVO_USUARIOS):
        return ["Brayan", "Serghiño"] # Respaldo por defecto
    try:
        with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as archivo:
            usuarios = json.load(archivo)
            return [u["nombre"] for u in usuarios if u.get("estado", "Activo") == "Activo"]
    except Exception:
        return ["Brayan", "Serghiño"]

def cargar_productos_menu():
    if not os.path.exists(ARCHIVO_MENU):
        return [
            {"id": 1, "nombre": "Milanesa con papas", "precio": 35.00},
            {"id": 2, "nombre": "Pizza Familiar", "precio": 80.00},
            {"id": 3, "nombre": "Soda 2L", "precio": 14.00}
        ]
    try:
        with open(ARCHIVO_MENU, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except Exception:
        return []

def validar_venta(hora, vendedor, origen, total_texto, pago):
    hora = hora.strip()
    if not hora:
        raise ValueError("La hora no puede estar vacía.")
    vendedor = vendedor.strip()
    if not vendedor:
        raise ValueError("Debes seleccionar un vendedor.")
    if origen not in ORIGENES_VENTA:
        raise ValueError("Selecciona un origen válido.")
    try:
        total = float(total_texto)
        if total <= 0:
            raise ValueError()
    except ValueError:
        raise ValueError("El total debe ser un número válido mayor a 0.")
    if pago not in METODOS_PAGO:
        raise ValueError("Selecciona un método de pago válido.")
    return hora, vendedor, origen, total, pago

def agregar_venta(hora, vendedor, origen, total_texto, pago):
    hora, vendedor, origen, total, pago = validar_venta(hora, vendedor, origen, total_texto, pago)
    ventas = cargar_ventas()
    nueva = {
        "id": max((v["id"] for v in ventas), default=0) + 1,
        "hora": hora,
        "vendedor": vendedor,
        "origen": origen,
        "total": total,
        "pago": pago,
    }
    ventas.append(nueva)
    guardar_ventas(ventas)
    return nueva

def editar_venta(id_venta, hora, vendedor, origen, total_texto, pago):
    hora, vendedor, origen, total, pago = validar_venta(hora, vendedor, origen, total_texto, pago)
    ventas = cargar_ventas()
    for venta in ventas:
        if venta["id"] == id_venta:
            venta["hora"] = hora
            venta["vendedor"] = vendedor
            venta["origen"] = origen
            venta["total"] = total
            venta["pago"] = pago
            guardar_ventas(ventas)
            return venta
    raise ValueError("La venta ya no existe.")

def eliminar_venta(id_venta):
    ventas = cargar_ventas()
    nuevas_ventas = [v for v in ventas if v["id"] != id_venta]
    if len(nuevas_ventas) == len(ventas):
        raise ValueError("Esa venta ya no existe.")
    guardar_ventas(nuevas_ventas)


def abrir_ventas(ventana_padre, es_admin=False):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Registro de Ventas")
    ventana.geometry("900x650")
    ventana.configure(bg="snow")

    tk.Label(ventana, text="Gestión de Ventas", font=("Arial", 24), bg="snow").pack(pady=15)

    barra = tk.Frame(ventana, bg="snow")
    barra.pack(pady=5)
    tk.Label(barra, text="Filtrar por pago:", bg="snow").pack(side=tk.LEFT, padx=5)
    filtro = ttk.Combobox(barra, values=["todos"] + METODOS_PAGO, state="readonly", width=12)
    filtro.set("todos")
    filtro.pack(side=tk.LEFT, padx=(0, 15))

    marco_tabla = tk.Frame(ventana, bg="snow")
    marco_tabla.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    tabla = ttk.Treeview(
        marco_tabla,
        columns=("id", "hora", "vendedor", "origen", "total", "pago"),
        show="headings",
        height=10,
    )
    tabla.heading("id", text="ID")
    tabla.heading("hora", text="Hora")
    tabla.heading("vendedor", text="Vendedor")
    tabla.heading("origen", text="Origen")
    tabla.heading("total", text="Total (Bs)")
    tabla.heading("pago", text="Método Pago")

    tabla.column("id", width=50, anchor="center")
    tabla.column("hora", width=90, anchor="center")
    tabla.column("vendedor", width=160)
    tabla.column("origen", width=120, anchor="center")
    tabla.column("total", width=120, anchor="e")
    tabla.column("pago", width=130, anchor="center")

    barra_scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra_scroll.set)
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refrescar():
        tabla.delete(*tabla.get_children())
        for v in cargar_ventas():
            if filtro.get() != "todos" and v["pago"] != filtro.get():
                continue
            tabla.insert(
                "",
                tk.END,
                values=(v["id"], v["hora"], v["vendedor"], v["origen"], f"Bs {v['total']:.2f}", v["pago"]),
            )

    filtro.bind("<<ComboboxSelected>>", lambda evento: refrescar())

    if es_admin:
        crear_panel_admin_ventas(ventana, tabla, refrescar)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
    refrescar()
    return ventana

def crear_panel_admin_ventas(ventana, tabla, refrescar):
    panel = tk.LabelFrame(ventana, text="Administrar ventas (Selección múltiple de menú)", bg="snow", padx=10, pady=10)
    panel.pack(padx=20, pady=5, fill=tk.X)

    tk.Label(panel, text="Hora", bg="snow").grid(row=0, column=0, padx=5)
    entrada_hora = tk.Entry(panel, width=10)
    entrada_hora.grid(row=1, column=0, padx=5, pady=5)
    entrada_hora.insert(0, datetime.now().strftime("%H:%M"))

    tk.Label(panel, text="Vendedor (Usuarios)", bg="snow").grid(row=0, column=1, padx=5)
    vendedores_disponibles = cargar_nombres_vendedores()
    combo_vendedor = ttk.Combobox(panel, values=vendedores_disponibles, state="readonly", width=16)
    combo_vendedor.grid(row=1, column=1, padx=5, pady=5)
    if vendedores_disponibles:
        combo_vendedor.current(0)

    tk.Label(panel, text="Origen", bg="snow").grid(row=0, column=2, padx=5)
    combo_origen = ttk.Combobox(panel, values=ORIGENES_VENTA, state="readonly", width=12)
    combo_origen.grid(row=1, column=2, padx=5, pady=5)
    combo_origen.set(ORIGENES_VENTA[0])

    tk.Label(panel, text="Método Pago", bg="snow").grid(row=0, column=3, padx=5)
    combo_pago = ttk.Combobox(panel, values=METODOS_PAGO, state="readonly", width=12)
    combo_pago.grid(row=1, column=3, padx=5, pady=5)
    combo_pago.set(METODOS_PAGO[0])


    tk.Label(panel, text="Productos del Menú (Selección Múltiple):", bg="snow").grid(row=2, column=0, columnspan=2, padx=5, sticky="w", pady=(10, 0))
    
    marco_lista_menu = tk.Frame(panel)
    marco_lista_menu.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
    
    listbox_menu = tk.Listbox(marco_lista_menu, selectmode=tk.MULTIPLE, height=4, width=35)
    scrollbar_menu = ttk.Scrollbar(marco_lista_menu, orient="vertical", command=listbox_menu.yview)
    listbox_menu.configure(yscrollcommand=scrollbar_menu.set)
    listbox_menu.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar_menu.pack(side=tk.RIGHT, fill=tk.Y)

    productos_menu = cargar_productos_menu()
    for prod in productos_menu:
        listbox_menu.insert(tk.END, f"{prod['nombre']} - Bs {prod['precio']:.2f}")

    tk.Label(panel, text="Total Calculado (Bs):", bg="snow", font=("Arial", 10, "bold")).grid(row=2, column=2, padx=5, sticky="w", pady=(10, 0))
    entrada_total = tk.Entry(panel, width=15, font=("Arial", 11, "bold"))
    entrada_total.grid(row=3, column=2, padx=5, pady=5, sticky="nw")
    entrada_total.insert(0, "0.00")

    def calcular_total_seleccionado(event=None):
        indices = listbox_menu.curselection()
        suma = 0.0
        for i in indices:
            texto_prod = listbox_menu.get(i)
            
            try:
                precio_str = texto_prod.split("Bs ")[1]
                suma += float(precio_str)
            except Exception:
                pass
        entrada_total.delete(0, tk.END)
        entrada_total.insert(0, f"{suma:.2f}")

    listbox_menu.bind("<<ListboxSelect>>", calcular_total_seleccionado)

    def limpiar():
        entrada_hora.delete(0, tk.END)
        entrada_hora.insert(0, datetime.now().strftime("%H:%M"))
        if vendedores_disponibles:
            combo_vendedor.current(0)
        combo_origen.set(ORIGENES_VENTA[0])
        combo_pago.set(METODOS_PAGO[0])
        listbox_menu.selection_clear(0, tk.END)
        entrada_total.delete(0, tk.END)
        entrada_total.insert(0, "0.00")

    def id_seleccionado():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Primero selecciona una venta de la tabla.")
            return None
        return int(tabla.item(seleccion[0])["values"][0])

    def al_seleccionar(evento):
        seleccion = tabla.selection()
        if not seleccion:
            return
        id_v = int(tabla.item(seleccion[0])["values"][0])
        for v in cargar_ventas():
            if v["id"] == id_v:
                entrada_hora.delete(0, tk.END)
                entrada_hora.insert(0, v["hora"])
                if v["vendedor"] in vendedores_disponibles:
                    combo_vendedor.set(v["vendedor"])
                combo_origen.set(v["origen"])
                combo_pago.set(v["pago"])
                entrada_total.delete(0, tk.END)
                entrada_total.insert(0, str(v["total"]))
                break

    tabla.bind("<<TreeviewSelect>>", al_seleccionar)

    def agregar():
        try:
            agregar_venta(entrada_hora.get(), combo_vendedor.get(), combo_origen.get(), entrada_total.get(), combo_pago.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def editar():
        id_v = id_seleccionado()
        if id_v is None:
            return
        try:
            editar_venta(id_v, entrada_hora.get(), combo_vendedor.get(), combo_origen.get(), entrada_total.get(), combo_pago.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def eliminar():
        id_v = id_seleccionado()
        if id_v is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar la venta seleccionada?"):
            return
        try:
            eliminar_venta(id_v)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    botones = tk.Frame(panel, bg="snow")
    botones.grid(row=4, column=0, columnspan=4, pady=12)
    tk.Button(botones, text="Agregar", width=10, command=agregar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Editar", width=10, command=editar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Eliminar", width=10, command=eliminar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Limpiar", width=10, command=limpiar).pack(side=tk.LEFT, padx=5)