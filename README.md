# Plataforma de Indicadores de Salud

Sistema web para busqueda nominal, dashboard, carga de datos y automatizacion semanal de indicadores de salud.

## Levantar con Docker

Requisitos: Docker Desktop y Docker Compose.

```powershell
docker compose up --build
```

Servicios:

- Frontend: `http://localhost:4173`
- Backend: `http://localhost:8000/health`
- PostgreSQL: `localhost:5433`
- Base por defecto: `indicator_tracking`

El contenedor del backend espera a PostgreSQL y ejecuta migraciones automaticamente con Alembic.

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

Requisitos: Python 3.12, Node.js y PostgreSQL local.

Crear base de datos:

```powershell
createdb -U postgres indicator_tracking
```

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic -c alembic.ini upgrade head
uvicorn main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Comandos utiles

```powershell
docker compose logs -f backend
docker compose exec backend python -m backend.db.backup
docker compose down
```

Para borrar tambien volumenes locales:

```powershell
docker compose down -v
```
