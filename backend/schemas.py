from datetime import date, datetime
from typing import Any, List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    source_file: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthUserResponse(BaseModel):
    username: str
    display_name: str
    role: str
    role_label: str
    permissions: List[str] = []
    auth_enabled: bool = False


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


class MonthlyCompliance(BaseModel):
    month: str
    year: int
    month_key: str | None = None
    compliant: bool
    semaphore: str = "red"
    coverage: float
    denominator: int
    numerator: int
    in_verification_period: bool = True


class OmisoItem(BaseModel):
    Mes_eva: str | None = None
    month: str | None = None
    year: int | None = None
    subindicator_code: str | None = None
    subindicator_name: str | None = None
    afi_DNI: str | None = None
    NumCNV: str | None = None
    fec_Nac: str | None = None
    afi_nombres: str | None = None
    afi_appaterno: str | None = None
    afi_apmaterno: str | None = None
    Desc_prov: str | None = None
    Des_MicroRed: str | None = None
    pre_CodigoRENAES: str | None = None
    Des_EESS: str | None = None
    component: str | None = None
    components_observed: str | None = None
    attention_date: str | None = None
    attention_age_days: int | None = None
    attention_facility: str | None = None
    attention_professional: str | None = None
    clinical_alerts: List[str] = []
    reason: str


class ReportSummary(BaseModel):
    period_start: date
    period_end: date
    cut_off_date: date | None = None
    target_coverage: float
    months_evaluated: int
    months_met: int
    committed: bool
    monthly: List[MonthlyCompliance]
    omisos: List[OmisoItem]
    subindicators: dict[str, Any] = {}
    commitment_summary: dict[str, Any] = {}


class OmisosResponse(BaseModel):
    omisos: List[OmisoItem]


class FilterOptionsResponse(BaseModel):
    provinces: List[str]
    default_province: str = "ABANCAY"
    default_target_coverage: float = 70.7
    included_insurance_types: List[str] = []
    exclusion_criteria: dict[str, Any] = {}


class DataFileSummary(BaseModel):
    indicator_code: str | None = None
    indicator_name: str | None = None
    filename: str | None = None
    original_name: str | None = None
    file_size_bytes: int | None = None
    file_hash: str | None = None
    uploaded_at: str | None = None
    uploaded_by: str | None = None
    activated_at: str | None = None
    activated_by: str | None = None
    sheet_name: str | None = None
    cutoff_cell: str | None = None
    header_row: int | None = None
    cutoff_date: date | None = None
    total_rows: int | None = None
    total_columns: int | None = None
    loaded_columns: int | None = None
    required_columns_count: int | None = None
    missing_columns: List[str] = []
    omitted_columns: List[str] = []
    provinces: List[str] = []
    months: List[str] = []
    validation_label: str | None = None
    status_counts: dict[str, int] = {}
    denominator_counts: dict[str, int] = {}
    component_counts: dict[str, dict[str, int]] = {}
    obs_eval_counts: dict[str, int] = {}
    insurance_counts: dict[str, int] = {}
    storage_format: str | None = None
    source_preserved: bool | None = None
    files_received: int | None = None
    expected_files: int | None = None
    subindicators_found: List[str] = []
    missing_subindicators: List[str] = []
    duplicate_subindicators: List[str] = []
    unknown_files: List[str] = []
    subindicators: dict[str, Any] = {}
    cutoff_dates: dict[str, Any] = {}
    cutoff_date_mismatch: bool = False
    package_files: List[dict[str, Any]] = []
    total_loaded_columns: int | None = None


class DataUploadPreviewResponse(BaseModel):
    upload_id: str
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    summary: DataFileSummary


class DataActivateRequest(BaseModel):
    upload_id: str


class DataCurrentResponse(BaseModel):
    has_data: bool
    active_file: str | None = None
    summary: DataFileSummary | None = None
    processing: bool = False
    job_id: str | None = None
    job_status: str | None = None
    message: str | None = None
    error: str | None = None


class UploadHistoryItem(BaseModel):
    id: str
    indicator_code: str
    status: str
    is_active: bool = False
    original_filename: str | None = None
    stored_file_path: str | None = None
    file_hash: str | None = None
    cutoff_date: date | None = None
    uploaded_by: str | None = None
    activated_at: datetime | None = None
    activated_by: str | None = None
    rows_total: int = 0
    columns_total: int = 0
    loaded_columns: int = 0
    storage_format: str | None = None
    source_preserved: bool = True
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    processing_summary: dict[str, Any] = {}
    validation_summary: dict[str, Any] = {}


class UploadHistoryResponse(BaseModel):
    uploads: List[UploadHistoryItem]


class AuditEventItem(BaseModel):
    id: str
    indicator_code: str
    upload_id: str | None = None
    event_type: str
    actor: str | None = None
    actor_role: str | None = None
    message: str | None = None
    details: dict[str, Any] = {}
    created_at: datetime | None = None


class AuditEventsResponse(BaseModel):
    events: List[AuditEventItem]


class PersonalData(BaseModel):
    afi_DNI: str | None = None
    NumCNV: str | None = None
    afi_nombres: str | None = None
    afi_appaterno: str | None = None
    afi_apmaterno: str | None = None
    fec_Nac: str | None = None
    peso: float | None = None
    edadGEst: int | None = None
    Desc_prov: str | None = None
    Des_MicroRed: str | None = None
    pre_CodigoRENAES: str | None = None
    Des_EESS: str | None = None


class VacunaRecord(BaseModel):
    codigo: str
    fecha: str | None = None
    resultado: str | None = None
    edad_atencion_dias: int | None = None
    cumple: bool = False
    estado: str = "pendiente"
    mensaje: str | None = None
    establecimiento_atencion: str | None = None
    profesional: str | None = None
    lab: str | None = None
    lote: str | None = None
    ventana_normativa: str | None = None
    fecha_inicio: date | None = None
    fecha_limite: date | None = None
    dosis: List[dict[str, Any]] = []
    dosis_registradas: int = 0
    dosis_evaluadas: int = 0
    entregas: List[dict[str, Any]] = []
    tipo_atencion: str | None = None


class CREDRecord(BaseModel):
    numero: int
    fecha: str | None = None
    edad_atencion_dias: int | None = None
    cumple: bool = False
    estado: str = "pendiente"
    mensaje: str | None = None
    fecha_inicio: date | None = None
    fecha_limite: date | None = None


class TamizajeRecord(BaseModel):
    fecha: str | None = None
    edad_atencion_dias: int | None = None
    cumple: bool = False
    estado: str = "pendiente"
    mensaje: str | None = None
    fecha_inicio: date | None = None
    fecha_limite: date | None = None


class SearchDNIResult(BaseModel):
    personal: PersonalData
    vacunas: dict[str, VacunaRecord]
    clinical_alerts: List[str] = []
    cred_controls: List[CREDRecord]
    tamizaje: TamizajeRecord
    paquete_completo: bool
    subindicators: List[dict[str, Any]] = []
