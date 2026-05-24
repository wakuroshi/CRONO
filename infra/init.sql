CREATE TABLE IF NOT EXISTS time_contexts (
    id VARCHAR(50) PRIMARY KEY,
    time_config JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS model_entities (
    id SERIAL PRIMARY KEY,
    period_id VARCHAR(50) REFERENCES time_contexts(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS solver_outputs (
    id SERIAL PRIMARY KEY,
    period_id VARCHAR(50) REFERENCES time_contexts(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    results JSONB,
    executed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO time_contexts (id, time_config)
VALUES (
    '2026-1CR',
    '{
        "terminologia": {
		"nivel_grupo_1": "Carrera",
		"nivel_grupo_2": "Semestre",
		"unidad_tarea": "Asignatura",
		"unidad_agente": "Profesor"
	},
	"tiempo": {
		"dias": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
		"slots_por_dia": 10
	},
        "solver": {
            "tiempo_max_segundos": 60.0,
            "penalizacion_dispersion": 150,
            "penalizacion_hueco": 50,
            "penalizacion_max_dias": 1000,
            "dias_objetivo_subgrupo": 4
        }
    }'
);

INSERT INTO model_entities (period_id, entity_type, payload)
VALUES (
    '2026-1CR',
    'disponibilidad_agentes',
    '{
        "PROF_DEPORTES": [0,1,2,3,4, 10,11,12,13,14, 20,21,22,23,24, 30,31,32,33,34, 40,41,42,43,44],
        "PROF_CIENCIAS_A": [5,6,7,8,9, 15,16,17,18,19, 25,26,27,28,29, 35,36,37,38,39, 45,46,47,48,49],
        "PROF_CIENCIAS_B": [0,1,2,3,4,5,6,7,8,9, 10,11,12,13,14,15, 30,31,32,33,34,35],
        "PROF_FISICA_X": [10,11,12,13,14, 20,21,22,23,24, 30,31,32,33,34, 40,41,42,43,44],
        "PROF_HUMANIDADES": [0,1,2, 10,11,12, 20,21,22, 30,31,32, 40,41,42],
        "PROF_IDIOMAS": [5,6,7, 15,16,17, 25,26,27, 45,46,47],
        "PROF_COMP_LOGICA": [0,1,2,3, 20,21,22,23, 40,41,42,43],
        "PROF_COMP_ALGO": [0,1,2,3,4,5,6,7,8,9, 10,11,12,13,14, 20,21,22,23,24, 30,31,32,33,34],
        "PROF_ING_GENERAL": [0,1,2,3,4,5,6,7,8,9, 10,11,12,13,14, 20,21,22,23,24, 30,31,32,33,34, 40,41,42,43,44],
        "PROF_CIVIL_DISEÑO": [35,36,37,38,39, 45,46,47,48,49],
        "PROF_COMP_AVANZADA": [35,36,37,38,39, 45,46,47,48,49]
    }'
);

-- Entidad: asignacion_agentes
INSERT INTO model_entities (period_id, entity_type, payload)
VALUES (
    '2026-1CR',
    'asignacion_agentes',
    '{
        "EFS01202": "PROF_DEPORTES",
        "GAN01404": "PROF_CIENCIAS_A",
        "LOG01404": "PROF_COMP_LOGICA",
        "MAI01506": "PROF_CIENCIAS_B",
        "VEC01202": "PROF_HUMANIDADES",
        "ALI02304": "PROF_CIENCIAS_A",
        "CIN02303": "PROF_HUMANIDADES",
        "FIS02405": "PROF_FISICA_X",
        "GDS02203": "PROF_CIVIL_DISEÑO",
        "MAI02506": "PROF_CIENCIAS_B",
        "PRO02305": "PROF_COMP_ALGO",
        "ING03303": "PROF_IDIOMAS",
        "EDI03304": "PROF_CIENCIAS_A",
        "FIS03405": "PROF_FISICA_X",
        "IIN03202": "PROF_ING_GENERAL",
        "MAI03304": "PROF_CIENCIAS_B",
        "PRO03305": "PROF_COMP_ALGO",
        "DIB03204": "PROF_CIVIL_DISEÑO",
        "FEL04304": "PROF_FISICA_X",
        "PRO04405": "PROF_COMP_AVANZADA"
    }'
);

-- Estructura: Ingenieria Civil
INSERT INTO model_entities (period_id, entity_type, payload)
VALUES (
    '2026-1CR',
    'estructuras',
    '{
        "grupo": "Ingeniería Civil",
        "subgrupos": [
            {
                "id": "1",
                "tareas": [
                    { "id": "EFS01202", "nombre": "Educación Física Y Salud", "bloques": 2 },
                    { "id": "GAN01404", "nombre": "Geometría Analítica", "bloques": 4 },
                    { "id": "LOG01404", "nombre": "Lógica", "bloques": 4 },
                    { "id": "MAI01506", "nombre": "Matemática I", "bloques": 6 },
                    { "id": "VEC01202", "nombre": "Venezuela Contemporánea", "bloques": 2 }
                ]
            },
            {
                "id": "2",
                "tareas": [
                    { "id": "ALI02304", "nombre": "Álgebra Lineal", "bloques": 4 },
                    { "id": "CIN02303", "nombre": "Creatividad E Inventiva", "bloques": 3 },
                    { "id": "FIS02405", "nombre": "Física I", "bloques": 5 },
                    { "id": "GDS02203", "nombre": "Geometría Descriptiva", "bloques": 3 },
                    { "id": "MAI02506", "nombre": "Matemática II", "bloques": 6 },
                    { "id": "PRO02305", "nombre": "Programación I", "bloques": 5 }
                ]
            },
            {
                "id": "3",
                "tareas": [
                    { "id": "DIB03204", "nombre": "Dibujo", "bloques": 4, "recurso": "lab_computacion" },
                    { "id": "EDI03304", "nombre": "Ecuaciones Diferenciales", "bloques": 4 },
                    { "id": "FIS03405", "nombre": "Física II", "bloques": 5 },
                    { "id": "IIN03202", "nombre": "Introducción a la Ingeniería", "bloques": 2 },
                    { "id": "MAI03304", "nombre": "Matemática III", "bloques": 4 },
                    { "id": "PRO03305", "nombre": "Programación II", "bloques": 5 }
                ]
            }
        ]
    }'
);

-- Estructura: Ingenieria de Computación
INSERT INTO model_entities (period_id, entity_type, payload)
VALUES (
    '2026-1CR',
    'estructuras',
    '{
        "grupo": "Ingeniería de Computación",
        "subgrupos": [
            {
                "id": "1",
                "tareas": [
                    { "id": "EFS01202", "nombre": "Educación Física Y Salud", "bloques": 2 },
                    { "id": "GAN01404", "nombre": "Geometría Analítica", "bloques": 4 },
                    { "id": "LOG01404", "nombre": "Lógica", "bloques": 4 },
                    { "id": "MAI01506", "nombre": "Matemática I", "bloques": 6 },
                    { "id": "VEC01202", "nombre": "Venezuela Contemporánea", "bloques": 2 }
                ]
            },
            {
                "id": "2",
                "tareas": [
                    { "id": "ALI02304", "nombre": "Álgebra Lineal", "bloques": 4 },
                    { "id": "CIN02303", "nombre": "Creatividad E Inventiva", "bloques": 3 },
                    { "id": "FIS02405", "nombre": "Física I", "bloques": 5 },
                    { "id": "MAI02506", "nombre": "Matemática II", "bloques": 6 },
                    { "id": "PRO02305", "nombre": "Programación I", "bloques": 5, "recurso": "lab_computacion" }
                ]
            },
            {
                "id": "3",
                "tareas": [
                    { "id": "ING03303", "nombre": "Inglés I", "bloques": 3 },
                    { "id": "EDI03304", "nombre": "Ecuaciones Diferenciales", "bloques": 4 },
                    { "id": "FIS03405", "nombre": "Física II", "bloques": 5 },
                    { "id": "IIN03202", "nombre": "Introducción a la Ingeniería", "bloques": 2 },
                    { "id": "MAI03304", "nombre": "Matemática III", "bloques": 4 },
                    { "id": "PRO03305", "nombre": "Programación II", "bloques": 5, "recurso": "lab_computacion" }
                ]
            },
            {
                "id": "4",
                "tareas": [
                    { "id": "FEL04304", "nombre": "Fundamentos de Electrónica", "bloques": 4 },
                    { "id": "PRO04405", "nombre": "Programación III", "bloques": 5, "recurso": "lab_computacion" }
                ]
            }
        ]
    }'
);
