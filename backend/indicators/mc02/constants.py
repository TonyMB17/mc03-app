"""Central constants for MC-02.

This module exposes the names that should be shared across loader, dashboard
and evaluator code. The concrete business values still live in ``config.py`` so
the operative Excel contract remains in one place.
"""

from .config import CODIGOS_ESTANDAR, REGLAS_NEGOCIO


ESTADOS_COMPONENTE = {
    "CUMPLE": "cumple",
    "PROGRAMADO": "programado",
    "PENDIENTE_EN_PLAZO": "pendiente_en_plazo",
    "INCUMPLIMIENTO_FUERA_PLAZO": "incumplimiento_fuera_plazo",
    "FUERA_DE_VENTANA": "fuera_de_ventana",
    "DATO_INSUFICIENTE": "dato_insuficiente",
    "EXCLUIDO_DENOMINADOR": "excluido_denominador",
}

VENTANAS_ATENCION = REGLAS_NEGOCIO["VENTANAS_ATENCION"]
COMPONENTES_ACTIVOS = REGLAS_NEGOCIO["COMPONENTES_ACTIVOS"]
CRITERIOS_EXCLUSION = REGLAS_NEGOCIO["CRITERIOS_EXCLUSION"]
CRITERIOS_OMITIDOS = REGLAS_NEGOCIO["CRITERIOS_OMITIDOS_ACTUALMENTE"]
CODIGOS = CODIGOS_ESTANDAR
