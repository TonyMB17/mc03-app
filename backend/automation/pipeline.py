"""Download, validate and optionally activate indicator files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from ..db.session import SessionLocal
    from ..indicators.registry import get_indicator
except ImportError:
    from db.session import SessionLocal
    from indicators.registry import get_indicator

from .cloud_source import DEFAULT_BASE_URL, CloudFile, DiresaCloudClient, env_bool, targets_for_indicators


DEFAULT_DOWNLOAD_ROOT = Path(__file__).resolve().parents[1] / "automation_downloads"


@dataclass
class DownloadedCloudFile:
    cloud_file: CloudFile
    path: Path


@dataclass
class IndicatorImportResult:
    indicator_code: str
    valid: bool
    activated: bool
    files: list[str]
    errors: list[str]
    warnings: list[str]
    summary: dict[str, Any]
    upload_id: str | None = None


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def combined_sha256(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.name):
        digest.update(path.name.encode("utf-8"))
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def batch_directory(root: Path | None = None) -> Path:
    base = root or Path(os.getenv("AUTOMATION_DOWNLOAD_DIR", DEFAULT_DOWNLOAD_ROOT))
    return base / datetime.now().strftime("%Y%m%d_%H%M%S")


def write_manifest(download_dir: Path, downloads: list[DownloadedCloudFile]) -> Path:
    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "files": [
            {
                **asdict(item.cloud_file),
                "created_at": item.cloud_file.created_at.isoformat(timespec="seconds") if item.cloud_file.created_at else None,
                "local_path": str(item.path),
                "sha256": file_sha256(item.path),
            }
            for item in downloads
        ],
    }
    manifest_path = download_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    return manifest_path


def download_latest_files(
    indicators: list[str] | None = None,
    download_root: Path | None = None,
    *,
    verify_tls: bool | None = None,
    log=None,
) -> tuple[Path, list[DownloadedCloudFile]]:
    download_dir = batch_directory(download_root)
    selected_targets = targets_for_indicators(indicators)
    if log:
        log(f"Iniciando automatizacion para {len(selected_targets)} archivo(s).")
        log(f"Carpeta temporal: {download_dir}")

    client = DiresaCloudClient(
        base_url=os.getenv("DIRESA_CLOUD_BASE_URL", DEFAULT_BASE_URL),
        verify_tls=verify_tls if verify_tls is not None else env_bool("DIRESA_CLOUD_VERIFY_TLS", True),
    )
    with client:
        if log:
            log("Conectando con DIRESA Cloud...")
        login_payload = client.login()
        if log:
            user = (login_payload.get("user") or {}).get("username") or "usuario autenticado"
            log(f"Sesion iniciada como {user}.")
        downloads = []
        for index, target in enumerate(selected_targets, start=1):
            if log:
                log(f"[{index}/{len(selected_targets)}] Buscando {target.key}: {target.query}")
            cloud_file = client.latest_file(target)
            if log:
                created = cloud_file.created_at.isoformat(sep=" ", timespec="seconds") if cloud_file.created_at else "sin fecha"
                log(f"Encontrado: {cloud_file.name} | fecha {created} | tamano {cloud_file.size_label or cloud_file.size or '-'}")
            path = client.download(cloud_file, download_dir)
            if log:
                log(f"Descargado: {path.name}")
            downloads.append(DownloadedCloudFile(cloud_file=cloud_file, path=path))
    write_manifest(download_dir, downloads)
    return download_dir, downloads


def group_downloads(downloads: list[DownloadedCloudFile]) -> dict[str, list[DownloadedCloudFile]]:
    grouped: dict[str, list[DownloadedCloudFile]] = {}
    for item in downloads:
        grouped.setdefault(item.cloud_file.indicator_code, []).append(item)
    return grouped


def prepare_indicator(indicator_code: str, paths: list[Path]) -> dict[str, Any]:
    definition = get_indicator(indicator_code)
    module = definition.module
    if hasattr(module, "prepare_data_files") and len(paths) > 1:
        prepared = module.prepare_data_files(paths)
        return {
            "data": prepared.get("data"),
            "cutoff_date": prepared.get("cutoff_date") or prepared.get("cutoff_dates"),
            "validation": prepared["validation"],
        }
    if hasattr(module, "prepare_data_file"):
        prepared = module.prepare_data_file(paths[0])
        return {
            "data": prepared.get("data"),
            "cutoff_date": prepared.get("cutoff_date"),
            "validation": prepared["validation"],
        }
    validation = definition.validate_data_file(paths[0])
    loaded = definition.load_sample_data(paths[0]) if validation.get("valid") else None
    return {
        "data": loaded.get("data") if loaded else None,
        "cutoff_date": loaded.get("cutoff_date") if loaded else validation.get("summary", {}).get("cutoff_date"),
        "validation": validation,
    }


def activate_indicator(
    indicator_code: str,
    prepared: dict[str, Any],
    source_path: Path,
    file_paths: list[Path],
    validation_summary: dict[str, Any],
) -> str:
    definition = get_indicator(indicator_code)
    persister = getattr(definition.module, "persist_active_upload", None)
    if persister is None:
        raise RuntimeError(f"El indicador {indicator_code} no tiene persistencia activa configurada.")
    metadata = {
        "original_name": source_path.name if len(file_paths) == 1 else f"{indicator_code}_paquete_automatico",
        "uploaded_by": "automation",
        "activated_by": "automation",
        "actor_role": "system",
        "activated_at": datetime.now().isoformat(timespec="seconds"),
        "file_hash": combined_sha256(file_paths),
    }
    with SessionLocal() as db:
        upload_id = persister(
            db,
            prepared["data"],
            prepared.get("cutoff_date"),
            source_path,
            metadata,
            validation_summary,
        )
    return str(upload_id)


def validate_and_optionally_activate(
    download_dir: Path,
    downloads: list[DownloadedCloudFile],
    *,
    activate: bool = False,
    source_preserved: bool = True,
) -> list[IndicatorImportResult]:
    manifest_path = download_dir / "manifest.json"
    results: list[IndicatorImportResult] = []
    prepared_items: list[tuple[IndicatorImportResult, dict[str, Any], list[Path]]] = []
    for indicator_code, items in sorted(group_downloads(downloads).items()):
        paths = [item.path for item in items]
        prepared = prepare_indicator(indicator_code, paths)
        validation = prepared["validation"]
        valid = bool(validation.get("valid"))
        summary = dict(validation.get("summary") or {})
        summary["automation_files"] = [item.path.name for item in items]
        summary["automation_created_at"] = datetime.now().isoformat(timespec="seconds")
        summary["source_preserved"] = source_preserved
        result = IndicatorImportResult(
            indicator_code=indicator_code,
            valid=valid,
            activated=False,
            upload_id=None,
            files=[str(path) for path in paths],
            errors=list(validation.get("errors") or []),
            warnings=list(validation.get("warnings") or []),
            summary=summary,
        )
        results.append(result)
        prepared_items.append((result, prepared, paths))

    if activate and all(result.valid for result in results):
        for result, prepared, paths in prepared_items:
            source_path = paths[0] if len(paths) == 1 else manifest_path
            result.upload_id = activate_indicator(result.indicator_code, prepared, source_path, paths, result.summary)
            result.activated = True

    return results


def cleanup_download_dir(download_dir: Path) -> None:
    if download_dir.exists():
        shutil.rmtree(download_dir)


def run_cloud_import_with_logs(
    log,
    indicators: list[str] | None = None,
    *,
    activate: bool = False,
    cleanup_after_activation: bool = False,
    download_root: Path | None = None,
    verify_tls: bool | None = None,
) -> dict[str, Any]:
    download_dir, downloads = download_latest_files(
        indicators,
        download_root,
        verify_tls=verify_tls,
        log=log,
    )
    log("Manifest guardado: manifest.json")

    log("Validando archivos descargados...")
    results = validate_and_optionally_activate(
        download_dir,
        downloads,
        activate=activate,
        source_preserved=not (cleanup_after_activation and activate),
    )
    for result in results:
        status = "VALIDO" if result.valid else "ERROR"
        cutoff = result.summary.get("cutoff_date") or "-"
        rows = result.summary.get("total_rows") or 0
        log(f"{result.indicator_code.upper()}: {status} | corte {cutoff} | filas {rows}")
        for warning in result.warnings:
            log(f"Advertencia {result.indicator_code}: {warning}")
        for error in result.errors:
            log(f"Error {result.indicator_code}: {error}")
        if result.activated:
            log(f"{result.indicator_code.upper()}: activado con upload_id {result.upload_id}.")

    output = {
        "download_dir": str(download_dir),
        "activated": activate,
        "results": [asdict(result) for result in results],
    }
    result_path = download_dir / "result.json"
    result_path.write_text(json.dumps(output, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    log(f"Resultado guardado: {result_path.name}")

    all_valid = all(result.valid for result in results)
    all_activated = all(result.activated for result in results)
    if cleanup_after_activation and activate and all_valid and all_activated:
        cleanup_download_dir(download_dir)
        log("Archivos temporales eliminados despues de la activacion.")
        output["download_dir_deleted"] = True
    else:
        output["download_dir_deleted"] = False

    log("Proceso terminado correctamente.")
    return output


def run_cloud_import(
    indicators: list[str] | None = None,
    *,
    activate: bool = False,
    download_root: Path | None = None,
    verify_tls: bool | None = None,
) -> dict[str, Any]:
    download_dir, downloads = download_latest_files(indicators, download_root, verify_tls=verify_tls)
    results = validate_and_optionally_activate(download_dir, downloads, activate=activate)
    output = {
        "download_dir": str(download_dir),
        "activated": activate,
        "results": [asdict(result) for result in results],
    }
    (download_dir / "result.json").write_text(json.dumps(output, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Descarga y procesa archivos semanales desde DIRESA Cloud.")
    parser.add_argument("--indicator", action="append", dest="indicators", help="Indicador a procesar: mc02, mc03, si02. Puede repetirse.")
    parser.add_argument("--activate", action="store_true", help="Activa los datos si la validacion es correcta.")
    parser.add_argument("--download-root", type=Path, default=None, help="Carpeta raiz para guardar descargas.")
    parser.add_argument("--insecure", action="store_true", help="Desactiva verificacion TLS para la plataforma externa.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_cloud_import(
        indicators=args.indicators,
        activate=args.activate,
        download_root=args.download_root,
        verify_tls=False if args.insecure else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=json_default))


if __name__ == "__main__":
    main()
