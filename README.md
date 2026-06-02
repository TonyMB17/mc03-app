# Plataforma de Seguimiento de Indicadores

Sistema web para seguimiento nominal y dashboard de indicadores de salud de la Red de Salud Abancay. Incluye backend FastAPI, frontend React/Vite, PostgreSQL, migraciones Alembic, auditoria de cargas, usuarios por roles y respaldo de base de datos.

## Estructura

- `backend/`: API FastAPI, indicadores, seguridad, migraciones y respaldo.
- `frontend/`: app React con Vite, Tailwind y DaisyUI.
- `data_samples/`: archivos Excel de ejemplo.
- `docs/`: documentacion tecnica ampliada.

## Levantar con Docker

Requisitos: Docker Desktop y Docker Compose.

```powershell
docker compose up --build
```

Servicios:

- Frontend: `http://localhost:4173`
- Backend: `http://localhost:8000/health`
- PostgreSQL host: `localhost:5433`
- Base: `indicator_tracking`
- Usuario/password: `postgres/postgres`

Automatizacion incluida:

- El backend espera a PostgreSQL.
- Ejecuta automaticamente migraciones: `alembic -c alembic.ini upgrade head`.
- La activacion de cargas corre en segundo plano dentro del backend; no requiere worker externo.
- Conserva PostgreSQL y respaldos en volumenes Docker; `backend_uploads` y `backend_processed_uploads` se usan durante cargas en curso.

Comandos utiles:

```powershell
docker compose logs -f backend
docker compose exec backend python -m backend.db.backup
docker compose down
```

Para borrar tambien la base y volumenes:

```powershell
docker compose down -v
```

## Variables principales

Crear `.env` o `backend/.env` si se requiere sobrescribir valores:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/indicator_tracking
AUTH_ENABLED=true
AUTH_SECRET_KEY=change-this-secret-before-production
AUTH_TOKEN_TTL_MINUTES=480
BACKUP_RETENTION_DAYS=30
UPLOAD_RETENTION_DAYS=7
DIRESA_CLOUD_BASE_URL=https://cloud.diresaapurimac.gob.pe
DIRESA_CLOUD_USERNAME=
DIRESA_CLOUD_PASSWORD=
DIRESA_CLOUD_VERIFY_TLS=true
AUTOMATION_DOWNLOAD_DIR=backend/automation_downloads
```

## Levantar sin Docker

Requisitos: Python 3.12, Node.js, PostgreSQL local y herramientas cliente de PostgreSQL si se usara respaldo con `pg_dump`.

### 1. Base de datos

Crear la base:

```powershell
createdb -U postgres indicator_tracking
```

Configurar variables:

```powershell
Copy-Item backend\.env.example backend\.env
```

Revisar `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/indicator_tracking
AUTH_ENABLED=false
```

### 2. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic -c alembic.ini upgrade head
uvicorn main:app --reload
```

Desde la raiz tambien se puede usar:

```powershell
backend\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Backend: `http://localhost:8000/health`

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Frontend local: `http://localhost:4173`

## Automatizacion y mantenimiento

La automatizacion operativa vive dentro del backend: migraciones al iniciar con Docker, activacion de cargas en segundo plano, limpieza de versiones antiguas y respaldo manual con retencion.

### Migraciones

- Con Docker se ejecutan solas al iniciar el backend.
- Sin Docker se ejecutan manualmente:

```powershell
cd backend
alembic -c alembic.ini upgrade head
```

### Respaldo de PostgreSQL

```powershell
cd backend
python -m backend.db.backup
```

El respaldo usa `pg_dump`. Si no esta en el `PATH`, configurar en `backend/.env`:

```env
PG_DUMP_PATH=C:\Program Files\PostgreSQL\18\bin\pg_dump.exe
BACKUP_RETENTION_DAYS=30
```

Los respaldos se guardan en `backend/backups/` y se limpian automaticamente segun `BACKUP_RETENTION_DAYS`.

### Retencion de cargas antiguas

```env
UPLOAD_RETENTION_DAYS=7
```

Despues de activar una nueva carga, el backend elimina versiones `superseded` o `failed` que ya no sean activas y superen ese numero de dias. La version activa no se borra. Los archivos temporales/procesados usados durante la activacion se eliminan al terminar la activacion.

## Seguridad

Roles base:

- `clinical`: busqueda nominal.
- `supervisor`: busqueda, dashboard y descargas.
- `admin`: busqueda, dashboard, descargas, configuracion, carga de datos y usuarios.

En desarrollo puede usarse `AUTH_ENABLED=false`. En produccion usar `AUTH_ENABLED=true`, cambiar `AUTH_SECRET_KEY` y administrar usuarios desde la vista **Usuarios**.

## Documentacion ampliada

- Docker: `docs/README_Docker.md`
- PostgreSQL/migracion: `docs/README_PostgreSQL_Migration.md`
- Arquitectura: `docs/ARQUITECTURA_PLATAFORMA_INDICADORES.md`
- Diseno USI: `docs/README_DISENO_PLATAFORMA_SALUD.md`
