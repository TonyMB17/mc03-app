from datetime import date
from typing import Any, List

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    source_file: str


class MonthlyCompliance(BaseModel):
    month: str
    year: int
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


class OmisosResponse(BaseModel):
    omisos: List[OmisoItem]


class FilterOptionsResponse(BaseModel):
    provinces: List[str]
    default_province: str = "ABANCAY"
    default_target_coverage: float = 70.7
    included_insurance_types: List[str] = []
    exclusion_criteria: dict[str, Any] = {}


class DataFileSummary(BaseModel):
    filename: str | None = None
    original_name: str | None = None
    file_size_bytes: int | None = None
    uploaded_at: str | None = None
    activated_at: str | None = None
    cutoff_date: date | None = None
    total_rows: int | None = None
    total_columns: int | None = None
    provinces: List[str] = []
    months: List[str] = []
    obs_eval_counts: dict[str, int] = {}
    insurance_counts: dict[str, int] = {}


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
    fecha_inicio: date | None = None
    fecha_limite: date | None = None


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
    cred_controls: List[CREDRecord]
    tamizaje: TamizajeRecord
    paquete_completo: bool
