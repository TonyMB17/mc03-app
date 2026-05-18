"""MC-02 vaccine component definitions and age rules."""

VACCINE_COMPONENTS = [
    {
        "key": "neumococo",
        "label": "Vacuna neumococo",
        "obs": "Obs_NEU",
        "flag": "obs_neu1",
        "date": "fecha_NEU",
        "age": "edad_NEU",
        "code": "CIE_NEU",
        "lab": "Lab_NEU",
        "lote": "Lote_Pag_Reg_NEU",
        "facility": "EESS_Ate_NEU",
        "window": "NEUMOCOCO",
        "doses": [
            {"label": "1 dosis", "date": "fecha_NEU", "age": "edad_NEU", "code": "CIE_NEU", "lab": "Lab_NEU", "lote": "Lote_Pag_Reg_NEU", "facility": "EESS_Ate_NEU"},
            {"label": "2 dosis", "date": "fecha_2NEU", "age": "edad_2NEU", "code": "CIE_NEU_2NEU", "lab": "Lab_2NEU", "lote": "Lote_Pag_Reg_2NEU", "facility": "EESS_Ate_2NEU"},
        ],
    },
    {
        "key": "rotavirus",
        "label": "Vacuna rotavirus",
        "obs": "Obs_ROT",
        "flag": "obs_rot1",
        "date": "fecha_1Rot",
        "age": "edad_1Rot",
        "code": "CIE_NEU_1Rot",
        "lab": "Lab_1Rot",
        "lote": "Lote_Pag_Reg_1Rot",
        "facility": "EESS_Ate_1Rot",
        "window": "ROTAVIRUS",
        "doses": [
            {"label": "1 dosis", "date": "fecha_1Rot", "age": "edad_1Rot", "code": "CIE_NEU_1Rot", "lab": "Lab_1Rot", "lote": "Lote_Pag_Reg_1Rot", "facility": "EESS_Ate_1Rot"},
            {"label": "2 dosis", "date": "fecha_2Rot", "age": "edad_2Rot", "code": "CIE_NEU_2Rot", "lab": "Lab_2Rot", "lote": "Lote_Pag_Reg_2Rot", "facility": "EESS_Ate_2Rot"},
        ],
    },
    {
        "key": "antipolio",
        "label": "Vacuna antipolio",
        "obs": "Obs_ANT",
        "flag": "obs_ant1",
        "date": "fecha_1ANT",
        "age": "edad_1ANT",
        "code": "CIE_ANT_1ANT",
        "lab": "Lab_1ANT",
        "lote": "Lote_Pag_Reg_1ANT",
        "facility": "EESS_Ate_1ANT",
        "window": "ANTIPOLIO",
        "doses": [
            {"label": "1 dosis", "date": "fecha_1ANT", "age": "edad_1ANT", "code": "CIE_ANT_1ANT", "lab": "Lab_1ANT", "lote": "Lote_Pag_Reg_1ANT", "facility": "EESS_Ate_1ANT"},
            {"label": "2 dosis", "date": "fecha_2ANT", "age": "edad_2ANT", "code": "CIE_ANT_2ANT", "lab": "Lab_2ANT", "lote": "Lote_Pag_Reg_2ANT", "facility": "EESS_Ate_2ANT"},
            {"label": "3 dosis", "date": "fecha_3ANT", "age": "edad_3ANT", "code": "CIE_ANT_3ANT", "lab": "Lab_3ANT", "lote": "Lote_Pag_Reg_3ANT", "facility": "EESS_Ate_3ANT"},
        ],
    },
    {
        "key": "pentavalente",
        "label": "Vacuna pentavalente",
        "obs": "Obs_PEN",
        "flag": "obs_pen1",
        "date": "fecha_1PENT",
        "age": "edad_1PENT",
        "code": "CIE_PEN_1PENT",
        "lab": "Lab_1PENT",
        "lote": "Lote_Pag_Reg_1PENT",
        "facility": "EESS_Ate_1PENT",
        "window": "PENTAVALENTE",
        "doses": [
            {"label": "1 dosis", "date": "fecha_1PENT", "age": "edad_1PENT", "code": "CIE_PEN_1PENT", "lab": "Lab_1PENT", "lote": "Lote_Pag_Reg_1PENT", "facility": "EESS_Ate_1PENT"},
            {"label": "2 dosis", "date": "fecha_2PENT", "age": "edad_2PENT", "code": "CIE_PEN_2PENT", "lab": "Lab_2PENT", "lote": "Lote_Pag_Reg_2PENT", "facility": "EESS_Ate_2PENT"},
            {"label": "3 dosis", "date": "fecha_3PENT", "age": "edad_3PENT", "code": "CIE_PEN_3PENT", "lab": "Lab_3PENT", "lote": "Lote_Pag_Reg_3PENT", "facility": "EESS_Ate_3PENT"},
        ],
    },
]

VACCINE_WINDOWS = {
    "NEUMOCOCO": {
        "descripcion": "Vacuna antineumococica segun edad.",
        "rangos": [
            {"edad_min": 0, "edad_max": 119, "dosis_requeridas": 0, "mensaje": "Aun no exige dosis para cumplimiento."},
            {"edad_min": 120, "edad_max": 189, "dosis_requeridas": 1, "mensaje": "Debe contar con 1 dosis."},
            {"edad_min": 190, "edad_max": 364, "dosis_requeridas": 2, "mensaje": "Debe contar con 2 dosis acumuladas."},
        ],
        "edad_dosis": {1: {"min_dias": 55, "max_dias": 119}},
        "intervalo_dosis": {"min_dias": 28, "max_dias": 70},
    },
    "ROTAVIRUS": {
        "descripcion": "Vacuna rotavirus; aplicacion maxima hasta 240 dias.",
        "rangos": [
            {"edad_min": 0, "edad_max": 189, "dosis_requeridas": 0, "mensaje": "Aun no exige dosis para cumplimiento."},
            {"edad_min": 190, "edad_max": 240, "dosis_requeridas": 1, "mensaje": "Debe contar con 1 dosis aplicada oportunamente."},
            {"edad_min": 241, "edad_max": 364, "dosis_requeridas": 2, "mensaje": "Debe contar con 2 dosis acumuladas aplicadas hasta los 240 dias."},
        ],
        "edad_dosis": {1: {"min_dias": 55, "max_dias": 210}, 2: {"max_dias": 240}},
        "intervalo_dosis": {"min_dias": 28, "max_edad_dias": 240},
    },
    "ANTIPOLIO": {
        "descripcion": "Vacuna antipolio segun edad.",
        "rangos": [
            {"edad_min": 0, "edad_max": 119, "dosis_requeridas": 0, "mensaje": "Aun no exige dosis para cumplimiento."},
            {"edad_min": 120, "edad_max": 189, "dosis_requeridas": 1, "mensaje": "Debe contar con 1 dosis."},
            {"edad_min": 190, "edad_max": 259, "dosis_requeridas": 2, "mensaje": "Debe contar con 2 dosis acumuladas."},
            {"edad_min": 260, "edad_max": 364, "dosis_requeridas": 3, "mensaje": "Debe contar con 3 dosis acumuladas."},
        ],
        "edad_dosis": {1: {"min_dias": 55, "max_dias": 119}},
        "intervalo_dosis": {"min_dias": 28, "max_dias": 70},
    },
    "PENTAVALENTE": {
        "descripcion": "Vacuna pentavalente segun edad.",
        "rangos": [
            {"edad_min": 0, "edad_max": 119, "dosis_requeridas": 0, "mensaje": "Aun no exige dosis para cumplimiento."},
            {"edad_min": 120, "edad_max": 189, "dosis_requeridas": 1, "mensaje": "Debe contar con 1 dosis."},
            {"edad_min": 190, "edad_max": 259, "dosis_requeridas": 2, "mensaje": "Debe contar con 2 dosis acumuladas."},
            {"edad_min": 260, "edad_max": 364, "dosis_requeridas": 3, "mensaje": "Debe contar con 3 dosis acumuladas."},
        ],
        "edad_dosis": {1: {"min_dias": 55, "max_dias": 119}},
        "intervalo_dosis": {"min_dias": 28, "max_dias": 70},
    },
}
