"""MC-02 indicator module."""

from .processor import build_report_summary, get_filter_options, load_sample_data, search_by_dni, validate_data_file

CODE = "mc02"
NAME = "Paquete integrado menores de 12 meses"
DEFAULT_TARGET_COVERAGE = 80.9
DEFAULT_PROVINCE = "ABANCAY"

__all__ = [
    "CODE",
    "NAME",
    "DEFAULT_PROVINCE",
    "DEFAULT_TARGET_COVERAGE",
    "build_report_summary",
    "get_filter_options",
    "load_sample_data",
    "search_by_dni",
    "validate_data_file",
]
