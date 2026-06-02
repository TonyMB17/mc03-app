# Automatizacion de Carga Semanal

Este flujo descarga los archivos mas recientes desde DIRESA Cloud, los valida con las reglas existentes del sistema y opcionalmente los activa en PostgreSQL.

## Variables

Configurar en `.env` o `backend/.env`:

```env
DIRESA_CLOUD_BASE_URL=https://cloud.diresaapurimac.gob.pe
DIRESA_CLOUD_USERNAME=usuario
DIRESA_CLOUD_PASSWORD=contrasena
DIRESA_CLOUD_VERIFY_TLS=true
AUTOMATION_DOWNLOAD_DIR=backend/automation_downloads
```

Si el certificado TLS de la plataforma externa falla en el entorno local, se puede ejecutar el comando con `--insecure`.

## Validar sin Activar

Desde la raiz del proyecto:

```powershell
backend\.venv\Scripts\python.exe -m backend.automation.pipeline --insecure
```

Este comando:

- Inicia sesion en DIRESA Cloud.
- Busca los archivos configurados para MC-02, MC-03 y SI-02.
- Descarga el archivo mas reciente de cada busqueda.
- Valida cada indicador.
- Guarda `manifest.json` y `result.json` en `backend/automation_downloads/<fecha_hora>/`.

## Procesar Solo un Indicador

```powershell
backend\.venv\Scripts\python.exe -m backend.automation.pipeline --indicator si02 --insecure
backend\.venv\Scripts\python.exe -m backend.automation.pipeline --indicator mc02 --insecure
backend\.venv\Scripts\python.exe -m backend.automation.pipeline --indicator mc03 --insecure
```

## Activar en Base de Datos

Usar solo cuando la validacion sea correcta:

```powershell
backend\.venv\Scripts\python.exe -m backend.automation.pipeline --activate --insecure
```

La activacion usa los mismos adaptadores de persistencia del sistema manual, registra el origen como `automation` y conserva el hash de los archivos descargados.

## Archivos Buscados

- `SI_02_01_Niños de 209 dias Con Hierro_DosajeHemoglobina`
- `SI_02_02_Niños BPN_Prematuridad 209 dias Con Hierro_DosajeHemoglobina`
- `SI_02_03_Niños de 394dias DX_Anemia con Hierro_DosajeHemoglobina`
- `SI_02_04_Niños de 394dias sin_DX_Anemia con Hierro_DosajeHemoglobina`
- `MC 02_FT MC_02 _INFANTIL`
- `MC 03_FT_BCG_HVB_PAQUETE RN`
