"""MC-02 hemoglobin dosage component definition and age rule."""

HEMOGLOBIN_COMPONENTS = [
    {
        "key": "hemoglobina",
        "label": "Dosaje de hemoglobina",
        "obs": "Obs_Dh",
        "flag": "Obs_dh1",
        "date": "fecha_1DH",
        "age": "edad_1DH",
        "code": "CIE_DH_1DH",
        "lab": "Lab_1DH",
        "lote": "Lote_Pag_Reg_1DH",
        "facility": "EESS_Ate_1DH",
        "window": "DOSAJE_HEMOGLOBINA",
    },
]

HEMOGLOBIN_WINDOWS = {
    "DOSAJE_HEMOGLOBINA": {
        "descripcion": "Dosaje de hemoglobina en sangre.",
        "rangos": [
            {"edad_min": 0, "edad_max": 209, "dosis_requeridas": 0, "mensaje": "Aun no exige dosaje para cumplimiento."},
            {"edad_min": 210, "edad_max": 364, "dosis_requeridas": 1, "mensaje": "Debe contar con 1 dosaje realizado entre 170 y 209 dias."},
        ],
        "ventana_atencion": {"inicio_dia": 170, "fin_dia": 209},
    },
}
