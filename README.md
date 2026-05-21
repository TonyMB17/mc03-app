# Plataforma de Indicadores - Red de Salud Abancay

Sistema web para seguimiento nominal y dashboard de indicadores sanitarios.

## Requisitos

- Docker Desktop con Docker Compose.
- Git.
- Archivo `.env` en la raiz del proyecto o `backend/.env`.

## Configuracion

Crear o actualizar `.env` con las variables de produccion:

```env
AUTH_ENABLED=true
AUTH_SECRET_KEY=cambia-esta-clave-por-una-segura
AUTH_TOKEN_TTL_MINUTES=480
AUTH_USERS_JSON={"clinico":{"password":"clave-clinico","role":"clinical","display_name":"Usuario clinico"},"supervisor":{"password":"clave-supervisor","role":"supervisor","display_name":"Usuario supervisor"},"admin":{"password":"clave-admin","role":"admin","display_name":"Administrador"}}
```

Las contrasenas de `AUTH_USERS_JSON` no se guardan en git. Al levantar el backend en Docker, primero se ejecutan las migraciones de base de datos y luego se sincronizan esos usuarios en PostgreSQL.

## Instalacion con Docker

Desde la raiz del proyecto:

```powershell
docker compose up --build -d
```

Servicios:

- Frontend: `http://localhost:4173`
- Backend: `http://localhost:8000`
- PostgreSQL: puerto local `5433`, base `indicator_tracking`

## Actualizar Produccion

```powershell
git pull origin main
docker compose up --build -d
```

Si cambiaste contrasenas en `.env`, vuelve a levantar el backend para sincronizarlas:

```powershell
docker compose up --build -d backend
```

## Comandos Utiles

Ver logs:

```powershell
docker compose logs -f backend
docker compose logs -f frontend
```

Detener servicios:

```powershell
docker compose down
```

Respaldar datos antes de cambios importantes:

```powershell
docker compose exec db pg_dump -U postgres indicator_tracking > backup_indicator_tracking.sql
```
