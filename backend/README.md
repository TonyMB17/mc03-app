# Backend - Sistema de Seguimiento Neonatal

Esta carpeta contiene el backend FastAPI para el proyecto MC-03.

## Instalación

1. Crear un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

## Arrancar el servidor

Si estás dentro de la carpeta `backend`:

```powershell
uvicorn main:app --reload
```

O bien, usando el script de arranque:

```powershell
uvicorn run:app --reload
```

Si prefieres ejecutar desde la raíz del proyecto:

```powershell
uvicorn backend.main:app --reload
```

## Endpoints principales

- `GET /health`
- `GET /api/report/summary`
- `GET /api/report/omisos`

La lógica de reporte está preparada para ser extendida con datos reales de HIS y el padrón nominal.
