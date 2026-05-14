"""MC-03 business rules.

The concrete implementation still lives in `processor.py` while the module is
being migrated. This file keeps the same folder contract for every indicator.
"""

from .config import CODIGOS_ESTANDAR, REGLAS_NEGOCIO

__all__ = ["CODIGOS_ESTANDAR", "REGLAS_NEGOCIO"]
