"""MC-02 operative Excel column contract."""

COLUMNAS_EXCEL = {
    "UBICACION": ["Ubigeo", "Renaes", "provincia", "Distrito", "Distrito_FED",
                  "Juntos&CunaMas", "Red", "MicroRed", "EESS"],
    
    "DATOS_GENERALES": ["DNI o CNV", "NumCNV", "Nombres", "Ape_Paterno", "Ape_Materno",
                        "Fec_Nac", "EESS_Nacimiento", "NomApellMadre", "DNIMadre", "Celular", "Obs_Niño", "Hist_Clin"],
    
    "FUENTE_CNV": [
        "Peso", "Edad_Gestacional", "Est_Nac_CNV", "Est_Nac_HIS"
    ],
    
    "Dx_ANEMIA": [
        "Fec_Anemia", "Dx_Anemia"
    ],
    
    "CRED_RECIEN_NACIDO_1": [
        "fecha_1RN", "Lab_1RN", "edad _1RN", "CIE_CRED_1RN", "CPT_CRED_1RN", "Lote_Pag_Reg_1RN", "EESS_Ate_1RN", "Prof_1RN", "difRn1"
    ],
    
    "CRED_RECIEN_NACIDO_2": [
        "fecha_2RN", "Lab_2RN", "edad_2RN", "CIE_CRED_2RN", "CPT_CRED_2RN", "Lote_Pag_Reg_2RN", "EESS_Ate_2RN", "Prof_2RN", "DifRn2"
    ],
    
    "CRED_RECIEN_NACIDO_3": [
        "fecha_3RN", "Lab_3RN", "edad_3RN", "CIE_CRED_3RN", "CPT_CRED_3RN", "Lote_Pag_Reg_3RN", "EESS_Ate_3RN", "Prof_3RN", "Dif3Rn"
    ],
    
    "CRED_RECIEN_NACIDO_4": [
        "fecha_4RN", "Lab_4RN", "edad_4RN", "CIE_CRED_4RN", "CPT_CRED_4RN", "Lote_Pag_Reg_4RN", "EESS_Ate_4RN", "Prof_4RN", "Dif4Rns"
    ],
    
    "CRED_MAYOR_1": [
        "fecha_1CRED", "Lab_1CRED", "edad_1CRED", "CIE_CRED_1CRED", "CPT_CRED_1CRED", "Lote_Pag_Reg_1CRED", "EESS_Ate_1CRED", "Prof_1CRED", "difcred1dias"
    ],
    
    "CRED_MAYOR_2": [
        "fecha_2CRED", "Lab_2CRED", "edad_2CRED", "CIE_CRED_2CRED", "CPT_CRED_2CRED", "Lote_Pag_Reg_2CRED", "EESS_Ate_2CRED", "Prof_2CRED", "difecred2dia"
    ],
    
    "CRED_MAYOR_3": [
        "fecha_3CRED", "Lab_3CRED", "edad_3CRED", "CIE_CRED_3CRED", "CPT_CRED_3CRED", "Lote_Pag_Reg_3CRED", "EESS_Ate_3CRED", "Prof_3CRED", "difere3cred"
    ],
    
    "CRED_MAYOR_4": [
        "fecha_4CRED", "Lab_4CRED", "edad_4CRED", "CIE_CRED_4CRED", "CPT_CRED_4CRED", "Lote_Pag_Reg_4CRED", "EESS_Ate_4CRED", "Prof_4CRED", "dif4creddias"
    ],
    
    "CRED_MAYOR_5": [
        "fecha_5CRED", "Lab_5CRED", "edad_5CRED", "CIE_CRED_5CRED", "CPT_CRED_5CRED", "Lote_Pag_Reg_5CRED", "EESS_Ate_5CRED", "Prof_5CRED", "difere5cred"
    ],
    
    "CRED_MAYOR_6": [
        "fecha_6CRED", "Lab_6CRED", "edad_6CRED", "CIE_CRED_6CRED", "CPT_CRED_6CRED", "Lote_Pag_Reg_6CRED", "EESS_Ate_6CRED", "Prof_6CRED", "dief6diascred"
    ],
    
    "CRED_MAYOR_7": [
        "fecha_7CRED", "Lab_7CRED", "edad_7CRED", "CIE_CRED_7CRED", "CPT_CRED_7CRED", "Lote_Pag_Reg_7CRED", "EESS_Ate_7CRED", "Prof_7CRED", "difere7dias"
    ],
    
    "CRED_MAYOR_8": [
        "fecha_8CRED", "Lab_8CRED", "edad_8CRED", "CIE_CRED_8CRED", "CPT_CRED_8CRED", "Lote_Pag_Reg_8CRED", "EESS_Ate_8CRED", "Prof_8CRED", "difere8dias"
    ],
    
    "CRED_MAYOR_9": [
        "fecha_9CRED", "Lab_9CRED", "edad_9CRED", "CIE_CRED_9CRED", "CPT_CRED_9CRED", "Lote_Pag_Reg_9CRED", "EESS_Ate_9CRED", "Prof_9CRED", "diefer9diascred"
    ],
    
    "CRED_MAYOR_10": [
        "fecha_10CRED", "Lab_10CRED", "edad_10CRED", "CIE_CRED_10CRED", "CPT_CRED_10CRED", "Lote_Pag_Reg_10CRED", "EESS_Ate_10CRED", "Prof_10CRED", "diefer10credd"
    ],
    
    "CRED_MAYOR_11": [
        "fecha_11CRED", "Lab_11CRED", "edad_11CRED", "CIE_CRED_11CRED", "CPT_CRED_11CRED", "Lote_Pag_Reg_11CRED", "EESS_Ate_11CRED", "Prof_11CRED", "difere11cred"
    ],
    
    "VACUNA_NEUMOCOCO_1": [
        "fecha_NEU", "Lab_NEU", "edad_NEU", "CIE_NEU", "Lote_Pag_Reg_NEU", "EESS_Ate_NEU"
    ],
    
    "VACUNA_NEUMOCOCO_2": [
        "fecha_2NEU", "Lab_2NEU", "edad_2NEU", "CIE_NEU_2NEU", "Lote_Pag_Reg_2NEU", "EESS_Ate_2NEU"
    ],
    
    "VACUNA_ROTAVIRUS_1": [
        "fecha_1Rot", "Lab_1Rot", "edad_1Rot", "CIE_NEU_1Rot", "Lote_Pag_Reg_1Rot", "EESS_Ate_1Rot"
    ],
    
    "VACUNA_ROTAVIRUS_2": [
        "fecha_2Rot", "Lab_2Rot", "edad_2Rot", "CIE_NEU_2Rot", "Lote_Pag_Reg_2Rot", "EESS_Ate_2Rot"
    ],
    
    "VACUNA_ANTIPOLIO_1": [
        "fecha_1ANT", "Lab_1ANT", "edad_1ANT", "CIE_ANT_1ANT", "Lote_Pag_Reg_1ANT", "EESS_Ate_1ANT"
    ],
    
    "VACUNA_ANTIPOLIO_2": [
        "fecha_2ANT", "Lab_2ANT", "edad_2ANT", "CIE_ANT_2ANT", "Lote_Pag_Reg_2ANT", "EESS_Ate_2ANT"
    ],
    
    "VACUNA_ANTIPOLIO_3": [
        "fecha_3ANT", "Lab_3ANT", "edad_3ANT", "CIE_ANT_3ANT", "Lote_Pag_Reg_3ANT", "EESS_Ate_3ANT"
    ],
    
    "VACUNA_PENTEVALENTE_1": [
        "fecha_1PENT", "Lab_1PENT", "edad_1PENT", "CIE_PEN_1PENT", "Lote_Pag_Reg_1PENT", "EESS_Ate_1PENT"
    ],
    
    "VACUNA_PENTEVALENTE_2": [
        "fecha_2PENT", "Lab_2PENT", "edad_2PENT", "CIE_PEN_2PENT", "Lote_Pag_Reg_2PENT", "EESS_Ate_2PENT"
    ],
    
    "VACUNA_PENTEVALENTE_3": [
        "fecha_3PENT", "Lab_3PENT", "edad_3PENT", "CIE_PEN_3PENT", "Lote_Pag_Reg_3PENT", "EESS_Ate_3PENT"
    ],
    
    "TRATAMIENTO_ANEMIA_1": [
        "fecha_1Hier", "Lab_1Hier", "edad_1Hier", "CIE_TratHierro_1Hier", "CIE_Anemia_1Hier", "Lote_Pag_Reg_1Hier", "EESS_Ate_1Hier"
    ],
    
    "TRATAMIENTO_ANEMIA_2": [
        "fecha_2Hier", "Lab_2Hier", "edad_2Hier", "CIE_TratHierro_2Hier", "CIE_Anemia_2Hier", "Lote_Pag_Reg_2Hier", "EESS_Ate_2Hier"
    ],
    
    "TRATAMIENTO_ANEMIA_3": [
        "fecha_3Hier", "Lab_3Hier", "edad_3Hier", "CIE_TratHierro_3Hier", "CIE_Anemia_3Hier", "Lote_Pag_Reg_3Hier", "EESS_Ate_3Hier"
    ],
    
    "TRATAMIENTO_ANEMIA_4": [
        "fecha_4Hier", "Lab_4Hier", "edad_4Hier", "CIE_TratHierro_4Hier", "CIE_Anemia_4Hier", "Lote_Pag_Reg_4Hier", "EESS_Ate_4Hier"
    ],
    
    "TRATAMIENTO_ANEMIA_5": [
        "fecha_5Hier", "Lab_5Hier", "edad_5Hier", "CIE_TratHierro_5Hier", "CIE_Anemia_5Hier", "Lote_Pag_Reg_5Hier", "EESS_Ate_5Hier"
    ],
    
    "TRATAMIENTO_ANEMIA_6": [
        "fecha_6Hier", "Lab_6Hier", "edad_6Hier", "CIE_TratHierro_6Hier", "CIE_Anemia_6Hier", "Lote_Pag_Reg_6Hier", "EESS_Ate_6Hier"
    ],
    
    "SUPLEMENTACION_HIERRO_MENOR_6_MESES_1": [
        "fecha_1prev", "Lab_1prev", "edad_1prev", "CIE_Hierro_1prev", "CPT_PMT_1prev", "Lote_Pag_Reg_1prev", "EESS_Ate_1prev"
    ],
    
    "SUPLEMENTACION_HIERRO_MENOR_6_MESES_2": [
        "fecha_2prev", "Lab_2prev", "edad_2prev", "CIE_Hierro_2prev", "CPT_PMT_2prev", "Lote_Pag_Reg_2prev", "EESS_Ate_2prev"
    ],
    
    "SUPLEMENTACION_HIERRO_MENOR_6_MESES_3": [
        "fecha_3prev", "Lab_3prev", "edad_3prev", "CIE_Hierro_3prev", "CPT_PMT_3prev", "Lote_Pag_Reg_3prev", "EESS_Ate_3prev"
    ],
    
    "SUPLEMENTACION_HIERRO_MENOR_6_MESES_4": [
        "fecha_4prev", "Lab", "edad_4prev", "CIE_Hierro_4prev", "CPT_PMT_4prev", "Lote_Pag_Reg_4prev", "EESS_Ate_4prev"
    ],
    
    "SUPLEMENTACION_HIERRO_MENOR_6_MESES_5": [
        "fecha_5prev", "Lab_5prev", "edad_5prev", "CIE_Hierro_5prev", "CPT_PMT_5prev", "Lote_Pag_Reg_5prev", "EESS_Ate_5prev"
    ],
    
    "SUPLEMETACION_HIERRO_PREVENTIVO_MAYOR_6_MESES_1": [
        "fecha_1prevhierr", "Lab_1prevhierr", "edad_1prevhierr", "CIE_Hierro_1prevhierr", "Lote_Pag_Reg_1prevhierr", "EESS_Ate_1prevhierr", "Intervalo1s"
    ],
    
    "SUPLEMETACION_HIERRO_PREVENTIVO_MAYOR_6_MESES_2": [
        "fecha_2prevhierr", "Lab_2prevhierr", "edad_2prevhierr", "CIE_Hierro_2prevhierr", "Lote_Pag_Reg_2prevhierr", "EESS_Ate_2prevhierr", "Intervalo2s"
    ],
    
    "SUPLEMETACION_HIERRO_PREVENTIVO_MAYOR_6_MESES_3": [
        "fecha_3prevhierr", "Lab_3prevhierr", "edad_3prevhierr", "CIE_Hierro_3prevhierr", "Lote_Pag_Reg_3prevhierr", "EESS_Ate_3prevhierr", "Intervalo3s"
    ],
    
    "SUPLEMETACION_HIERRO_PREVENTIVO_MAYOR_6_MESES_4": [
        "fecha_4prevhierr", "Lab_4prevhierr", "edad_4prevhierr", "CIE_Hierro_4prevhierr", "Lote_Pag_Reg_4prevhierr", "EESS_Ate_4prevhierr", "Intervalo4s"
    ],
    
    "SUPLEMETACION_HIERRO_PREVENTIVO_MAYOR_6_MESES_5": [
        "fecha_5prevhierr", "Lab_5prevhierr", "edad_5prevhierr", "CIE_Hierro_5prevhierr", "Lote_Pag_Reg_5prevhierr", "EESS_Ate_5prevhierr", "intervalo5s"
    ],
    
    "SUPLEMETACION_HIERRO_PREVENTIVO_MAYOR_6_MESES_6": [
        "fecha_6prevhierr", "Lab_6prevhierr", "edad_6prevhierr", "CIE_Hierro_6prevhierr", "Lote_Pag_Reg_6prevhierr", "EESS_Ate_6prevhierr", "Intervalo6s"
    ],
    
    "DOSAJE_HEMOGLOBINA_1": [
        "fecha_1DH", "Lab_1DH", "edad_1DH", "CIE_DH_1DH", "Lote_Pag_Reg_1DH", "EESS_Ate_1DH"
    ]
}

RESUMEN = {
    "Mes_Nac": {
        "descripcion": "Mes de nacimiento del niño"
    },
    
    "obs_credRN1": {
        "descripcion": "Observación de CRED recién nacido"
    },
    
    "Obs_CRED1mas": {
        "descripcion": "Observación de CRED mayor a 1 mes"
    },
    
    "Cred_cumple": {
        "descripcion": "Indica si cumple con CRED de recien nacido y mayor a 1 mes según corresponda"
    },
    
    "obs_neu1": {
        "descripcion": "Observación de vacuna neumococo"
    },
    
    "obs_rot1": {
        "descripcion": "Observación de vacuna Rotavirus"
    },
    
    "obs_ant1": {
        "descripcion": "Observación de vacuna antipolio"
    },
    
    "obs_pen1": {
        "descripcion": "Observación de vacuna Pentavalente"
    },
    
    "Obs_Anemia": {
        "descripcion": "Observacion operativa del tratamiento de anemia; aplica solo cuando existe Dx_Anemia o Fec_Anemia."
    },
    
    "obs_suple41": {
        "descripcion": "Observación de suplementación 4 meses"
    },
    
    "obs_suple61": {
        "descripcion": "Observación de suplementación 6 meses"
    },
    
    "Obs_dh1": {
        "descripcion": "Observación de dosaje de hemoglobina"
    },
    
    "Estado": {
        "descripcion": "Estado actual del registro respecto al indicador"
    },
    
    "Registros": {
        "descripcion": "Cantidad de registros"
    }
}
