"""MC-02 iron supplementation and anemia-treatment component definitions."""

IRON_COMPONENTS = [
    {
        "key": "hierro_menor_6m",
        "label": "Hierro menor de 6 meses",
        "obs": "Obs_Hierros",
        "flag": "obs_suple41",
        "date": "fecha_1prev",
        "age": "edad_1prev",
        "code": "CIE_Hierro_1prev",
        "lab": "Lab_1prev",
        "lote": "Lote_Pag_Reg_1prev",
        "facility": "EESS_Ate_1prev",
        "window": "HIERRO_MENOR_6_MESES",
        "delivery_kind": "Suplementacion preventiva 4 meses",
        "deliveries": [
            {"label": "Entrega 1", "kind": "Preventiva 4 meses", "date": "fecha_1prev", "age": "edad_1prev", "code": "CIE_Hierro_1prev", "lab": "Lab_1prev", "lote": "Lote_Pag_Reg_1prev", "facility": "EESS_Ate_1prev"},
            {"label": "Entrega 2", "kind": "Preventiva 4 meses", "date": "fecha_2prev", "age": "edad_2prev", "code": "CIE_Hierro_2prev", "lab": "Lab_2prev", "lote": "Lote_Pag_Reg_2prev", "facility": "EESS_Ate_2prev"},
            {"label": "Entrega 3", "kind": "Preventiva 4 meses", "date": "fecha_3prev", "age": "edad_3prev", "code": "CIE_Hierro_3prev", "lab": "Lab_3prev", "lote": "Lote_Pag_Reg_3prev", "facility": "EESS_Ate_3prev"},
            {"label": "Entrega 4", "kind": "Preventiva 4 meses", "date": "fecha_4prev", "age": "edad_4prev", "code": "CIE_Hierro_4prev", "lab": "Lab", "lote": "Lote_Pag_Reg_4prev", "facility": "EESS_Ate_4prev"},
            {"label": "Entrega 5", "kind": "Preventiva 4 meses", "date": "fecha_5prev", "age": "edad_5prev", "code": "CIE_Hierro_5prev", "lab": "Lab_5prev", "lote": "Lote_Pag_Reg_5prev", "facility": "EESS_Ate_5prev"},
        ],
    },
    {
        "key": "hierro_mayor_6m",
        "label": "Hierro mayor de 6 meses",
        "obs": "OBS_SUPLE6",
        "flag": "obs_suple61",
        "date": "fecha_1prevhierr",
        "age": "edad_1prevhierr",
        "code": "CIE_Hierro_1prevhierr",
        "lab": "Lab_1prevhierr",
        "lote": "Lote_Pag_Reg_1prevhierr",
        "facility": "EESS_Ate_1prevhierr",
        "window": "HIERRO_MAYOR_6_MESES",
        "delivery_kind": "Suplementacion/tratamiento 6 a 11 meses",
        "deliveries": [
            {"label": "Entrega 1", "kind": "Preventiva 6 a 11 meses", "date": "fecha_1prevhierr", "age": "edad_1prevhierr", "code": "CIE_Hierro_1prevhierr", "lab": "Lab_1prevhierr", "lote": "Lote_Pag_Reg_1prevhierr", "facility": "EESS_Ate_1prevhierr", "interval": "Intervalo1s"},
            {"label": "Entrega 2", "kind": "Preventiva 6 a 11 meses", "date": "fecha_2prevhierr", "age": "edad_2prevhierr", "code": "CIE_Hierro_2prevhierr", "lab": "Lab_2prevhierr", "lote": "Lote_Pag_Reg_2prevhierr", "facility": "EESS_Ate_2prevhierr", "interval": "Intervalo2s"},
            {"label": "Entrega 3", "kind": "Preventiva 6 a 11 meses", "date": "fecha_3prevhierr", "age": "edad_3prevhierr", "code": "CIE_Hierro_3prevhierr", "lab": "Lab_3prevhierr", "lote": "Lote_Pag_Reg_3prevhierr", "facility": "EESS_Ate_3prevhierr", "interval": "Intervalo3s"},
            {"label": "Entrega 4", "kind": "Preventiva 6 a 11 meses", "date": "fecha_4prevhierr", "age": "edad_4prevhierr", "code": "CIE_Hierro_4prevhierr", "lab": "Lab_4prevhierr", "lote": "Lote_Pag_Reg_4prevhierr", "facility": "EESS_Ate_4prevhierr", "interval": "Intervalo4s"},
            {"label": "Entrega 5", "kind": "Preventiva 6 a 11 meses", "date": "fecha_5prevhierr", "age": "edad_5prevhierr", "code": "CIE_Hierro_5prevhierr", "lab": "Lab_5prevhierr", "lote": "Lote_Pag_Reg_5prevhierr", "facility": "EESS_Ate_5prevhierr", "interval": "intervalo5s"},
            {"label": "Entrega 6", "kind": "Preventiva 6 a 11 meses", "date": "fecha_6prevhierr", "age": "edad_6prevhierr", "code": "CIE_Hierro_6prevhierr", "lab": "Lab_6prevhierr", "lote": "Lote_Pag_Reg_6prevhierr", "facility": "EESS_Ate_6prevhierr", "interval": "Intervalo6s"},
            {"label": "Tratamiento 1", "kind": "Tratamiento de anemia", "date": "fecha_1Hier", "age": "edad_1Hier", "code": "CIE_TratHierro_1Hier", "anemia_code": "CIE_Anemia_1Hier", "lab": "Lab_1Hier", "lote": "Lote_Pag_Reg_1Hier", "facility": "EESS_Ate_1Hier"},
            {"label": "Tratamiento 2", "kind": "Tratamiento de anemia", "date": "fecha_2Hier", "age": "edad_2Hier", "code": "CIE_TratHierro_2Hier", "anemia_code": "CIE_Anemia_2Hier", "lab": "Lab_2Hier", "lote": "Lote_Pag_Reg_2Hier", "facility": "EESS_Ate_2Hier"},
            {"label": "Tratamiento 3", "kind": "Tratamiento de anemia", "date": "fecha_3Hier", "age": "edad_3Hier", "code": "CIE_TratHierro_3Hier", "anemia_code": "CIE_Anemia_3Hier", "lab": "Lab_3Hier", "lote": "Lote_Pag_Reg_3Hier", "facility": "EESS_Ate_3Hier"},
            {"label": "Tratamiento 4", "kind": "Tratamiento de anemia", "date": "fecha_4Hier", "age": "edad_4Hier", "code": "CIE_TratHierro_4Hier", "anemia_code": "CIE_Anemia_4Hier", "lab": "Lab_4Hier", "lote": "Lote_Pag_Reg_4Hier", "facility": "EESS_Ate_4Hier"},
            {"label": "Tratamiento 5", "kind": "Tratamiento de anemia", "date": "fecha_5Hier", "age": "edad_5Hier", "code": "CIE_TratHierro_5Hier", "anemia_code": "CIE_Anemia_5Hier", "lab": "Lab_5Hier", "lote": "Lote_Pag_Reg_5Hier", "facility": "EESS_Ate_5Hier"},
            {"label": "Tratamiento 6", "kind": "Tratamiento de anemia", "date": "fecha_6Hier", "age": "edad_6Hier", "code": "CIE_TratHierro_6Hier", "anemia_code": "CIE_Anemia_6Hier", "lab": "Lab_6Hier", "lote": "Lote_Pag_Reg_6Hier", "facility": "EESS_Ate_6Hier"},
        ],
    },
]

IRON_WINDOWS = {
    "HIERRO_MENOR_6_MESES": {
        "descripcion": "Suplementacion preventiva con hierro en esquema de 4 meses.",
        "rangos": [
            {"edad_min": 0, "edad_max": 130, "entregas_requeridas": 0, "mensaje": "Aun no exige entrega de hierro de 4 meses."},
            {"edad_min": 131, "edad_max": 364, "entregas_requeridas": 1, "mensaje": "Debe contar con 1 entrega de hierro entre 110 y 130 dias."},
        ],
        "ventana_atencion": {"inicio_dia": 110, "fin_dia": 130},
        "exclusiones": ["99499"],
    },
    "HIERRO_MAYOR_6_MESES": {
        "descripcion": "Suplementacion preventiva o tratamiento con hierro/micronutrientes en ninos de 6 a 11 meses.",
        "rangos": [
            {"edad_min": 0, "edad_max": 209, "entregas_requeridas": 0, "mensaje": "Aun no exige entrega de hierro de 6 meses."},
            {"edad_min": 210, "edad_max": 279, "entregas_requeridas": 1, "mensaje": "Debe contar con al menos 1 entrega."},
            {"edad_min": 280, "edad_max": 349, "entregas_requeridas": 2, "mensaje": "Debe contar con al menos 2 entregas validas."},
            {"edad_min": 350, "edad_max": 364, "entregas_requeridas": 3, "mensaje": "Debe contar con al menos 3 entregas validas cuando corresponde hierro preventivo."},
        ],
        "intervalo_hierro": {"min_dias": 25, "max_dias": 70},
        "intervalo_micronutrientes": {"min_dias": 25, "max_dias": 35},
        "exclusiones": ["99499", "99199.17 + LAB TA en primera entrega", "99199.19 + LAB TA en primera entrega"],
    },
}
