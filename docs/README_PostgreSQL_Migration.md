# Migracion a PostgreSQL para Indicadores

Este documento define la ruta de migracion para que los Excel semanales sean una entrada de datos y no la fuente viva de consulta. El objetivo es que busqueda por DNI, dashboard y descargas lean datos procesados, versionados e indexados en PostgreSQL.

## Contexto operativo

- Cada semana se cargaran archivos Excel para multiples indicadores.
- La busqueda por DNI/CNV sera la vista mas usada por el personal clinico.
- El dashboard y descargas seran usados por un grupo menor de usuarios supervisores.
- La carga de datos y configuracion quedara restringida a administradores.
- El sistema debe evitar reprocesar Excel en cada consulta.

## Principio de arquitectura

```text
Excel semanal
-> validacion
-> procesamiento del indicador
-> almacenamiento versionado
-> activacion de version
-> consultas sobre datos procesados
```

El Excel debe conservarse solo como respaldo o evidencia de carga. Las consultas operativas deben usar tablas PostgreSQL con indices.

## Fase 1: Base tecnica

Preparar la conexion y migraciones de PostgreSQL.

Entregables:

- Variable `DATABASE_URL` en `.env`.
- Dependencias backend: SQLAlchemy, Alembic, psycopg y python-dotenv.
- Modulos base:
  - `backend/db/base.py`
  - `backend/db/session.py`
  - `backend/db/models.py`
- Configuracion inicial de Alembic.

Objetivo: que el backend pueda conectarse a PostgreSQL y crear tablas mediante migraciones controladas.

## Fase 2: Modelo general de cargas

Crear tablas reutilizables para todos los indicadores.

Tablas sugeridas:

- `indicator_uploads`: carga semanal, indicador, archivo, fecha de corte, estado, usuario, hash y resumen.
- `indicator_active_uploads`: carga activa por indicador.
- `indicator_records`: registros nominales procesados.
- `component_results`: resultado por componente del indicador.
- `dashboard_summaries`: resumen precalculado por indicador, provincia y periodo.
- `indicator_omissions`: incumplidos procesados para tabla y exportacion.

Objetivo: tener una estructura comun para MC-02, MC-03 y futuros indicadores.

## Fase 3: Persistir MC-02 sin cambiar lecturas

Al cargar MC-02, guardar en PostgreSQL lo procesado, manteniendo temporalmente las respuestas actuales desde memoria.

Flujo:

```text
Excel MC-02
-> validar
-> leer tabla operativa
-> evaluar componentes
-> guardar registros
-> guardar componentes
-> guardar dashboard
-> guardar omisos
```

Objetivo: probar escritura y consistencia sin afectar busqueda ni dashboard.

## Fase 4: Busqueda por DNI desde PostgreSQL

Cambiar la busqueda nominal de MC-02 para leer desde la carga activa en BD.

Indices recomendados:

```sql
CREATE INDEX ON indicator_records (indicator_code, dni);
CREATE INDEX ON indicator_records (indicator_code, cnv);
CREATE INDEX ON indicator_records (upload_id, dni);
CREATE INDEX ON indicator_records (upload_id, cnv);
```

Objetivo: que la vista mas usada sea rapida y no dependa de Excel ni dataframes.

## Fase 5: Dashboard desde PostgreSQL

Cambiar los endpoints de resumen, incumplidos y descarga para leer resumos precalculados.

Endpoints involucrados:

- `GET /api/report/summary`
- `GET /api/report/incumplidos`
- `GET /api/report/incumplidos.xlsx`

Objetivo: evitar re-evaluar todos los registros al abrir el dashboard.

## Fase 6: Activacion versionada

Formalizar estados de carga:

```text
pending -> processing -> validated -> active
                        -> failed
```

Reglas:

- Una carga nueva no reemplaza a la activa hasta que el administrador la active.
- Si falla una carga, la version activa anterior sigue disponible.
- Debe conservarse el historial de cargas.

## Fase 7: Procesamiento en segundo plano

Mover el trabajo pesado fuera del request HTTP.

Ruta incremental:

- Inicio: `FastAPI BackgroundTasks`.
- Escala posterior: Redis + RQ o Celery.

Objetivo: que la carga semanal no bloquee la API.

## Fase 8: Migrar MC-03 y estandarizar indicadores

Repetir el patron probado en MC-02 para MC-03.

Objetivo:

- Cada indicador define validacion y reglas.
- Todos persisten en tablas generales.
- El frontend consume una API comun.

## Fase 9: Seguridad, usuarios y roles

Roles previstos:

- Usuario clinico: busqueda por DNI/CNV.
- Usuario supervisor: dashboard y descargas.
- Administrador: carga, configuracion y activacion.

La implementacion actual persiste usuarios, roles y permisos en PostgreSQL. `AUTH_USERS_JSON` queda como semilla inicial para despliegues, pero la administracion operativa se hace desde la vista de usuarios del frontend.

## Fase 10: Auditoria y respaldo

Agregar:

- historial de cargas
- usuario que sube y activa
- hash de archivo
- logs de procesamiento
- backups de BD
- politica de retencion de Excel originales

## Decision actual

La base de datos recomendada para el entorno local y despliegues iniciales es:

```text
indicator_tracking
```

Se eligio este nombre porque el sistema ya no representa solo MC-03, sino un seguimiento multiindicador.

La implementacion ya completo las fases 1 a 10 para la base multiindicador inicial: MC-02 y MC-03 persisten cargas versionadas en PostgreSQL, las consultas usan la carga activa, el procesamiento corre en segundo plano, los roles protegen las vistas sensibles y la auditoria deja historial de cargas y eventos. El siguiente incremento natural es incorporar nuevos indicadores usando el mismo contrato.

## Estado de implementacion

### Fase 1 completada

- Dependencias SQLAlchemy, Alembic, psycopg y python-dotenv.
- `DATABASE_URL` en `.env`.
- Paquete `backend/db`.
- Entorno Alembic en `backend/alembic`.

### Fase 2 completada a nivel de esquema

Modelos creados:

- `IndicatorUpload`
- `IndicatorActiveUpload`
- `IndicatorRecord`
- `ComponentResult`
- `DashboardSummary`
- `IndicatorOmission`

Migracion inicial:

- `backend/alembic/versions/0001_indicator_storage.py`

Comando para crear la base local, ajustando usuario si corresponde:

```powershell
createdb -U postgres indicator_tracking
```

Si `createdb` o `psql` no estan en el PATH, la base tambien puede crearse desde Python usando la conexion administrativa a `postgres` y el usuario configurado en `.env`.

Comando para crear las tablas:

```powershell
cd backend
alembic -c alembic.ini upgrade head
```

### Fase 3 completada como escritura inicial para MC-02

- `backend/indicators/mc02/storage.py` persiste una carga MC-02 procesada en las tablas generales.
- Al activar una carga MC-02, el backend guarda:
  - registros nominales en `indicator_records`
  - resultados por componente en `component_results`
  - resumen precalculado en `dashboard_summaries`
  - incumplidos en `indicator_omissions`
  - referencia activa en `indicator_active_uploads`
- Las lecturas de busqueda por DNI, dashboard y exportacion siguen usando el flujo actual en memoria; el cambio de lectura queda para Fase 4 y Fase 5.
- Validacion local con Excel MC-02: 5,789 registros, 40,523 resultados de componentes, 117 resumenes de dashboard y 728 omisos persistidos.

### Fase 4 completada para busqueda MC-02

- `backend/indicators/mc02/storage.py` expone `search_active_by_dni`.
- `GET /api/search/dni/{dni}?indicator=mc02` consulta primero la carga activa en PostgreSQL.
- Si no existe carga activa en BD o PostgreSQL no esta disponible durante esta etapa transicional, el endpoint mantiene el flujo anterior desde memoria.
- Si existe carga activa en BD y el DNI/CNV no pertenece a esa carga y provincia, responde `404`.
- La respuesta mantiene el mismo contrato usado por `SearchDNI.jsx`: datos personales, componentes, alertas clinicas, tamizaje de compatibilidad y estado del paquete.
- Validacion local con DNIs `94424954`, `94429011`, `94405414`, `94429279` y `94332765`: resultado desde BD consistente con resultado desde dataframe.

### Fase 5 completada para dashboard MC-02

- `backend/indicators/mc02/storage.py` expone `build_active_report_summary`.
- `GET /api/report/summary?indicator=mc02` lee `dashboard_summaries` e `indicator_omissions` desde la carga activa en PostgreSQL.
- `GET /api/report/omisos`, `GET /api/report/incumplidos`, `GET /api/report/omisos.csv`, `GET /api/report/incumplidos.csv` y `GET /api/report/incumplidos.xlsx` reutilizan el mismo resumen activo.
- Durante la transicion, si no existe carga activa en PostgreSQL o la BD no esta disponible, se conserva el fallback al dataframe en memoria.
- La cobertura mensual se lee precalculada y el semaforo se recalcula con la meta solicitada por el usuario.
- Validacion local ABANCAY: PostgreSQL y dataframe coinciden en 13 cohortes, 199 incumplidos, denominador, numerador, cobertura y semaforo para metas 80.9 y 70.7.

### Fase 6 completada como activacion segura MC-02

- La activacion de MC-02 persiste primero en PostgreSQL y solo actualiza la version activa en memoria si la persistencia termina correctamente.
- `indicator_uploads.status` usa la secuencia `processing -> validated -> active`.
- Si ocurre un error durante procesamiento o escritura, la carga queda marcada como `failed` con `error_message` y la version activa previa no se reemplaza.
- Cuando una nueva carga queda activa, la carga anterior pasa a `superseded`.
- El estado `pending` sigue representado por la carga pendiente en memoria entre `upload-preview` y `activate`.
- Validacion local: la carga activa existente permanece `active` y apuntada por `indicator_active_uploads`; la suite MC-02 confirma el marcado `failed` del flujo de error.

### Fase 7 completada como procesamiento en segundo plano inicial

- `POST /api/data/activate?indicator=mc02` ya no espera a que termine la persistencia pesada en PostgreSQL.
- La respuesta de activacion puede devolver `processing=true`, `job_id`, `job_status` y `message`.
- `GET /api/data/activation/{job_id}?indicator=mc02` permite consultar el avance del trabajo.
- La vista de carga hace polling cada 2 segundos mientras el trabajo esta `queued` o `processing`.
- Si el trabajo termina en `activated`, la vista refresca la fuente activa; si termina en `failed`, muestra el error y conserva la version anterior.
- En esta fase se usa `FastAPI BackgroundTasks`. La ruta futura para mayor escala sigue siendo Redis + RQ o Celery.

### Fase 8 completada como migracion inicial de MC-03

- `backend/indicators/mc03/storage.py` replica el patron versionado de MC-02 sobre las tablas generales.
- MC-03 persiste registros nominales, resultados de BCG, HvB, CRED y tamizaje, resumenes por provincia y omisos.
- `backend/indicators/mc03/__init__.py` expone `persist_active_upload`, `active_upload_id`, `search_active_by_dni` y `build_active_report_summary`.
- La activacion de MC-03 queda integrada al flujo comun de `BackgroundTasks`, igual que MC-02.
- La busqueda por DNI/CNV, dashboard, tabla de incumplidos y descargas usan PostgreSQL primero cuando existe una carga activa MC-03.
- El dataframe en memoria se conserva como fallback transicional para escenarios sin carga activa en BD.
- Validacion local con Excel MC-03: 2,553 registros, 15,318 resultados de componentes, 99 resumenes de dashboard y 788 omisos persistidos en la carga completa.
- Validacion ABANCAY desde PostgreSQL: resumen mensual coincide con el dataframe y conserva 188 omisos, `months_met = 0` y `committed = False`.

### Fase 9 completada como control de acceso por roles

- Se agrego `backend/security.py` con autenticacion por usuario/contrasena y tokens Bearer firmados con `AUTH_SECRET_KEY`.
- Roles implementados:
  - `clinical`: busqueda por DNI/CNV.
  - `supervisor`: busqueda, dashboard y descargas.
  - `admin`: busqueda, dashboard, descargas, configuracion, carga, activacion y administracion de usuarios.
- Endpoints protegidos:
  - Busqueda: `clinical`, `supervisor`, `admin`.
  - Reportes y descargas: `supervisor`, `admin`.
  - Configuracion y carga de datos: `admin`.
- Se agregaron tablas `app_users`, `app_roles`, `app_permissions`, `app_user_roles` y `app_role_permissions` mediante `backend/alembic/versions/0003_users_roles_permissions.py`.
- Las contrasenas se almacenan con hash Argon2 mediante `pwdlib[argon2]`.
- `AUTH_USERS_JSON` funciona como semilla inicial y no reemplaza cuentas existentes.
- Se agregaron endpoints administrativos `GET/POST/PATCH /api/security/users` y `GET /api/security/roles`.
- El frontend agrega vista **Usuarios** para crear cuentas, asignar rol, activar/desactivar usuarios y renovar contrasenas.
- El frontend agrega login, conserva token en `localStorage`, envia `Authorization: Bearer ...` y oculta vistas sin permiso.
- Las descargas Excel ahora usan el cliente autenticado para poder enviar el token.
- En desarrollo `AUTH_ENABLED=false` permite trabajar como administrador local sin bloquear pruebas.
- Validacion HTTP real con `AUTH_ENABLED=true`: sin token responde `401`; usuario clinico busca pero recibe `403` en dashboard; supervisor ve dashboard pero recibe `403` en carga; admin accede a carga.

### Fase 10 completada como auditoria y respaldo inicial

- Se agrego la tabla `indicator_audit_events` mediante `backend/alembic/versions/0002_indicator_audit_events.py`.
- Se agrego `backend/db/audit.py` para registrar eventos y consultar historial de cargas.
- Las cargas registran `file_hash` SHA-256, `uploaded_by`, `activated_by`, estado, resumen de validacion y resumen de procesamiento.
- Los persisters de MC-02 y MC-03 registran eventos:
  - `upload_processing_started`
  - `upload_activated`
  - `upload_failed`
- Se agregaron endpoints administrativos:
  - `GET /api/data/uploads?indicator=mc03`
  - `GET /api/audit/events?indicator=mc03`
- La vista de carga muestra historial de versiones con estado activo, actor, corte, registros y hash.
- Se agrego `backend/db/backup.py` para ejecutar respaldo manual con `pg_dump`:

```powershell
python -m backend.db.backup
```

- Los respaldos se guardan en `backend/backups/`, carpeta excluida de git.
- Variables documentadas: `PG_DUMP_PATH`, `BACKUP_RETENTION_DAYS` y `UPLOAD_RETENTION_DAYS`.
- La retencion automatica se aplica a respaldos `.dump` y a cargas historicas en PostgreSQL. Las versiones `superseded` o `failed` se eliminan despues de `UPLOAD_RETENTION_DAYS` dias sin estar activas; la version activa nunca se purga por esta regla.
- Los archivos temporales y procesados de una carga persistida se eliminan al activarla para evitar acumular Excel o paquetes intermedios en disco.
