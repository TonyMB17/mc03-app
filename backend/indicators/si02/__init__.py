"""SI-02 indicator package."""

from .config import CODE, DEFAULT_PROVINCE, DEFAULT_TARGET_COVERAGE, NAME, SUBINDICATORS
from .commitment import build_commitment_summary, current_commitment_met
from .excel_loader import (
    identify_subindicator,
    load_sample_data,
    load_subindicator_data,
    operational_columns,
    prepare_data_file,
    prepare_data_files,
    prepare_subindicator_file,
    prepare_upload_package,
    required_columns,
    validate_data_file,
    validate_subindicator_file,
    validate_upload_package,
)
from .evaluator import evaluate_dataframe, evaluate_row
from .processor import build_package_summary, build_report_summary, build_subindicator_summary, get_filter_options, search_by_dni
from .storage import active_upload_id, build_active_report_summary, persist_active_upload, search_active_by_dni

__all__ = [
    "CODE",
    "DEFAULT_PROVINCE",
    "DEFAULT_TARGET_COVERAGE",
    "NAME",
    "SUBINDICATORS",
    "active_upload_id",
    "build_commitment_summary",
    "identify_subindicator",
    "load_sample_data",
    "load_subindicator_data",
    "operational_columns",
    "prepare_data_file",
    "prepare_data_files",
    "prepare_subindicator_file",
    "prepare_upload_package",
    "required_columns",
    "validate_data_file",
    "validate_subindicator_file",
    "validate_upload_package",
    "build_package_summary",
    "build_report_summary",
    "build_active_report_summary",
    "build_subindicator_summary",
    "current_commitment_met",
    "evaluate_dataframe",
    "evaluate_row",
    "get_filter_options",
    "persist_active_upload",
    "search_active_by_dni",
    "search_by_dni",
]
