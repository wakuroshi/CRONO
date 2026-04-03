from datetime import datetime

# Constantes para la construccion de la tabla de horario
horario = ["Horas", "Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]
hour = "7:00 AM"
object_hour = datetime.strptime(hour, "%I:%M %p")
class_time = 45
columns = []
filas_datos = []
