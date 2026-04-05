from datetime import datetime

# Constantes para la construccion de la tabla de horario
horario = ["Horas", "Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
hour = "7:00 AM"
object_hour = datetime.strptime(hour, "%I:%M %p")
class_time = 45
columns = []
rows = []

MATERIAS_DATA = {
    "EFS01202": "Educación Física",
    "GAN01404": "Geometría Analítica",
    "LOG01404": "Lógica",
    "MAI01506": "Matemática I",
    "VEC01202": "Venezuela Contemporánea",
    "ALI02304": "Álgebra Lineal",
    "CIN02303": "Cálculo Integral",
    "FIS02405": "Física I",
    "GDS02203": "Geometría Descriptiva",
    "MAI02506": "Matemática II",
    "PRO02305": "Programación I",
    "ING03303": "Inglés",
    "EDI03304": "Estructuras Discretas I",
    "FIS03405": "Física II",
    "IIN03202": "Introducción a la Ingeniería",
    "MAI03304": "Matemática III",
    "PRO03305": "Programación II",
    "PRO04405": "Programación III",
    "DIB03204": "Dibujo",
}
