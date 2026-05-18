"""Persistence adapter for SI-02 multi-file processed uploads."""

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
    from ...db.audit import record_audit_event
    from ...db.models import (
        ComponentResult,
        DashboardSummary,
        IndicatorActiveUpload,
        IndicatorOmission,
        IndicatorRecord,
        IndicatorUpload,
    )
except ImportError:
    from db.audit import record_audit_event
    from db.models import (
        ComponentResult,
        DashboardSummary,
        IndicatorActiveUpload,
        IndicatorOmission,
        IndicatorRecord,
        IndicatorUpload,
    )

from .config import CODE, DEFAULT_PROVINCE, DEFAULT_TARGET_COVERAGE, EXPECTED_PACKAGE_CODES, SUBINDICATORS
from .commitment import build_commitment_summary, current_commitment_met
from .evaluator import component_rules, evaluate_dataframe, evaluate_row
from .processor import ALL_PROVINCES_TOKEN, filter_data, omiso_from_row
from .utils import clean_value, parse_month_key, to_date, to_int, to_number


UPLOAD_STATUS_PROCESSING = "processing"
UPLOAD_STATUS_VALIDATED = "validated"
UPLOAD_STATUS_ACTIVE = "active"
UPLOAD_STATUS_FAILED = "failed"
UPLOAD_STATUS_SUPERSEDED = "superseded"


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


def row_json(row: pd.Series, subindicator_code: str) -> dict[str, Any]:
    data = {str(column): jsonable(row.get(column)) for column in row.index}
    data["subindicator_code"] = subindicator_code
    data["subindicator_name"] = SUBINDICATORS[subindicator_code].title
    return data


def text_value(row: pd.Series, column: str) -> str | None:
    value = clean_value(row.get(column))
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


def primary_cutoff_date(value: Any) -> date | None:
    if isinstance(value, dict):
        dates = [item for item in value.values() if isinstance(item, date)]
        return max(dates) if dates else None
    return value if isinstance(value, date) else None


def package_shape(package_data: dict[str, pd.DataFrame] | pd.DataFrame | None) -> tuple[int, int]:
    if package_data is None:
        return 0, 0
    if isinstance(package_data, pd.DataFrame):
        return len(package_data), len(package_data.columns)
    return (
        sum(len(df) for df in package_data.values() if df is not None),
        sum(len(df.columns) for df in package_data.values() if df is not None),
    )


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
    parts = [text_value(row, "NOMBRE"), text_value(row, "APELLPAT"), text_value(row, "APEMAT")]
    value = " ".join(part for part in parts if part)
    return value or None


def period_values(row: pd.Series, subindicator_code: str) -> tuple[str | None, str | None, int | None, int | None]:
    spec = SUBINDICATORS[subindicator_code]
    period_key = text_value(row, spec.month_column)
    parsed = parse_month_key(period_key)
    if parsed:
        year, month, label = parsed
        return period_key, label, year, month
    return period_key, None, None, None


def personal_data(row: pd.Series, subindicator_code: str) -> dict[str, Any]:
    spec = SUBINDICATORS[subindicator_code]
    return {
        "dni": identifier_value(row, "afi_dni"),
        "cnv": identifier_value(row, "NUMCNV"),
        "nombres": text_value(row, "NOMBRE"),
        "apellido_paterno": text_value(row, "APELLPAT"),
        "apellido_materno": text_value(row, "APEMAT"),
        "fecha_nacimiento": jsonable(to_date(row.get("FEC_NAC"))),
        "provincia": text_value(row, spec.province_column),
        "distrito": text_value(row, "distrito"),
        "microred": text_value(row, "des_micro"),
        "renaes": text_value(row, "Renaes_ate"),
        "establecimiento": text_value(row, "EESS"),
        "subindicator_code": subindicator_code,
        "subindicator_name": spec.title,
    }


def create_record(upload_id: PythonUUID, row: pd.Series, subindicator_code: str, package: dict[str, Any]) -> IndicatorRecord:
    spec = SUBINDICATORS[subindicator_code]
    period_key, period_label, period_year, period_month = period_values(row, subindicator_code)
    return IndicatorRecord(
        id=uuid4(),
        upload_id=upload_id,
        indicator_code=CODE,
        dni=identifier_value(row, "afi_dni"),
        cnv=identifier_value(row, "NUMCNV"),
        full_name=full_name(row),
        first_names=text_value(row, "NOMBRE"),
        paternal_surname=text_value(row, "APELLPAT"),
        maternal_surname=text_value(row, "APEMAT"),
        birth_date=to_date(row.get("FEC_NAC")),
        province=text_value(row, spec.province_column),
        district=text_value(row, "distrito"),
        microred=text_value(row, "des_micro"),
        facility_code=text_value(row, "Renaes_ate"),
        facility=text_value(row, "EESS"),
        period_key=period_key,
        period_label=period_label,
        period_year=period_year,
        period_month=period_month,
        denominator=True,
        package_complete=bool(package["complete"]),
        clinical_alerts=[],
        personal_data=personal_data(row, subindicator_code),
        raw_selected_data=row_json(row, subindicator_code),
    )


def component_group(component_key: str) -> str:
    if "hierro" in component_key:
        return "hierro"
    if "dosaje" in component_key or component_key.startswith("dh_"):
        return "dosaje"
    if "anemia" in component_key:
        return "anemia"
    if component_key == "ta":
        return "termino_tratamiento"
    return "otros"


def attention_date_from_detail(detail: dict[str, Any]) -> date | None:
    if detail.get("fecha"):
        return to_date(detail.get("fecha"))
    deliveries = detail.get("entregas") or []
    if deliveries:
        return to_date(deliveries[0].get("date"))
    return None


def code_from_detail(detail: dict[str, Any]) -> str | None:
    if detail.get("codigo"):
        return clean_value(detail.get("codigo"))
    deliveries = detail.get("entregas") or []
    if deliveries:
        return clean_value(deliveries[0].get("code")) or None
    return None


def lab_from_detail(detail: dict[str, Any]) -> str | None:
    if detail.get("lab"):
        return clean_value(detail.get("lab"))
    deliveries = detail.get("entregas") or []
    if deliveries:
        return clean_value(deliveries[0].get("lab")) or None
    return None


def interval_from_detail(detail: dict[str, Any]) -> int | None:
    if detail.get("intervalo_dias") is not None:
        return to_int(detail.get("intervalo_dias"))
    deliveries = detail.get("entregas") or []
    if deliveries:
        return to_int(deliveries[0].get("interval"))
    return None


def create_component_results(
    upload_id: PythonUUID,
    record_id: PythonUUID,
    subindicator_code: str,
    package: dict[str, Any],
) -> list[ComponentResult]:
    rules = {rule.key: rule for rule in component_rules(subindicator_code)}
    items: list[ComponentResult] = []
    for component_key, detail in package["details"].items():
        rule = rules.get(component_key)
        storage_key = f"{subindicator_code}.{component_key}"
        detail_payload = dict(detail)
        detail_payload["component_key"] = component_key
        detail_payload["storage_component_key"] = storage_key
        detail_payload["subindicator_code"] = subindicator_code
        detail_payload["subindicator_name"] = SUBINDICATORS[subindicator_code].title
        detail_payload["observed_only"] = bool(rule.observed_only) if rule else False
        items.append(
            ComponentResult(
                id=uuid4(),
                upload_id=upload_id,
                record_id=record_id,
                indicator_code=CODE,
                component_key=storage_key,
                component_label=detail.get("label") or (rule.label if rule else component_key),
                component_group=component_group(component_key),
                complies=bool(detail.get("cumple")),
                status=detail.get("estado") or "pendiente",
                message=detail.get("mensaje"),
                result_text=detail.get("resultado"),
                attention_date=attention_date_from_detail(detail),
                attention_age_days=interval_from_detail(detail),
                code=code_from_detail(detail),
                lab=lab_from_detail(detail),
                lot=None,
                attention_facility=None,
                professional=None,
                details=jsonable(detail_payload),
            )
        )
    return items


def create_omission(
    upload_id: PythonUUID,
    record_id: PythonUUID,
    row: pd.Series,
    subindicator_code: str,
    evaluation: pd.Series,
) -> IndicatorOmission:
    omiso = omiso_from_row(row, subindicator_code, evaluation)
    patient_name = " ".join(
        part for part in [omiso.get("afi_nombres"), omiso.get("afi_appaterno"), omiso.get("afi_apmaterno")] if part
    )
    reason = omiso.get("reason") or "No cumple SI-02."
    omiso["subindicator_name"] = SUBINDICATORS[subindicator_code].title
    return IndicatorOmission(
        id=uuid4(),
        upload_id=upload_id,
        record_id=record_id,
        indicator_code=CODE,
        province=omiso.get("Desc_prov"),
        period_key=omiso.get("Mes_eva"),
        period_label=omiso.get("month"),
        dni=omiso.get("afi_DNI"),
        cnv=omiso.get("NumCNV"),
        patient_name=patient_name or None,
        birth_date=to_date(row.get("FEC_NAC")),
        facility=omiso.get("Des_EESS"),
        components_observed=omiso.get("components_observed"),
        reason=reason,
        clinical_alerts=[],
        export_data=jsonable(omiso),
    )


def province_values(package_data: dict[str, pd.DataFrame]) -> list[str]:
    values: set[str] = set()
    for code, df in package_data.items():
        column = SUBINDICATORS[code].province_column
        if column not in df:
            continue
        values.update(value for value in df[column].dropna().astype(str).str.strip().tolist() if value)
    return sorted(values)


def create_dashboard_summaries(
    upload_id: PythonUUID,
    package_data: dict[str, pd.DataFrame],
    evaluation_cache: dict[str, pd.DataFrame],
    provinces: list[str],
) -> list[DashboardSummary]:
    summaries: list[DashboardSummary] = []
    for province in [ALL_PROVINCES_TOKEN, *provinces]:
        province_key = "ALL" if province == ALL_PROVINCES_TOKEN else province
        for code in EXPECTED_PACKAGE_CODES:
            df = package_data.get(code)
            if df is None:
                continue
            spec = SUBINDICATORS[code]
            filtered = filter_data(df, code, province)
            evaluated = evaluation_cache[code]
            target = spec.target_coverage
            month_values = []
            for value in filtered.get(spec.month_column, pd.Series(dtype=object)).dropna().unique().tolist():
                parsed = parse_month_key(value)
                if parsed:
                    month_values.append(parsed)

            for year, month, month_name in sorted(set(month_values), key=lambda item: (item[0], item[1])):
                month_key = f"{year}_{month}"
                month_df = filtered[filtered[spec.month_column].astype(str).str.strip() == month_key]
                month_eval = evaluated.loc[month_df.index] if not evaluated.empty else pd.DataFrame()
                denominator = len(month_df)
                numerator = int(month_eval["cumple"].sum()) if not month_eval.empty else 0
                coverage = round((numerator / denominator) * 100, 2) if denominator else 0.0
                compliant = denominator > 0 and coverage >= target
                summary_item = {
                    "subindicator_code": code,
                    "subindicator_name": spec.title,
                    "month": month_name,
                    "year": year,
                    "month_key": month_key,
                    "coverage": coverage,
                    "denominator": denominator,
                    "numerator": numerator,
                    "target_coverage": target,
                    "compliant": compliant,
                    "semaphore": "green" if compliant else "red",
                    "in_verification_period": True,
                }
                summaries.append(
                    DashboardSummary(
                        id=uuid4(),
                        upload_id=upload_id,
                        indicator_code=CODE,
                        province=province_key,
                        period_key=f"{code}:{month_key}",
                        period_label=month_name,
                        period_year=year,
                        period_month=month,
                        denominator=denominator,
                        numerator=numerator,
                        coverage=Decimal(str(coverage)),
                        target_coverage=Decimal(str(target)),
                        semaphore=summary_item["semaphore"],
                        compliant=compliant,
                        in_verification_period=True,
                        summary_data=jsonable(summary_item),
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
    if detail.get("codigo") is None:
        detail["codigo"] = ""
    detail.setdefault("fecha", jsonable(component.attention_date))
    detail.setdefault("edad_atencion_dias", component.attention_age_days)
    detail.setdefault("cumple", bool(component.complies))
    detail.setdefault("estado", component.status or "pendiente")
    detail.setdefault("mensaje", component.message)
    detail.setdefault("lab", component.lab)
    detail.setdefault("entregas", [])
    detail.setdefault("dosis", [])
    return jsonable(detail)


def search_result_from_records(records: list[IndicatorRecord], component_results: list[ComponentResult]) -> dict[str, Any]:
    components_by_record: dict[PythonUUID, list[ComponentResult]] = {}
    for component in component_results:
        components_by_record.setdefault(component.record_id, []).append(component)

    first_record = records[0]
    subindicators = []
    flat_components = {}
    for record in records:
        raw_data = record.raw_selected_data or {}
        subindicator_code = raw_data.get("subindicator_code")
        components = sorted(components_by_record.get(record.id, []), key=lambda item: item.component_key)
        details = {component.details.get("component_key", component.component_key): detail_from_component_result(component) for component in components}
        for component in components:
            flat_components[component.component_key] = detail_from_component_result(component)
        subindicators.append(
            {
                "subindicator_code": subindicator_code,
                "subindicator_name": raw_data.get("subindicator_name"),
                "complete": bool(record.package_complete),
                "details": details,
                "reasons": [component.message for component in components if not component.complies and not (component.details or {}).get("observed_only")],
            }
        )

    personal = first_record.personal_data or {}
    return {
        "personal": {
            "afi_DNI": first_record.dni,
            "NumCNV": first_record.cnv,
            "afi_nombres": first_record.first_names,
            "afi_appaterno": first_record.paternal_surname,
            "afi_apmaterno": first_record.maternal_surname,
            "fec_Nac": jsonable(first_record.birth_date),
            "peso": to_number((first_record.raw_selected_data or {}).get("Peso")),
            "edadGEst": to_int((first_record.raw_selected_data or {}).get("SEMANAGESTACION")),
            "Desc_prov": first_record.province or personal.get("provincia"),
            "Des_MicroRed": first_record.microred,
            "pre_CodigoRENAES": first_record.facility_code,
            "Des_EESS": first_record.facility,
        },
        "vacunas": flat_components,
        "clinical_alerts": [],
        "cred_controls": [],
        "tamizaje": {},
        "paquete_completo": all(record.package_complete for record in records),
        "subindicators": subindicators,
    }


def search_active_by_dni(db: Session, dni: str, province: str | None = DEFAULT_PROVINCE) -> dict[str, Any] | None:
    upload_id = active_upload_id(db)
    if upload_id is None:
        return None

    search_value = re.sub(r"\.0$", "", clean_value(dni))
    if not search_value:
        return None

    statement = select(IndicatorRecord).where(
        IndicatorRecord.upload_id == upload_id,
        or_(IndicatorRecord.dni == search_value, IndicatorRecord.cnv == search_value),
    )
    if province and province != ALL_PROVINCES_TOKEN:
        statement = statement.where(IndicatorRecord.province.ilike(province.strip()))

    records = db.execute(statement).scalars().all()
    if not records:
        return None

    record_ids = [record.id for record in records]
    components = db.execute(select(ComponentResult).where(ComponentResult.record_id.in_(record_ids))).scalars().all()
    return search_result_from_records(records, components)


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
    item.setdefault("reason", omission.reason)
    item.setdefault("clinical_alerts", [])
    return jsonable(item)


def sort_omissions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def key(item: dict[str, Any]) -> tuple[str, int, int, str]:
        parsed = parse_month_key(item.get("Mes_eva"))
        year, month = (parsed[0], parsed[1]) if parsed else (0, 0)
        name = " ".join(
            clean_value(item.get(part))
            for part in ["afi_appaterno", "afi_apmaterno", "afi_nombres", "afi_DNI"]
            if clean_value(item.get(part))
        )
        return clean_value(item.get("subindicator_code")), year, month, name

    return sorted(items, key=key)


def report_summary_from_rows(
    upload: IndicatorUpload,
    dashboard_rows: list[DashboardSummary],
    omissions: list[IndicatorOmission],
    target_coverage: float | None = None,
) -> dict[str, Any]:
    subindicators: dict[str, dict[str, Any]] = {}
    aggregate_by_period: dict[tuple[int, int, str], dict[str, Any]] = {}

    for row in sorted(dashboard_rows, key=lambda item: ((item.summary_data or {}).get("subindicator_code", ""), item.period_year or 0, item.period_month or 0)):
        item = dict(row.summary_data or {})
        code = item.get("subindicator_code")
        if not code:
            continue
        target = float(item.get("target_coverage") or target_coverage or DEFAULT_TARGET_COVERAGE)
        monthly_item = {
            "month": row.period_label,
            "year": row.period_year,
            "month_key": f"{row.period_year}_{row.period_month}",
            "in_verification_period": row.in_verification_period,
            "compliant": row.denominator > 0 and float(row.coverage or 0) >= target,
            "semaphore": "green" if row.denominator > 0 and float(row.coverage or 0) >= target else "red",
            "coverage": float(row.coverage or 0),
            "denominator": row.denominator,
            "numerator": row.numerator,
            "target_coverage": target,
            "subindicator_code": code,
            "subindicator_name": item.get("subindicator_name"),
        }
        summary = subindicators.setdefault(
            code,
            {
                "subindicator_code": code,
                "subindicator_name": item.get("subindicator_name"),
                "target_coverage": target,
                "months_evaluated": 0,
                "months_met": 0,
                "monthly": [],
                "omisos": [],
            },
        )
        summary["monthly"].append(monthly_item)
        summary["months_evaluated"] += 1
        if monthly_item["compliant"]:
            summary["months_met"] += 1

        key = (row.period_year or 0, row.period_month or 0, row.period_label or "")
        aggregate = aggregate_by_period.setdefault(key, {"denominator": 0, "numerator": 0})
        aggregate["denominator"] += row.denominator
        aggregate["numerator"] += row.numerator

    omissions_export = sort_omissions([omission_export(item) for item in omissions])
    for item in omissions_export:
        code = item.get("subindicator_code")
        if code in subindicators:
            subindicators[code]["omisos"].append(item)

    top_target = DEFAULT_TARGET_COVERAGE if target_coverage is None else float(target_coverage)
    monthly = []
    for (year, month, label), values in sorted(aggregate_by_period.items()):
        denominator = values["denominator"]
        numerator = values["numerator"]
        coverage = round((numerator / denominator) * 100, 2) if denominator else 0.0
        compliant = denominator > 0 and coverage >= top_target
        monthly.append(
            {
                "month": label,
                "year": year,
                "month_key": f"{year}_{month}",
                "in_verification_period": True,
                "compliant": compliant,
                "semaphore": "green" if compliant else "red",
                "coverage": coverage,
                "denominator": denominator,
                "numerator": numerator,
            }
        )

    period_pairs = [(year, month) for year, month, _ in aggregate_by_period.keys() if year and month]
    first_month = min(period_pairs, default=None)
    last_month = max(period_pairs, default=None)
    period_start = date(first_month[0], first_month[1], 1) if first_month else date(2026, 1, 1)
    period_end = date(last_month[0], last_month[1], 28) if last_month else date(2026, 12, 31)

    commitment_summary = build_commitment_summary(subindicators, upload.cutoff_date)

    return {
        "period_start": period_start,
        "period_end": period_end,
        "cut_off_date": upload.cutoff_date,
        "target_coverage": top_target,
        "months_evaluated": len(monthly),
        "months_met": sum(1 for item in monthly if item["compliant"]),
        "committed": current_commitment_met(subindicators, upload.cutoff_date),
        "monthly": monthly,
        "omisos": omissions_export,
        "subindicators": subindicators,
        "commitment_summary": commitment_summary,
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
    package_data: dict[str, pd.DataFrame],
    cutoff_dates: dict[str, date] | date | None,
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
    row_count, column_count = package_shape(package_data)
    cutoff_date = primary_cutoff_date(cutoff_dates)

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
        loaded_columns=int(validation_summary.get("total_loaded_columns") or validation_summary.get("loaded_columns") or column_count),
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
        message="Procesamiento de paquete SI-02 iniciado.",
        details={"filename": metadata.get("original_name"), "file_hash": metadata.get("file_hash")},
    )
    db.commit()

    try:
        missing_codes = [code for code in EXPECTED_PACKAGE_CODES if code not in package_data]
        if missing_codes:
            raise ValueError("Faltan subindicadores SI-02 en el paquete: " + ", ".join(missing_codes))

        evaluations = {code: evaluate_dataframe(package_data[code], code) for code in EXPECTED_PACKAGE_CODES}
        provinces = province_values(package_data)
        records: list[IndicatorRecord] = []
        components: list[ComponentResult] = []
        omissions: list[IndicatorOmission] = []

        for code in EXPECTED_PACKAGE_CODES:
            df = package_data[code]
            evaluated = evaluations[code]
            for index, row in df.iterrows():
                package = evaluate_row(row, code)
                record = create_record(upload_id, row, code, package)
                records.append(record)
                components.extend(create_component_results(upload_id, record.id, code, package))
                if not package["complete"]:
                    omissions.append(create_omission(upload_id, record.id, row, code, evaluated.loc[index]))

        dashboard_summaries = create_dashboard_summaries(upload_id, package_data, evaluations, provinces)
        upload = db.get(IndicatorUpload, upload_id)
        upload.processing_summary = {
            "records": len(records),
            "component_results": len(components),
            "omissions": len(omissions),
            "dashboard_summaries": len(dashboard_summaries),
            "subindicators": {code: int(len(package_data[code])) for code in EXPECTED_PACKAGE_CODES},
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
            message="Paquete SI-02 activado correctamente.",
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
            message="El paquete SI-02 fallo durante el procesamiento.",
            details={"error": str(exc)[:4000]},
        )
        db.commit()
        raise

    return upload_id
