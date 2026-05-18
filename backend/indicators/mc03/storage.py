"""Persistence adapter for MC-03 processed uploads."""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID as PythonUUID
from uuid import uuid4

import pandas as pd
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

try:
    from ...db.models import (
        ComponentResult,
        DashboardSummary,
        IndicatorActiveUpload,
        IndicatorOmission,
        IndicatorRecord,
        IndicatorUpload,
    )
    from ...db.audit import record_audit_event
except ImportError:
    from db.models import (
        ComponentResult,
        DashboardSummary,
        IndicatorActiveUpload,
        IndicatorOmission,
        IndicatorRecord,
        IndicatorUpload,
    )
    from db.audit import record_audit_event

from .config import (
    ALL_PROVINCES_TOKEN,
    CODE,
    CODIGOS_ESTANDAR,
    DEFAULT_PROVINCE,
    DEFAULT_TARGET_COVERAGE,
    MONTHS_2026,
    VERIFICATION_MONTHS,
)
from .denominator import is_in_denominator
from .processor import build_report_summary, evaluate_package
from .utils import clean_text, coverage_semaphore, parse_month_key, to_date, to_int, to_number


UPLOAD_STATUS_PROCESSING = "processing"
UPLOAD_STATUS_VALIDATED = "validated"
UPLOAD_STATUS_ACTIVE = "active"
UPLOAD_STATUS_FAILED = "failed"
UPLOAD_STATUS_SUPERSEDED = "superseded"
MONTH_NUMBERS = {label: month for month, label in MONTHS_2026}

COMPONENTS = [
    {
        "key": "BCG",
        "package_key": "bcg",
        "label": "Vacuna BCG",
        "group": "vacunas",
        "code": CODIGOS_ESTANDAR["BCG"],
        "date_col": "fec1_BCG",
        "result_col": "resul1_BCG",
        "age_col": "Edad_ate1_BCG",
        "facility_col": "eess_BCG1",
    },
    {
        "key": "HVB",
        "package_key": "hvb",
        "label": "Vacuna HvB",
        "group": "vacunas",
        "code": CODIGOS_ESTANDAR["HVB"],
        "date_col": "fecHVB",
        "result_col": "resulHVB",
        "age_col": "Edad_ateHVB",
        "facility_col": "eess_HVB",
    },
    {
        "key": "cred_1",
        "package_key": "cred_1",
        "label": "CRED 1",
        "group": "cred",
        "code": CODIGOS_ESTANDAR["CRED"],
        "date_col": "Fecha_Atencion_1",
        "result_col": "CIE10_1",
        "age_col": "Edad_Atencion_1",
        "lab_col": "Lab_1",
        "lot_col": "Registro_1",
        "facility_col": "EESS_Atencion_1",
    },
    {
        "key": "cred_2",
        "package_key": "cred_2",
        "label": "CRED 2",
        "group": "cred",
        "code": CODIGOS_ESTANDAR["CRED"],
        "date_col": "Fecha_Atencion_2",
        "result_col": "CIE10_2",
        "age_col": "Edad_Atencion_2",
        "lab_col": "Lab_2",
        "lot_col": "Registro_2",
        "facility_col": "EESS_Atencion2",
    },
    {
        "key": "cred_3",
        "package_key": "cred_3",
        "label": "CRED 3",
        "group": "cred",
        "code": CODIGOS_ESTANDAR["CRED"],
        "date_col": "Fecha_Atencion_3",
        "result_col": "CIE10_3",
        "age_col": "Edad_Atencion_3",
        "lab_col": "Lab_3",
        "lot_col": "Registro_3",
        "facility_col": "EESS_Atencion_3",
    },
    {
        "key": "tamizaje",
        "package_key": "tamizaje",
        "label": "Tamizaje neonatal",
        "group": "tamizaje",
        "code": CODIGOS_ESTANDAR["TAMIZAJE"],
        "date_col": "Fecha_Atencion_TN",
        "result_col": "Codigo_HIS_TN",
        "age_col": "Edad_Atencion_TN",
        "lab_col": "Lab_TN",
        "lot_col": "Registro_TN",
        "facility_col": "EESS_Atencion_TN",
    },
]
COMPONENT_BY_KEY = {component["key"]: component for component in COMPONENTS}
COMPONENT_ORDER = {component["key"]: index for index, component in enumerate(COMPONENTS)}


def missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (dict, list, tuple, set)):
        return False
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def jsonable(value: Any) -> Any:
    if missing(value):
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(item) for item in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            return str(value)
    return value


def row_json(row: pd.Series) -> dict[str, Any]:
    return {str(column): jsonable(row.get(column)) for column in row.index}


def text_value(row: pd.Series, column: str) -> str | None:
    value = clean_text(row.get(column))
    return value or None


def identifier_value(row: pd.Series, column: str) -> str | None:
    value = text_value(row, column)
    return re.sub(r"\.0$", "", value) if value else None


def parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def dataframe_shape(df: pd.DataFrame | None) -> tuple[int, int]:
    if df is None:
        return 0, 0
    return len(df), len(df.columns)


def fail_upload(db: Session, upload_id: PythonUUID, error: Exception) -> None:
    db.rollback()
    upload = db.get(IndicatorUpload, upload_id)
    if upload is None:
        return
    upload.status = UPLOAD_STATUS_FAILED
    upload.error_message = str(error)[:4000]
    upload.processing_summary = {"error": str(error)[:4000]}
    db.commit()


def full_name(row: pd.Series) -> str | None:
    parts = [text_value(row, "afi_nombres"), text_value(row, "afi_appaterno"), text_value(row, "afi_apmaterno")]
    value = " ".join(part for part in parts if part)
    return value or None


def period_values(row: pd.Series) -> tuple[str | None, str | None, int | None, int | None]:
    period_key = text_value(row, "Mes_eva")
    year, month, label = parse_month_key(period_key)
    return period_key, label, year, month


def personal_data(row: pd.Series) -> dict[str, Any]:
    return {
        "dni": identifier_value(row, "afi_DNI"),
        "cnv": identifier_value(row, "NumCNV"),
        "nombres": text_value(row, "afi_nombres"),
        "apellido_paterno": text_value(row, "afi_appaterno"),
        "apellido_materno": text_value(row, "afi_apmaterno"),
        "fecha_nacimiento": jsonable(to_date(row.get("fec_Nac"))),
        "provincia": text_value(row, "Desc_prov"),
        "distrito": text_value(row, "Desc_Dist"),
        "microred": text_value(row, "Des_MicroRed"),
        "renaes": text_value(row, "pre_CodigoRENAES"),
        "establecimiento": text_value(row, "Des_EESS"),
    }


def create_record(upload_id: PythonUUID, row: pd.Series, package: dict[str, Any]) -> IndicatorRecord:
    period_key, period_label, period_year, period_month = period_values(row)
    denominator = bool(period_year and period_month and is_in_denominator(row, period_year, period_month))
    return IndicatorRecord(
        id=uuid4(),
        upload_id=upload_id,
        indicator_code=CODE,
        dni=identifier_value(row, "afi_DNI"),
        cnv=identifier_value(row, "NumCNV"),
        full_name=full_name(row),
        first_names=text_value(row, "afi_nombres"),
        paternal_surname=text_value(row, "afi_appaterno"),
        maternal_surname=text_value(row, "afi_apmaterno"),
        birth_date=to_date(row.get("fec_Nac")),
        province=text_value(row, "Desc_prov"),
        district=text_value(row, "Desc_Dist"),
        microred=text_value(row, "Des_MicroRed"),
        facility_code=text_value(row, "pre_CodigoRENAES"),
        facility=text_value(row, "Des_EESS"),
        period_key=period_key,
        period_label=period_label,
        period_year=period_year,
        period_month=period_month,
        denominator=denominator,
        package_complete=bool(package["complete"]),
        clinical_alerts=[],
        personal_data=personal_data(row),
        raw_selected_data=row_json(row),
    )


def component_detail(row: pd.Series, package: dict[str, Any], component: dict[str, str]) -> dict[str, Any]:
    detail = dict(package["details"].get(component["package_key"], {}))
    detail.update(
        {
            "codigo": component["code"],
            "fecha": jsonable(to_date(row.get(component["date_col"]))),
            "resultado": text_value(row, component["result_col"]),
            "edad_atencion_dias": to_int(row.get(component["age_col"])),
            "establecimiento_atencion": text_value(row, component.get("facility_col", "")),
            "lab": text_value(row, component.get("lab_col", "")),
            "lote": text_value(row, component.get("lot_col", "")),
        }
    )
    return jsonable(detail)


def create_component_results(upload_id: PythonUUID, record_id: PythonUUID, row: pd.Series, package: dict[str, Any]) -> list[ComponentResult]:
    items: list[ComponentResult] = []
    for component in COMPONENTS:
        detail = component_detail(row, package, component)
        items.append(
            ComponentResult(
                id=uuid4(),
                upload_id=upload_id,
                record_id=record_id,
                indicator_code=CODE,
                component_key=component["key"],
                component_label=component["label"],
                component_group=component["group"],
                complies=bool(detail.get("cumple")),
                status=detail.get("estado") or "pendiente",
                message=detail.get("mensaje"),
                result_text=detail.get("resultado"),
                attention_date=to_date(row.get(component["date_col"])),
                attention_age_days=detail.get("edad_atencion_dias"),
                code=detail.get("codigo"),
                lab=detail.get("lab"),
                lot=detail.get("lote"),
                attention_facility=detail.get("establecimiento_atencion"),
                professional=None,
                details=detail,
            )
        )
    return items


def non_compliant_components(package: dict[str, Any]) -> list[dict[str, str]]:
    items = []
    for component in COMPONENTS:
        detail = package["details"].get(component["package_key"], {})
        if not detail.get("cumple"):
            items.append(
                {
                    "key": component["key"],
                    "label": component["label"],
                    "message": detail.get("mensaje") or "No cumple componente.",
                }
            )
    return items


def create_omission(upload_id: PythonUUID, record_id: PythonUUID, row: pd.Series, package: dict[str, Any]) -> IndicatorOmission:
    period_key, period_label, period_year, _ = period_values(row)
    observed = non_compliant_components(package)
    components_observed = "\n".join(item["label"] for item in observed)
    reason = "\n".join(f"{item['label']}: {item['message']}" for item in observed) or "No cumple paquete recien nacido."
    export_data = {
        "Mes_eva": period_key,
        "month": period_label,
        "year": period_year,
        "afi_DNI": identifier_value(row, "afi_DNI"),
        "NumCNV": identifier_value(row, "NumCNV"),
        "fec_Nac": jsonable(to_date(row.get("fec_Nac"))),
        "afi_nombres": text_value(row, "afi_nombres"),
        "afi_appaterno": text_value(row, "afi_appaterno"),
        "afi_apmaterno": text_value(row, "afi_apmaterno"),
        "Desc_prov": text_value(row, "Desc_prov"),
        "Des_MicroRed": text_value(row, "Des_MicroRed"),
        "pre_CodigoRENAES": text_value(row, "pre_CodigoRENAES"),
        "Des_EESS": text_value(row, "Des_EESS"),
        "component": observed[0]["key"] if observed else None,
        "components_observed": components_observed or None,
        "clinical_alerts": [],
        "reason": reason,
    }
    return IndicatorOmission(
        id=uuid4(),
        upload_id=upload_id,
        record_id=record_id,
        indicator_code=CODE,
        province=export_data["Desc_prov"],
        period_key=period_key,
        period_label=period_label,
        dni=export_data["afi_DNI"],
        cnv=export_data["NumCNV"],
        patient_name=full_name(row),
        birth_date=to_date(row.get("fec_Nac")),
        facility=export_data["Des_EESS"],
        components_observed=export_data["components_observed"],
        reason=reason,
        clinical_alerts=[],
        export_data=jsonable(export_data),
    )


def create_dashboard_summaries(
    upload_id: PythonUUID,
    df: pd.DataFrame,
    cutoff_date: date | None,
    provinces: list[str],
) -> list[DashboardSummary]:
    summaries: list[DashboardSummary] = []
    for province in [ALL_PROVINCES_TOKEN, *provinces]:
        report = build_report_summary(df, cutoff_date, province, DEFAULT_TARGET_COVERAGE)
        province_key = "ALL" if province == ALL_PROVINCES_TOKEN else province
        for item in report["monthly"]:
            month_number = MONTH_NUMBERS.get(item["month"])
            period_key = f"{item['year']}_{month_number}" if month_number else f"{item['year']}_{item['month']}"
            summaries.append(
                DashboardSummary(
                    id=uuid4(),
                    upload_id=upload_id,
                    indicator_code=CODE,
                    province=province_key,
                    period_key=period_key,
                    period_label=item["month"],
                    period_year=item["year"],
                    period_month=month_number,
                    denominator=item["denominator"],
                    numerator=item["numerator"],
                    coverage=Decimal(str(item["coverage"])),
                    target_coverage=Decimal(str(report["target_coverage"])),
                    semaphore=item["semaphore"],
                    compliant=item["compliant"],
                    in_verification_period=item["in_verification_period"],
                    summary_data=jsonable(item),
                )
            )
    return summaries


def active_upload_id(db: Session) -> PythonUUID | None:
    active = db.get(IndicatorActiveUpload, CODE)
    return active.upload_id if active else None


def db_province_key(province: str | None) -> str:
    if not province or province == ALL_PROVINCES_TOKEN:
        return "ALL"
    return province.strip().upper()


def detail_from_component_result(component: ComponentResult) -> dict[str, Any]:
    detail = dict(component.details or {})
    detail.setdefault("codigo", component.code or "")
    detail.setdefault("fecha", jsonable(component.attention_date))
    detail.setdefault("resultado", component.result_text)
    detail.setdefault("edad_atencion_dias", component.attention_age_days)
    detail.setdefault("cumple", bool(component.complies))
    detail.setdefault("estado", component.status or "pendiente")
    detail.setdefault("mensaje", component.message)
    detail.setdefault("establecimiento_atencion", component.attention_facility)
    detail.setdefault("profesional", component.professional)
    detail.setdefault("lab", component.lab)
    detail.setdefault("lote", component.lot)
    return jsonable(detail)


def search_result_from_record(record: IndicatorRecord, component_results: list[ComponentResult]) -> dict[str, Any]:
    raw_data = record.raw_selected_data or {}
    ordered_components = sorted(component_results, key=lambda item: COMPONENT_ORDER.get(item.component_key, len(COMPONENT_ORDER)))
    details = {component.component_key: detail_from_component_result(component) for component in ordered_components}

    cred_controls = []
    for number in range(1, 4):
        key = f"cred_{number}"
        detail = details.get(key, {})
        cred_controls.append(
            {
                "numero": number,
                "fecha": detail.get("fecha"),
                "edad_atencion_dias": detail.get("edad_atencion_dias"),
                "cumple": bool(detail.get("cumple")),
                "estado": detail.get("estado", "pendiente"),
                "mensaje": detail.get("mensaje"),
                "fecha_inicio": detail.get("fecha_inicio"),
                "fecha_limite": detail.get("fecha_limite"),
            }
        )

    tamizaje = details.get("tamizaje", {})
    return {
        "personal": {
            "afi_DNI": record.dni,
            "NumCNV": record.cnv,
            "afi_nombres": record.first_names,
            "afi_appaterno": record.paternal_surname,
            "afi_apmaterno": record.maternal_surname,
            "fec_Nac": jsonable(record.birth_date),
            "peso": to_number(raw_data.get("peso")),
            "edadGEst": to_int(raw_data.get("edadGEst")),
            "Desc_prov": record.province,
            "Des_MicroRed": record.microred,
            "pre_CodigoRENAES": record.facility_code,
            "Des_EESS": record.facility,
        },
        "vacunas": {
            "BCG": details.get("BCG", {"codigo": CODIGOS_ESTANDAR["BCG"], "cumple": False}),
            "HVB": details.get("HVB", {"codigo": CODIGOS_ESTANDAR["HVB"], "cumple": False}),
        },
        "clinical_alerts": record.clinical_alerts or [],
        "cred_controls": cred_controls,
        "tamizaje": {
            "fecha": tamizaje.get("fecha"),
            "edad_atencion_dias": tamizaje.get("edad_atencion_dias"),
            "cumple": bool(tamizaje.get("cumple")),
            "estado": tamizaje.get("estado", "pendiente"),
            "mensaje": tamizaje.get("mensaje"),
            "fecha_inicio": tamizaje.get("fecha_inicio"),
            "fecha_limite": tamizaje.get("fecha_limite"),
        },
        "paquete_completo": bool(record.package_complete),
    }


def search_active_by_dni(db: Session, dni: str, province: str | None = DEFAULT_PROVINCE) -> dict[str, Any] | None:
    upload_id = active_upload_id(db)
    if upload_id is None:
        return None

    search_value = re.sub(r"\.0$", "", clean_text(dni))
    if not search_value:
        return None

    statement = select(IndicatorRecord).where(
        IndicatorRecord.upload_id == upload_id,
        or_(IndicatorRecord.dni == search_value, IndicatorRecord.cnv == search_value),
    )
    if province and province != ALL_PROVINCES_TOKEN:
        statement = statement.where(IndicatorRecord.province.ilike(province.strip()))

    record = db.execute(statement.limit(1)).scalars().first()
    if record is None:
        return None

    components = db.execute(select(ComponentResult).where(ComponentResult.record_id == record.id)).scalars().all()
    return search_result_from_record(record, components)


def omission_export(omission: IndicatorOmission) -> dict[str, Any]:
    item = dict(omission.export_data or {})
    item.setdefault("Mes_eva", omission.period_key)
    item.setdefault("month", omission.period_label)
    item.setdefault("afi_DNI", omission.dni)
    item.setdefault("NumCNV", omission.cnv)
    item.setdefault("fec_Nac", jsonable(omission.birth_date))
    item.setdefault("Desc_prov", omission.province)
    item.setdefault("Des_EESS", omission.facility)
    item.setdefault("components_observed", omission.components_observed)
    item.setdefault("clinical_alerts", omission.clinical_alerts or [])
    item.setdefault("reason", omission.reason)
    if not isinstance(item.get("clinical_alerts"), list):
        item["clinical_alerts"] = []
    if not clean_text(item.get("reason")):
        item["reason"] = omission.reason or "No cumple paquete recien nacido."
    return jsonable(item)


def sort_omissions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(item: dict[str, Any]) -> tuple[int, int, str]:
        year, month, _ = parse_month_key(item.get("Mes_eva"))
        name = " ".join(
            clean_text(item.get(part))
            for part in ["afi_appaterno", "afi_apmaterno", "afi_nombres", "afi_DNI"]
            if clean_text(item.get(part))
        )
        return year or 0, month or 0, name

    return sorted(items, key=key)


def report_summary_from_rows(
    upload: IndicatorUpload,
    dashboard_rows: list[DashboardSummary],
    omissions: list[IndicatorOmission],
    target_coverage: float | None = None,
) -> dict[str, Any]:
    target = DEFAULT_TARGET_COVERAGE if target_coverage is None else max(0.0, min(100.0, float(target_coverage)))
    ordered_rows = sorted(dashboard_rows, key=lambda item: (item.period_year or 0, item.period_month or 0))
    monthly = []
    for row in ordered_rows:
        coverage = float(row.coverage or 0)
        monthly.append(
            {
                "month": row.period_label,
                "year": row.period_year,
                "in_verification_period": row.in_verification_period,
                "compliant": row.denominator > 0 and coverage >= target,
                "semaphore": coverage_semaphore(coverage, target),
                "coverage": coverage,
                "denominator": row.denominator,
                "numerator": row.numerator,
            }
        )

    verification_monthly = [item for item in monthly if item["in_verification_period"]]
    months_met = sum(1 for item in verification_monthly if item["compliant"])
    return {
        "period_start": date(2026, 6, 1),
        "period_end": date(2026, 11, 30),
        "cut_off_date": upload.cutoff_date,
        "target_coverage": target,
        "months_evaluated": len(verification_monthly),
        "months_met": months_met,
        "committed": months_met >= 5,
        "monthly": monthly,
        "omisos": sort_omissions([omission_export(item) for item in omissions]),
    }


def build_active_report_summary(
    db: Session,
    province: str | None = DEFAULT_PROVINCE,
    target_coverage: float | None = None,
) -> dict[str, Any] | None:
    upload_id = active_upload_id(db)
    if upload_id is None:
        return None

    upload = db.get(IndicatorUpload, upload_id)
    if upload is None:
        return None

    province_key = db_province_key(province)
    dashboard_rows = (
        db.execute(
            select(DashboardSummary).where(
                DashboardSummary.upload_id == upload_id,
                DashboardSummary.province == province_key,
            )
        )
        .scalars()
        .all()
    )
    omissions_statement = select(IndicatorOmission).where(IndicatorOmission.upload_id == upload_id)
    if province_key != "ALL":
        omissions_statement = omissions_statement.where(IndicatorOmission.province.ilike(province_key))
    omissions = db.execute(omissions_statement).scalars().all()
    return report_summary_from_rows(upload, dashboard_rows, omissions, target_coverage)


def persist_active_upload(
    db: Session,
    df: pd.DataFrame,
    cutoff_date: date | None,
    source_path: Path,
    metadata: dict[str, Any] | None = None,
    validation_summary: dict[str, Any] | None = None,
) -> PythonUUID:
    metadata = metadata or {}
    validation_summary = validation_summary or {}
    upload_id = uuid4()
    activated_at = parse_datetime(metadata.get("activated_at")) or datetime.now()
    uploaded_by = metadata.get("uploaded_by")
    activated_by = metadata.get("activated_by") or uploaded_by
    actor_role = metadata.get("actor_role")
    row_count, column_count = dataframe_shape(df)

    upload = IndicatorUpload(
        id=upload_id,
        indicator_code=CODE,
        status=UPLOAD_STATUS_PROCESSING,
        original_filename=metadata.get("original_name"),
        stored_file_path=str(source_path),
        file_hash=metadata.get("file_hash"),
        cutoff_date=cutoff_date,
        uploaded_by=uploaded_by,
        activated_at=activated_at,
        rows_total=int(validation_summary.get("total_rows") or row_count),
        columns_total=int(validation_summary.get("total_columns") or column_count),
        loaded_columns=int(validation_summary.get("loaded_columns") or column_count),
        storage_format=validation_summary.get("storage_format"),
        source_preserved=bool(validation_summary.get("source_preserved", True)),
        validation_summary=jsonable(validation_summary),
    )
    db.add(upload)
    db.commit()
    record_audit_event(
        db,
        CODE,
        "upload_processing_started",
        actor=activated_by,
        actor_role=actor_role,
        upload_id=upload_id,
        message="Procesamiento de carga MC-03 iniciado.",
        details={"filename": metadata.get("original_name"), "file_hash": metadata.get("file_hash")},
    )
    db.commit()

    try:
        provinces = [
            value
            for value in sorted(df.get("Desc_prov", pd.Series(dtype=object)).dropna().astype(str).str.strip().unique().tolist())
            if value
        ]
        records: list[IndicatorRecord] = []
        components: list[ComponentResult] = []
        omissions: list[IndicatorOmission] = []

        for _, row in df.iterrows():
            package = evaluate_package(row, cutoff_date)
            record = create_record(upload_id, row, package)
            records.append(record)
            components.extend(create_component_results(upload_id, record.id, row, package))
            if record.denominator and not package["complete"]:
                omissions.append(create_omission(upload_id, record.id, row, package))

        dashboard_summaries = create_dashboard_summaries(upload_id, df, cutoff_date, provinces)
        upload = db.get(IndicatorUpload, upload_id)
        upload.processing_summary = {
            "records": len(records),
            "component_results": len(components),
            "omissions": len(omissions),
            "dashboard_summaries": len(dashboard_summaries),
            "default_province": DEFAULT_PROVINCE,
        }
        upload.status = UPLOAD_STATUS_VALIDATED
        db.flush()

        active = db.get(IndicatorActiveUpload, CODE)
        if active:
            previous_upload = db.get(IndicatorUpload, active.upload_id)
            if previous_upload and previous_upload.id != upload_id:
                previous_upload.status = UPLOAD_STATUS_SUPERSEDED
            active.upload_id = upload_id
            active.activated_at = activated_at
            active.activated_by = activated_by
        else:
            active = IndicatorActiveUpload(indicator_code=CODE, upload_id=upload_id, activated_at=activated_at, activated_by=activated_by)

        upload.status = UPLOAD_STATUS_ACTIVE
        db.add(active)
        db.add_all(records)
        db.add_all(components)
        db.add_all(omissions)
        db.add_all(dashboard_summaries)
        record_audit_event(
            db,
            CODE,
            "upload_activated",
            actor=activated_by,
            actor_role=actor_role,
            upload_id=upload_id,
            message="Carga MC-03 activada correctamente.",
            details=upload.processing_summary,
        )
        db.commit()
    except Exception as exc:
        fail_upload(db, upload_id, exc)
        record_audit_event(
            db,
            CODE,
            "upload_failed",
            actor=activated_by,
            actor_role=actor_role,
            upload_id=upload_id,
            message="La carga MC-03 fallo durante el procesamiento.",
            details={"error": str(exc)[:4000]},
        )
        db.commit()
        raise

    return upload_id
