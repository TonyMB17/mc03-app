"""MC-02 indicator module."""

from .processor import (
    build_report_summary,
    get_filter_options,
    load_sample_data,
    active_upload_id,
    build_active_report_summary,
    persist_active_upload,
    prepare_data_file,
    search_active_by_dni,
    search_by_dni,
    validate_data_file,
)

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
    "active_upload_id",
    "build_active_report_summary",
    "prepare_data_file",
    "persist_active_upload",
    "search_active_by_dni",
    "search_by_dni",
    "validate_data_file",
]
