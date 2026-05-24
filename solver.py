from ortools.sat.python import cp_model
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class TimeConfig:
    dias: List[str]
    slots_por_dia: int

def solve_model(estructuras_data: Dict, disponibilidad_agentes: Dict, asignacion_agentes: Dict, config: TimeConfig, solver_config=None, force_prereq_overlap: bool = False):
    model = cp_model.CpModel()
    num_bloques = len(config.dias) * config.slots_por_dia
    all_vars = {}
    penalties = []
    recursos_globales = {}

    if solver_config:
        p_dispersion = solver_config.get("penalizacion_dispersion", 150)
        p_hueco = solver_config.get("penalizacion_hueco", 50)
        p_max_dias = solver_config.get("penalizacion_max_dias", 1000)
        dias_objetivo = solver_config.get("dias_objetivo_subgrupo", 4)
        tiempo_max = solver_config.get("tiempo_max_segundos", 60.0)
    else:
        p_dispersion = 150
        p_hueco = 50
        p_max_dias = 1000
        dias_objetivo = 4
        tiempo_max = 60.0

    print("Iniciando Solver...")

    # REGISTRO DE VARIABLES Y RESTRICCIONES DURAS
    for grupo_name, data in estructuras_data.items():
        for subgrupo in data.get("subgrupos", []):
            subgrupo_id = str(subgrupo["id"]) # Asegurado como string
            subgrupo_vars = []

            for tarea in subgrupo.get("tareas", []):
                sid = tarea["id"]
                n_bloques = tarea["bloques"]
                recurso_req = tarea.get("recurso")

                if sid not in all_vars:
                    sub_vars = [model.NewBoolVar(f"v_{sid}_b{i}") for i in range(num_bloques)]
                    all_vars[sid] = sub_vars

                    # Carga horaria
                    model.Add(sum(sub_vars) == n_bloques).WithName(f"Carga_{sid}")

                    # Ventanas operativas del agente
                    agente = asignacion_agentes.get(sid)
                    if agente in disponibilidad_agentes:
                        indices_validos = disponibilidad_agentes[agente]
                        for i in range(num_bloques):
                            if i not in indices_validos:
                                model.Add(sub_vars[i] == 0).WithName(f"Disp_{agente}_{sid}_B{i}")

                    # Mutex de recursos
                    if recurso_req:
                        if recurso_req not in recursos_globales:
                            recursos_globales[recurso_req] = [[] for _ in range(num_bloques)]
                        for i in range(num_bloques):
                            recursos_globales[recurso_req][i].append(sub_vars[i])

                subgrupo_vars.append(all_vars[sid])

            # No solapamiento de tareas en el mismo subgrupo
            for i in range(num_bloques):
                model.Add(sum(s_v[i] for s_v in subgrupo_vars) <= 1).WithName(f"NoChoque_Sub_{subgrupo_id}_B{i}")

    # EXCLUSION MUTUA POR RECURSO
    for res_name, bloques_recurso in recursos_globales.items():
        for i in range(num_bloques):
            if bloques_recurso[i]:
                model.Add(sum(bloques_recurso[i]) <= 1).WithName(f"Mutex_{res_name}_B{i}")

    # NO SOLAPAMIENTO MULTITAREA PARA LOS AGENTES
    agente_map = {}
    for sid, agente in asignacion_agentes.items():
        if sid in all_vars:
            if agente not in agente_map:
                agente_map[agente] = []
            agente_map[agente].append(all_vars[sid])

    for agente, vars_list in agente_map.items():
        for i in range(num_bloques):
            model.Add(sum(m_v[i] for m_v in vars_list) <= 1).WithName(f"NoChoqueAgente_{agente}_B{i}")

    # LÓGICA DE COMPACTACIÓN Y PENALIZACIONES
    for sid, vars_list in all_vars.items():
        dias_activos = []
        for d_idx in range(len(config.dias)):
            day_start = d_idx * config.slots_por_dia
            day_vars = vars_list[day_start : day_start + config.slots_por_dia]

            transiciones = []
            for i in range(len(day_vars) - 1):
                t = model.NewBoolVar(f't_{sid}_d{d_idx}_b{i}')
                model.Add(day_vars[i+1] > day_vars[i]).OnlyEnforceIf(t)
                model.Add(day_vars[i+1] <= day_vars[i]).OnlyEnforceIf(t.Not())
                transiciones.append(t)

            model.Add(sum(transiciones) <= 1).WithName(f"Contig_{sid}_D{d_idx}")

            esta_dia = model.NewBoolVar(f'act_{sid}_d{d_idx}')
            model.AddMaxEquality(esta_dia, day_vars)
            dias_activos.append(esta_dia)

        num_dias = model.NewIntVar(0, 7, f'ndias_{sid}')
        model.Add(num_dias == sum(dias_activos))

        es_muy_disperso = model.NewBoolVar(f'disperso_{sid}')
        model.Add(num_dias <= 2).OnlyEnforceIf(es_muy_disperso.Not())
        penalties.append(es_muy_disperso * p_dispersion)

    # PENALIZACIONES DE HUECOS Y EXCESO DE JORNADAS
    for grupo_name, data in estructuras_data.items():
        for subgrupo in data.get("subgrupos", []):
            subgrupo_id = str(subgrupo["id"])

            subgrupo_tasks_vars = [all_vars[tarea["id"]] for tarea in subgrupo.get("tareas", []) if tarea["id"] in all_vars]
            if not subgrupo_tasks_vars:
                continue

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

            rango_maximo = model.NewBoolVar(f'max_dias_{grupo_name}_SUB_{subgrupo_id}')
            model.Add(total_dias_subgrupo <= dias_objetivo).OnlyEnforceIf(rango_maximo.Not())
            penalties.append(rango_maximo * p_max_dias)

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
                    
                    model.AddBoolOr([b_i.Not(), b_next, b_after.Not(), ventana])
                    penalties.append(ventana * p_hueco)

    model.Minimize(sum(penalties))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tiempo_max
    status = solver.Solve(model)

    print(f"Estado del Solver: {solver.StatusName(status)}")

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        mapa_resultados = {c: {} for c in estructuras_data.keys()}
        for grupo_name, data in estructuras_data.items():
            for subgrupo in data.get("subgrupos", []):
                subgrupo_id_str = str(subgrupo["id"])
                tareas_output = []

                for tarea in subgrupo.get("tareas", []):
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
                        "nombre": tarea["nombre"], 
                        "agente": asignacion_agentes.get(sid), 
                        "recurso": tarea.get("recurso"), 
                        "horario": bloques_asig
                    })
                mapa_resultados[grupo_name][subgrupo_id_str] = tareas_output
        return mapa_resultados

    return None
