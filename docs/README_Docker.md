# Docker para la plataforma de indicadores

Esta configuracion levanta tres servicios:

- `db`: PostgreSQL con la base `indicator_tracking`.
- `backend`: FastAPI, aplica migraciones Alembic al iniciar y expone `8000`.
- `frontend`: React compilado servido por Nginx, con proxy a `/api`, expuesto en `4173`.

## Requisitos

- Docker Desktop instalado y en ejecucion.
- Docker Compose disponible con `docker compose version`.

## Levantar el sistema

Desde la raiz del proyecto:

```powershell
docker compose up --build
```

Luego abrir:

```text
http://localhost:4173
```

El backend tambien queda disponible en:

```text
http://localhost:8000/health
```

## Base de datos

El contenedor PostgreSQL usa:

```text
host local: localhost
puerto local: 5433
base: indicator_tracking
usuario: postgres
password: postgres
```

Dentro de Docker, el backend usa:

```text
postgresql+psycopg://postgres:postgres@db:5432/indicator_tracking
```

La base persiste en el volumen Docker `postgres_data`. Al iniciar el backend se ejecuta:

```powershell
alembic -c alembic.ini upgrade head
```

## Carga de Excel

Los Excel operativos se cargan desde la vista **Carga datos** del sistema. No es necesario copiarlos manualmente al contenedor.

La carpeta local `data_samples/` se monta como solo lectura en `/app/data_samples` para mantener compatibilidad con los archivos de ejemplo durante desarrollo. Esos archivos no se copian dentro de la imagen Docker.

Los archivos subidos y procesados persisten en estos volumenes:

- `backend_uploads`
- `backend_processed_uploads`
- `backend_backups`

## Comandos utiles

Ver logs:

```powershell
docker compose logs -f
```

Ver logs solo del backend:

```powershell
docker compose logs -f backend
```

Detener servicios:

```powershell
docker compose down
```

Detener y borrar datos persistidos:

```powershell
docker compose down -v
```

Entrar al backend:

```powershell
docker compose exec backend sh
```

Entrar a PostgreSQL:

```powershell
docker compose exec db psql -U postgres -d indicator_tracking
```

## Seguridad

Por defecto `AUTH_ENABLED=false` para desarrollo local. Para un entorno real, cambia en `docker-compose.yml`:

```yaml
AUTH_ENABLED: "true"
AUTH_SECRET_KEY: "un-secreto-largo-y-unico"
AUTH_USERS_JSON: '{"admin":{"password":"clave-segura","role":"admin","display_name":"Administrador"}}'
```

## Puertos

- Frontend: `4173:80`
- Backend: `8000:8000`
- PostgreSQL: `5433:5432`

Se usa `5433` en el host para evitar conflicto con PostgreSQL local en `5432`.
