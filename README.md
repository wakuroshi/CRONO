# Crono app

## Run the app

### uv

Resolución Global: CRONO evalúa todas las carreras simultáneamente para evitar choques entre materias, permitiendo materias compartidas entre carreras.

Basado en Restricciones (CP-SAT): Utiliza lógica matemática avanzada para garantizar que el horario entregado sea 100% factible.

Optimización de "Huecos": Implementa una función objetivo que penaliza las horas libres entre clases y los patrones de horarios fragmentados (ventanas).

Modularidad JSON: Entrada y salida de datos totalmente en formato JSON para facilitar la integración con algun frontend.

## 🛠️ Requisitos Técnicos

Python 3.8 o superior
Google OR-Tools

Para instalar las dependencias:

```bash
uv run flet run
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

For more details on running the app, refer to the [Getting Started Guide](https://flet.dev/docs/).

--help (-h): Muestra ayuda.

### Android

--mallas_dir: La carpeta de las mallas curriculares (default: ./data/mallas/)

For more details on building and signing `.apk` or `.aab`, refer to the [Android Packaging Guide](https://flet.dev/docs/publish/android/).

### iOS

```bash
flet build ipa -v
```

- GUI

```bash
flet build macos -v
```

For more details on building macOS package, refer to the [macOS Packaging Guide](https://flet.dev/docs/publish/macos/).

### Linux

```bash
flet build linux -v
```

For more details on building Linux package, refer to the [Linux Packaging Guide](https://flet.dev/docs/publish/linux/).

### Windows

```bash
flet build windows -v
```

For more details on building Windows package, refer to the [Windows Packaging Guide](https://flet.dev/docs/publish/windows/).

### Web

```bash
flet build web -v
```

For more details on building Web app, refer to the [Web Packaging Guide](https://flet.dev/docs/publish/web/).
