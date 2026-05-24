from ortools.sat.python import cp_model
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class TimeConfig:
    dias: List[str]
    slots_por_dia: int

def solve_model(estructuras_data: Dict, availability: Dict, task_dependencies: Dict, config: TimeConfig, solver_config=None, force_prereq_overlap: bool = False):
    model = cp_model.CpModel()
    num_bloques = len(config.dias) * config.slots_por_dia
    all_vars = {}
    penalties = []

    recursos_globales = {}

    # Cargar penalizaciones e infraestructura de forma dinamica desde el config parser
    if solver_config:
        p_dispersion = solver_config.get("penalizacion_dispersion", 150)
        p_hueco = solver_config.get("penalizacion_hueco", 50)
        p_max_dias = solver_config.get("penalizacion_max_dias", 1000)
        dias_objetivo = solver_config.get("dias_objetivo_subgrupo", 4)
        tiempo_max = solver_config.get("tiempo_max_segundos", 60.0)
    # Fallback
    else:
        p_dispersion = 150
        p_hueco = 50
        p_max_dias = 1000
        dias_objetivo = 4
        tiempo_max = 60.0

    print("Iniciando Solver...")

    # REGISTRO DE VARIABLES Y RESTRICCIONES DURAS
    for grupo_name, data in estructuras_data.items():
        for subgrupo in data.get("subgroups", []):
            subgrupo_id = subgrupo["number"]
            subgrupo_vars = []

            for tarea in subgrupo.get("tasks", []):
                sid = tarea["id"]
                n_blocks = tarea["blocks"]

                # Identificador de recurso
                recurso_req = tarea.get("recurso")

                if sid not in all_vars:
                    # PUNTERO UNICO (increible lol)
                    sub_vars = [model.NewBoolVar(f"v_{sid}_b{i}") for i in range(num_bloques)]
                    all_vars[sid] = sub_vars

                    # Restriccion Dura: Carga horaria requerida de bloques por tarea
                    model.Add(sum(sub_vars) == n_blocks).WithName(f"Carga_{sid}")

                    # Restriccion Dura: Ventanas operativas de la entidad dependiente
                    dependencia = task_dependencies.get(sid)
                    if dependencia in availability:
                        valid_indices = availability[dependencia]
                        for i in range(num_bloques):
                            if i not in valid_indices:
                                model.Add(sub_vars[i] == 0).WithName(f"Disp_{dependencia}_{sid}_B{i}")

                    # Registro matricial de la tarea en recursos globales de exclusion mutua (mutex)
                    if recurso_req:
                        if recurso_req not in recursos_globales:
                            recursos_globales[recurso_req] = [[] for _ in range(num_bloques)]
                        for i in range(num_bloques):
                            recursos_globales[recurso_req][i].append(sub_vars[i])

                subgrupo_vars.append(all_vars[sid])

            # Restriccion Dura: No solapamiento de tareas concurrentes dentro del mismo subgrupo
            for i in range(num_bloques):
                model.Add(sum(s_v[i] for s_v in subgrupo_vars) <= 1).WithName(f"NoChoque_Sub_{subgrupo_id}_B{i}")

    # EXCLUSION MUTUA POR RECURSO (Mutex por recurso)
    for res_name, bloques_recurso in recursos_globales.items():
        for i in range(num_bloques):
            if bloques_recurso[i]:
                # Solo una tarea que requiera 'recurso' puede usar el bloque i
                model.Add(sum(bloques_recurso[i]) <= 1).WithName(f"Mutex_{res_name}_B{i}")

    # RESTRICCION DE NO SOLAPAMIENTO MULTITAREA PARA LAS DEPENDENCIAS
    dep_map = {}
    for sid, dep in task_dependencies.items():
        if sid in all_vars:
            if dep not in dep_map:
                dep_map[dep] = []
            dep_map[dep].append(all_vars[sid])

    for dep, vars_list in dep_map.items():
        for i in range(num_bloques):
            model.Add(sum(m_v[i] for m_v in vars_list) <= 1).WithName(f"NoChoqueDep_{dep}_B{i}")


    # LOGICA DE COMPACTACION Y PENALIZACIONES POR DISPERSION DE TAREA
    for sid, vars_list in all_vars.items():
        dias_activos = []
        for d_idx in range(len(config.dias)):
            day_start = d_idx * config.slots_por_dia
            day_vars = vars_list[day_start : day_start + config.slots_por_dia]

            # Intentar que todo quede pegado
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

        # Penalizacion soft: Evitar la dispersión de una sola tarea en más de 2 días
        num_dias = model.NewIntVar(0, 7, f'ndias_{sid}')
        model.Add(num_dias == sum(dias_activos))

        es_muy_disperso = model.NewBoolVar(f'disperso_{sid}')
        model.Add(num_dias <= 2).OnlyEnforceIf(es_muy_disperso.Not())
        penalties.append(es_muy_disperso * p_dispersion)

    # PENALIZACIONES DE HUECOS (GAPS) Y EXCESO DE JORNADAS POR SUBGRUPO
    for grupo_name, data in estructuras_data.items():
        for subgrupo in data.get("subgroups", []):
            subgrupo_id = subgrupo["number"]

            # Obtener variables exclusivamente de las tareas pertenecientes a este subgrupo
            subgrupo_tasks_vars = [all_vars[tarea["id"]] for tarea in subgrupo.get("tasks", []) if tarea["id"] in all_vars]
            if not subgrupo_tasks_vars:
                continue

            # Control de jornadas del subgrupo completo
            dias_activos_subgrupo = []
            for d_idx in range(len(config.dias)):
                day_start = d_idx * config.slots_por_dia
                dia_ocupado = model.NewBoolVar(f'dia_ocupado_{grupo_name}_SUB_{subgrupo_id}_d{d_idx}')

                vars_dia = []
                for sub_vars in subgrupo_tasks_vars:
                    vars_dia.extend(sub_vars[day_start : day_start + config.slots_por_dia])

                model.AddMaxEquality(dia_ocupado, vars_dia)
                dias_activos_subgrupo.append(dia_ocupado)

            total_dias_subgrupo = model.NewIntVar(0, 7, f'tot_dias_{grupo_name}_SUB_{subgrupo_id}')

            model.Add(total_dias_subgrupo == sum(dias_activos_subgrupo))

            # Penalizacion soft: Intentar concentrar las tareas del subgrupo en x dias objetivo o menos
            rango_maximo = model.NewBoolVar(f'max_dias_{grupo_name}_SUB_{subgrupo_id}')
            model.Add(total_dias_subgrupo <= dias_objetivo).OnlyEnforceIf(rango_maximo.Not())
            penalties.append(rango_maximo * p_max_dias)

            # Penalizacion soft: Deteccion y multa de huecos intermedios (Gaps o ventanas muertas)
            for d_idx in range(len(config.dias)):
                day_start = d_idx * config.slots_por_dia
                for i in range(day_start, day_start + config.slots_por_dia - 2):
                    b_i = model.NewBoolVar(f'occ_{grupo_name}_SUB_{subgrupo_id}_b{i}')
                    b_next = model.NewBoolVar(f'occ_{grupo_name}_SUB_{subgrupo_id}_b{i+1}')
                    b_after = model.NewBoolVar(f'occ_{grupo_name}_SUB_{subgrupo_id}_b{i+2}')

                    model.AddMaxEquality(b_i, [v[i] for v in subgrupo_tasks_vars])
                    model.AddMaxEquality(b_next, [v[i+1] for v in subgrupo_tasks_vars])
                    model.AddMaxEquality(b_after, [v[i+2] for v in subgrupo_tasks_vars])
                    ventana = model.NewBoolVar(f'gap_{grupo_name}_SUB_{subgrupo_id}_b{i}')
                    # si b_i=1, b_next=0, b_after=1 -> entonces ventana DEBE ser 1
                    model.AddBoolOr([b_i.Not(), b_next, b_after.Not(), ventana])
                    penalties.append(ventana * p_hueco)

    # Minimizar la sumatoria global de penalizaciones asignadas
    model.Minimize(sum(penalties))

    # Aqui ya es la logica del solver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tiempo_max
    status = solver.Solve(model)

    # prints de resultados
    print(f"Estado del Solver: {solver.StatusName(status)}")

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        results_map = {c: {} for c in estructuras_data.keys()}
        for grupo_name, data in estructuras_data.items():
            for subgrupo in data.get("subgroups", []):
                subgrupo_id_str = str(subgrupo["number"])
                tareas_output = []

                for tarea in subgrupo.get("tasks", []):
                    sid = tarea["id"]
                    bloques_asig = []

                    for i, v in enumerate(all_vars[sid]):
                        if solver.Value(v):
                            dia_idx = i // config.slots_por_dia
                            bloques_asig.append({
                                "index": i, 
                                "dia": config.dias[dia_idx], 
                                "bloque_id": i % config.slots_por_dia
                            })

                    tareas_output.append({
                        "id": sid, 
                        "nombre": tarea["name"], 
                        "dependencia": task_dependencies.get(sid), 
                        "recurso": tarea.get("recurso"), 
                        "horario": bloques_asig
                    })
                results_map[grupo_name][subgrupo_id_str] = tareas_output
        return results_map

    return None
