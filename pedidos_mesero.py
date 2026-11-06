"""Pedidos del mesero: solo la lógica y los datos, sin ventanas.

Usa el mismo archivo y el mismo formato que el módulo Pedidos del administrador
(pedidos.py), así los pedidos del mesero aparecen en el dashboard sin cambiar nada.

Un pedido del mesero se guarda en pedidos.json así:

    {
        "id": "P-1052",                    # igual que los del administrador
        "mesa": "Mesa 04",                 # mesa o canal ("Para llevar", "Delivery")
        "articulos": "2x Silpancho, 1x Refresco",
        "total": 80.0,
        "estado": "Pendiente",
        "mesero": "Zabala",                # datos extra (solo los pedidos del mesero)
        "fecha": "2026-11-05T19:30:00",
        "items": [{"id": 1, "nombre": "Silpancho", "precio": 35.0, "cantidad": 2}, ...]
    }

"items" guarda el precio de ESE momento: si luego se cambia el precio en el menú,
los informes viejos no se alteran. También es lo que permitirá el informe de lo
más y lo menos vendido.

Al cobrar un pedido se registra solo una venta en ventas.json.
"""
from datetime import datetime

import pedidos
import ventas

PENDIENTE, EN_PREPARACION, LISTO = "Pendiente", "En preparación", "Listo"
ENTREGADO, COBRADO, CANCELADO = "Entregado", "Cobrado", "Cancelado"

# Para pasar al estado de la izquierda, el pedido tiene que estar en uno de la derecha.
DESDE = {
    ENTREGADO: (PENDIENTE, EN_PREPARACION, LISTO),
    COBRADO: (ENTREGADO,),
    CANCELADO: (PENDIENTE, EN_PREPARACION, LISTO, ENTREGADO),
}


def hoy():
    return datetime.now().strftime("%Y-%m-%d")


def texto_articulos(items):
    """'2x Silpancho, 1x Refresco'"""
    return ", ".join(f"{i['cantidad']}x {i['nombre']}" for i in items)


def total_items(items):
    return round(sum(i["precio"] * i["cantidad"] for i in items), 2)


def siguiente_codigo(lista):
    """Código nuevo: P-<número siguiente>. Respeta los códigos que ya existen."""
    numeros = []
    for p in lista:
        texto = str(p["id"])
        if texto.startswith("P-") and texto[2:].isdigit():
            numeros.append(int(texto[2:]))
    return f"P-{max(numeros, default=1000) + 1}"


def crear_pedido(mesero, canal, items):
    """Guarda un pedido nuevo (queda Pendiente). Lanza ValueError si algo falla.

    items es una lista de {"id", "nombre", "precio", "cantidad"}.
    """
    if canal not in pedidos.CANALES_PEDIDO:
        raise ValueError("Elige la mesa o el canal del pedido.")
    if not items:
        raise ValueError("Agrega al menos un producto al pedido.")
    limpios = []
    for item in items:
        if item["cantidad"] <= 0:
            raise ValueError("Las cantidades deben ser mayores que cero.")
        limpios.append({"id": item["id"], "nombre": item["nombre"],
                        "precio": float(item["precio"]), "cantidad": int(item["cantidad"])})

    lista = pedidos.cargar_pedidos()
    pedido = {
        "id": siguiente_codigo(lista),
        "mesa": canal,
        "articulos": texto_articulos(limpios),
        "total": total_items(limpios),
        "estado": PENDIENTE,
        "mesero": mesero,
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "items": limpios,
    }
    lista.append(pedido)
    pedidos.guardar_pedidos(lista)
    return pedido


def origen_de_venta(canal):
    """Pasa el canal del pedido al 'origen' que usa el módulo Ventas."""
    return canal if canal in ("Para llevar", "Delivery") else "Salón"


def validar_cambio(id_pedido, nuevo_estado):
    """Lanza ValueError si el pedido no existe o no puede pasar a ese estado.
    La ventana lo usa ANTES de preguntar el método de pago."""
    for pedido in pedidos.cargar_pedidos():
        if pedido["id"] == id_pedido:
            if pedido["estado"] not in DESDE.get(nuevo_estado, ()):
                raise ValueError(f"Un pedido {pedido['estado'].lower()} no se puede pasar a "
                                 f"{nuevo_estado.lower()}.")
            return pedido
    raise ValueError("Ese pedido ya no existe.")


def cambiar_estado(id_pedido, nuevo_estado, pago=None):
    """Pasa un pedido a otro estado respetando el orden permitido.

    Al pasar a Cobrado hay que decir cómo se pagó (pago) y se registra una venta.
    """
    validar_cambio(id_pedido, nuevo_estado)
    lista = pedidos.cargar_pedidos()
    for pedido in lista:
        if pedido["id"] != id_pedido:
            continue
        if nuevo_estado == COBRADO:
            venta = ventas.agregar_venta(
                datetime.now().strftime("%H:%M"), pedido.get("mesero", "—"),
                origen_de_venta(pedido["mesa"]), str(pedido["total"]), pago or "")
            pedido["venta_id"] = venta["id"]
        pedido["estado"] = nuevo_estado
        pedidos.guardar_pedidos(lista)
        return pedido
    raise ValueError("Ese pedido ya no existe.")


def pedidos_de(mesero, fecha=None, estado=None):
    """Pedidos de un mesero, los más nuevos primero. fecha: 'AAAA-MM-DD' o None."""
    resultado = []
    for p in pedidos.cargar_pedidos():
        if p.get("mesero") != mesero:
            continue
        if fecha is not None and not p.get("fecha", "").startswith(fecha):
            continue
        if estado is not None and p["estado"] != estado:
            continue
        resultado.append(p)
    return list(reversed(resultado))
