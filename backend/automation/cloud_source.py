"""DIRESA cloud search and download client."""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

import httpx


DEFAULT_BASE_URL = "https://cloud.diresaapurimac.gob.pe"


@dataclass(frozen=True)
class CloudFileTarget:
    key: str
    indicator_code: str
    query: str
    output_filename: str
    subindicator_code: str | None = None


@dataclass(frozen=True)
class CloudFile:
    target_key: str
    indicator_code: str
    name: str
    short_id: str
    download_url: str
    created_at: datetime | None
    size: int | None
    size_label: str | None
    relative_path: str | None
    output_filename: str
    subindicator_code: str | None = None


FILE_TARGETS: tuple[CloudFileTarget, ...] = (
    CloudFileTarget(
        key="si02_01",
        indicator_code="si02",
        subindicator_code="si02_01",
        query="SI_02_01_Ni\u00f1os de 209 dias Con Hierro_DosajeHemoglobina",
        output_filename="SI_02_01_Ninos_209dias_Hierro_DosajeHemoglobina.xlsx",
    ),
    CloudFileTarget(
        key="si02_02",
        indicator_code="si02",
        subindicator_code="si02_02",
        query="SI_02_02_Ni\u00f1os BPN_Prematuridad 209 dias Con Hierro_DosajeHemoglobina",
        output_filename="SI_02_02_Ninos_BPN_Prematuridad_Hierro_DosajeHemoglobina.xlsx",
    ),
    CloudFileTarget(
        key="si02_03",
        indicator_code="si02",
        subindicator_code="si02_03",
        query="SI_02_03_Ni\u00f1os de 394dias DX_Anemia con Hierro_DosajeHemoglobina",
        output_filename="SI_02_03_Ninos_394dias_DX_Anemia_Hierro_DosajeHemoglobina.xlsx",
    ),
    CloudFileTarget(
        key="si02_04",
        indicator_code="si02",
        subindicator_code="si02_04",
        query="SI_02_04_Ni\u00f1os de 394dias sin_DX_Anemia con Hierro_DosajeHemoglobina",
        output_filename="SI_02_04_Ninos_394dias_sin_DX_Anemia_Hierro_DosajeHemoglobina.xlsx",
    ),
    CloudFileTarget(
        key="mc02",
        indicator_code="mc02",
        query="MC 02_FT MC_02 _INFANTIL",
        output_filename="MC_02_FT_MC_02_INFANTIL.xlsx",
    ),
    CloudFileTarget(
        key="mc03",
        indicator_code="mc03",
        query="MC 03_FT_BCG_HVB_PAQUETE RN",
        output_filename="MC_03_FT_BCG_HVB_PAQUETE_RN.xlsx",
    ),
)


def target_map() -> dict[str, CloudFileTarget]:
    return {target.key: target for target in FILE_TARGETS}


def targets_for_indicators(indicators: Iterable[str] | None = None) -> list[CloudFileTarget]:
    requested = {item.lower() for item in indicators or [] if item}
    if not requested:
        return list(FILE_TARGETS)
    return [target for target in FILE_TARGETS if target.indicator_code in requested or target.key in requested]


def env_bool(name: str, default: bool = True) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def parse_cloud_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace(" ", "T"))
    except ValueError:
        return None


def normalize_text(value: str | None) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text).strip().lower()


def safe_filename(value: str) -> str:
    clean_name = unicodedata.normalize("NFKD", value)
    clean_name = "".join(char for char in clean_name if not unicodedata.combining(char))
    clean_name = re.sub(r"[^A-Za-z0-9._-]+", "_", clean_name).strip("._")
    return clean_name or "archivo.xlsx"


def cloud_file_from_payload(target: CloudFileTarget, payload: dict[str, Any]) -> CloudFile:
    return CloudFile(
        target_key=target.key,
        indicator_code=target.indicator_code,
        subindicator_code=target.subindicator_code,
        name=str(payload.get("name") or payload.get("original_name") or ""),
        short_id=str(payload.get("short_id") or ""),
        download_url=str(payload.get("download_url") or ""),
        created_at=parse_cloud_datetime(payload.get("created_at")),
        size=int(payload["size"]) if payload.get("size") is not None else None,
        size_label=payload.get("size_formatted"),
        relative_path=payload.get("relative_path"),
        output_filename=target.output_filename,
    )


class DiresaCloudClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        username: str | None = None,
        password: str | None = None,
        verify_tls: bool = True,
        timeout_seconds: float = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username or os.getenv("DIRESA_CLOUD_USERNAME")
        self.password = password or os.getenv("DIRESA_CLOUD_PASSWORD")
        self.verify_tls = verify_tls
        self.client = httpx.Client(
            base_url=self.base_url,
            follow_redirects=True,
            timeout=timeout_seconds,
            verify=verify_tls,
        )

    @classmethod
    def from_env(cls) -> "DiresaCloudClient":
        return cls(
            base_url=os.getenv("DIRESA_CLOUD_BASE_URL", DEFAULT_BASE_URL),
            verify_tls=env_bool("DIRESA_CLOUD_VERIFY_TLS", True),
        )

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "DiresaCloudClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def login(self) -> dict[str, Any]:
        if not self.username or not self.password:
            raise ValueError("Configura DIRESA_CLOUD_USERNAME y DIRESA_CLOUD_PASSWORD.")
        response = self.client.post(
            "/api/auth_api.php?action=login",
            json={"username": self.username, "password": self.password},
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("success"):
            raise RuntimeError(payload.get("error") or "No se pudo iniciar sesion en DIRESA Cloud.")
        return payload

    def search(self, query: str) -> list[dict[str, Any]]:
        response = self.client.get("/api/index.php", params={"action": "search", "q": query})
        response.raise_for_status()
        payload = response.json()
        if not payload.get("success"):
            raise RuntimeError(payload.get("error") or f"Busqueda fallida: {query}")
        return list(payload.get("files") or [])

    def latest_file(self, target: CloudFileTarget) -> CloudFile:
        query_norm = normalize_text(target.query)
        files = [
            payload
            for payload in self.search(target.query)
            if str(payload.get("extension") or "").lower() == "xlsx"
        ]
        matched = [
            payload
            for payload in files
            if query_norm in normalize_text(payload.get("name") or payload.get("original_name"))
        ]
        candidates = matched or files
        if not candidates:
            raise FileNotFoundError(f"No se encontro archivo para {target.key}: {target.query}")
        candidates.sort(key=lambda item: parse_cloud_datetime(item.get("created_at")) or datetime.min, reverse=True)
        return cloud_file_from_payload(target, candidates[0])

    def download(self, file: CloudFile, destination_dir: Path) -> Path:
        destination_dir.mkdir(parents=True, exist_ok=True)
        filename = safe_filename(file.output_filename or file.name)
        destination = destination_dir / filename
        download_url = file.download_url or f"{self.base_url}/api/file.php?id={file.short_id}&download=1"
        with self.client.stream("GET", download_url) as response:
            response.raise_for_status()
            with destination.open("wb") as output:
                for chunk in response.iter_bytes():
                    if chunk:
                        output.write(chunk)
        return destination
