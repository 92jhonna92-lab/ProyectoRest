import json
import os

def login(nombre_usuario,contraseña):
    return nombre_usuario=="admin" and contraseña=="admin"

def loginC(nombre_usuario,contraseña):
    return nombre_usuario=="user" and contraseña=="user"
