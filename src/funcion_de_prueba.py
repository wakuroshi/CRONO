# Funcion que recibe una lista y pasa todo a json
import json as js
import os

# Constantes
directorio_actual = os.getcwd()
name = input("En que periodo estamos?")
datos = {}
ruta_atras = os.path.join(directorio_actual, "..", "data", "periodos", name)
ruta_atras = os.path.normpath(ruta_atras)


# Carga el json creado anteriormente con los datos del objeto profesor
def rec_prof(profesor):

    ruta_json = os.path.join(ruta_atras, "availability.json")

    try:
        os.makedirs(ruta_atras)
        with open(ruta_json, "x") as file:
            js.dump(datos, file, indent=0)
    except FileExistsError:
        print("error")

    data = {profesor.assigment: (list(profesor.blocks))}
    with open(ruta_json, "a") as file:
        js.dump(data, file, indent=2)
