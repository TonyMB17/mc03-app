"""MC-03 indicator module."""

from .processor import build_report_summary, get_filter_options, load_sample_data, search_by_dni, validate_data_file

CODE = "mc03"
NAME = "Paquete recien nacido"
DEFAULT_PROVINCE = "ABANCAY"
DEFAULT_TARGET_COVERAGE = 70.7

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
