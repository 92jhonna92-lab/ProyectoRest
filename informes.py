"""Informes del restaurante: solo cálculos, sin ventanas ni archivos.

Cada función recibe los datos ya cargados (listas de pedidos, ventas, menú...) y
devuelve el resultado. Así se pueden probar solas (ver test_informes.py) y el
Resumen del dashboard solo tiene que dibujarlos.
"""
import re

# Un pedido cuenta como "vendido" cuando ya se entregó o se cobró.
ESTADOS_VENDIDOS = ("Entregado", "Cobrado")
# Un pedido está "activo" mientras todavía hay que atenderlo.
ESTADOS_ACTIVOS = ("Pendiente", "En preparación", "Listo")


def lineas_de_pedido(pedido):
    """Qué productos lleva un pedido: lista de (nombre, cantidad, precio).

    Los pedidos del mesero traen "items" con el precio de ese momento. Los que escribió
    el administrador solo traen texto ('2x Silpancho, 1x Refresco'): se separa el texto
    y el precio queda en None (se buscará en el menú).
    """
    if pedido.get("items"):
        return [(i["nombre"], i["cantidad"], i["precio"]) for i in pedido["items"]]
    lineas = []
    for trozo in str(pedido.get("articulos", "")).split(","):
        coincide = re.match(r"^\s*(\d+)\s*x\s+(.+?)\s*$", trozo, re.IGNORECASE)
        if coincide:
            lineas.append((coincide.group(2), int(coincide.group(1)), None))
    return lineas


def ranking_productos(pedidos, menu):
    """Productos del menú ordenados del más al menos vendido.

    Devuelve una lista de (nombre, cantidad vendida, total en Bs). Los productos que
    no se vendieron salen al final con 0, así se ve cuál es el menos vendido.
    """
    precios = {p["nombre"].strip().lower(): p["precio"] for p in menu}
    nombres = {p["nombre"].strip().lower(): p["nombre"].strip() for p in menu}
    cantidades = {clave: 0 for clave in nombres}
    montos = {clave: 0.0 for clave in nombres}

    for pedido in pedidos:
        if pedido.get("estado") not in ESTADOS_VENDIDOS:
            continue
        for nombre, cantidad, precio in lineas_de_pedido(pedido):
            clave = nombre.strip().lower()
            nombres.setdefault(clave, nombre.strip())     # producto que ya no está en el menú
            if precio is None:
                precio = precios.get(clave, 0.0)
            cantidades[clave] = cantidades.get(clave, 0) + cantidad
            montos[clave] = montos.get(clave, 0.0) + precio * cantidad

    filas = [(nombres[c], cantidades[c], round(montos[c], 2)) for c in cantidades]
    return sorted(filas, key=lambda f: (-f[1], f[0].lower()))


def ranking_vendedores(ventas):
    """Quién vendió más: lista de (vendedor, cantidad de ventas, total en Bs), de mayor a menor total."""
    cuentas, totales = {}, {}
    for v in ventas:
        cuentas[v["vendedor"]] = cuentas.get(v["vendedor"], 0) + 1
        totales[v["vendedor"]] = totales.get(v["vendedor"], 0.0) + v["total"]
    filas = [(nombre, cuentas[nombre], round(totales[nombre], 2)) for nombre in cuentas]
    return sorted(filas, key=lambda f: (-f[2], f[0].lower()))


def resumen_general(pedidos, ventas, mesas, stock):
    """Los cuatro números de arriba del Resumen."""
    activos = [p for p in pedidos if p.get("estado") in ESTADOS_ACTIVOS]
    return {
        "total_ventas": round(sum(v["total"] for v in ventas), 2),
        "cantidad_ventas": len(ventas),
        "pedidos_activos": len(activos),
        "pedidos_pendientes": sum(1 for p in activos if p["estado"] == "Pendiente"),
        "mesas_disponibles": sum(1 for m in mesas if m.get("estado") == "Disponible"),
        "mesas_total": len(mesas),
        "stock_bajo": [s["producto"] for s in stock if s.get("estado") == "Bajo"],
    }
