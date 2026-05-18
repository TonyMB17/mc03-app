# config.py - Configuración de Estructuras de Datos y Reglas de Negocio
# Red de Salud Abancay - Sistema NeoAbancay

CODE = "mc03"
NAME = "Paquete recien nacido"
DEFAULT_PROVINCE = "ABANCAY"
DEFAULT_TARGET_COVERAGE = 70.7
ALL_PROVINCES_TOKEN = "__ALL__"

EXCEL_SHEET = "Detalle_Ate"
CUTOFF_CELL = "B8"
HEADER_ROW = 10

MONTHS_2026 = [
    (1, "enero"),
    (2, "febrero"),
    (3, "marzo"),
    (4, "abril"),
    (5, "mayo"),
    (6, "junio"),
    (7, "julio"),
    (8, "agosto"),
    (9, "setiembre"),
    (10, "octubre"),
    (11, "noviembre"),
]
MONTH_LABELS = {month: name for month, name in MONTHS_2026}
VERIFICATION_MONTHS = {6, 7, 8, 9, 10, 11}

# 1. CODIGOS PRESTACIONALES (Según Ficha Técnica MC-03)
CODIGOS_ESTANDAR = {
    "BCG": "90585",        # [cite: 95]
    "HVB": "90744",        # [cite: 95]
    "CRED": "99381.01",    # [cite: 46, 97]
    "TAMIZAJE": "36416"    # [cite: 102]
}

# 2. AGRUPACIÓN DE CABECERAS DEL EXCEL
# Mapeo de columnas para facilitar la lectura y filtrado con Pandas
COLUMNAS_EXCEL = {
    "UBICACION": [
        "ubigeo", "Desc_prov", "Desc_Dist", "Des_Red", 
        "Des_MicroRed", "pre_CodigoRENAES", "Des_EESS", "fed"
    ],
    
    "DATOS_GENERALES": [
        "afi_DNI", "NumCNV", "afi_nombres", "afi_appaterno", 
        "afi_apmaterno", "NomApellMadre", "DNIMadre", "Celular", 
        "Esta_pac", "his_cli", "peso", "edadGEst", "Est_Nac", "fec_Nac"
    ],
    
    "EVALUACION": [
        "Mes_eva", "Obs_Eval", "Obs_CRED", "Obs_General"
    ],
    
    "VACUNA_BCG": [
        "fec1_BCG", "resul1_BCG", "Edad_ate1_BCG", 
        "BCG_1_1", "reg_BCG1", "eess_BCG1", "Obs_BCG"
    ],
    
    "VACUNA_HVB": [
        "fecHVB", "resulHVB", "Edad_ateHVB", 
        "sg_HVB", "reg_HVB", "eess_HVB", "Obs_HVB"
    ],
    
    "CRED_1": [
        "Fecha_Atencion_1", "Lab_1", "Edad_Atencion_1", 
        "CIE10_1", "Codigo_HIS_1", "Registro_1", "EESS_Atencion_1"
    ],
    
    "CRED_2": [
        "Fecha_Atencion_2", "Lab_2", "Edad_Atencion_2", 
        "CIE10_2", "Codigo_HIS_2", "Registro_2", "EESS_Atencion2", "Intervalo_2"
    ],
    
    "CRED_3": [
        "Fecha_Atencion_3", "Lab_3", "Edad_Atencion_3", 
        "CIE10_3", "Codigo_HIS_3", "Registro_3", "EESS_Atencion_3", "Intervalo_3"
    ],
    
    "CRED_4": [ # Control adicional no contemplado en el numerador principal pero registrado
        "Fecha_Atencion_4", "lab_4", "Edad_Atencion_4", 
        "CIE10_4", "Codigo_HIS_4", "Registro_4", "EESS_Atencion_4", "Intervalo_4"
    ],
    
    "TAMIZAJE": [
        "Fecha_Atencion_TN", "Lab_TN", "Edad_Atencion_TN", 
        "Codigo_HIS_TN", "Registro_TN", "EESS_Atencion_TN", "Obs_TM"
    ]
}

# 3. REGLAS DE TIEMPOS Y PERIODOS (Validación de Ventanas Temporales)
REGLAS_NEGOCIO = {
    "META_COBERTURA_MENSUAL": 70.7,

    "SEGUROS_INCLUIDOS": {"SIS", "NINGUNO", "SIN SEGURO", "SIN_SEGURO",""},

    "VACUNAS_PLAZO_MAX_HORAS": 24, # [cite: 15, 43, 95]
    
    "TAMIZAJE_VENTANA": {
        "inicio_dia": 2, # [cite: 17, 44, 102]
        "fin_dia": 6     # [cite: 17, 44, 102]
    },
    
    "CRED_VENTANAS": {
        "1ER_CRED": {"inicio": 3, "fin": 6},   # [cite: 98]
        "2DO_CRED": {"inicio": 7, "fin": 14},  # [cite: 99]
        "3ER_CRED": {"inicio": 15, "fin": 21}  # [cite: 100]
    },
    
    "INTERVALO_MIN_CRED": 7, # Días mínimos entre controles [cite: 105]
    
    "CRITERIOS_EXCLUSION": {
        "PESO_MIN": 2500,     # 
        "GESTACION_MIN": 37   # 
    }
}

REQUIRED_COLUMNS = [
    "Mes_eva",
    "Obs_Eval",
    "Esta_pac",
    "Desc_prov",
    "afi_DNI",
    "NumCNV",
    "fec_Nac",
    "fec1_BCG",
    "resul1_BCG",
    "Edad_ate1_BCG",
    "fecHVB",
    "resulHVB",
    "Edad_ateHVB",
    "Fecha_Atencion_1",
    "Codigo_HIS_1",
    "Edad_Atencion_1",
    "Fecha_Atencion_2",
    "Codigo_HIS_2",
    "Edad_Atencion_2",
    "Intervalo_2",
    "Fecha_Atencion_3",
    "Codigo_HIS_3",
    "Edad_Atencion_3",
    "Intervalo_3",
    "Fecha_Atencion_TN",
    "Codigo_HIS_TN",
    "Edad_Atencion_TN",
]
