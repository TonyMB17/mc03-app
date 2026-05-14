"""Compatibility facade for MC-03 configuration.

MC-03-specific constants now live in `backend.indicators.mc03.config`. This
module remains so existing imports continue to work during the migration.
"""

try:
    from .indicators.mc03.config import CODIGOS_ESTANDAR, COLUMNAS_EXCEL, REGLAS_NEGOCIO
except ImportError:
    from indicators.mc03.config import CODIGOS_ESTANDAR, COLUMNAS_EXCEL, REGLAS_NEGOCIO

__all__ = ["CODIGOS_ESTANDAR", "COLUMNAS_EXCEL", "REGLAS_NEGOCIO"]
