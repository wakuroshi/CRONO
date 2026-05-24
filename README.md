# CRONO - v1.0

> **Constraint-based Rostering Organizer for Nodal Optimization**

CRONO es un motor de optimización de horarios basado en **Programación por Restricciones (Constraint Programming)**. Diseñado de forma agnóstica a la infraestructura, utilizando **Google OR-Tools (CP-SAT)** para modelar y resolver problemas combinatorios masivos de asignación de bloques horarios.

El motor evalúa de forma simultánea múltiples mallas curriculares, dependencias de entidades y ventanas operativas, garantizando soluciones 100% factibles mientras minimiza funciones de costo complejas (ventanas muertas, dispersión de tareas y fatiga de jornadas).

---

## Características Clave de la v1.0

* **Arquitectura de Persistencia Híbrida:** Capacidad de operar de forma aislada mediante sistemas de archivos locales (`JSON`) o en entornos de red distribuidos mediante conectividad nativa a bases de datos relacionales (`PostgreSQL` con tipos binarios `JSONB`).
* **Optimización Parametrizada Dinámica:** Control total de los pesos de las penalizaciones (*soft constraints*) y umbrales de días objetivos mediante archivos de configuración personalizados para cada periodo `config.json`) sin necesidad de recompilar el modelo matemático.
* **Modelo SAT de Continuidad Temporal:** Algoritmos internos dedicados a forzar la asignación contigua de bloques de una misma tarea dentro del mismo día, eliminando fragmentaciones absurdas.
* **Hilos de Ejecución Eficientes:** Optimización del espacio de búsqueda que reduce problemas combinatorios de miles de variables a resoluciones en milisegundos bajo el motor CP-SAT.

---

## Instalación

```bash
git clone https://codeberg.org/wirtnel/CRONO
cd CRONO
python -m venv .venv
source .venv/bin/activate
pip install requirements.txt
```

## Uso

CRONO v1.0 expande su usabilidad CLI para dos modos de uso según la infraestructura:

* **`--periodo <ID>` (Requerido):** Establece el contexto de tiempo para la ejecución. 
  * *En modo de producción:* Actúa como clave primaria (`PK`) para consultar las tablas `schedule_periods` y `entities_metadata`.
  * *En modo local:* Define el nombre de la carpeta dentro de `data/periodos/` desde donde se cargarán los archivos JSON.

* **`--local` (Opcional):** Modifica el backend de entrada/salida del pipeline. Al activarse, el motor entra en un modo aislado, omitiendo por completo la validación de variables de entorno y el socket de red hacia PostgreSQL, forzando la lectura y escritura directamente en el sistema de archivos local (`data/`).

* **`--estructuras_dir <PATH>` (Opcional | Por defecto: `data/estructuras`):** Especifica el directorio físico donde residen los payloads de las mallas curriculares en formato JSON. *Nota: Este parámetro es ignorado en el modo de producción, ya que las mallas se extraen dinámicamente de la base de datos relacional.*

* **`--prereq` (Opcional | Experimental):** *[WIP]* Activa de forma explícita la optimización del flujo y ordenamiento de precedencia académica. Fuerza al solucionador a evaluar las dependencias de prelación entre asignaturas antes de fijar las variables booleanas en la matriz de asignación.

Para usar el modo DB (predeterminado), recomiendo trabajar con podman, usando de referencia [container-compose.yml](./container-compose.yml) para la creacion de la base de datos. Una base pre-hecha para pruebas esta en [init.sql](./infra/init.sql). Se proporciono un .env de ejemplo en [example.env](./example.env), simplemente renombralo a .env si quieres usar la DB de testeo.

---

## Layout del Proyecto

```
CRONO/
├── data/
│   ├── estructuras/                # Mallas curriculares agnósticas (Ej: ING_COMPUTACION.json)
│   └── periodos/                   # Periodos de tiempo
│       ├── availability.json       # Ventanas de disponibilidad de entidades
│       └── task_dependencies.json  # Grafo dirigido de dependencias (Tarea -> Recurso)
├── outputs/                        # Matrices calculadas resultantes (Respaldos JSON locales)
├── infra/                          # Directorio para todo lo relacionado con SQL (WIP)
│    └──init.sql                    # init para el sql de testeo.
├── main.py                         # Pipeline principal y orquestador de entornos de ejecución
├── container-compose.yml           # Composer para la DB.
└── solver.py                       # El "Cerebro" del sistema (Modelo CP-SAT de OR-Tools)

```

# TO-DO
- [ ] (WIP) Finalizar CRONO[S]tudio, la implementación GUI first-party de CRONO. (https://codeberg.org/CausedCrawdad/Crono-Studio)
- [ ] (WIP) Implementar totalmente flag --prereq que beneficia el solapamiento de tareas con su prerequisitos.
- [ ] Bloques estáticos fijados por el usuario para bloquear horas fijas para ciertas tareas antes de que el solver optimice el resto del espacio.
