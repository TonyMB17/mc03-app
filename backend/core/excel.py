from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import load_workbook

from .dates import parse_excel_date


def open_workbook(filepath: Path):
    return load_workbook(filepath, data_only=True, read_only=True)


def read_sheet(filepath: Path, sheet_name: str, header_row: int) -> pd.DataFrame:
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=header_row - 1, engine="openpyxl")
    df.columns = [str(column).strip() for column in df.columns]
    return df


def read_cutoff_date(filepath: Path, sheet_name: str, cell: str) -> Any:
    workbook = open_workbook(filepath)
    if sheet_name not in workbook.sheetnames:
        raise ValueError(f"La hoja '{sheet_name}' no se encuentra en el archivo de datos")
    return parse_excel_date(workbook[sheet_name][cell].value)


def build_validation_error(message: str, summary: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"valid": False, "errors": [message], "warnings": [], "summary": summary or {}}
