"""Registry for available indicator modules."""

from . import mc02, mc03
try:
    from ..core.indicators import IndicatorDefinition
except ImportError:
    from core.indicators import IndicatorDefinition


INDICATORS = {
    mc02.CODE: IndicatorDefinition.from_module(mc02),
    mc03.CODE: IndicatorDefinition.from_module(mc03),
}


def list_indicators() -> list[IndicatorDefinition]:
    return list(INDICATORS.values())


def get_indicator(code: str) -> IndicatorDefinition:
    return INDICATORS[code.lower()]
