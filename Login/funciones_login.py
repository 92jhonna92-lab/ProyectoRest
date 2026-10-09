import administrador, usuario

def login(usuario,contraseña):
    return usuario=="admin" and contraseña=="admin"

def loginC(usuario,contraseña):
    return usuario=="user" and contraseña=="user"