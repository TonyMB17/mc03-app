# Backend - Sistema de Seguimiento Neonatal

Esta carpeta contiene el backend FastAPI para el proyecto MC-03.

## Instalación

1. Crear un entorno virtual:

```powershell
C:\Users\USUARIO\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
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

El entorno virtual esperado es `backend/.venv` con Python 3.12. Evita crear `.venv` o `.venv312` en la raiz del proyecto.

## Endpoints principales

- `GET /health`
- `GET /api/report/summary`
- `GET /api/report/omisos`

## PostgreSQL

La migracion a base de datos inicia con SQLAlchemy y Alembic. Copia el archivo de ejemplo y ajusta tus credenciales locales:

```powershell
Copy-Item .env.example .env
```

Variable principal:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/indicator_tracking
```

## Seguridad por roles

La fase 9 agrega autenticacion por token firmado y tres roles:

- `clinical`: busqueda por DNI/CNV.
- `supervisor`: busqueda, dashboard y descargas.
- `admin`: busqueda, dashboard, descargas, configuracion y carga de datos.

Variables:

```env
AUTH_ENABLED=true
AUTH_SECRET_KEY=usar-un-secreto-largo
AUTH_TOKEN_TTL_MINUTES=480
AUTH_USERS_JSON={"admin":{"password":"cambiar-admin","role":"admin","display_name":"Administrador"}}
```

En desarrollo `AUTH_ENABLED=false` deja pasar como administrador local para no bloquear pruebas.

## Auditoria y respaldo

La fase 10 registra historial de cargas y eventos de auditoria:

- archivo original
- hash SHA-256
- usuario que sube
- usuario que activa
- estado de procesamiento
- errores de carga
- eventos `upload_processing_started`, `upload_activated` y `upload_failed`

Endpoints de administracion:

- `GET /api/data/uploads?indicator=mc03`
- `GET /api/audit/events?indicator=mc03`

Respaldo manual de PostgreSQL:

```powershell
python -m backend.db.backup
```

El script usa `pg_dump`, por lo que las herramientas cliente de PostgreSQL deben estar disponibles en el `PATH` o se debe configurar `PG_DUMP_PATH`. Los respaldos se escriben en `backend/backups/`, carpeta excluida de git, y se eliminan automaticamente los `.dump` mas antiguos que `BACKUP_RETENTION_DAYS`.

Variables de retencion:

```env
BACKUP_RETENTION_DAYS=30
UPLOAD_RETENTION_DAYS=90
```

Base sugerida:

```powershell
createdb -U postgres indicator_tracking
```

Comandos base de migracion:

```powershell
alembic -c alembic.ini current
alembic -c alembic.ini upgrade head
```

La lógica de reporte está preparada para ser extendida con datos reales de HIS y el padrón nominal.
