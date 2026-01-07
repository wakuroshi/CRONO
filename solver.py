from ortools.sat.python import cp_model

# Config (posiblemente se pueda mover a un json, aun evaluando eso)

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
HORAS_INICIO = [
    "07:00", "07:45", "08:30", "09:15",
    "10:00", "10:45", "11:30", "12:15",
    "13:00", "13:45", "14:30", "15:15",
    "16:00", "16:45", "17:30", "18:15"
]

def generar_universo_bloques():
    return [f"{d}_{h}" for d in DIAS for h in HORAS_INICIO]

def solve_global_career(career_data, availability, assignments, time_limit=60):
    model = cp_model.CpModel()
    bloques = generar_universo_bloques()
    num_bloques = len(bloques)

# Inicializacion variables y listas

    all_vars = {}      
    sub_to_sem = {}    
    sub_map = {}       
    penalties = []


    for sem in career_data["semesters"]:
        sem_num = sem["number"]
        for sub in sem["subjects"]:
            sid = sub["id"]
            sub_to_sem[sid] = sem_num
            sub_map[sid] = sub
            
            prof_id = assignments.get(sid)
            prof_avail = availability.get(prof_id, []) if prof_id else []
            
            vars_list = []
            for b_name in bloques:
                if b_name in prof_avail:
                    v = model.NewBoolVar(f"{sid}_{b_name}")
                else:
                    v = model.NewBoolVar(f"{sid}_{b_name}_fixed")
                    model.Add(v == 0)
                vars_list.append(v)
            
            all_vars[sid] = vars_list
            model.Add(sum(vars_list) == sub["blocks"])

# Reglas

    # 1. El profesor no puede estar en dos materias a la vez
    prof_to_vars = {}
    for sid, prof in assignments.items():
        if prof not in prof_to_vars: prof_to_vars[prof] = []
        prof_to_vars[prof].append(all_vars[sid])

    for prof, lists in prof_to_vars.items():
        for i in range(num_bloques):
            model.Add(sum(l[i] for l in lists) <= 1)

    # 2. El semestre no puede tener dos materias a la vez
    sem_to_vars = {}
    for sid, sem_num in sub_to_sem.items():
        if sem_num not in sem_to_vars: sem_to_vars[sem_num] = []
        sem_to_vars[sem_num].append(all_vars[sid])

    for sem_num, lists in sem_to_vars.items():
        for i in range(num_bloques):
            model.Add(sum(l[i] for l in lists) <= 1)

# Compactar (todavia en desarrollo)

    for sid, vars_list in all_vars.items():
        # agrupacion por dia
        vars_by_day = {}
        for i, b in enumerate(bloques):
            d = b.split("_")[0]
            if d not in vars_by_day: vars_by_day[d] = []
            vars_by_day[d].append(vars_list[i])

        dias_activos = []
        for d, day_vars in vars_by_day.items():
            # Consecutividad: Si bloque i e i+2 están activos, i+1 tambien deberia estarlo asi no esta saltando (creo que podria ser mas elegante pero no se jsajsjas)
            for i in range(len(day_vars) - 2):
                model.AddBoolOr([day_vars[i].Not(), day_vars[i+1], day_vars[i+2].Not()])
            
            # Revisar si ya se esta dando la materia
            esta_dia = model.NewBoolVar(f'{sid}_{d}_activo')
            model.AddMaxEquality(esta_dia, day_vars)
            dias_activos.append(esta_dia)

        # Penalizar dispersión: Evitar que una materia se reparta en mas de 2 dias (quiero refactorizar esto para que no sea esto sino algo con una logica mas robusta)
        num_dias = model.NewIntVar(0, 6, f'num_dias_{sid}')
        model.Add(num_dias == sum(dias_activos))
        
        es_muy_disperso = model.NewBoolVar(f'disperso_{sid}')
        model.Add(num_dias > 2).OnlyEnforceIf(es_muy_disperso)
        penalties.append(es_muy_disperso * 100) # Penalizacion alta

# Penalizar huecos, similar a la logica de consecutividad, esto tambien si llego a cambiar la consecutividad y dispersion podria incluso desaparecer
    for sem_num, lists in sem_to_vars.items():
        for i in range(num_bloques - 2):
            bloque_i = model.NewBoolVar(f'sem_{sem_num}_b{i}_occ')
            bloque_i1 = model.NewBoolVar(f'sem_{sem_num}_b{i+1}_occ')
            bloque_i2 = model.NewBoolVar(f'sem_{sem_num}_b{i+2}_occ')
            
            model.AddMaxEquality(bloque_i, [l[i] for l in lists])
            model.AddMaxEquality(bloque_i1, [l[i+1] for l in lists])
            model.AddMaxEquality(bloque_i2, [l[i+2] for l in lists])
            
            ventana = model.NewBoolVar(f'ventana_sem_{sem_num}_{i}')
            # Si (bloque_i AND NOT bloque_i1 AND bloque_i2) then tiene ventana de materia
            model.AddBoolAnd([bloque_i, bloque_i1.Not(), bloque_i2]).OnlyEnforceIf(ventana)
            penalties.append(ventana * 50)

    model.Minimize(sum(penalties))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.Solve(model)

    result = {}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for sem in sorted(set(sub_to_sem.values())):
            materias = []
            for sid, vars_list in all_vars.items():
                if sub_to_sem[sid] != sem: continue
                
                bloques_asig = []
                for i, v in enumerate(vars_list):
                    if solver.Value(v):
                        d, h = bloques[i].split("_")
                        bloques_asig.append({"bloque": bloques[i], "dia": d, "hora": h})
                
                if bloques_asig:
                    materias.append({
                        "id": sid,
                        "nombre": sub_map[sid]["name"],
                        "profesor": assignments.get(sid),
                        "horario": bloques_asig
                    })
            result[sem] = materias
    return result
