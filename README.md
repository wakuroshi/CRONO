# ⏱️ CRONO: Constraint-based Rostering Organizer for Nodal Optimization

CRONO es un motor de optimización de horarios académicos basado en restricciones (Constraint Programming). Utiliza el solver de Google OR-Tools para resolver el problema de asignación de bloques horarios, asegurando que no existan conflictos entre profesores, semestres o requisitos de infraestructura, mientras busca maximizar la comodidad del horario mediante penalizaciones inteligentes.

## 🚀 Características Principales

Resolución Global: CRONO evalúa todas las carreras simultáneamente para evitar choques entre materias, permitiendo materias compartidas entre carreras.

Basado en Restricciones (CP-SAT): Utiliza lógica matemática avanzada para garantizar que el horario entregado sea 100% factible.

Optimización de "Huecos": Implementa una función objetivo que penaliza las horas libres entre clases y los patrones de horarios fragmentados (ventanas).

Modularidad JSON: Entrada y salida de datos totalmente en formato JSON para facilitar la integración con algun frontend.

## 🛠️ Requisitos Técnicos

Python 3.8 o superior
Google OR-Tools

Para instalar las dependencias:

```bash
pip install ortools
```

## 📂 Estructura del Proyecto

```CRONO/
├── data/
│   ├── ING_COMPUTACION.json       # Definición de la malla curricular
│   └── periodos/
│       └── 2026-1CR/
│           ├── assignments.json    # Relación Materia-Profesor
│           └── availability.json   # Disponibilidad horaria de cada Prof.
├── outputs/                        # Horarios generados por semestre
├── main.py                         # Punto de entrada del script
└── solver.py                       # El "cerebro" (Lógica de OR-Tools)
```

## ⚙️ Cómo Funciona

CRONO procesa tres capas de datos para construir el modelo matemático:

Capa de Materias: Extrae la cantidad de bloques semanales necesarios por asignatura.

Capa de Profesores: Cruza la disponibilidad del docente con las materias asignadas.

Capa de Optimización: Evalúa billones de combinaciones posibles para encontrar una que cumpla con:

Hard Constraints: Ningún profesor puede estar en dos lugares a la vez; ninguna materia de un mismo semestre puede solaparse.

Soft Constraints: Minimizar bloques aislados (ej. una clase de 45 min rodeada de horas libres); minimizar uso de días para intentar dejarle al menos un día libre al estudiante.

## 🖥️ Uso

Para generar los horarios de un período:

```bash
python main.py --period 2026-1CR
```

### Parámetros:

--help (-h): Muestra ayuda.

--period: La carpeta del periodo académico actual.

--mallas_dir: La carpeta de las mallas curriculares (default: ./data/mallas/)

## 📄 Formato de Salida

El sistema generará archivos JSON individuales por cada semestre en la carpeta outputs/. Cada archivo contiene el detalle de las materias, el profesor asignado y los bloques específicos (día y hora).

## 🪡 TO-DO

- GUI

- Expandir versatilidad (generacion manual asistida en vez de solo automatica, parametrización del algoritmo y constraints)

