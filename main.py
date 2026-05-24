import os
import sys
import json
import csv
import psycopg
import argparse
from pathlib import Path
from dotenv import load_dotenv
from solver import solve_model, TimeConfig

# --- CONSTANTES INFRAESTRUCTURA DE DATOS ---
TABLA_TIEMPOS   = "time_contexts"
TABLA_ENTIDADES  = "model_entities"
TABLA_RESULTADOS = "solver_outputs"

def cargar_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def verificar_env(base_path: Path):
    env_path = base_path / ".env"

    if not env_path.exists():
        print(f"Error Crítico: Archivo de configuración local '.env' no encontrado.", file=sys.stderr)
        print(f"Se esperaba encontrarlo en la raíz: {env_path.resolve()}", file=sys.stderr)
        print("Por favor, crea el archivo con las credenciales de PostgreSQL antes de continuar.", file=sys.stderr)
        sys.exit(1)

    # Cargar forzando override
    load_dotenv(env_path, override=True)

    variables_requeridas = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD"]
    faltantes = [var for var in variables_requeridas if not os.getenv(var)]

    if faltantes:
        print(f"Error Crítico: El archivo .env existe pero tiene campos vacíos o corruptos.", file=sys.stderr)
        print(f"Faltan definir las siguientes variables: {', '.join(faltantes)}", file=sys.stderr)
        print("La ejecución se ha abortado.", file=sys.stderr)
        sys.exit(1)

    if faltantes:
        print(f"Error Crítico: El entorno de producción no está completamente definido.", file=sys.stderr)
        print(f"Faltan las siguientes variables de entorno: {', '.join(faltantes)}", file=sys.stderr)
        print("La ejecucion se ha abortado.", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--periodo", required=True, help="ID del periodo temporal de planificación.")
    parser.add_argument("--local", action="store_true", help="Activa el modo de prueba usando archivos JSON locales.")
    parser.add_argument("--estructuras_dir", default=None, help="Directorio de estructuras JSON. (Solo requerido en --local)")
    parser.add_argument("--prereq", action="store_true", help="Forzar solapamiento de prerrequisitos")

    args = parser.parse_args()
    base_path = Path(__file__).parent

    # Declaracion de variables de control que alimentaran al solver
    config = None
    solver_config = None
    availability = {}
    task_dependencies = {}
    estructuras_payload = {}

    # --- Entrada modo local (no DB) ---
    if args.local:
        print("--- MODO LOCAL: Cargando archivos JSON ---")

        ruta_estructuras = args.estructuras_dir if args.estructuras_dir else "data/estructuras"
        estructuras_path = base_path / ruta_estructuras

        if not estructuras_path.exists():
            print(f"Error: El directorio de estructuras '{estructuras_path}' no existe.", file=sys.stderr)
            sys.exit(1)

        periodo_path = base_path / "data" / "periodos" / args.periodo
        try:
            # Carga del archivo único de configuración del periodo
            conf_periodo = cargar_json(periodo_path / "config.json")

            config = TimeConfig(
                dias=conf_periodo["tiempo"]["dias"], 
                slots_por_dia=conf_periodo["tiempo"]["slots_por_dia"]
            )
            solver_config = conf_periodo["solver"]

            availability = cargar_json(periodo_path / "availability.json")
            task_dependencies = cargar_json(periodo_path / "task_dependencies.json")
        except FileNotFoundError as e:
            print(f"Error al cargar archivos del periodo local: {e}", file=sys.stderr)
            sys.exit(1)

        for file_path in estructuras_path.glob("*.json"):
            data = cargar_json(file_path)
            llave_grupo = data.get("career", data.get("estructura_nombre"))
            estructuras_payload[llave_grupo] = data

    # --- Entrada modo db ---
    else:
        print("--- MODO PRODUCCIÓN: Validando entorno y conectando a PostgreSQL ---")

        verificar_env(base_path)

        db_host = os.getenv("POSTGRES_HOST")
        db_port = os.getenv("POSTGRES_PORT")
        db_name = os.getenv("POSTGRES_DB")
        db_user = os.getenv("POSTGRES_USER")
        db_pass = os.getenv("POSTGRES_PASSWORD")

        conn_string = f"host={db_host} port={db_port} dbname={db_name} user={db_user} password={db_pass}"

        try:
            with psycopg.connect(conn_string) as conn:
                with conn.cursor() as cur:

                    # Consulta 1: Configuracion de tiempo
                    cur.execute(f"SELECT time_config FROM {TABLA_TIEMPOS} WHERE id = %s;", (args.periodo,))
                    period_row = cur.fetchone()
                    if not period_row:
                        print(f"Error: El periodo '{args.periodo}' no existe en la base de datos.", file=sys.stderr)
                        sys.exit(1)
                    t_data = period_row[0]
                    config = TimeConfig(dias=t_data["dias"], slots_por_dia=t_data["slots_por_dia"])
                    # Extraer parametros dinamicos si se expandio la columna o la estructura del JSONB
                    solver_config = t_data.get("solver")

                    # Consulta 2: Disponibilidad general
                    cur.execute(f"SELECT payload FROM {TABLA_ENTIDADES} WHERE period_id = %s AND entity_type = 'availability';", (args.periodo,))
                    availability = cur.fetchone()[0]

                    # Consulta 3: Dependencias de las tareas (WIP)
                    cur.execute(f"SELECT payload FROM {TABLA_ENTIDADES} WHERE period_id = %s AND entity_type = 'task_dependencies';", (args.periodo,))
                    task_dependencies = cur.fetchone()[0]

                    # Consulta 4: Estructuras
                    cur.execute(f"SELECT payload FROM {TABLA_ENTIDADES} WHERE period_id = %s AND entity_type = 'estructuras';", (args.periodo,))
                    mallas_rows = cur.fetchall()

                    for row in mallas_rows:
                        data = row[0]
                        llave_grupo = data.get("career", data.get("estructura_nombre"))
                        estructuras_payload[llave_grupo] = data

        except psycopg.OperationalError as e:
            print(f"Error crítico de conexión a la base de datos PostgreSQL: {e}", file=sys.stderr)
            sys.exit(1)

    # Ejecucion del modelo
    print(f"Resolviendo modelo para {len(estructuras_payload)} estructuras de datos...")
    resultados = solve_model(
        estructuras_data=estructuras_payload,
        availability=availability,
        task_dependencies=task_dependencies,
        config=config,
        solver_config=solver_config,
        force_prereq_overlap=args.prereq
    )

    # Persistencia de salidas en modo producción (JSONB)
    if resultados:
        if not args.local:
            try:
                with psycopg.connect(conn_string) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            f"INSERT INTO {TABLA_RESULTADOS} (period_id, status, results) VALUES (%s, %s, %s);",
                            (args.periodo, "OPTIMAL_OR_FEASIBLE", psycopg.types.json.Jsonb(resultados))
                        )
                        conn.commit()
                print("Resultados guardados de forma nativa en la base de datos (JSONB).")
            except psycopg.Error as e:
                print(f"Error al escribir resultados en DB: {e}", file=sys.stderr)

        # Generacion de archivos locales (Tanto para local como para respaldo en prod) - Formato CSV y json
        output_base = base_path / "outputs"
        for grupo_name, subgrupos in resultados.items():
            grupo_tag = grupo_name.replace(" ", "_").upper()
            grupo_dir = output_base / grupo_tag
            grupo_dir.mkdir(parents=True, exist_ok=True)

            for subgrupo_id, tareas in subgrupos.items():
                base_filename = f"{grupo_tag}_{args.periodo}_SUB_{subgrupo_id}"
                
                # 1. ESCRITURA DEL ARCHIVO JSON (Fidelidad de Objeto/Estructura Árbol)
                json_path = grupo_dir / f"{base_filename}.json"
                try:
                    with open(json_path, 'w', encoding='utf-8') as f_json:
                        json.dump({
                            "grupo_raiz": grupo_name,
                            "periodo": args.periodo,
                            "subgrupo": subgrupo_id,
                            "results": tareas
                        }, f_json, indent=2, ensure_ascii=False)
                except IOError as e:
                    print(f"Error de I/O al escribir el archivo JSON {base_filename}.json: {e}", file=sys.stderr)

                # 2. ESCRITURA DEL ARCHIVO CSV (Estructura Tabular Aplanada)
                csv_path = grupo_dir / f"{base_filename}.csv"
                try:
                    # 'newline=""' previene líneas en blanco intermedias debido al manejo de fin de línea (\r\n)
                    with open(csv_path, mode='w', newline='', encoding='utf-8') as f_csv:
                        writer = csv.writer(f_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        
                        # Escribir Cabecera (Esquema Tabular)
                        writer.writerow(["Grupo_Raiz", "Subgrupo", "Tarea_ID", "Tarea_Nombre", "Dependencia", "Recurso", "Dia", "Bloque_ID", "Index_Absoluto"])
                        
                        # Desenrollar el árbol en filas planas (Relación 1:N con los bloques de tiempo)
                        for tarea in tareas:
                            sid = tarea["id"]
                            nombre = tarea["nombre"]
                            dependencia = tarea["dependencia"] if tarea["dependencia"] else "Ninguna"
                            recurso = tarea["recurso"] if tarea["recurso"] else "No_Asignado"
                            
                            if tarea["horario"]:
                                for bloque in tarea["horario"]:
                                    writer.writerow([
                                        grupo_name,
                                        subgrupo_id,
                                        sid,
                                        nombre,
                                        dependencia,
                                        recurso,
                                        bloque["dia"],
                                        bloque["bloque_id"],
                                        bloque["index"]
                                    ])
                            else:
                                writer.writerow([grupo_name, subgrupo_id, sid, nombre, dependencia, recurso, "SIN_ASIGNAR", -1, -1])
                                
                except IOError as e:
                    print(f"Error de I/O al escribir el archivo CSV {base_filename}.csv: {e}", file=sys.stderr)
                    
        print("Estructuras de optimización exportadas exitosamente en formatos duales (.json y .csv).")

if __name__ == "__main__":
    main()
