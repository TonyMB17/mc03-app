import json
import re
import shutil
from datetime import datetime
from io import BytesIO, StringIO
from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

try:
    from .schemas import (
        DataActivateRequest,
        DataCurrentResponse,
        DataUploadPreviewResponse,
        FilterOptionsResponse,
        HealthResponse,
        OmisosResponse,
        ReportSummary,
        SearchDNIResult,
    )
    from .services import build_report_summary, get_filter_options, load_sample_data, search_by_dni, validate_data_file
    from .indicators.registry import get_indicator, list_indicators
except ImportError:
    from schemas import (
        DataActivateRequest,
        DataCurrentResponse,
        DataUploadPreviewResponse,
        FilterOptionsResponse,
        HealthResponse,
        OmisosResponse,
        ReportSummary,
        SearchDNIResult,
    )
    from services import build_report_summary, get_filter_options, load_sample_data, search_by_dni, validate_data_file
    from indicators.registry import get_indicator, list_indicators

app = FastAPI(
    title="Sistema de Seguimiento Neonatal - MC-03",
    description="API para monitoreo de vacunacion, CRED, tamizaje neonatal y carga de datos.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path(__file__).resolve().parent.parent / "data_samples" / "MC 03_FT_BCG_HVB_PAQUETE RN.xlsx"
DATA_FILES = {
    "mc03": DATA_FILE,
    "mc02": Path(__file__).resolve().parent.parent / "data_samples" / "MC 02_FT MC_02 _INFANTIL.xlsx",
}
UPLOADS_DIR = Path(__file__).resolve().parent / "uploads"
DATA_STATE_FILE = Path(__file__).resolve().parent / "data_state.json"


def _json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _safe_filename(filename: str) -> str:
    clean_name = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(filename).name).strip("._")
    return clean_name or "archivo_indicador.xlsx"


def _load_data_state() -> dict | None:
    if not DATA_STATE_FILE.exists():
        return None
    try:
        return json.loads(DATA_STATE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _write_data_state(state: dict) -> None:
    DATA_STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2, default=_json_default), encoding="utf-8")


def _indicator_definition(indicator: str):
    try:
        return get_indicator(indicator.lower())
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Indicador no disponible: {indicator}")


def _indicator_store(indicator: str) -> dict:
    store = getattr(app.state, "indicator_data", {})
    return store.get(indicator.lower(), {})


def _active_dataframe(indicator: str):
    return _indicator_store(indicator).get("data")


def _active_cutoff_date(indicator: str):
    return _indicator_store(indicator).get("cutoff_date")


def _build_current_summary(filepath: Path, metadata: dict | None = None, indicator: str = "mc03") -> dict:
    definition = _indicator_definition(indicator)
    validation = definition.validate_data_file(filepath)
    summary = validation["summary"]
    return {
        "indicator_code": summary.get("indicator_code", definition.code),
        "indicator_name": summary.get("indicator_name", definition.name),
        "filename": filepath.name,
        "original_name": (metadata or {}).get("original_name") or filepath.name,
        "file_size_bytes": summary.get("file_size_bytes"),
        "uploaded_at": (metadata or {}).get("uploaded_at"),
        "activated_at": (metadata or {}).get("activated_at"),
        "sheet_name": summary.get("sheet_name"),
        "cutoff_cell": summary.get("cutoff_cell"),
        "header_row": summary.get("header_row"),
        "cutoff_date": summary.get("cutoff_date"),
        "total_rows": summary.get("total_rows"),
        "total_columns": summary.get("total_columns"),
        "required_columns_count": summary.get("required_columns_count"),
        "missing_columns": summary.get("missing_columns", []),
        "omitted_columns": summary.get("omitted_columns", []),
        "provinces": summary.get("provinces", []),
        "months": summary.get("months", []),
        "validation_label": summary.get("validation_label"),
        "status_counts": summary.get("status_counts", {}),
        "denominator_counts": summary.get("denominator_counts", {}),
        "component_counts": summary.get("component_counts", {}),
        "obs_eval_counts": summary.get("obs_eval_counts", {}),
        "insurance_counts": summary.get("insurance_counts", {}),
    }


def _activate_data_file(filepath: Path, metadata: dict | None = None, indicator: str = "mc03") -> None:
    definition = _indicator_definition(indicator)
    sample_bundle = definition.load_sample_data(filepath)
    if sample_bundle is None:
        raise HTTPException(status_code=404, detail="No se encontro el archivo de datos")

    app.state.indicator_data[indicator] = {
        "data": sample_bundle["data"],
        "cutoff_date": sample_bundle["cutoff_date"],
        "active_file": filepath,
        "current_data_summary": _build_current_summary(filepath, metadata, indicator),
    }

    if indicator == "mc03":
        app.state.data = sample_bundle["data"]
        app.state.cutoff_date = sample_bundle["cutoff_date"]
        app.state.active_file = filepath
        app.state.current_data_summary = app.state.indicator_data[indicator]["current_data_summary"]


def _filter_omisos_by_month(omisos: list[dict], month: str | None) -> list[dict]:
    if not month:
        return omisos
    return [item for item in omisos if item.get("Mes_eva") == month]


def _incumplidos_xlsx(omisos: list[dict]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Incumplidos"

    columns = [
        ("Mes evaluacion", "Mes_eva"),
        ("Mes", "month"),
        ("Anio", "year"),
        ("DNI", "afi_DNI"),
        ("CNV", "NumCNV"),
        ("Fecha de nacimiento", "fec_Nac"),
        ("Nombres", "afi_nombres"),
        ("Apellido paterno", "afi_appaterno"),
        ("Apellido materno", "afi_apmaterno"),
        ("Provincia", "Desc_prov"),
        ("Microred", "Des_MicroRed"),
        ("Codigo RENAES", "pre_CodigoRENAES"),
        ("Establecimiento", "Des_EESS"),
        ("Componente observado", "component"),
        ("Fecha atencion observada", "attention_date"),
        ("Edad atencion dias", "attention_age_days"),
        ("EESS atencion", "attention_facility"),
        ("Profesional atencion", "attention_professional"),
        ("Alertas clinicas", "clinical_alerts"),
        ("Motivo de incumplimiento", "reason"),
    ]

    for column_index, (header, _) in enumerate(columns, start=1):
        cell = sheet.cell(row=1, column=column_index, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="0F172A")

    for row_index, item in enumerate(omisos, start=2):
        for column_index, (_, key) in enumerate(columns, start=1):
            value = item.get(key)
            if isinstance(value, list):
                value = "; ".join(str(part) for part in value if part)
            sheet.cell(row=row_index, column=column_index, value=value)

    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for column_index, (header, key) in enumerate(columns, start=1):
        max_length = len(header)
        for item in omisos:
            max_length = max(max_length, len(str(item.get(key) or "")))
        sheet.column_dimensions[get_column_letter(column_index)].width = min(max_length + 2, 55)

    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


@app.on_event("startup")
def startup_event():
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    app.state.pending_uploads = {}
    app.state.indicator_data = {}

    state = _load_data_state()
    active_file = Path(state["active_file"]) if state and state.get("active_file") else DATA_FILE
    if not active_file.exists():
        active_file = DATA_FILE

    try:
        _activate_data_file(active_file, state, "mc03")
    except Exception:
        app.state.data = None
        app.state.cutoff_date = None
        app.state.active_file = None
        app.state.current_data_summary = None

    for indicator, filepath in DATA_FILES.items():
        if indicator == "mc03" or not filepath.exists():
            continue
        try:
            _activate_data_file(filepath, None, indicator)
        except Exception:
            app.state.indicator_data[indicator] = {
                "data": None,
                "cutoff_date": None,
                "active_file": None,
                "current_data_summary": None,
            }


@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
def health_check():
    source_file = str(app.state.active_file) if getattr(app.state, "active_file", None) else str(DATA_FILE)
    return HealthResponse(status="ok", version="0.1.0", source_file=source_file)


@app.get("/api/indicators", tags=["Sistema"])
def api_indicators():
    return [
        {
            "code": indicator.code,
            "name": indicator.name,
            "has_data": _indicator_store(indicator.code).get("data") is not None,
        }
        for indicator in list_indicators()
    ]


@app.get("/api/data/current", response_model=DataCurrentResponse, tags=["Carga de datos"])
def api_data_current(indicator: str = Query("mc03")):
    definition = _indicator_definition(indicator)
    indicator = definition.code
    store = _indicator_store(indicator)
    active_file = store.get("active_file")
    return DataCurrentResponse(
        has_data=store.get("data") is not None,
        active_file=str(active_file) if active_file else None,
        summary=store.get("current_data_summary"),
    )


@app.post("/api/data/upload-preview", response_model=DataUploadPreviewResponse, tags=["Carga de datos"])
def api_data_upload_preview(file: UploadFile = File(...), indicator: str = Query("mc03")):
    definition = _indicator_definition(indicator)
    indicator = definition.code
    suffix = Path(file.filename or "").suffix.lower()
    if suffix != ".xlsx":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos Excel .xlsx")

    upload_id = uuid4().hex
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = _safe_filename(file.filename or f"archivo_{definition.code}.xlsx")
    destination = UPLOADS_DIR / f"{timestamp}_{upload_id[:8]}_{original_name}"

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    validation = definition.validate_data_file(destination)
    uploaded_at = datetime.now().isoformat(timespec="seconds")
    summary = {
        **validation["summary"],
        "filename": destination.name,
        "original_name": file.filename,
        "uploaded_at": uploaded_at,
    }

    app.state.pending_uploads[upload_id] = {
        "path": str(destination),
        "original_name": file.filename,
        "uploaded_at": uploaded_at,
        "valid": validation["valid"],
        "indicator": indicator,
    }

    return DataUploadPreviewResponse(
        upload_id=upload_id,
        valid=validation["valid"],
        errors=validation["errors"],
        warnings=validation["warnings"],
        summary=summary,
    )


@app.post("/api/data/activate", response_model=DataCurrentResponse, tags=["Carga de datos"])
def api_data_activate(payload: DataActivateRequest, indicator: str = Query("mc03")):
    definition = _indicator_definition(indicator)
    indicator = definition.code
    pending = app.state.pending_uploads.get(payload.upload_id)
    if pending is None:
        raise HTTPException(status_code=404, detail="No se encontro la carga pendiente")
    if pending.get("indicator") != indicator:
        raise HTTPException(status_code=400, detail="La carga pendiente corresponde a otro indicador")
    if not pending["valid"]:
        raise HTTPException(status_code=400, detail="El archivo tiene errores de validacion y no puede activarse")

    filepath = Path(pending["path"])
    validation = definition.validate_data_file(filepath)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail="El archivo ya no supera la validacion")

    metadata = {
        "active_file": str(filepath),
        "original_name": pending["original_name"],
        "uploaded_at": pending["uploaded_at"],
        "activated_at": datetime.now().isoformat(timespec="seconds"),
    }
    _activate_data_file(filepath, metadata, indicator)
    if indicator == "mc03":
        _write_data_state(metadata)
    app.state.pending_uploads.pop(payload.upload_id, None)

    return DataCurrentResponse(
        has_data=True,
        active_file=str(filepath),
        summary=_indicator_store(indicator).get("current_data_summary"),
    )


@app.get("/api/config/options", response_model=FilterOptionsResponse, tags=["Configuracion"])
def api_config_options(indicator: str = Query("mc03")):
    data = _active_dataframe(indicator)
    if data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    definition = _indicator_definition(indicator)
    return FilterOptionsResponse(**definition.get_filter_options(data))


@app.get("/api/report/summary", response_model=ReportSummary, tags=["Reporte"])
def api_report_summary(province: str = Query("ABANCAY"), target: float = Query(70.7), indicator: str = Query("mc03")):
    data = _active_dataframe(indicator)
    if data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    definition = _indicator_definition(indicator)
    summary_dict = definition.build_report_summary(data, _active_cutoff_date(indicator), province, target)
    return ReportSummary(**summary_dict)


@app.get("/api/report/omisos", response_model=OmisosResponse, tags=["Reporte"])
def api_report_omisos(province: str = Query("ABANCAY"), indicator: str = Query("mc03")):
    data = _active_dataframe(indicator)
    if data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    definition = _indicator_definition(indicator)
    summary = definition.build_report_summary(data, _active_cutoff_date(indicator), province)
    return OmisosResponse(omisos=summary["omisos"])


@app.get("/api/report/incumplidos", response_model=OmisosResponse, tags=["Reporte"])
def api_report_incumplidos(province: str = Query("ABANCAY"), indicator: str = Query("mc03")):
    data = _active_dataframe(indicator)
    if data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    definition = _indicator_definition(indicator)
    summary = definition.build_report_summary(data, _active_cutoff_date(indicator), province)
    return OmisosResponse(omisos=summary["omisos"])


@app.get("/api/report/omisos.csv", tags=["Reporte"])
def api_report_omisos_csv(province: str = Query("ABANCAY"), indicator: str = Query("mc03")):
    data = _active_dataframe(indicator)
    if data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    definition = _indicator_definition(indicator)
    summary = definition.build_report_summary(data, _active_cutoff_date(indicator), province)
    output = StringIO()
    pd.DataFrame(summary["omisos"]).to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="omisos_{indicator}.csv"'},
    )


@app.get("/api/report/incumplidos.csv", tags=["Reporte"])
def api_report_incumplidos_csv(province: str = Query("ABANCAY"), month: str | None = Query(None), indicator: str = Query("mc03")):
    data = _active_dataframe(indicator)
    if data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    definition = _indicator_definition(indicator)
    summary = definition.build_report_summary(data, _active_cutoff_date(indicator), province)
    output = StringIO()
    pd.DataFrame(_filter_omisos_by_month(summary["omisos"], month)).to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="incumplidos_{indicator}.csv"'},
    )


@app.get("/api/report/incumplidos.xlsx", tags=["Reporte"])
def api_report_incumplidos_xlsx(province: str = Query("ABANCAY"), month: str | None = Query(None), indicator: str = Query("mc03")):
    data = _active_dataframe(indicator)
    if data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    definition = _indicator_definition(indicator)
    summary = definition.build_report_summary(data, _active_cutoff_date(indicator), province)
    content = _incumplidos_xlsx(_filter_omisos_by_month(summary["omisos"], month))
    filename_month = f"_{month}" if month else ""
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="incumplidos_{indicator}{filename_month}.xlsx"'},
    )


@app.get("/api/search/dni/{dni}", response_model=SearchDNIResult, tags=["Busqueda"])
def api_search_dni(dni: str, province: str = Query("ABANCAY"), indicator: str = Query("mc03")):
    data = _active_dataframe(indicator)
    if data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    definition = _indicator_definition(indicator)
    result = definition.search_by_dni(data, dni, _active_cutoff_date(indicator), province)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No se encontro registro para DNI: {dni}")

    return SearchDNIResult(**result)
