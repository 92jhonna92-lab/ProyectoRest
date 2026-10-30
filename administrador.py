import funciones_login
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from menu import abrir_menu, cargar_menu
from usuarios import abrir_usuarios, cargar_usuarios

def abrir_ventana_principal(nombre_usuario,ventana):
    ventana_principal = tk.Toplevel(ventana)
    ventana_principal.title("Restaurante")
    ventana_principal.geometry("1200x760")
    ventana_principal.minsize(950, 620)
    modulo_actual = "Resumen"

    area_contenido = None
    datos = {

    "Pedidos": [("P-1048", "Mesa 04", "2", "Bs 24,00", "En preparación"),
                ("P-1047", "Mesa 02", "3", "Bs 38,50", "Pendiente"),
                ("P-1046", "Para llevar", "1", "Bs 14,00", "Listo")],

    "Mesas": [("Mesa 01", "2 personas", "Disponible", "—"),
              ("Mesa 02", "4 personas", "Ocupada", "P-1047"),
              ("Mesa 03", "2 personas", "Disponible", "—"),
              ("Mesa 04", "4 personas", "Ocupada", "P-1048")],

    "Stock": [("ST-01", "Carne de res", "Carnes", "8 kg", "Normal"),
              ("ST-02", "Tomate", "Verduras", "3 kg", "Bajo"),
              ("ST-03", "Queso", "Lácteos", "6 kg", "Normal")],

    "Usuarios": [("U-001", "Ana Pérez", "Administradora", "ana@restaurante.com", "Activo"),
                 ("U-002", "Luis Rojas", "Cajero", "luis@restaurante.com", "Activo"),
                 ("U-003", "Marta Solís", "Mesera", "marta@restaurante.com", "Inactivo")],

    "Ventas": [("V-2081", "12:42", "Ana Pérez", "Mesa 04", "Bs 24,00", "Efectivo"),
               ("V-2080", "12:37", "Luis Rojas", "Mesa 02", "Bs 38,50", "Tarjeta"),
               ("V-2079", "12:31", "Ana Pérez", "Para llevar", "Bs 14,00", "QR")]
}

    ventana_principal.columnconfigure(1, weight=1)
    ventana_principal.rowconfigure(0, weight=1)


    panel_lateral = ttk.Frame(ventana_principal, padding=(16, 20))
    panel_lateral.grid(row=0, column=0, sticky="ns")
    panel_lateral.columnconfigure(0, weight=1)

    ttk.Label(panel_lateral, text="RESTAURANTE", font=("TkDefaultFont", 15, "bold")).grid(row=0, column=0, sticky="w")

    ttk.Label(panel_lateral, text="PANEL DE GESTIÓN").grid(row=1, column=0, sticky="w", pady=(4, 20))
    ttk.Separator(panel_lateral).grid(row=2, column=0, sticky="ew", pady=(0, 14))
    ttk.Label(panel_lateral, text="MÓDULOS", font=("TkDefaultFont", 9, "bold")).grid(row=3, column=0, sticky="w", pady=(0, 8))

    modulos = ("Resumen", "Menús", "Pedidos", "Mesas", "Finanzas", "Stock", "Usuarios", "Ventas")

    for numero_fila, nombre_modulo in enumerate(modulos, start=4):
        boton = ttk.Button(panel_lateral, text=nombre_modulo,
                          command=lambda nombre=nombre_modulo: mostrar_modulo(nombre))
        boton.grid(row=numero_fila, column=0, sticky="ew", pady=2, ipady=4)

    panel_principal = ttk.Frame(ventana_principal, padding=(24, 20))
    panel_principal.grid(row=0, column=1, sticky="nsew")
    panel_principal.columnconfigure(0, weight=1)
    panel_principal.rowconfigure(1, weight=1)

    encabezado = ttk.Frame(panel_principal)
    encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 18))
    encabezado.columnconfigure(0, weight=1)

    def limpiar_contenedor(contenedor):
        for control in contenedor.winfo_children():
            control.destroy()

    def dibujar_encabezado(titulo, subtitulo, texto_boton=None, accion_boton=None):
        limpiar_contenedor(encabezado)
        bloque_titulo = ttk.Frame(encabezado)
        bloque_titulo.grid(row=0, column=0, sticky="w")
        ttk.Label(bloque_titulo, text=titulo, font=("TkDefaultFont", 21, "bold")).pack(anchor="w")
        ttk.Label(bloque_titulo, text=subtitulo).pack(anchor="w", pady=(4, 0))
        if texto_boton:
            ttk.Button(encabezado, text=texto_boton, command=accion_boton).grid(row=0, column=1, sticky="e")

    def dibujar_tabla(contenedor, nombres_columnas, filas, altura=9):
        marco_tabla = ttk.Frame(contenedor)
        marco_tabla.pack(fill="both", expand=True)
        marco_tabla.columnconfigure(0, weight=1)
        marco_tabla.rowconfigure(0, weight=1)
        tabla = ttk.Treeview(marco_tabla, columns=nombres_columnas, show="headings", height=altura)

        for indice, nombre in enumerate(nombres_columnas):
            tabla.heading(nombre, text=nombre)
            tabla.column(nombre, width=90 if indice == 0 else 140, anchor="w")
        barra = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        
        for fila in filas:
            tabla.insert("", "end", values=fila)
        return tabla

    def mostrar_formulario(modulo, valores=None):
        formulario = tk.Toplevel(ventana_principal)
        formulario.title("Editar registro" if valores else "Nuevo registro · " + modulo)
        formulario.transient(ventana_principal)

        cuerpo = ttk.Frame(formulario, padding=18)
        cuerpo.pack(fill="both", expand=True)
        campos_por_modulo = {"Menús": ("Nombre", "Categoría", "Precio", "Estado"),
                            "Pedidos": ("Mesa o canal", "Cantidad", "Total", "Estado"),
                            "Mesas": ("Nombre", "Capacidad", "Estado", "Área"),
                            "Stock": ("Producto", "Categoría", "Cantidad", "Mínimo"),
                            "Usuarios": ("Nombre", "Rol", "Correo", "Estado"),
                            "Ventas": ("Pedido", "Vendedor", "Método de pago", "Total")}
        campos = campos_por_modulo.get(modulo, ("Desde", "Hasta", "Tipo de reporte"))

        for fila, etiqueta in enumerate(campos):
            ttk.Label(cuerpo, text=etiqueta).grid(row=fila, column=0, sticky="w", padx=(0, 12), pady=5)
            entrada = ttk.Entry(cuerpo, width=30)
            entrada.grid(row=fila, column=1, sticky="ew", pady=5, ipady=3)

            if valores and fila < len(valores):
                entrada.insert(0, valores[fila])

        botones = ttk.Frame(cuerpo)
        botones.grid(row=len(campos), column=0, columnspan=2, sticky="e", pady=(14, 0))
        ttk.Button(botones, text="Cancelar", command=formulario.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(botones, text="Guardar", command=lambda: guardar_ejemplo(formulario)).pack(side="right")

    def guardar_ejemplo(formulario):
        formulario.destroy()
        messagebox.showinfo("Formulario de ejemplo", "La interfaz está lista. Aquí conectarías el guardado real.")

    def ver_detalle(tabla):
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showinfo("Selecciona una fila", "Haz clic en un registro de la tabla primero.")
            return
        valores = tabla.item(seleccion[0], "values")
        messagebox.showinfo("Detalle del registro", "\n".join(str(valor) for valor in valores))

    def dibujar_acciones(tabla):
        acciones = ttk.Frame(area_contenido)
        acciones.pack(fill="x", pady=(10, 0))

        ttk.Label(acciones, text="Selecciona una fila para ver o editar el registro.").pack(side="left")
        ttk.Button(acciones, text="Ver detalle", command=lambda: ver_detalle(tabla)).pack(side="right")
        ttk.Button(acciones, text="Editar", command=lambda: editar_seleccion(tabla)).pack(side="right", padx=7)
        ttk.Button(acciones, text="Eliminar", command=lambda: eliminar_seleccion(tabla)).pack(side="right")

    def editar_seleccion(tabla):
        seleccion = tabla.selection()
        if seleccion:
            valores = tabla.item(seleccion[0], "values")
            mostrar_formulario(modulo_actual, valores)
        else:
            messagebox.showinfo("Selecciona una fila", "Haz clic en un registro antes de editar.")

    def eliminar_seleccion(tabla):
        seleccion = tabla.selection()
        if seleccion:
            confirmar = messagebox.askyesno("Confirmar", "¿Quitar este registro de la tabla de ejemplo?")
            if confirmar:
                tabla.delete(seleccion[0])
        else:
            messagebox.showinfo("Selecciona una fila", "Haz clic en un registro antes de eliminar.")

    def dibujar_indicadores(contenedor, indicadores):
        fila_tarjetas = ttk.Frame(contenedor)
        fila_tarjetas.pack(fill="x", pady=(0, 14))
        for titulo, valor, nota in indicadores:
            tarjeta = ttk.LabelFrame(fila_tarjetas, text=titulo, padding=12)
            tarjeta.pack(side="left", fill="both", expand=True, padx=5)
            ttk.Label(tarjeta, text=valor, font=("TkDefaultFont", 17, "bold")).pack(anchor="w")
            ttk.Label(tarjeta, text=nota).pack(anchor="w", pady=(4, 0))

    def dibujar_barra_filtros(contenedor, filtros):
        barra = ttk.Frame(contenedor)
        barra.pack(fill="x", pady=(0, 12))
        ttk.Label(barra, text="Buscar:").pack(side="left", padx=(0, 6))
        ttk.Entry(barra, width=24).pack(side="left", padx=(0, 14), ipady=3)

        for nombre, opciones in filtros:
            ttk.Label(barra, text=nombre + ":").pack(side="left", padx=(0, 5))
            lista = ttk.Combobox(barra, values=opciones, state="readonly", width=14)
            lista.current(0)
            lista.pack(side="left", padx=(0, 12))

    def dibujar_pantalla_crud(titulo, descripcion, columnas, filas, filtros, texto_nuevo):
        dibujar_encabezado(titulo, descripcion, "+  " + texto_nuevo,
                        lambda: mostrar_formulario(modulo_actual))
        dibujar_barra_filtros(area_contenido, filtros)
        caja_tabla = ttk.LabelFrame(area_contenido, text="Registros", padding=10)
        caja_tabla.pack(fill="both", expand=True)
        tabla = dibujar_tabla(caja_tabla, columnas, filas)
        dibujar_acciones(tabla)

    def dibujar_resumen():
        dibujar_encabezado("Resumen del restaurante", "Vista general de la operación de hoy",
                        "+  Registrar venta", lambda: mostrar_modulo("Ventas"))
        dibujar_indicadores(area_contenido, (("VENTAS DE HOY", "Bs 2.480,50", "31 transacciones"),
                                            ("PEDIDOS ACTIVOS", "12", "3 requieren atención"),
                                            ("MESAS DISPONIBLES", "5", "de 12 mesas"),
                                            ("STOCK BAJO", "2 productos", "Revisar inventario")))
        recientes = ttk.LabelFrame(area_contenido, text="Pedidos recientes", padding=10)
        recientes.pack(fill="both", expand=True)
        dibujar_tabla(recientes, ("Pedido", "Mesa", "Artículos", "Total", "Estado"), datos["Pedidos"], altura=6)

    def dibujar_mesas():
        dibujar_encabezado("Mesas", "Consulta la disponibilidad y ocupación del salón",
                        "+  Nueva mesa", lambda: mostrar_formulario("Mesas"))
        dibujar_indicadores(area_contenido, (("TOTAL", "12", "Salón y terraza"),
                                            ("DISPONIBLES", "5", "Listas para asignar"),
                                            ("OCUPADAS", "6", "En servicio"),
                                            ("RESERVADAS", "1", "Próxima: 13:30")))
        caja_mesas = ttk.LabelFrame(area_contenido, text="Estado de mesas", padding=10)
        caja_mesas.pack(fill="both", expand=True)
        tabla = dibujar_tabla(caja_mesas, ("Mesa", "Capacidad", "Estado", "Pedido o reserva"), datos["Mesas"])
        dibujar_acciones(tabla)

    def dibujar_finanzas():
        dibujar_encabezado("Finanzas", "Reportes de ingresos y gastos por periodo",
                        "Exportar reporte", lambda: messagebox.showinfo("Reporte", "Aquí conectarías la exportación."))
        dibujar_barra_filtros(area_contenido, (("Periodo", ("Este mes", "Hoy", "Esta semana", "Personalizado")),
                                            ("Tipo", ("Todos", "Ventas", "Gastos"))))
        dibujar_indicadores(area_contenido, (("INGRESOS", "Bs 48.260,00", "Periodo seleccionado"),
                                            ("GASTOS", "Bs 18.450,00", "Costos registrados"),
                                            ("UTILIDAD NETA", "Bs 29.810,00", "Resultado del periodo")))
        caja_reporte = ttk.LabelFrame(area_contenido, text="Ventas por método de pago", padding=10)
        caja_reporte.pack(fill="both", expand=True)
        dibujar_tabla(caja_reporte, ("Método", "Transacciones", "Total"),
                    (("Efectivo", "186", "Bs 14.820,00"), ("Tarjeta", "224", "Bs 26.540,00"),
                    ("QR", "83", "Bs 6.900,00")), altura=6)

    def dibujar_usuarios():
        dibujar_encabezado("Usuarios", "Usuarios del restaurante (se guardan en menu.json).",
                                   "Administrar usuarios", administrar_usuarios)
        caja_menu = ttk.LabelFrame(area_contenido, text="Usuarios", padding=10)
        caja_menu.pack(fill="both", expand=True)
        filas = [(p["id"], p["nombre"], p["categoria"].capitalize(), p["estado"])
                for p in cargar_usuarios()]
        dibujar_tabla(caja_menu, ("ID", "Nombre", "Categoría", "Estado"), filas, altura=12)


    def administrar_menu():
        """Abre la ventana del menú real y, al cerrarla, vuelve a dibujar la tabla."""
        ventana_menu = abrir_menu(ventana_principal, es_admin=True)

        def al_cerrar(evento):

            if evento.widget is not ventana_menu or modulo_actual != "Menús":
                return
            try:
                mostrar_modulo("Menús")
            except tk.TclError:
                pass    # el panel se estaba cerrando al mismo tiempo: nohay nada que redibujar

        ventana_menu.bind("<Destroy>", al_cerrar)





    def administrar_usuarios():
        """Abre la ventana del menú real y, al cerrarla, vuelve a dibujar la tabla."""
        ventana_usuarios = abrir_usuarios(ventana_principal, es_admin=True)
        
        def al_cerrar(evento):
                    
            if evento.widget is not ventana_usuarios or modulo_actual != "Usuarios":
                return
            try:
                mostrar_modulo("Usuarios")
            except tk.TclError:
                pass    # el panel se estaba cerrando al mismo tiempo: no hay nada que redibujar
        ventana_usuarios.bind("<Destroy>", al_cerrar)

    def dibujar_menus():
        dibujar_encabezado("Menús", "Productos del restaurante (se guardan en menu.json).",
                           "Administrar menú", administrar_menu)
        caja_menu = ttk.LabelFrame(area_contenido, text="Productos", padding=10)
        caja_menu.pack(fill="both", expand=True)
        filas = [(p["id"], p["nombre"], p["categoria"].capitalize(), f"Bs {p['precio']:.2f}")
                 for p in cargar_menu()]
        dibujar_tabla(caja_menu, ("ID", "Nombre", "Categoría", "Precio"), filas, altura=12)

    def mostrar_modulo(nombre):
        nonlocal modulo_actual, area_contenido, encabezado
        modulo_actual = nombre
        limpiar_contenedor(panel_principal)

        encabezado = ttk.Frame(panel_principal)
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        encabezado.columnconfigure(0, weight=1)

        area_contenido = ttk.Frame(panel_principal)
        area_contenido.grid(row=1, column=0, sticky="nsew")
        area_contenido.columnconfigure(0, weight=1)
        area_contenido.rowconfigure(0, weight=1)

        if nombre == "Resumen":
            dibujar_resumen()
        elif nombre == "Menús":
            dibujar_menus()
        elif nombre == "Pedidos":
            dibujar_pantalla_crud("Pedidos", "Administra pedidos y revisa su estado de preparación.",
                                ("Pedido", "Mesa o canal", "Artículos", "Total", "Estado"), datos["Pedidos"],
                                (("Estado", ("Todos", "Pendiente", "En preparación", "Listo", "Entregado")),), "Nuevo pedido")
        elif nombre == "Mesas":
            dibujar_mesas()
        elif nombre == "Finanzas":
            dibujar_finanzas()
        elif nombre == "Stock":
            dibujar_pantalla_crud("Stock", "Controla existencias y productos por debajo del mínimo.",
                                ("Código", "Producto", "Categoría", "Cantidad", "Estado"), datos["Stock"],
                                (("Categoría", ("Todas", "Carnes", "Verduras", "Lácteos")),
                                ("Estado", ("Todos", "Normal", "Bajo"))), "Nuevo producto")
        elif nombre == "Usuarios":
            dibujar_usuarios()
        elif nombre == "Ventas":
            dibujar_pantalla_crud("Ventas", "Consulta transacciones y registra nuevas ventas.",
                                ("Venta", "Hora", "Vendedor", "Origen", "Total", "Pago"), datos["Ventas"],
                                (("Fecha", ("Hoy", "Ayer", "Esta semana")),
                                ("Método", ("Todos", "Efectivo", "Tarjeta", "QR"))), "Registrar venta")
    mostrar_modulo("Resumen")
    return ventana_principal
