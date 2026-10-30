

import json
import os
import tkinter as tk
from tkinter import messagebox

ARCHIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "categorias.json")

INICIALES = {
    "menu": ["plato", "bebida", "postre"],
    "usuarios": ["Administrador", "Mesero", "Mascota"],
}



def _leer_todo():
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (OSError, json.JSONDecodeError):
        return {}


def cargar_categorias(tipo):
    """Lista de categorías de 'menu' o 'usuarios' (si no hay archivo, usa las iniciales)."""
    lista = _leer_todo().get(tipo)
    if not isinstance(lista, list) or not lista:
        lista = list(INICIALES[tipo])
    return lista


def guardar_categorias(tipo, lista):
    todo = _leer_todo()
    todo[tipo] = lista
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        json.dump(todo, archivo, indent=4, ensure_ascii=False)


def _buscar(lista, nombre):
    """Devuelve el nombre tal como está guardado (sin importar mayúsculas) o None."""
    for c in lista:
        if c.lower() == nombre.strip().lower():
            return c
    return None


def agregar_categoria(tipo, nombre):
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("Escribe el nombre de la categoría.")
    lista = cargar_categorias(tipo)
    if _buscar(lista, nombre):
        raise ValueError("Esa categoría ya existe.")
    lista.append(nombre)
    guardar_categorias(tipo, lista)


def renombrar_categoria(tipo, viejo, nuevo, items, guardar_items, protegidas=()):
    """Cambia el nombre y también el de todos los items que la usaban."""
    nuevo = nuevo.strip()
    if viejo in protegidas:
        raise ValueError(f"'{viejo}' no se puede renombrar: el sistema la necesita.")
    if not nuevo:
        raise ValueError("Escribe el nuevo nombre.")
    lista = cargar_categorias(tipo)
    otra = _buscar(lista, nuevo)
    if otra and otra != viejo:
        raise ValueError("Esa categoría ya existe.")
    lista = [nuevo if c == viejo else c for c in lista]
    guardar_categorias(tipo, lista)
    for item in items:
        if item["categoria"] == viejo:
            item["categoria"] = nuevo
    guardar_items(items)


def eliminar_categoria(tipo, nombre, items, protegidas=()):
    if nombre in protegidas:
        raise ValueError(f"'{nombre}' no se puede eliminar: el sistema la necesita.")
    usados = sum(1 for i in items if i["categoria"] == nombre)
    if usados:
        raise ValueError(f"No se puede eliminar: {usados} registro(s) usan '{nombre}'. "
                         "Cámbialos de categoría primero.")
    guardar_categorias(tipo, [c for c in cargar_categorias(tipo) if c != nombre])



def abrir_gestor_categorias(ventana_padre, tipo, titulo, cargar_items, guardar_items,
                            al_cambiar, protegidas=()):
    """Ventanita para agregar, renombrar y eliminar categorías.
    al_cambiar() se llama después de cada cambio para que la ventana de atrás se actualice."""
    ventana = tk.Toplevel(ventana_padre)
    ventana.title(titulo)
    ventana.geometry("340x420")
    ventana.configure(bg="snow")
    ventana.transient(ventana_padre)

    tk.Label(ventana, text=titulo, font=("Arial", 14), bg="snow").pack(pady=10)
    lista = tk.Listbox(ventana, height=9, exportselection=False)
    lista.pack(padx=20, fill=tk.BOTH, expand=True)

    tk.Label(ventana, text="Nombre", bg="snow").pack(pady=(10, 0))
    entrada = tk.Entry(ventana, width=25)
    entrada.pack(pady=4)

    def refrescar():
        lista.delete(0, tk.END)
        for c in cargar_categorias(tipo):
            lista.insert(tk.END, c + ("   (fija)" if c in protegidas else ""))
        al_cambiar()

    def seleccionada():
        sel = lista.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Primero selecciona una categoría de la lista.",
                                   parent=ventana)
            return None
        return cargar_categorias(tipo)[sel[0]]

    def al_elegir(evento):
        sel = lista.curselection()
        if sel:
            entrada.delete(0, tk.END)
            entrada.insert(0, cargar_categorias(tipo)[sel[0]])

    lista.bind("<<ListboxSelect>>", al_elegir)

    def ejecutar(accion):
        try:
            accion()
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=ventana)
            return
        entrada.delete(0, tk.END)
        refrescar()

    def agregar():
        ejecutar(lambda: agregar_categoria(tipo, entrada.get()))

    def renombrar():
        viejo = seleccionada()
        if viejo is not None:
            ejecutar(lambda: renombrar_categoria(tipo, viejo, entrada.get(),
                                                 cargar_items(), guardar_items, protegidas))

    def eliminar():
        nombre = seleccionada()
        if nombre is None:
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar la categoría '{nombre}'?",
                                   parent=ventana):
            return
        ejecutar(lambda: eliminar_categoria(tipo, nombre, cargar_items(), protegidas))

    botones = tk.Frame(ventana, bg="snow")
    botones.pack(pady=8)
    tk.Button(botones, text="Agregar", width=9, command=agregar).pack(side=tk.LEFT, padx=3)
    tk.Button(botones, text="Renombrar", width=9, command=renombrar).pack(side=tk.LEFT, padx=3)
    tk.Button(botones, text="Eliminar", width=9, command=eliminar).pack(side=tk.LEFT, padx=3)
    tk.Button(ventana, text="Cerrar", command=ventana.destroy).pack(pady=(0, 10))
    refrescar()
    return ventana
