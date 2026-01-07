import argparse
import json
import sys
from pathlib import Path
from solver import solve_global_career

def cargar_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en {path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: El archivo {path} no tiene un formato JSON válido.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generador de Horarios Globales")
    parser.add_argument("--career", required=True, help="Nombre del archivo de carrera en data/ (ej: ING_COMPUTACION.json)")
    parser.add_argument("--period", required=True, help="ID del periodo en data/periodos/ (ej: 2026-1CR)")
    parser.add_argument("--time-limit", type=int, default=60, help="Tiempo máximo para el solver (segundos)")
    
    args = parser.parse_args()

    # Definicion de rutas
    base_path = Path(__file__).parent
    career_path = base_path / "data" / args.career
    period_dir = base_path / "data" / "periodos" / args.period
    assignments_path = period_dir / "assignments.json"
    availability_path = period_dir / "availability.json"
    output_dir = base_path / "outputs"
    output_dir.mkdir(exist_ok=True)

    # Carga de archivos
    print(f"Cargando datos para {args.career}...")
    career_data = cargar_json(career_path)
    assignments = cargar_json(assignments_path)
    availability = cargar_json(availability_path)

    print(f"Iniciando resolucion global para el periodo {args.period}...")
    
    # Call al solver para que interprete la data 
    resultados_globales = solve_global_career(
        career_data, 
        availability, 
        assignments, 
        time_limit=args.time_limit
    )

    if not resultados_globales:
        print("No se pudo encontrar una solución óptima o factible.")
        return

    # Guardar resultados por semestre
    for sem_num, materias in resultados_globales.items():
        output_file = output_dir / f"{Path(args.career).stem}_{args.period}_semestre_{sem_num}.json"
        
        data_final = {
            "carrera": career_data["career"],
            "periodo": args.period,
            "semestre": sem_num,
            "materias": materias
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_final, f, indent=2, ensure_ascii=False)
        
        print(f"Archivo generado: {output_file.name}")

    print("\nProceso completado exitosamente.")

if __name__ == "__main__":
    main()
