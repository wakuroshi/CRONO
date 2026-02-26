import json


def Mod_Json(Nueva_hora):
    with open("json_de_prueba.json", "r") as file:
        data = json.load(file)

    Profesor = input("Por favor Introduce la catedra")
    while True:
        Nueva_hora = input("Introduce Una nueva hora  (Ejemplo: Lunes 8:00) :")
        if Nueva_hora.lower() == "salir":
            break

        data[Profesor].append(Nueva_hora)
        print(f"La {Nueva_hora} ha sido agregada con exito")

    with open("json_de_prueba.json", "w") as file:
        json.dump(data, file, indent=4)
