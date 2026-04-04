import json
import argparse
from pathlib import Path
from solver import solve_university_model, TimeConfig

def cargar_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # Argumentos del parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--mallas_dir", default="data/mallas")
    parser.add_argument("--periodo", required=True)
    args = parser.parse_args()

    # CONFIG DIAS Y BLOQUES POR DIA
    config = TimeConfig(
        dias=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
        slots_por_dia=10
    )


    # Estructura de directorios
    base_path = Path(__file__).parent
    period_path = base_path / "data" / "periodos" / args.periodo
    
    availability = cargar_json(period_path / "availability.json")
    assignments = cargar_json(period_path / "assignments.json")
    
    # Cargar todas las mallas de la carpeta
    careers_payload = {}
    mallas_path = base_path / args.mallas_dir
    for file_path in mallas_path.glob("*.json"):
        data = cargar_json(file_path)
        careers_payload[data["career"]] = data

    print(f"Resolviendo modelo para {len(careers_payload)} carreras...")
    resultados = solve_university_model(careers_payload, availability, assignments, config)

    if resultados:
        output_base = base_path / "outputs"
        for career_name, semestres in resultados.items():
            career_tag = career_name.replace(" ", "_").upper()
            career_dir = output_base / career_tag
            career_dir.mkdir(parents=True, exist_ok=True)
            
            for sem_num, materias in semestres.items():
                filename = f"{career_tag}_{args.periodo}_SEM_{sem_num}.json"
                with open(career_dir / filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        "career": career_name,
                        "period": args.periodo,
                        "semester": sem_num,
                        "results": materias
                    }, f, indent=2, ensure_ascii=False)
        print("Archivos generados correctamente.")

if __name__ == "__main__":
    main()
