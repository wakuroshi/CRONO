from ortools.sat.python import cp_model
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class TimeConfig:
    dias: List[str]
    slots_por_dia: int

def solve_university_model(careers_data: Dict, availability: Dict, assignments: Dict, config: TimeConfig):
    model = cp_model.CpModel()
    num_bloques = len(config.dias) * config.slots_por_dia
    all_vars = {}
    penalties = []

    print(f"--- Iniciando Modelo con Lógica de Compactación Corregida ---")

    # REGISTRO DE VARIABLES Y RESTRICCIONES DURAS
    for career_name, data in careers_data.items():
        for sem in data["semesters"]:
            sem_num = sem["number"]
            sem_vars = []
            
            for sub in sem["subjects"]:
                sid = sub["id"]
                n_blocks = sub["blocks"]
                
                if sid not in all_vars:
                    # PUNTERO UNICO (increible lol)
                    sub_vars = [model.NewBoolVar(f"v_{sid}_b{i}") for i in range(num_bloques)]
                    all_vars[sid] = sub_vars
                    
                    # Restriccion: Cumplir con la carga horaria
                    model.Add(sum(sub_vars) == n_blocks).WithName(f"Carga_{sid}")
                    
                    # Restriccion: Disponibilidad del Profesor
                    prof = assignments.get(sid)
                    if prof in availability:
                        valid_indices = availability[prof]
                        for i in range(num_bloques):
                            if i not in valid_indices:
                                model.Add(sub_vars[i] == 0).WithName(f"Disp_{prof}_{sid}_B{i}")
                
                sem_vars.append(all_vars[sid])
            
            # Restriccion: No solapamiento por semestre (Alumnos)
            for i in range(num_bloques):
                model.Add(sum(s_v[i] for s_v in sem_vars) <= 1).WithName(f"NoChoque_Sem{sem_num}_B{i}")

    # RESTRICCION DE PROFESORES (No estar en dos lugares a la vez)
    prof_map = {}
    for sid, prof in assignments.items():
        if sid in all_vars:
            if prof not in prof_map: prof_map[prof] = []
            prof_map[prof].append(all_vars[sid])
            
    for prof, vars_list in prof_map.items():
        for i in range(num_bloques):
            model.Add(sum(m_v[i] for m_v in vars_list) <= 1).WithName(f"NoChoqueProf_{prof}_B{i}")

    # LOGICA DE COMPACTACION Y PENALIZACIONES (SC por Materia, no pueden ser duras porque eso romperia en casos complicados)
    for sid, vars_list in all_vars.items():
        dias_activos = []
        
        for d_idx in range(len(config.dias)):
            day_start = d_idx * config.slots_por_dia
            day_vars = vars_list[day_start : day_start + config.slots_por_dia]
            
            # Intentar que quede todo pegado
            transiciones = []
            for i in range(len(day_vars) - 1):
                t = model.NewBoolVar(f't_{sid}_d{d_idx}_b{i}')
                # t es verdadero solo si el bloque actual es 0 y el siguiente es 1
                model.Add(day_vars[i+1] > day_vars[i]).OnlyEnforceIf(t)
                model.Add(day_vars[i+1] <= day_vars[i]).OnlyEnforceIf(t.Not())
                transiciones.append(t)
            
            model.Add(sum(transiciones) <= 1).WithName(f"Contig_{sid}_D{d_idx}")

            # Sencillo, simplemente evita usar varianza de dias (por eso dias_activos hace append a cada dia)
            esta_dia = model.NewBoolVar(f'act_{sid}_d{d_idx}')
            model.AddMaxEquality(esta_dia, day_vars)
            dias_activos.append(esta_dia)

        # Evitar que una materia se reparta en mas de 2 días, es tedioso ver una materia en 3 dias separados
        num_dias = model.NewIntVar(0, 5, f'ndias_{sid}')
        model.Add(num_dias == sum(dias_activos))
        
        es_muy_disperso = model.NewBoolVar(f'disperso_{sid}')
        model.Add(num_dias <= 2).OnlyEnforceIf(es_muy_disperso.Not())
        penalties.append(es_muy_disperso * 150) # Penalizacion alta por disperion

    # penalizar huecos
    for career_name, data in careers_data.items():
        for sem in data["semesters"]:
            sem_subjects_vars = [all_vars[sub["id"]] for sub in sem["subjects"]]
            
            # dias totales
            dias_activos_alumno = []
            for d_idx in range(len(config.dias)):
                day_start = d_idx * config.slots_por_dia
                dia_ocupado = model.NewBoolVar(f'dia_ocupado_{career_name}_S{sem["number"]}_d{d_idx}')
                
                vars_dia = []
                for sub_vars in sem_subjects_vars:
                    vars_dia.extend(sub_vars[day_start : day_start + config.slots_por_dia])
                
                # Si hay alguna clase este dia para este semestre, dia_ocupado es 1
                if vars_dia:
                    model.AddMaxEquality(dia_ocupado, vars_dia)
                else:
                    model.Add(dia_ocupado == 0)
                dias_activos_alumno.append(dia_ocupado)

            total_dias_alumno = model.NewIntVar(0, 5, f'tot_dias_{career_name}_S{sem["number"]}')
            model.Add(total_dias_alumno == sum(dias_activos_alumno))

            va_5_dias = model.NewBoolVar(f'5_dias_{career_name}_S{sem["number"]}')
            # Si el solver no paga la multa de penalizacion, lo forzamos a 4 dias o menos
            model.Add(total_dias_alumno <= 4).OnlyEnforceIf(va_5_dias.Not())
            # Multa absurdamente grande para priorizar darle un dia libre al estudiante
            penalties.append(va_5_dias * 1000)

            # huecos (dia)
            for d_idx in range(len(config.dias)):
                day_start = d_idx * config.slots_por_dia
                for i in range(day_start, day_start + config.slots_por_dia - 2):
                    b_i = model.NewBoolVar(f'occ_{career_name}_S{sem["number"]}_b{i}')
                    b_next = model.NewBoolVar(f'occ_{career_name}_S{sem["number"]}_b{i+1}')
                    b_after = model.NewBoolVar(f'occ_{career_name}_S{sem["number"]}_b{i+2}')
                    
                    model.AddMaxEquality(b_i, [v[i] for v in sem_subjects_vars])
                    model.AddMaxEquality(b_next, [v[i+1] for v in sem_subjects_vars])
                    model.AddMaxEquality(b_after, [v[i+2] for v in sem_subjects_vars])
                    
                    ventana = model.NewBoolVar(f'gap_{career_name}_S{sem["number"]}_b{i}')
                    # si b_i=1, b_next=0, b_after=1 -> entonces ventana DEBE ser 1
                    model.AddBoolOr([b_i.Not(), b_next, b_after.Not(), ventana])
                    penalties.append(ventana * 50)

    # el modelo debe minimizar la sumatoria de penalizaciones
    model.Minimize(sum(penalties))

    # Aqui ya es la logica del solver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0 # Se podria subir mas, no fue necesario en testeo
    status = solver.Solve(model)
   
   # prints de resultados
    print(f"Estado del Solver: {solver.StatusName(status)}")

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        results_map = {c: {} for c in careers_data.keys()}
        for career_name, data in careers_data.items():
            for sem in data["semesters"]:
                sem_num = sem["number"]
                materias_output = []
                for sub in sem["subjects"]:
                    sid = sub["id"]
                    bloques_asig = []
                    for i, v in enumerate(all_vars[sid]):
                        if solver.Value(v):
                            dia_idx = i // config.slots_por_dia
                            bloques_asig.append({
                                "index": i, 
                                "dia": config.dias[dia_idx], 
                                "bloque_id": i % config.slots_por_dia
                            })
                    materias_output.append({
                        "id": sid, 
                        "nombre": sub["name"], 
                        "profesor": assignments.get(sid), 
                        "horario": bloques_asig
                    })
                results_map[career_name][sem_num] = materias_output
        return results_map
    
    return None
