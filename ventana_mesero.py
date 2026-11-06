
import tkinter as tk
from tkinter import messagebox, ttk

import pedidos
import pedidos_mesero as pm
import ventas
from categorias import cargar_categorias
from menu import cargar_menu


# ---------------------------------------------------------------------------
# Pedido nuevo
# ---------------------------------------------------------------------------

def abrir_nuevo_pedido(ventana_padre, mesero, al_guardar=None):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Nuevo pedido")
    ventana.geometry("900x650")
    ventana.minsize(800, 560)
    ventana.configure(bg="snow")

    tk.Label(ventana, text="Nuevo pedido", font=("Arial", 22), bg="snow").pack(pady=10)

    
    barra_final = tk.Frame(ventana, bg="snow")
    barra_final.pack(side=tk.BOTTOM, pady=10)

   
    marco_canal = tk.Frame(ventana, bg="snow")
    marco_canal.pack(pady=5)
    tk.Label(marco_canal, text="Mesa o canal:", bg="snow").pack(side=tk.LEFT, padx=5)
    combo_canal = ttk.Combobox(marco_canal, values=pedidos.CANALES_PEDIDO,
                               state="readonly", width=16)
    combo_canal.pack(side=tk.LEFT)

    cuerpo = tk.Frame(ventana, bg="snow")
    cuerpo.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

    
    izquierda = tk.LabelFrame(cuerpo, text="Menú", bg="snow", padx=8, pady=8)
    izquierda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

    filtro = ttk.Combobox(izquierda, state="readonly", width=15,
                          values=["todos"] + cargar_categorias("menu"))
    filtro.set("todos")
    filtro.pack(anchor="w", pady=(0, 5))

    barra_cantidad = tk.Frame(izquierda, bg="snow")
    barra_cantidad.pack(side=tk.BOTTOM, pady=(8, 0))
    tk.Label(barra_cantidad, text="Cantidad:", bg="snow").pack(side=tk.LEFT)
    cantidad = tk.Spinbox(barra_cantidad, from_=1, to=50, width=4)
    cantidad.pack(side=tk.LEFT, padx=5)

    tabla_menu = ttk.Treeview(izquierda, columns=("nombre", "precio", "categoria"),
                              show="headings", height=10)
    tabla_menu.heading("nombre", text="Producto")
    tabla_menu.heading("precio", text="Precio")
    tabla_menu.heading("categoria", text="Categoría")
    tabla_menu.column("nombre", width=190)
    tabla_menu.column("precio", width=70, anchor="center")
    tabla_menu.column("categoria", width=90, anchor="center")
    tabla_menu.pack(fill=tk.BOTH, expand=True)

    def llenar_menu():
        tabla_menu.delete(*tabla_menu.get_children())
        for p in cargar_menu():
            if filtro.get() != "todos" and p["categoria"] != filtro.get():
                continue
           
            tabla_menu.insert("", tk.END, iid=str(p["id"]),
                              values=(p["nombre"], f"Bs {p['precio']:.2f}",
                                      p["categoria"].capitalize()))

    filtro.bind("<<ComboboxSelected>>", lambda evento: llenar_menu())

  
    derecha = tk.LabelFrame(cuerpo, text="Pedido", bg="snow", padx=8, pady=8)
    derecha.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    texto_total = tk.StringVar(value="Total: Bs 0.00")
    tk.Label(derecha, textvariable=texto_total, font=("Arial", 14, "bold"),
             bg="snow").pack(side=tk.BOTTOM, pady=(8, 0))
    boton_quitar = tk.Button(derecha, text="Quitar producto")
    boton_quitar.pack(side=tk.BOTTOM, pady=(8, 0))

    tabla_pedido = ttk.Treeview(derecha, columns=("cant", "nombre", "subtotal"),
                                show="headings", height=10)
    tabla_pedido.heading("cant", text="Cant.")
    tabla_pedido.heading("nombre", text="Producto")
    tabla_pedido.heading("subtotal", text="Subtotal")
    tabla_pedido.column("cant", width=50, anchor="center")
    tabla_pedido.column("nombre", width=190)
    tabla_pedido.column("subtotal", width=90, anchor="center")
    tabla_pedido.pack(fill=tk.BOTH, expand=True)

   
    items = {}

    def refrescar_pedido():
        tabla_pedido.delete(*tabla_pedido.get_children())
        for item in items.values():
            subtotal = item["precio"] * item["cantidad"]
            tabla_pedido.insert("", tk.END, iid=str(item["id"]),
                                values=(item["cantidad"], item["nombre"], f"Bs {subtotal:.2f}"))
        texto_total.set(f"Total: Bs {pm.total_items(list(items.values())):.2f}")

    def agregar_al_pedido():
        seleccion = tabla_menu.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Primero selecciona un producto del menú.",
                                   parent=ventana)
            return
        try:
            cuantos = int(cantidad.get())
            if cuantos <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero mayor que cero.",
                                 parent=ventana)
            return
        id_producto = int(seleccion[0])
        if id_producto in items:                     
            items[id_producto]["cantidad"] += cuantos
        else:
            producto = next(p for p in cargar_menu() if p["id"] == id_producto)
            items[id_producto] = {"id": id_producto, "nombre": producto["nombre"],
                                  "precio": producto["precio"], "cantidad": cuantos}
        refrescar_pedido()

    def quitar_del_pedido():
        seleccion = tabla_pedido.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Primero selecciona un producto del pedido.",
                                   parent=ventana)
            return
        del items[int(seleccion[0])]
        refrescar_pedido()

    boton_quitar.config(command=quitar_del_pedido)
    tk.Button(barra_cantidad, text="Agregar al pedido",
              command=agregar_al_pedido).pack(side=tk.LEFT, padx=10)

    def guardar():
        try:
            pedido = pm.crear_pedido(mesero, combo_canal.get(), list(items.values()))
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=ventana)
            return
        messagebox.showinfo(
            "Listo",
            f"Pedido {pedido['id']} guardado ({pedido['mesa']}).\n"
            f"Total: Bs {pedido['total']:.2f}",
            parent=ventana,
        )
        ventana.destroy()
        if al_guardar:
            al_guardar()

    tk.Button(barra_final, text="Guardar pedido", width=15,
              command=guardar).pack(side=tk.LEFT, padx=8)
    tk.Button(barra_final, text="Cancelar", width=10,
              command=ventana.destroy).pack(side=tk.LEFT, padx=8)

    llenar_menu()
    return ventana




COLORES_ESTADO = {
    pm.PENDIENTE: "#b45309",       # ámbar oscuro
    pm.EN_PREPARACION: "#b45309",
    pm.LISTO: "#0e7490",           # turquesa
    pm.ENTREGADO: "#1d4ed8",       # azul
    pm.COBRADO: "#15803d",         # verde
    pm.CANCELADO: "gray",
}


def pedir_pago(ventana_padre):
    """Pregunta cómo pagó el cliente. Devuelve 'Efectivo', 'Tarjeta' o 'QR'; None si se cancela."""
    dialogo = tk.Toplevel(ventana_padre)
    dialogo.title("Cobrar pedido")
    dialogo.geometry("300x150")
    dialogo.configure(bg="snow")
    dialogo.transient(ventana_padre)
    dialogo.grab_set()                      

    tk.Label(dialogo, text="Método de pago:", bg="snow").pack(pady=(15, 5))
    combo = ttk.Combobox(dialogo, values=ventas.METODOS_PAGO, state="readonly", width=15)
    combo.pack()
    elegido = []

    def aceptar():
        if not combo.get():
            messagebox.showwarning("Aviso", "Elige un método de pago.", parent=dialogo)
            return
        elegido.append(combo.get())
        dialogo.destroy()

    barra = tk.Frame(dialogo, bg="snow")
    barra.pack(pady=15)
    tk.Button(barra, text="Cobrar", width=9, command=aceptar).pack(side=tk.LEFT, padx=5)
    tk.Button(barra, text="Cancelar", width=9, command=dialogo.destroy).pack(side=tk.LEFT, padx=5)
    dialogo.wait_window()                  
    return elegido[0] if elegido else None


def abrir_mis_pedidos(ventana_padre, mesero):
    ventana = tk.Toplevel(ventana_padre)
    ventana.title("Mis pedidos")
    ventana.geometry("1000x600")
    ventana.minsize(850, 480)
    ventana.configure(bg="snow")

    tk.Label(ventana, text="Mis pedidos", font=("Arial", 22), bg="snow").pack(pady=10)

    
    barra_botones = tk.Frame(ventana, bg="snow")
    barra_botones.pack(side=tk.BOTTOM, pady=10)
    texto_resumen = tk.StringVar()
    tk.Label(ventana, textvariable=texto_resumen, bg="snow").pack(side=tk.BOTTOM)

  
    barra = tk.Frame(ventana, bg="snow")
    barra.pack(pady=5)
    tk.Label(barra, text="Estado:", bg="snow").pack(side=tk.LEFT, padx=5)
    filtro_estado = ttk.Combobox(barra, state="readonly", width=14,
                                 values=["todos"] + pedidos.ESTADOS_PEDIDOS)
    filtro_estado.set("todos")
    filtro_estado.pack(side=tk.LEFT)
    solo_hoy = tk.BooleanVar(value=True)
    tk.Checkbutton(barra, text="Solo los de hoy", variable=solo_hoy, bg="snow",
                   command=lambda: refrescar()).pack(side=tk.LEFT, padx=15)

  
    marco = tk.Frame(ventana, bg="snow")
    marco.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
    tabla = ttk.Treeview(marco, columns=("id", "fecha", "mesa", "articulos", "total", "estado"),
                         show="headings", height=10)
    for nombre, titulo, ancho, anclaje in (
        ("id", "Pedido", 70, "center"), ("fecha", "Fecha y hora", 125, "center"),
        ("mesa", "Mesa o canal", 100, "center"), ("articulos", "Artículos", 380, "w"),
        ("total", "Total", 80, "center"), ("estado", "Estado", 110, "center"),
    ):
        tabla.heading(nombre, text=titulo)
        tabla.column(nombre, width=ancho, anchor=anclaje)
    for estado, color in COLORES_ESTADO.items():
        tabla.tag_configure(estado, foreground=color)
    scroll = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=scroll.set)
    tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refrescar():
        tabla.delete(*tabla.get_children())
        lista = pm.pedidos_de(
            mesero,
            fecha=pm.hoy() if solo_hoy.get() else None,
            estado=None if filtro_estado.get() == "todos" else filtro_estado.get(),
        )
        for p in lista:
            tabla.insert("", tk.END, iid=p["id"], tags=(p["estado"],), values=(
                p["id"], p["fecha"].replace("T", " ")[:16], p["mesa"], p["articulos"],
                f"Bs {p['total']:.2f}", p["estado"],
            ))
        texto_resumen.set(f"{len(lista)} pedido(s) en la lista")

    filtro_estado.bind("<<ComboboxSelected>>", lambda evento: refrescar())

    def pedido_elegido():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Primero selecciona un pedido de la tabla.",
                                   parent=ventana)
            return None
        return seleccion[0]

    def cambiar(nuevo_estado):
        id_pedido = pedido_elegido()
        if id_pedido is None:
            return
        try:
            pm.validar_cambio(id_pedido, nuevo_estado)      
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=ventana)
            return
        pago = None
        if nuevo_estado == pm.CANCELADO and not messagebox.askyesno(
                "Confirmar", f"¿Cancelar el pedido {id_pedido}?", parent=ventana):
            return
        if nuevo_estado == pm.COBRADO:
            pago = pedir_pago(ventana)
            if pago is None:
                return
        try:
            pm.cambiar_estado(id_pedido, nuevo_estado, pago)
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=ventana)
            return
        refrescar()

    tk.Button(barra_botones, text="Marcar entregado",
              command=lambda: cambiar(pm.ENTREGADO)).pack(side=tk.LEFT, padx=5)
    tk.Button(barra_botones, text="Marcar cobrado",
              command=lambda: cambiar(pm.COBRADO)).pack(side=tk.LEFT, padx=5)
    tk.Button(barra_botones, text="Cancelar pedido",
              command=lambda: cambiar(pm.CANCELADO)).pack(side=tk.LEFT, padx=5)
    tk.Button(barra_botones, text="Actualizar", command=refrescar).pack(side=tk.LEFT, padx=5)
    tk.Button(barra_botones, text="Cerrar", command=ventana.destroy).pack(side=tk.LEFT, padx=5)

    refrescar()
    return ventana
