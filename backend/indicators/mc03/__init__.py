"""MC-03 indicator module."""

from .config import CODE, DEFAULT_PROVINCE, DEFAULT_TARGET_COVERAGE, NAME
from .processor import build_report_summary, get_filter_options, load_sample_data, search_by_dni, validate_data_file
from .storage import active_upload_id, build_active_report_summary, persist_active_upload, search_active_by_dni

__all__ = [
    "CODE",
    "NAME",
    "DEFAULT_PROVINCE",
    "DEFAULT_TARGET_COVERAGE",
    "active_upload_id",
    "build_report_summary",
    "build_active_report_summary",
    "get_filter_options",
    "load_sample_data",
    "persist_active_upload",
    "search_active_by_dni",
    "search_by_dni",
    "validate_data_file",
]
