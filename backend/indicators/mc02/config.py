"""MC-02 indicator-level configuration.

This module keeps the general identity and operational defaults of the
indicator. Domain rules live in focused modules: service codes in ``codes.py``,
component windows in ``components/`` and the Excel contract in
``excel_schema.py``.
"""

from .codes import CODIGOS_ESTANDAR
from .components import COMPONENT_WINDOWS
from .excel_schema import COLUMNAS_EXCEL, RESUMEN


CODE = "mc02"
NAME = "Paquete integrado menores de 12 meses"
DEFAULT_PROVINCE = "ABANCAY"
DEFAULT_TARGET_COVERAGE = 80.9

EXCEL_SHEET = "Detalle_Ate"
CUTOFF_CELL = "D9"
HEADER_ROW = 10

REGLAS_NEGOCIO = {
    "META_COBERTURA_MENSUAL": DEFAULT_TARGET_COVERAGE,
    "PROVINCIA_DEFECTO": DEFAULT_PROVINCE,
    "COLUMNA_TIPO_SEGURO": "Obs_Niño",
    "SEGUROS_INCLUIDOS": {"SIS", "NINGUNO", "SIN SEGURO", "SIN_SEGURO", ""},
    "COLUMNA_DENOMINADOR": "Registros",
    "VALOR_DENOMINADOR": 1,
    "COLUMNA_NUMERADOR_OPERATIVO": "Estado",
    "COLUMNA_MES_EVALUACION": "Mes_Nac",
    "COLUMNA_PROVINCIA": "provincia",
    "CRITERIOS_EXCLUSION": {
        "COLUMNA_PESO": "Peso",
        "COLUMNA_GESTACION": "Edad_Gestacional",
        "PESO_MIN": 2500,
        "GESTACION_MIN": 37,
        "FUENTE": "CNV",
        "INCLUIR_VACIOS": True,
        "NOTA": "Excluir solo cuando Peso o Edad_Gestacional tengan valor conocido menor al umbral. Si el dato esta vacio, el registro permanece en el denominador.",
    },
    "CRITERIOS_OMITIDOS_ACTUALMENTE": {
        "CRED": "El Excel trae controles CRED, pero no se consideran en el calculo MC-02 actual.",
        "DNI_30_DIAS": "La ficha tecnica menciona DNI emitido hasta 30 dias, pero no corresponde al area salud.",
    },
    "ALERTA_ANEMIA": {
        "COLUMNAS_DIAGNOSTICO": ["Dx_Anemia"],
        "COLUMNAS_FECHA": ["Fec_Anemia"],
        "COLUMNA_OBSERVACION": "Obs_Anemia",
        "MENSAJE": "Si existe Dx_Anemia D509/D649 o Fec_Anemia, revisar entrega de hierro como tratamiento: primera entrega vinculada a anemia y al menos 3 entregas validas.",
        "NOTA_OBS_ANEMIA": (
            "Obs_Anemia no es fuente primaria de diagnostico. En el Excel operativo se usa para marcar el resultado "
            "del tratamiento solo cuando existe diagnostico de anemia. Si no hay Dx_Anemia o Fec_Anemia, Obs_Anemia "
            "puede indicar que el tratamiento no corresponde y no debe generar alerta clinica ni penalizar el cumplimiento."
        ),
    },
    "COMPONENTES_ACTIVOS": {
        "NEUMOCOCO": "obs_neu1",
        "ROTAVIRUS": "obs_rot1",
        "ANTIPOLIO": "obs_ant1",
        "PENTAVALENTE": "obs_pen1",
        "HIERRO_MENOR_6_MESES": "obs_suple41",
        "HIERRO_MAYOR_6_MESES": "obs_suple61",
        "DOSAJE_HEMOGLOBINA": "Obs_dh1",
    },
    "VENTANAS_ATENCION": COMPONENT_WINDOWS,
    "RESPONSABLE_ATENCION": {
        "NEUMOCOCO": {"eess": "EESS_Ate_NEU", "profesional": None},
        "ROTAVIRUS": {"eess": "EESS_Ate_1Rot", "profesional": None},
        "ANTIPOLIO": {"eess": "EESS_Ate_1ANT", "profesional": None},
        "PENTAVALENTE": {"eess": "EESS_Ate_1PENT", "profesional": None},
        "HIERRO_MENOR_6_MESES": {"eess": "EESS_Ate_1prev", "profesional": None},
        "HIERRO_MAYOR_6_MESES": {"eess": "EESS_Ate_1prevhierr", "profesional": None},
        "DOSAJE_HEMOGLOBINA": {"eess": "EESS_Ate_1DH", "profesional": None},
    },
}

__all__ = [
    "CODE",
    "CODIGOS_ESTANDAR",
    "COLUMNAS_EXCEL",
    "CUTOFF_CELL",
    "DEFAULT_PROVINCE",
    "DEFAULT_TARGET_COVERAGE",
    "EXCEL_SHEET",
    "HEADER_ROW",
    "NAME",
    "REGLAS_NEGOCIO",
    "RESUMEN",
]
