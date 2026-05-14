# Registro de decisiones y cambios - MC-03 App

## 2026-05-12

### Decisiones principales
- Se implementó un backend en `FastAPI` para el sistema de seguimiento neonatal.
- Se definieron endpoints iniciales:
  - `GET /health`
  - `GET /api/report/summary`
  - `GET /api/report/omisos`
- Se creó un frontend con `React`, `Vite` y `Tailwind CSS` para un dashboard de cumplimiento tipo HUD.
- El backend lee el archivo Excel `data_samples/MC 03_FT_BCG_HVB_PAQUETE RN.xlsx` desde la hoja `Detalle_Ate`, con cabeceras en la fila 10 y fecha de corte en `B8`.
- Se creó un esquema inicial de datos y configuraciones de negocio en `backend/config.py` para los códigos y reglas MC-03.

### Historial de cambios realizados
- Scaffold de backend creado: `backend/main.py`, `backend/schemas.py`, `backend/services.py`, `backend/requirements.txt`, `backend/README.md`.
- Scaffold de frontend creado: `frontend/package.json`, `frontend/vite.config.js`, `frontend/tailwind.config.js`, `frontend/postcss.config.js`, `frontend/index.html`, `frontend/src/main.jsx`, `frontend/src/App.jsx`, `frontend/src/index.css`, `frontend/README.md`.
- Archivo `.gitignore` agregado en la raíz del proyecto.
- `README.md` principal actualizado con instrucciones de arranque y estructura del workspace.
- Se ajustó la carga de Excel para usar la hoja y fila especificadas, y leer la fecha de corte desde `B8`.

### Estado actual
- Backend y frontend están preparados para ejecutarse.
- Dependencias de backend instaladas con Python 3.13.
- Dependencias de frontend instaladas con `npm`.
- El proyecto está listo para continuar con la lógica real de cálculo de cumplimiento y visualización de datos.

### Comandos para arrancar el proyecto

#### Backend
```powershell
cd "c:\Users\USUARIO\Documents\My projects\mc03-app\backend"
# Crear o activar entorno virtual si no existe
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

#### Frontend
```powershell
cd "c:\Users\USUARIO\Documents\My projects\mc03-app\frontend"
npm install
npm run dev
```

### Cómo verificar
- Backend: abrir `http://127.0.0.1:8000/health`
- Frontend: abrir la URL que muestre Vite, normalmente `http://127.0.0.1:4173`
- La aplicación frontend está configurada para hacer proxy a `/api` hacia el backend local.

### Siguientes pasos sugeridos
- Implementar el cálculo real de la tasa de cobertura con datos del padrón nominal y HIS.
- Agregar el endpoint de exportación de omisos en formato CSV.
- Mejorar el tablero con indicadores de semáforo por mes y alertas de incumplimiento.

### Avance posterior
- Se implementó el cálculo mensual real del reporte MC-03 para junio-noviembre 2026 usando `Mes_eva`.
- El denominador ahora filtra niños evaluados con seguro SIS o Sin Seguro, excluyendo bajo peso y prematuridad según reglas de negocio.
- El numerador ahora valida el paquete completo: BCG, HvB, 3 CRED en ventana/intervalo y tamizaje neonatal en ventana.
- Se corrigieron los omisos y se agregó `GET /api/report/omisos.csv` para descargar el listado en CSV.
- Se actualizó el frontend para mostrar meses cumplidos, conteo de omisos, tabla de omisos recientes y descarga CSV.
- Se creó un entorno local `.venv312` porque el `.venv` existente apunta a Python 3.13 con acceso denegado. El nuevo entorno está ignorado por `.gitignore`.

### Verificación realizada
- Backend validado con llamadas directas: salud OK, junio 2026 con denominador 13, numerador 0 y 13 omisos.
- Frontend validado con `npm.cmd run build`.
- App abierta en navegador integrado en `http://127.0.0.1:4173`, sin errores de consola.
- Búsqueda DNI probada con `94595491`, mostrando paquete incompleto correctamente.

### Organización de vistas
- Se separó la aplicación en dos vistas principales: `Búsqueda DNI` como vista inicial y `Dashboard indicador` como vista de seguimiento del compromiso.
- `frontend/src/App.jsx` ahora funciona como contenedor de navegación entre vistas.
- `frontend/src/Dashboard.jsx` concentra el resumen mensual, omisos y descarga CSV.
- `frontend/src/SearchDNI.jsx` queda enfocado en la consulta individual por DNI.
- Se validó la navegación en navegador integrado: la app inicia en búsqueda DNI y el botón `Dashboard indicador` muestra el seguimiento mensual sin errores de consola.

### Detalle operativo por prestación
- La búsqueda por DNI ahora devuelve y muestra `estado`, `mensaje`, `fecha_inicio` y `fecha_limite` para BCG, HvB, CRED 1-3 y tamizaje neonatal.
- Se distinguen estados: `Cumple`, `En ventana`, `Programado` e `Incumple`.
- Si no hay fecha registrada y aún está dentro de ventana, el sistema advierte la fecha límite.
- Si la ventana aún no inicia, el sistema muestra el próximo control con fecha de inicio y fecha límite.
- Si la atención se hizo fuera de plazo o con código incorrecto, el sistema marca incumplimiento con el motivo.
- Si los campos están vacíos y el plazo venció, el sistema informa que no se registra atención y muestra la fecha de vencimiento.
- Validación realizada con DNI `94635370`: CRED 2 aparece `En ventana` con límite `16/05/2026`, y CRED 3 aparece `Programado` desde `17/05/2026`.

### Historial del dashboard
- El resumen mensual ahora incluye enero-noviembre 2026 para visualizar historial y avance del indicador.
- Enero-mayo se marca como `Histórico`; junio-noviembre se marca como `Verificación`.
- La regla del compromiso se mantiene solo sobre los 6 meses oficiales de verificación.
- En la interfaz se cambió la denominación visible de `omisos` a `incumplidos`.
- Se agregó endpoint alternativo `GET /api/report/incumplidos` y descarga `GET /api/report/incumplidos.csv`.
- Validación realizada: el resumen devuelve 11 meses, `months_evaluated` permanece en 6, enero muestra cobertura histórica y junio mantiene el inicio del periodo oficial.

### Configuración de población objetivo
- Se agregó vista `Configuración` para seleccionar la población objetivo desde la columna `Desc_prov`.
- El filtro por defecto es `ABANCAY`, alineado a la población objetivo de la Red de Salud Abancay.
- Se agregó opción `Todos los datos` para calcular y visualizar el indicador con todas las provincias del archivo.
- El filtro se aplica al dashboard, búsqueda por DNI y descarga de incumplidos.
- El backend ahora expone `GET /api/config/options` con las provincias disponibles.
- Los registros incumplidos ahora incluyen provincia, microred, establecimiento y código RENAES para alertar al responsable del EESS.
- Validación realizada: con `ABANCAY` se obtienen 63 incumplidos; con `Todos los datos`, 138 incumplidos. La tabla del dashboard muestra la columna `Establecimiento`.

### Meta y semaforización
- Se actualizó la meta mensual por defecto del indicador a `70.7%`.
- La vista `Configuración` permite revisar y ajustar la meta del indicador.
- El dashboard semaforiza cada mes en dos estados:
  - `Cumple`: cobertura mayor o igual a la meta.
  - `No cumple`: cobertura menor a la meta.
- El backend acepta `target` en `GET /api/report/summary` y devuelve `target_coverage` y `semaphore` por mes.
- La vista `Configuración` ahora muestra criterios de evaluación basados en `Obs_Eval`: incluye `Evaluado` y excluye `No_Evaluado`.
- El cálculo del denominador ya no recalcula exclusión por peso ni edad gestacional; toma `Obs_Eval` como columna ya depurada por el archivo.
- La vista `Configuración` ahora muestra tipos de seguro incluidos: SIS, NINGUNO, SIN SEGURO, SIN_SEGURO y celdas vacías como `VACIO/SIN SEGURO`.
- Validación realizada con `ABANCAY` y meta `70.7%`: enero queda `No cumple`, febrero-marzo-abril `Cumple`, mayo-junio `No cumple`.

### Incumplidos por mes y exportación Excel
- La tabla de incumplidos del dashboard ahora se filtra por `Mes_eva`.
- Por defecto se selecciona el mes del corte del archivo; con corte `2026-05-11`, se muestra mayo 2026.
- La tabla de incumplidos ahora tiene paginación de 10 registros por página.
- Se agregó descarga Excel `GET /api/report/incumplidos.xlsx` con encabezados ordenados, autofiltro, columnas ajustadas y hoja `Incumplidos`.
- La descarga Excel acepta el parámetro `month` para exportar solo el mes seleccionado.
- Los registros incumplidos ahora incluyen `Mes_eva`, mes y año para permitir filtros mensuales.
- Validación realizada con `ABANCAY` y mayo 2026: 66 incumplidos, 7 páginas, descarga Excel OK.
### Mejora visual e identidad de salud
- Se instalo `lucide-react` para agregar iconos consistentes en navegacion, tarjetas, formularios, estados y tablas.
- Se actualizo la paleta visual con los acentos solicitados: `#E2CEFF`, `#FACEFF` y `#FFCEEB`, manteniendo superficies claras y estados clinicos verde/rojo para cumplimiento.
- Se agregaron animaciones de entrada, transiciones hover, sombras suaves y botones con icono para una experiencia mas agradable.
- Se retiro el tema oscuro base del `index.html` y se definio un fondo claro para alinear la interfaz con una plataforma de salud.
- Se redisenaron las vistas de busqueda, dashboard y configuracion con paneles claros, badges legibles, iconos por seccion y controles con foco visible.
- Validacion realizada: `npm.cmd run build` OK; navegador integrado abre busqueda y dashboard sin errores de consola.

### Ajuste de contraste de paleta
- Se reemplazo la paleta visual por `#FACEFF`, `#FFFACE` y `#CEFFFA`.
- Se redujo el uso de blanco puro usando fondos tintados, paneles con mezcla rosa/menta/amarillo y encabezados de tabla con color.
- Se mantuvieron los estados del indicador en verde y rojo para no confundir la lectura de cumplimiento.
- Validacion realizada: `npm.cmd run build` OK; busqueda y dashboard abren sin errores de consola.

### Refinamiento profesional de contraste
- Se ajusto la identidad visual para usar los colores pastel solo como acentos, evitando que dominen toda la plataforma.
- La cabecera ahora usa un gradiente profesional azul petroleo/teal con texto blanco de alto contraste.
- Los paneles volvieron a superficies blancas sobrias sobre fondo neutro, con bordes discretos y sombras controladas.
- Se normalizaron botones primarios y secundarios: primarios en teal con texto blanco, secundarios blancos con borde y hover claro.
- Se mejoro el contraste de tablas, chips, iconos y controles de formulario para que los textos sean mas legibles.
- Validacion realizada: `npm.cmd run build` OK; la vista principal abre en navegador integrado sin errores de consola.

### Limpieza de dashboard mensual
- Se elimino la seccion duplicada de tarjetas `Historial previo` / `Periodo de verificacion`, porque repetia la informacion de `Avance del indicador`.
- El dashboard ahora muestra en la tabla mensual solo meses con denominador mayor a 0.
- El selector de `Mes evaluacion` para incumplidos tambien se limita a meses con denominador mayor a 0.
- Validacion realizada: con `ABANCAY`, la tabla muestra enero-junio 2026 y oculta julio-noviembre porque estan en 0 de 0; `Historial previo` ya no aparece.

### Mes en evaluacion actual
- El dashboard identifica el mes actual de evaluacion a partir de la fecha de corte del archivo.
- Se agrego un bloque destacado dentro de `Avance del indicador` con cobertura actual, numerador, denominador y registros faltantes para alcanzar la meta.
- La fila del mes en evaluacion se resalta en la tabla mensual y reemplaza la etiqueta `Historico` / `Verificacion` por `Mes en evaluacion`.
- Validacion realizada con corte `10 de mayo de 2026`: mayo 2026 aparece como `Mes en evaluacion`, con avance `47 de 113`, cobertura `41.59%` y 33 registros faltantes para llegar a 70.7%.

### Ajustes de card e incumplidos
- El card `Meses cumplidos` ahora se calcula solo con meses evaluables hasta el mes actual de corte.
- Con corte de mayo 2026, el card muestra `3/5` porque febrero, marzo y abril cumplen; mayo sigue en evaluacion.
- En la tabla de incumplidos se retiro el codigo RENAES del detalle de establecimiento.
- Validacion realizada en dashboard: `Meses cumplidos` muestra `3/5` y ya no aparece texto `RENAES` en la tabla de incumplidos.

### Formato visual de fechas
- Se normalizo el formato de fechas en la busqueda por DNI a `dd mmm yyyy`, por ejemplo `04 may 2026`.
- El formateo se aplica a fecha de nacimiento, vacunas, controles CRED, tamizaje y ventanas normativas.
- Si una fecha viene con hora (`2026-05-04 00:00:00`), el frontend elimina la hora y muestra solo la fecha amigable.
- Validacion realizada con DNI `94635370`: ya no aparece `00:00:00` y las fechas se ven como `02 may 2026`, `05 may 2026`, etc.

### Fecha de nacimiento en incumplidos
- Los registros incumplidos ahora incluyen `fec_Nac` desde el backend.
- La tabla de `Incumplidos por mes de evaluacion` muestra la columna `Nacimiento` con formato `dd mmm yyyy`.
- La descarga Excel `incumplidos.xlsx` incluye la columna `Fecha de nacimiento`.
- Validacion realizada: la tabla muestra nacimientos como `02 may 2026` y el Excel se genera correctamente.

### Carga y activacion de nuevo Excel
- Se agrego la vista `Carga de datos` para subir un nuevo archivo `.xlsx`, validar su estructura y activarlo como fuente de datos del sistema.
- El backend ahora expone:
  - `GET /api/data/current`
  - `POST /api/data/upload-preview`
  - `POST /api/data/activate`
- La validacion revisa la hoja `Detalle_Ate`, fecha de corte en `B8`, columnas obligatorias, cantidad de registros, meses, provincias, seguros y conteo de `Obs_Eval`.
- Los archivos cargados se guardan en `backend/uploads/` y la fuente activa se registra en `backend/data_state.json`; ambos quedan ignorados por git.
- Se agrego `python-multipart` a `backend/requirements.txt` para soportar carga de archivos en FastAPI.
- Validacion realizada: `python -m compileall backend` OK y `npm.cmd run build` OK. No se pudo ejecutar import completo del backend porque el Python global no tiene dependencias backend instaladas; `pip install` con red quedo en timeout.

### Rediseño de vista de carga de datos
- Se mejoro visualmente `frontend/src/DataUploadView.jsx` manteniendo Tailwind CSS 3.
- La vista ahora tiene encabezado operativo con flujo de 3 pasos: subir archivo, validar datos y activar fuente.
- Se reemplazo el input de archivo basico por una zona de carga con borde punteado, icono y estado del archivo seleccionado.
- El resumen del archivo activo y el resultado de validacion usan tarjetas de metricas con mejor jerarquia visual.
- Validacion realizada: `npm.cmd run build` OK.

### Compactacion de vista de carga de datos
- Se redujo la altura general de `DataUploadView.jsx` ajustando padding, radios, tamanos de iconos y jerarquia tipografica.
- La zona de seleccion de Excel paso a un formato horizontal mas compacto.
- Las metricas y listas de validacion ahora usan tarjetas mas densas para evitar una pagina excesivamente extensa.
- Validacion realizada: `npm.cmd run build` OK.

### Reorganizacion en columnas de carga de datos
- Se rediseño `DataUploadView.jsx` con una fila superior para la fuente activa y dos columnas principales.
- La columna izquierda concentra seleccion del archivo, pasos del flujo y acciones.
- La columna derecha concentra el resultado de validacion, metricas y listas de resumen.
- Se eliminaron bloques grandes del diseño anterior para lograr una lectura mas ordenada.
- Validacion realizada: `npm.cmd run build` OK.

### Ajuste horizontal de tarjetas en carga de datos
- Los pasos de carga dejaron de mostrarse como filas verticales de ancho completo y ahora usan una grilla horizontal de 3 tarjetas.
- Las metricas del archivo activo y del resultado de validacion se muestran como cards independientes con `gap`, evitando bordes tipo tabla.
- Se ajustaron margenes y padding de los paneles principales para reducir espacio desperdiciado.
- Validacion realizada: `npm.cmd run build` OK.

### Tarjetas horizontales para encabezados de carga
- La seccion `Fuente de datos activa` ahora se muestra como una card dentro de la misma grilla de metricas.
- La seccion `Carga del archivo` ahora se muestra como una card junto a los tres pasos del flujo.
- Se agrego un componente local `SectionTitleCard` para unificar encabezados operativos en formato tarjeta.
- Validacion realizada: `npm.cmd run build` OK.
