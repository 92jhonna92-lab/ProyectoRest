import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

ARCHIVO_STOCK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stock.json")
CATEGORIAS_STOCK = ["Carnes", "Verduras", "Lácteos", "Bebidas", "Abarrotes"]
ESTADOS_STOCK = ["Normal", "Bajo"]

STOCK_INICIALES = [
    {"id": "ST-01", "producto": "Carne de res", "categoria": "Carnes", "cantidad": "8 kg", "estado": "Normal"},
    {"id": "ST-02", "producto": "Tomate", "categoria": "Verduras", "cantidad": "3 kg", "estado": "Bajo"},
    {"id": "ST-03", "producto": "Queso", "categoria": "Lácteos", "cantidad": "6 kg", "estado": "Normal"},
]

def guardar_stock(stock):
    with open(ARCHIVO_STOCK, "w", encoding="utf-8") as archivo:
        json.dump(stock, archivo, indent=4, ensure_ascii=False)

def cargar_stock():
    if not os.path.exists(ARCHIVO_STOCK):
        guardar_stock(STOCK_INICIALES)
        return [dict(s) for s in STOCK_INICIALES]
    try:
        with open(ARCHIVO_STOCK, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []

def validar_stock(codigo, producto, categoria, cantidad, estado):
    codigo = codigo.strip()
    if not codigo:
        raise ValueError("El código no puede estar vacío.")
    producto = producto.strip()
    if not producto:
        raise ValueError("El nombre del producto no puede estar vacío.")
    if categoria not in CATEGORIAS_STOCK:
        raise ValueError("Selecciona una categoría válida.")
    cantidad = cantidad.strip()
    if not cantidad:
        raise ValueError("La cantidad no puede estar vacía.")
    if estado not in ESTADOS_STOCK:
        raise ValueError("Selecciona un estado válido (Normal o Bajo).")
    return codigo, producto, categoria, cantidad, estado

def agregar_stock(codigo, producto, categoria, cantidad, estado):
    codigo, producto, categoria, cantidad, estado = validar_stock(codigo, producto, categoria, cantidad, estado)
    stock = cargar_stock()
    if any(s["id"] == codigo for s in stock):
        raise ValueError("Ya existe un producto con ese código.")
    nuevo = {
        "id": codigo,
        "producto": producto,
        "categoria": categoria,
        "cantidad": cantidad,
        "estado": estado,
    }
    stock.append(nuevo)
    guardar_stock(stock)
    return nuevo

def editar_stock(id_original, codigo_nuevo, producto, categoria, cantidad, estado):
    codigo_nuevo, producto, categoria, cantidad, estado = validar_stock(codigo_nuevo, producto, categoria, cantidad, estado)
    stock = cargar_stock()
    for item in stock:
        if item["id"] == id_original:
            item["id"] = codigo_nuevo
            item["producto"] = producto
            item["categoria"] = categoria
            item["cantidad"] = cantidad
            item["estado"] = estado
            guardar_stock(stock)
            return item
    raise ValueError("El producto ya no existe.")

def eliminar_stock(codigo):
    stock = cargar_stock()
    nuevo_stock = [s for s in stock if s["id"] != codigo]
    if len(nuevo_stock) == len(stock):
        raise ValueError("Ese producto ya no existe.")
    guardar_stock(nuevo_stock)


def abrir_stock(ventana_padre, es_admin=False):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Control de Stock e Inventario")
    ventana.geometry("950x630")
    ventana.configure(bg="snow")

    tk.Label(ventana, text="Control de Existencias", font=("Arial", 24), bg="snow").pack(pady=15)

    barra = tk.Frame(ventana, bg="snow")
    barra.pack(pady=5)
    
    tk.Label(barra, text="Buscar:", bg="snow").pack(side=tk.LEFT, padx=5)
    entrada_buscar = tk.Entry(barra, width=18)
    entrada_buscar.pack(side=tk.LEFT, padx=(0, 15), ipady=2)

    tk.Label(barra, text="Categoría:", bg="snow").pack(side=tk.LEFT, padx=5)
    filtro_categoria = ttk.Combobox(barra, values=["Todas"] + CATEGORIAS_STOCK, state="readonly", width=14)
    filtro_categoria.set("Todas")
    filtro_categoria.pack(side=tk.LEFT, padx=(0, 15))

    tk.Label(barra, text="Estado:", bg="snow").pack(side=tk.LEFT, padx=5)
    filtro_estado = ttk.Combobox(barra, values=["Todos"] + ESTADOS_STOCK, state="readonly", width=12)
    filtro_estado.set("Todos")
    filtro_estado.pack(side=tk.LEFT)

    marco_tabla = tk.Frame(ventana, bg="snow")
    marco_tabla.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    tabla = ttk.Treeview(
        marco_tabla,
        columns=("id", "producto", "categoria", "cantidad", "estado"),
        show="headings",
        height=10,
    )
    tabla.heading("id", text="Código")
    tabla.heading("producto", text="Producto")
    tabla.heading("categoria", text="Categoría")
    tabla.heading("cantidad", text="Cantidad")
    tabla.heading("estado", text="Estado")

    tabla.column("id", width=100, anchor="center")
    tabla.column("producto", width=250)
    tabla.column("categoria", width=150, anchor="center")
    tabla.column("cantidad", width=130, anchor="center")
    tabla.column("estado", width=130, anchor="center")

    barra_scroll = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra_scroll.set)
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    barra_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refrescar(evento=None):
        tabla.delete(*tabla.get_children())
        texto_busqueda = entrada_buscar.get().strip().lower()
        cat_sel = filtro_categoria.get()
        est_sel = filtro_estado.get()

        for s in cargar_stock():
            if cat_sel != "Todas" and s["categoria"] != cat_sel:
                continue
            if est_sel != "Todos" and s["estado"] != est_sel:
                continue
            if texto_busqueda and texto_busqueda not in s["id"].lower() and texto_busqueda not in s["producto"].lower():
                continue
            
            tabla.insert(
                "",
                tk.END,
                values=(s["id"], s["producto"], s["categoria"], s["cantidad"], s["estado"]),
            )

    filtro_categoria.bind("<<ComboboxSelected>>", refrescar)
    filtro_estado.bind("<<ComboboxSelected>>", refrescar)
    entrada_buscar.bind("<KeyRelease>", refrescar)

    if es_admin:
        crear_panel_admin_stock(ventana, tabla, refrescar)

    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=10)
    refrescar()
    return ventana

def crear_panel_admin_stock(ventana, tabla, refrescar):
    panel = tk.LabelFrame(ventana, text="Administrar inventario", bg="snow", padx=10, pady=10)
    panel.pack(padx=20, pady=5, fill=tk.X)

    tk.Label(panel, text="Código", bg="snow").grid(row=0, column=0, padx=5)
    entrada_codigo = tk.Entry(panel, width=12)
    entrada_codigo.grid(row=1, column=0, padx=5, pady=5)
    entrada_codigo.insert(0, "ST-04")

    tk.Label(panel, text="Producto", bg="snow").grid(row=0, column=1, padx=5)
    entrada_producto = tk.Entry(panel, width=22)
    entrada_producto.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(panel, text="Categoría", bg="snow").grid(row=0, column=2, padx=5)
    combo_categoria = ttk.Combobox(panel, values=CATEGORIAS_STOCK, state="readonly", width=14)
    combo_categoria.grid(row=1, column=2, padx=5, pady=5)

    tk.Label(panel, text="Cantidad (ej. 5 kg)", bg="snow").grid(row=0, column=3, padx=5)
    entrada_cantidad = tk.Entry(panel, width=14)
    entrada_cantidad.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(panel, text="Estado", bg="snow").grid(row=0, column=4, padx=5)
    combo_estado = ttk.Combobox(panel, values=ESTADOS_STOCK, state="readonly", width=12)
    combo_estado.grid(row=1, column=4, padx=5, pady=5)

    def limpiar():
        entrada_codigo.delete(0, tk.END)
        entrada_codigo.insert(0, "ST-05")
        entrada_producto.delete(0, tk.END)
        combo_categoria.set("")
        entrada_cantidad.delete(0, tk.END)
        combo_estado.set("")

    def id_seleccionado():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Primero selecciona un producto de la tabla[cite: 3].")
            return None
        return tabla.item(seleccion[0])["values"][0]

    def al_seleccionar(evento):
        seleccion = tabla.selection()
        if not seleccion:
            return
        id_s = tabla.item(seleccion[0])["values"][0]
        for s in cargar_stock():
            if str(s["id"]) == str(id_s):
                limpiar()
                entrada_codigo.delete(0, tk.END)
                entrada_codigo.insert(0, s["id"])
                entrada_producto.delete(0, tk.END)
                entrada_producto.insert(0, s["producto"])
                combo_categoria.set(s["categoria"])
                entrada_cantidad.delete(0, tk.END)
                entrada_cantidad.insert(0, s["cantidad"])
                combo_estado.set(s["estado"])
                break

    tabla.bind("<<TreeviewSelect>>", al_seleccionar)

    def agregar():
        try:
            agregar_stock(entrada_codigo.get(), entrada_producto.get(), combo_categoria.get(), entrada_cantidad.get(), combo_estado.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def editar():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona un producto para editar.")
            return
        id_original = tabla.item(seleccion[0])["values"][0]
        try:
            editar_stock(id_original, entrada_codigo.get(), entrada_producto.get(), combo_categoria.get(), entrada_cantidad.get(), combo_estado.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    def eliminar():
        id_s = id_seleccionado()
        if id_s is None:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar el producto del stock seleccionado?"):
            return
        try:
            eliminar_stock(id_s)
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return
        limpiar()
        refrescar()

    botones = tk.Frame(panel, bg="snow")
    botones.grid(row=2, column=0, columnspan=5, pady=10)
    tk.Button(botones, text="Agregar", width=10, command=agregar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Editar", width=10, command=editar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Eliminar", width=10, command=eliminar).pack(side=tk.LEFT, padx=5)
    tk.Button(botones, text="Limpiar", width=10, command=limpiar).pack(side=tk.LEFT, padx=5)