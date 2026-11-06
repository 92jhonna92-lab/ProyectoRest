
import re


ESTADOS_VENDIDOS = ("Entregado", "Cobrado")

ESTADOS_ACTIVOS = ("Pendiente", "En preparación", "Listo")


def lineas_de_pedido(pedido):
  
    if pedido.get("items"):
        return [(i["nombre"], i["cantidad"], i["precio"]) for i in pedido["items"]]
    lineas = []
    for trozo in str(pedido.get("articulos", "")).split(","):
        coincide = re.match(r"^\s*(\d+)\s*x\s+(.+?)\s*$", trozo, re.IGNORECASE)
        if coincide:
            lineas.append((coincide.group(2), int(coincide.group(1)), None))
    return lineas


def ranking_productos(pedidos, menu):
    
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
    
    cuentas, totales = {}, {}
    for v in ventas:
        cuentas[v["vendedor"]] = cuentas.get(v["vendedor"], 0) + 1
        totales[v["vendedor"]] = totales.get(v["vendedor"], 0.0) + v["total"]
    filas = [(nombre, cuentas[nombre], round(totales[nombre], 2)) for nombre in cuentas]
    return sorted(filas, key=lambda f: (-f[2], f[0].lower()))


def resumen_general(pedidos, ventas, mesas, stock):
    
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
