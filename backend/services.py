"""Compatibility facade for the MC-03 indicator processor.

The current API still imports functions from `backend.services`. During phase 1
we keep that public surface stable while moving MC-03-specific logic into the
indicator module.
"""

try:
    from .indicators.mc03.processor import (
        ALL_PROVINCES_TOKEN,
        DEFAULT_PROVINCE,
        MONTHS_2026,
        REQUIRED_COLUMNS,
        VERIFICATION_MONTHS,
        build_report_summary,
        evaluate_package,
        filter_data,
        get_filter_options,
        load_sample_data,
        search_by_dni,
        validate_data_file,
    )
except ImportError:
    from indicators.mc03.processor import (
        ALL_PROVINCES_TOKEN,
        DEFAULT_PROVINCE,
        MONTHS_2026,
        REQUIRED_COLUMNS,
        VERIFICATION_MONTHS,
        build_report_summary,
        evaluate_package,
        filter_data,
        get_filter_options,
        load_sample_data,
        search_by_dni,
        validate_data_file,
    )

__all__ = [
    "ALL_PROVINCES_TOKEN",
    "DEFAULT_PROVINCE",
    "MONTHS_2026",
    "REQUIRED_COLUMNS",
    "VERIFICATION_MONTHS",
    "build_report_summary",
    "evaluate_package",
    "filter_data",
    "get_filter_options",
    "load_sample_data",
    "search_by_dni",
    "validate_data_file",
]
