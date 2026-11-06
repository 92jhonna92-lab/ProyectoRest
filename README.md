# ProyectoRest - Sistema de Restaurante

Sistema de gestión de restaurante desarrollado en Python con interfaz gráfica Tkinter.

## Ejecución
Ejecuta `main.py` para iniciar la aplicación.

## Módulos principales
- `pantalla_Login.py`: inicio de sesión.
- `administrador.py`: panel de administración.
- `pantalla_usuario.py`: pantalla del mesero (nuevo pedido, mis pedidos, menú).
- `pedidos_mesero.py`: lógica de los pedidos del mesero (crear, cambiar de estado, cobrar).
- `ventana_mesero.py`: ventanas para tomar un pedido y ver mis pedidos.
- `menu.py`: gestión y consulta del menú.
- `usuarios.py`: gestión de usuarios.
- `categorias.py`: gestión de categorías.

## Roles
- **Administrador**: gestiona menú, usuarios, categorías, pedidos, mesas, ventas y stock
- **Mesero**: toma pedidos (por mesa o para llevar), los marca como entregados o cancelados y los cobra. Al cobrar se registra la venta automáticamente.

Usuario inicial: `admin` / `admin`. El administrador crea los meseros desde Usuarios

## Datos
Los archivos JSON almacenan los datos del proyecto
