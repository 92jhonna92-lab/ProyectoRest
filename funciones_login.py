# los usuarios nuevos lo crea el admin con sus categorias
from usuarios import buscar_cuenta


def login(nombre_usuario, contraseña):
    
    return buscar_cuenta(nombre_usuario, contraseña)
