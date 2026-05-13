from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

try:
    from .schemas import FilterOptionsResponse, HealthResponse, OmisosResponse, ReportSummary, SearchDNIResult
    from .services import build_report_summary, get_filter_options, load_sample_data, search_by_dni
except ImportError:
    from schemas import FilterOptionsResponse, HealthResponse, OmisosResponse, ReportSummary, SearchDNIResult
    from services import build_report_summary, get_filter_options, load_sample_data, search_by_dni

app = FastAPI(
    title="Sistema de Seguimiento Neonatal - MC-03",
    description="API inicial para monitoreo de vacunación, CRED y tamizaje neonatal.",
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


def _filter_omisos_by_month(omisos: list[dict], month: str | None) -> list[dict]:
    if not month:
        return omisos
    return [item for item in omisos if item.get("Mes_eva") == month]


def _incumplidos_xlsx(omisos: list[dict]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Incumplidos"

    columns = [
        ("Mes evaluación", "Mes_eva"),
        ("Mes", "month"),
        ("Año", "year"),
        ("DNI", "afi_DNI"),
        ("CNV", "NumCNV"),
        ("Fecha de nacimiento", "fec_Nac"),
        ("Nombres", "afi_nombres"),
        ("Apellido paterno", "afi_appaterno"),
        ("Apellido materno", "afi_apmaterno"),
        ("Provincia", "Desc_prov"),
        ("Microred", "Des_MicroRed"),
        ("Código RENAES", "pre_CodigoRENAES"),
        ("Establecimiento", "Des_EESS"),
        ("Motivo de incumplimiento", "reason"),
    ]

    for column_index, (header, _) in enumerate(columns, start=1):
        cell = sheet.cell(row=1, column=column_index, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="0F172A")

    for row_index, item in enumerate(omisos, start=2):
        for column_index, (_, key) in enumerate(columns, start=1):
            sheet.cell(row=row_index, column=column_index, value=item.get(key))

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
    """Carga datos de ejemplo si están disponibles."""
    sample_bundle = load_sample_data(DATA_FILE)
    if sample_bundle is None:
        app.state.data = None
        app.state.cutoff_date = None
    else:
        app.state.data = sample_bundle["data"]
        app.state.cutoff_date = sample_bundle["cutoff_date"]


@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
def health_check():
    return HealthResponse(status="ok", version="0.1.0", source_file=str(DATA_FILE))


@app.get("/api/config/options", response_model=FilterOptionsResponse, tags=["Configuración"])
def api_config_options():
    if app.state.data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    return FilterOptionsResponse(**get_filter_options(app.state.data))


@app.get("/api/report/summary", response_model=ReportSummary, tags=["Reporte"])
def api_report_summary(province: str = Query("ABANCAY"), target: float = Query(70.7)):
    if app.state.data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    summary_dict = build_report_summary(app.state.data, app.state.cutoff_date, province, target)
    return ReportSummary(**summary_dict)


@app.get("/api/report/omisos", response_model=OmisosResponse, tags=["Reporte"])
def api_report_omisos(province: str = Query("ABANCAY")):
    if app.state.data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    summary = build_report_summary(app.state.data, app.state.cutoff_date, province)
    return OmisosResponse(omisos=summary["omisos"])


@app.get("/api/report/incumplidos", response_model=OmisosResponse, tags=["Reporte"])
def api_report_incumplidos(province: str = Query("ABANCAY")):
    if app.state.data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    summary = build_report_summary(app.state.data, app.state.cutoff_date, province)
    return OmisosResponse(omisos=summary["omisos"])


@app.get("/api/report/omisos.csv", tags=["Reporte"])
def api_report_omisos_csv(province: str = Query("ABANCAY")):
    if app.state.data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    summary = build_report_summary(app.state.data, app.state.cutoff_date, province)
    output = StringIO()
    pd.DataFrame(summary["omisos"]).to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="omisos_mc03.csv"'},
    )


@app.get("/api/report/incumplidos.csv", tags=["Reporte"])
def api_report_incumplidos_csv(province: str = Query("ABANCAY"), month: str | None = Query(None)):
    if app.state.data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    summary = build_report_summary(app.state.data, app.state.cutoff_date, province)
    output = StringIO()
    pd.DataFrame(_filter_omisos_by_month(summary["omisos"], month)).to_csv(output, index=False)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="incumplidos_mc03.csv"'},
    )


@app.get("/api/report/incumplidos.xlsx", tags=["Reporte"])
def api_report_incumplidos_xlsx(province: str = Query("ABANCAY"), month: str | None = Query(None)):
    if app.state.data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    summary = build_report_summary(app.state.data, app.state.cutoff_date, province)
    content = _incumplidos_xlsx(_filter_omisos_by_month(summary["omisos"], month))
    filename_month = f"_{month}" if month else ""
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="incumplidos_mc03{filename_month}.xlsx"'},
    )


@app.get("/api/search/dni/{dni}", response_model=SearchDNIResult, tags=["Búsqueda"])
def api_search_dni(dni: str, province: str = Query("ABANCAY")):
    if app.state.data is None:
        raise HTTPException(status_code=404, detail="No hay datos cargados en el servidor")

    result = search_by_dni(app.state.data, dni, app.state.cutoff_date, province)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No se encontró registro para DNI: {dni}")

    return SearchDNIResult(**result)
