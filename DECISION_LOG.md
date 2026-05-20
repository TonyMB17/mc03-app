# Registro de decisiones y cambios - MC-03 App

## 2026-05-19

### Correccion de entorno Python
- Se consolidaron los entornos virtuales del backend en `backend/.venv`.
- Se eliminaron los entornos duplicados de la raiz: `.venv` y `.venv312`.
- El entorno vigente usa Python 3.12.13 desde `backend/.venv/Scripts/python.exe`.
- Se actualizaron `README.md` y `backend/README.md` para evitar recrear entornos virtuales fuera de `backend`.
- Validacion tecnica: imports de FastAPI, pandas, SQLAlchemy, psycopg y uvicorn OK; `pip check` OK; `python -m compileall -q -x "backend[\\/]\\.venv" backend` OK; pruebas `backend.indicators.mc02.tests.test_mc02_rules`, `backend.indicators.si02.tests.test_si02_excel_contract` y `backend.indicators.si02.tests.test_si02_rules` OK con 31 pruebas y 2 omitidas.

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

### Documento general de plataforma multiindicador
- Se creo `docs/ARQUITECTURA_PLATAFORMA_INDICADORES.md` como guia madre para evolucionar el sistema MC-03 hacia una plataforma multiindicador.
- El documento define objetivo, principios de diseno, estructura backend/frontend, contrato comun de indicadores, flujo de carga Excel, documentacion por indicador, endpoints futuros y fases de desarrollo.
- Se establecio que cada indicador tendra su propio `.md` con criterios especificos de ficha tecnica.
- La recomendacion inmediata queda registrada: modularizar MC-03 como primer indicador base antes de incorporar otros indicadores.

### Fase 1 - Modularizacion inicial de MC-03
- Se creo la estructura `backend/indicators/mc03/` para aislar la logica especifica del indicador MC-03.
- Se movio la configuracion MC-03 a `backend/indicators/mc03/config.py`.
- Se movio el procesamiento MC-03 a `backend/indicators/mc03/processor.py`.
- `backend/config.py` y `backend/services.py` quedaron como fachadas de compatibilidad para mantener activos los endpoints existentes sin cambiar comportamiento.
- Se agrego `backend/indicators/registry.py` con el primer registro disponible: `mc03`.
- Se agrego `backend/indicators/mc03/README_MC03.md` y el documento especifico `docs/indicadores/MC03_PAQUETE_RECIEN_NACIDO.md`.
- Validacion realizada: `python -m compileall backend` OK, el registro de indicadores reconoce `mc03`, y `/api/report/summary?province=ABANCAY&target=70.7` mantiene mayo con denominador 113, numerador 47, cobertura 41.59 y 188 incumplidos.

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

### Documento especifico MC-02
- Se examino la ficha tecnica MC-02.01 para iniciar la fase 2 con el nuevo indicador.
- Se copio el PDF fuente a `docs/MC-02_FT_PROCESAMIENTO_GR_241025.pdf` para mantener la referencia normativa dentro del proyecto.
- Se creo `docs/indicadores/MC02_PAQUETE_INTEGRADO_MENORES_12_MESES.md` como README especifico del indicador MC-02.
- El documento registra definicion, objetivo, formula, denominador, numerador, exclusiones, componentes del paquete integrado y reglas operativas principales.
- Componentes documentados: vacunas por edad, entrega de hierro o micronutrientes, dosaje de hemoglobina y DNI emitido hasta los 30 dias de nacido.
- Pendientes para implementacion: confirmar la meta numerica, validar las tablas extraidas contra el PDF original y mapear columnas cuando se reciba el Excel operativo de MC-02.

### Analisis del Excel operativo MC-02
- Se analizo el archivo operativo `MC 02_FT MC_02 _INFANTIL.xlsx`.
- La hoja principal es `Detalle_Ate`, la fecha de corte esta en `D9`, y los encabezados estan en la fila `10`.
- El archivo revisado tiene corte `11 may 2026`, `5,789` filas y `375` columnas en `Detalle_Ate`.
- La meta operativa se identifico en las hojas resumen como `0.809`, por lo que MC-02 debe usar `80.9%` por defecto.
- Se actualizaron las columnas requeridas en `docs/indicadores/MC02_PAQUETE_INTEGRADO_MENORES_12_MESES.md`.
- Se identifico que `Estado` marca cumplimiento general, `Registros` marca poblacion evaluada y `Obs_General` contiene el estado textual `Cumple` / `No_Cumple`.
- Se identificaron marcas precalculadas por componente: CRED, neumococo, rotavirus, antipolio, pentavalente, hierro, anemia y dosaje de hemoglobina.
- Decision tecnica: la primera implementacion de MC-02 debe aprovechar las marcas precalculadas del Excel y usar las columnas de detalle para auditoria y mensajes explicativos.

### Primera vista funcional MC-02
- Se agrego el modulo `backend/indicators/mc02/` con lectura de `Detalle_Ate`, fecha de corte en `D9` y encabezados en fila `10`.
- Se copio el Excel operativo a `data_samples/MC 02_FT MC_02 _INFANTIL.xlsx`.
- MC-02 quedo registrado en `backend/indicators/registry.py`.
- La API ahora acepta `indicator=mc02` en configuracion, resumen, incumplidos, descarga y busqueda por DNI/CNV.
- Para MC-02 se usa `provincia = ABANCAY` como filtro territorial por defecto.
- Denominador operativo: `Registros = 1`; numerador operativo: `Estado = 1`; meta por defecto: `80.9%`.
- El frontend incorpora selector de indicador `MC-03` / `MC-02` y propaga el indicador activo a busqueda, dashboard, configuracion y carga de datos.
- La busqueda individual muestra componentes dinamicos del paquete, no solo vacunas MC-03.
- Validacion realizada: `python -m compileall backend` OK, `npm.cmd run build` OK, API MC-02 con `TestClient` OK, y verificacion visual local del selector MC-02 y dashboard OK.

### Normalizacion de arquitectura multiindicador
- Se leyo `docs/ARQUITECTURA_PLATAFORMA_INDICADORES.md` y se alineo la estructura inicial del proyecto con la propuesta.
- Se creo `backend/core/` con utilidades compartidas para fechas, lectura Excel y contrato base de indicadores.
- El registro de indicadores ahora usa `IndicatorDefinition.from_module(...)`, leyendo codigo, nombre, meta por defecto y provincia por defecto desde cada modulo.
- Las carpetas `backend/indicators/mc02/` y `backend/indicators/mc03/` quedaron con el mismo molde: `config.py`, `rules.py`, `schema.py`, `processor.py` y README.
- MC-02 quedo conectado a utilidades comunes de Excel y fechas, manteniendo sus reglas en `config.py` y `rules.py`.
- Se creo la estructura frontend `components/`, `indicators/`, `pages/` y `utils/`.
- Se extrajeron componentes reutilizables: `IndicatorSelector` y `MetricCard`.
- Se creo `frontend/src/indicators/registry.js` para centralizar metadatos de MC-02 y MC-03.
- Se creo `frontend/src/utils/dates.js` para estandarizar formato `dd mmm yyyy` evitando desfases por zona horaria.
- Validacion realizada: `python -m compileall backend` OK, `npm.cmd run build` OK y carga MC-02 mantiene corte `2026-05-11` como tipo `date`.

### Ajuste operativo MC-02 sin CRED ni DNI
- Se actualizo `backend/indicators/mc02/processor.py` para usar las columnas declaradas en `backend/indicators/mc02/config.py`.
- Se omitieron los bloques CRED del calculo MC-02 actual, aunque el Excel los conserva para uso futuro.
- Se omitio el criterio de DNI emitido hasta los 30 dias porque no corresponde al area salud en esta implementacion local.
- El numerador MC-02 ya no depende directamente de `Estado`; ahora se recalcula con componentes activos: neumococo, rotavirus, antipolio, pentavalente, hierro menor de 6 meses, hierro mayor de 6 meses y dosaje de hemoglobina.
- `Estado` queda como columna de referencia operativa del Excel, pero no como fuente unica del cumplimiento en la plataforma.
- La validacion identifica columnas CRED presentes como omitidas, sin exigirlas para el calculo actual.
- Se actualizo `docs/indicadores/MC02_PAQUETE_INTEGRADO_MENORES_12_MESES.md` con esta decision.
- Validacion realizada: API MC-02 OK con 12 meses, 68 incumplidos para ABANCAY y meta 80.9%; la busqueda individual muestra solo los componentes activos; `npm.cmd run build` OK.

### Configuracion formal MC-02
- Se agregaron `CODIGOS_ESTANDAR` y `REGLAS_NEGOCIO` en `backend/indicators/mc02/config.py`, siguiendo el estilo de MC-03.
- `CODIGOS_ESTANDAR` incluye codigos de neumococo, rotavirus, antipolio, pentavalente, hemoglobina, anemia, hierro, multimicronutrientes y telemedicina excluida.
- `REGLAS_NEGOCIO` centraliza meta, provincia por defecto, columna de denominador, columna de numerador operativo, columna de mes, columna de provincia, seguros incluidos y criterios de exclusion.
- Se dejo explicito que el tipo de seguro MC-02 se lee desde `DATOS_GENERALES -> Obs_Niño`.
- `backend/indicators/mc02/rules.py` ahora deriva sus constantes desde `REGLAS_NEGOCIO`, evitando duplicar configuracion.
- Validacion realizada: `python -m compileall backend` OK; el Excel MC-02 valida correctamente; opciones de configuracion reportan `Obs_Niño` como columna de seguro; el resumen ABANCAY mantiene 12 meses y 68 incumplidos.

### Revision de definicion MC-02 y entrega de hierro
- Se volvio a analizar `docs/MC-02_FT_PROCESAMIENTO_GR_241025.pdf` para precisar la definicion del indicador.
- Se confirmo que el paquete tecnico incluye vacunas basicas, entrega de hierro, dosaje de hemoglobina y DNI emitido hasta 30 dias.
- Se mantiene la decision local de omitir DNI por no corresponder al area salud.
- Se documento en `backend/indicators/mc02/README_MC02.md` que CRED queda fuera del calculo actual y se conserva solo como informacion futura/auditoria.
- Se amplio la seccion de entrega de hierro con codigos, exclusiones, reglas transversales, suplementacion preventiva de 4 meses, tratamiento de anemia, suplementacion preventiva de 6 a 11 meses y esquemas con micronutrientes.
- Se dejo indicado que la implementacion actual usa marcas precalculadas del Excel, pero que el recalculo futuro desde atenciones crudas debe convertir esas reglas en funciones por ruta.

### Exclusiones de denominador MC-02
- Se agrego en `backend/indicators/mc02/config.py` que las exclusiones se evaluan con `Peso` y `Edad_Gestacional`.
- Bajo peso se define como `Peso < 2500` y prematuridad como `Edad_Gestacional < 37`.
- Las celdas vacias de `Peso` o `Edad_Gestacional` permanecen en el denominador porque no hay evidencia suficiente para excluirlas.
- El denominador MC-02 parte de `Registros = 1`, filtra `provincia = ABANCAY`, y luego excluye solo bajo peso o prematuridad con dato conocido.
- Se dejo documentado en `backend/indicators/mc02/README_MC02.md` que `Obs_Niño` es el tipo de seguro y `provincia` debe ser `ABANCAY`.
- Validacion con Excel operativo: ABANCAY tiene 190 registros base, 13 excluidos por bajo peso/prematuridad conocida, 177 registros finales en denominador; 4 vacios de peso/edad gestacional permanecen incluidos.
- Validacion realizada: `python -m compileall backend` OK y `npm.cmd run build` OK.

### Ventanas y responsables de atencion MC-02
- Se agregaron ventanas normativas en `REGLAS_NEGOCIO["VENTANAS_ATENCION"]` para neumococo, rotavirus, antipolio, pentavalente, hierro menor de 6 meses, hierro mayor de 6 meses y dosaje de hemoglobina.
- Los motivos de incumplimiento ahora diferencian entre atencion no registrada, atencion fuera de criterio y componente aun no exigible por edad.
- Si una ventana indica que un componente aun no es exigible, ese componente se considera programado y no genera incumplimiento.
- Se ampliaron los detalles de busqueda por DNI para mostrar establecimiento de atencion, profesional, LAB, lote y ventana normativa.
- Se ampliaron los registros de incumplidos y el Excel exportado con componente observado, fecha de atencion, edad de atencion, EESS de atencion y profesional.
- El Excel MC-02 revisado no trae columnas `Prof_*` para vacunas, hierro ni hemoglobina; solo existen en CRED. Por eso los componentes activos muestran `No disponible en Excel` en profesional cuando no hay columna fuente.
- Se documento esta limitacion en `backend/indicators/mc02/README_MC02.md`.
- Validacion realizada: API resumen MC-02 OK, busqueda por DNI OK, descarga Excel de incumplidos OK y `npm.cmd run build` OK.

### Carga de archivos por indicador
- Se amplio el contrato de resumen de carga para incluir codigo/nombre de indicador, hoja, celda de corte, fila de encabezados, columnas faltantes, columnas omitidas, conteos de estado, denominador y componentes.
- MC-02 valida su Excel con `Detalle_Ate`, corte en `D9`, encabezados en fila `10` y las columnas declaradas en `backend/indicators/mc02/config.py`.
- La validacion MC-02 muestra conteos de `Estado`, `Obs_Niño`, poblacion base `Registros = 1`, exclusiones por peso/edad gestacional y componentes activos.
- La vista de carga dejo de mostrar `Obs_Eval` como etiqueta fija y ahora usa la etiqueta de validacion de cada indicador.
- La pantalla de carga muestra estructura esperada del archivo y diferencia columnas faltantes de columnas presentes que no se evaluan actualmente.

### Seguimiento MC-02 por cohorte de nacimiento
- Se confirmo que el campo mensual MC-02 es `Mes_Nac`, interpretado como cohorte de nacimiento y no como mes de atencion.
- El procesamiento MC-02 ahora calcula edad al corte con `Fec_Nac` y la fecha de corte del Excel; `Edad_Act(dia)` queda como respaldo.
- Cada componente activo puede quedar como `programado`, `pendiente_en_plazo`, `cumple` o `incumplimiento_fuera_plazo`.
- Los mensajes de busqueda e incumplidos informan proximo inicio de ventana, fecha limite o incumplimiento fuera de plazo segun corresponda.
- El dashboard mantiene numerador y denominador agrupados por `Mes_Nac`, mostrando el avance acumulado de cada cohorte hasta la fecha de corte.

### Correccion denominador MC-02 por tipo de seguro
- Se corrigio `_is_in_denominator` para aplicar tambien el filtro de `Obs_Niño`.
- Los tipos incluidos quedan como `SIS`, `NINGUNO`, `SIN SEGURO`, `SIN_SEGURO` y celda vacia.
- Para la cohorte `Mes_Nac = 2026_5` en `ABANCAY`, el conteo pasa de 40 a 34 al excluir 5 registros `ESSALUD` y 1 registro `SANIDAD`.
- El resumen de carga ahora reporta `seguros_incluidos` y `excluidos_tipo_seguro` dentro de `denominator_counts`.

### Dosis desplegables en busqueda MC-02
- Se separaron las dosis registradas de vacunas en el resultado de busqueda por DNI para MC-02.
- El backend ahora entrega `dosis` por componente para neumococo, rotavirus, antipolio y pentavalente, con fecha, edad, codigo, LAB, lote y establecimiento cuando existe.
- El frontend mantiene la tarjeta minimalista con estado del componente y agrega un detalle desplegable para revisar las dosis sin sobrecargar la pantalla.
- Esta separacion aclara casos donde el componente agregado esta pendiente o fuera de plazo aunque una o mas dosis ya se hayan registrado.

### Validacion especifica de dosis de vacunas MC-02
- Se agrego evaluacion por dosis para vacunas MC-02 usando las reglas de ventana ya configuradas.
- Cada dosis puede quedar como `registrada`, `no_registrada`, `fuera_plazo` o `no_requerida`.
- Rotavirus valida edad maxima de 240 dias; si una dosis se aplica despues de ese limite, el componente queda como `incumplimiento_fuera_plazo`.
- Para vacunas con dosis sucesivas se valida intervalo minimo de 28 dias y maximo de 70 dias cuando la ficha lo define.
- Se verifico el caso `94350201`: rotavirus tiene primera dosis valida y segunda dosis a los 243 dias, por lo que se marca la segunda dosis como `fuera_plazo` y el componente como `incumplimiento_fuera_plazo`.
- Se corrigio la prioridad visual para casos completados antes de exigibilidad: el caso `94389087` ahora muestra rotavirus como `cumple` porque tiene dos dosis validas, aunque por edad aun siga dentro de ventana.
- Se ajusto nuevamente el caso `94389087`: pentavalente queda como `incumplimiento_fuera_plazo` porque la tercera dosis fue registrada y se audita contra la ventana activada por la segunda dosis; su ventana valida fue del 17 feb 2026 al 31 mar 2026 y la aplicacion fue a los 92 dias de intervalo.
- En busqueda por DNI se oculta el texto de ventana cuando el componente ya cumple; para observados se renombra como servicio segun edad actual.
- Se corrigio antipolio para usar el mismo esquema de edad que pentavalente: 1 dosis desde 120 dias, 2 dosis desde 190 dias y 3 dosis desde 260 dias.
- En el detalle de dosis de busqueda, las dosis validas ya no muestran ventana ni motivo; solo las dosis observadas muestran el detalle de incumplimiento.

### Reorganizacion backend MC-02
- Se redujo `backend/indicators/mc02/processor.py` para que actue como orquestador de carga, validacion, dashboard y busqueda.
- Se creo `backend/indicators/mc02/denominator.py` para separar denominador, seguros incluidos y exclusiones.
- Se creo `backend/indicators/mc02/vaccines.py` para concentrar componentes activos, dosis, ventanas e intervalos.
- Se creo `backend/indicators/mc02/utils.py` para conversiones comunes de fechas, numeros, textos, flags y meses.
- Se agregaron fronteras `iron.py`, `hemoglobin.py` y `messages.py` para futuras separaciones de hierro, hemoglobina y mensajes.
- Validacion posterior al refactor: mayo 2026 mantiene denominador 34; el caso `94389087` mantiene antipolio y pentavalente como `incumplimiento_fuera_plazo` por tercera dosis fuera de ventana.

### Ajuste visual de dosaje de hemoglobina MC-02
- En busqueda nominal, el componente `hemoglobina` ya no muestra `Dosis registradas` porque la ficha tecnica exige un dosaje entre 170 y 209 dias.
- La tarjeta de hemoglobina ahora muestra fecha de dosaje, edad al dosaje y ventana valida del dosaje.
- El backend calcula `edad_atencion_dias` desde fecha de nacimiento y fecha de atencion cuando el campo de edad no esta disponible.
- Las tarjetas de componentes que ya cumplen ya no muestran el mensaje inferior para reducir sobrecarga visual.
- Validacion realizada con DNI `94429279`: dosaje `04 may 2026`, edad al dosaje `189 dias`, estado `cumple`.
- Validacion tecnica: `python -m unittest indicators.mc02.tests.test_mc02_rules` OK y `npm.cmd run build` OK.

### Compactacion de hemoglobina cumplida MC-02
- Si el componente `hemoglobina` cumple, la busqueda nominal ya no muestra la caja inferior con fecha, edad y ventana para evitar duplicar informacion.
- La ventana valida del dosaje queda visible solo cuando el componente no cumple o requiere seguimiento.
- Validacion realizada: `npm.cmd run build` OK.

### Personalizacion de tarjetas de hierro MC-02
- El backend MC-02 ahora devuelve `entregas` para `hierro_menor_6m` y `hierro_mayor_6m`, separadas de `dosis` de vacunas.
- Las entregas incluyen fecha, edad de atencion, codigo, LAB, lote, intervalo cuando existe, EESS y tipo/ruta: preventiva 4 meses, preventiva 6 a 11 meses o tratamiento de anemia.
- La busqueda nominal ya no muestra `Dosis registradas` para hierro; muestra `Entregas registradas`, fecha/edad de entrega, tipo de entrega y resultado operativo del Excel.
- Para no sobrecargar la vista, el detalle desplegable de entregas solo aparece cuando hay multiples entregas o cuando el componente necesita seguimiento.
- Validacion realizada con DNI `94429279`: hierro mayor tiene 1 entrega preventiva el `04 may 2026` a los `189 dias`; hierro menor no registra entrega y queda fuera de plazo.
- Validacion tecnica: `python -m unittest indicators.mc02.tests.test_mc02_rules` OK, `python -m compileall indicators\mc02` OK y `npm.cmd run build` OK.

### Fallback visual de entregas de hierro MC-02
- Se ajusto `SearchDNI.jsx` para que, si una tarjeta de hierro tiene fecha de entrega pero el arreglo `entregas` no llega al frontend, la vista cuente esa atencion como 1 entrega registrada.
- Esto evita inconsistencias visuales durante recargas parciales del backend o respuestas antiguas, donde el cumplimiento y la fecha ya estaban disponibles pero el nuevo campo `entregas` aun no.
- Validacion backend con DNI `94429279`: `hierro_mayor_6m` devuelve 1 entrega preventiva, fecha `04 may 2026`, edad `189 dias`.
- Validacion realizada: `npm.cmd run build` OK.

### Correccion alerta anemia y tipo de hierro MC-02
- Se corrigio `backend/indicators/mc02/iron.py` para que `Obs_Anemia = 1` por si solo no genere alerta clinica de anemia.
- La alerta de anemia ahora requiere evidencia clinica: codigo/diagnostico `D509`/`D649`, fecha de anemia o fecha de tratamiento de anemia.
- Se ajusto el fallback visual de `SearchDNI.jsx` para que hierro mayor sin alerta de anemia se muestre como `Preventiva 6 a 11 meses`, evitando el texto ambiguo `Preventiva o tratamiento`.
- Se agregaron pruebas para el caso `Obs_Anemia = 1` sin diagnostico, para diagnostico real `D509`, y para entrega preventiva de hierro mayor.
- Validacion con DNI `94429279`: `clinical_alerts` queda vacio y `hierro_mayor_6m` muestra entrega `Preventiva 6 a 11 meses`.
- Validacion tecnica: `python -m unittest indicators.mc02.tests.test_mc02_rules` OK con 16 pruebas y `npm.cmd run build` OK.

### Fuente formal de alerta de anemia MC-02
- Se ajusto la alerta clinica de anemia para usar solo el bloque `Dx_ANEMIA`: columnas `Fec_Anemia` y `Dx_Anemia`.
- `Obs_Anemia` queda fuera de la alerta porque el Excel lo usa como resultado operativo para omitir tratamiento cuando no existe diagnostico de anemia.
- Las columnas de tratamiento (`CIE_Anemia_1Hier`, `fecha_1Hier`) tampoco disparan la alerta por si solas; se consideran trazabilidad de tratamiento, no fuente primaria de diagnostico.
- Se agregaron pruebas para confirmar que `CIE_Anemia_1Hier` sin `Dx_Anemia` no alerta, que `Dx_Anemia = D509` si alerta y que `Fec_Anemia` si alerta.
- Validacion con DNI `94429279`: `clinical_alerts` queda vacio.
- Validacion tecnica: `python -m unittest indicators.mc02.tests.test_mc02_rules` OK con 18 pruebas y `npm.cmd run build` OK.

### Nota de configuracion sobre Obs_Anemia
- Se agrego en `backend/indicators/mc02/config.py` la nota `NOTA_OBS_ANEMIA` dentro de `REGLAS_NEGOCIO["ALERTA_ANEMIA"]`.
- La nota deja explicito que `Obs_Anemia` se refiere al resultado operativo del tratamiento solo cuando existe diagnostico de anemia, y que por si sola no debe generar alerta clinica ni penalizar cumplimiento.
- Validacion realizada: `python -m compileall indicators\mc02` OK y `python -m unittest indicators.mc02.tests.test_mc02_rules` OK.

### Validacion nominal y omisos por cohorte MC-02
- Se valido el Excel operativo `data_samples/MC 02_FT MC_02 _INFANTIL.xlsx` con fecha de corte `2026-05-11` para la provincia `ABANCAY`.
- DNIs revisados explicitamente: `94424954`, `94429011`, `94405414` y `94429279`; todos coinciden entre busqueda nominal y la lista de incumplidos por `Mes_Nac`.
- Se agrego una muestra aleatoria reproducible de 10 DNIs del denominador y luego una validacion global de los 1222 registros del denominador.
- Resultado global: 1022 completos, 200 incumplidos, 200 omisos en dashboard, suma mensual de numerador 1022 y 0 inconsistencias.
- Se optimizo `evaluate_package` para reutilizar el cumplimiento ya calculado en los detalles de componentes.
- Se optimizo `build_report_summary` para evaluar cada fila una sola vez y usar el mismo paquete para numerador y omisos.
- Se alineo `REGLAS_NEGOCIO["ALERTA_ANEMIA"]` con la decision final: diagnostico solo desde `Dx_Anemia` y fecha solo desde `Fec_Anemia`; `Obs_Anemia` queda como resultado operativo de tratamiento cuando ya existe diagnostico.

### Reorganizacion interna MC-02 por componentes
- Se separo el catalogo de componentes activos en `backend/indicators/mc02/components/`.
- `components/vaccines.py` contiene vacunas, dosis y ventanas por edad.
- `components/iron.py` contiene hierro menor/mayor, entregas preventivas, tratamiento de anemia e intervalos.
- `components/hemoglobin.py` contiene el dosaje de hemoglobina y su ventana valida de 170 a 209 dias.
- Se movieron los codigos estandar a `codes.py` y el contrato del Excel a `excel_schema.py`.
- `config.py` queda como configuracion general y ensamblador de reglas, sin cargar el detalle de vacunas, suplementacion o dosaje.
- Se agrego `engine/component.py` como motor comun de evaluacion y `engine/package.py` como fachada del paquete completo.
- `messages.py` ahora construye mensajes visibles de cumplimiento, pendiente, programado y fuera de plazo.
- `vaccines.py`, `hemoglobin.py` y `schema.py` quedan como fachadas de compatibilidad temporal para imports existentes.
- Se actualizo `MC02_sistema_seguimiento_Abancay_Codex.md` con la nueva estructura y reglas de organizacion.

### Correccion conteo de dosis registradas MC-02
- Se corrigio la busqueda nominal para no contar dosis requeridas o evaluadas como dosis registradas.
- El backend ahora devuelve `dosis_registradas` por componente, calculado solo con dosis que tienen fecha o codigo en el Excel.
- El detalle `dosis` puede seguir incluyendo dosis requeridas sin registro para explicar el incumplimiento, pero la tarjeta muestra el conteo real registrado.
- En el frontend, el resumen del desplegable distingue entre dosis registradas y dosis requeridas sin registro.
- Validacion con DNI `94405414`: neumococo `0/2`, rotavirus `0/1`, antipolio `1/2`, pentavalente `1/2`, donde el primer valor es dosis registrada y el segundo dosis evaluada/requerida.
- Validacion global ABANCAY: 1222 registros del denominador, 0 diferencias entre `dosis_registradas` y las celdas reales de fecha/codigo del Excel.
- Ajuste de compatibilidad API: `codigo` vuelve a ser cadena vacia cuando no existe dato en Excel, porque el schema `VacunaRecord.codigo` exige `str`.
- Se agregaron al schema de respuesta los campos `dosis_registradas`, `dosis_evaluadas`, `entregas` y `tipo_atencion`.

### Extraccion de hierro menor de 6 meses desde bloque completo
- Se corrigio el componente `hierro_menor_6m` para no depender solo de `fecha_1prev` / `CIE_Hierro_1prev`.
- La atencion representativa ahora se extrae de todo el bloque `SUPLEMENTACION_HIERRO_MENOR_6_MESES_*`: `fecha_1prev` a `fecha_5prev`, sus edades, codigos, LAB, lote y EESS.
- Para hierro de 4 meses se prioriza una entrega registrada entre 110 y 130 dias de edad, segun ficha tecnica.
- Si una entrega valida aparece en una columna posterior, por ejemplo `fecha_4prev`, el componente puede cumplir y la tarjeta muestra esa entrega como fecha/codigo/edad/EESS principal.
- Validacion con DNI `94332765`: entrega en `fecha_4prev`, edad `122`, codigo `99199.17`, EESS `CASINCHIHUA`; el componente queda `cumple`.
- Validacion adicional: `94429011` muestra entrega en `fecha_4prev`, edad `123`, codigo `99199.17`, EESS `TAMBURCO`.
- Validacion global ABANCAY posterior al ajuste: 1222 registros en denominador, 1023 completos, 199 omisos, 0 inconsistencias entre busqueda nominal y dashboard.

### Ajuste rotavirus e hierro mayor no exigible MC-02
- Se comparo el DNI `94424954` contra el Excel operativo: `obs_rot1 = 0`, sin dosis de rotavirus, edad al corte `200` dias.
- Se ajusto la ventana de rotavirus a `0-189` no exigible, `190-240` con 1 dosis requerida, y `241-364` con 2 dosis acumuladas; la primera dosis mantiene edad maxima valida de `210` dias.
- Para `94424954`, rotavirus queda `pendiente_en_plazo`, `dosis_registradas = 0`, `dosis_evaluadas = 1`, y ya no aparece como programado/cumplido.
- Se corrigio el motor para que un componente no exigible sin fecha/codigo/entrega trazable no se pinte como `cumple` solo por flag operativo; queda `programado` y sigue cumpliendo para paquete parcial.
- Para `94424954`, `hierro_mayor_6m` queda `programado`, sin fecha ni entregas, porque tiene 200 dias y aun no es exigible.
- Se agregaron pruebas para rotavirus a los 189, 200 y 211 dias, y para hierro mayor no exigible sin trazabilidad.

### Dosaje de hemoglobina con trazabilidad obligatoria MC-02
- Se comparo el DNI `94424954`: `Obs_dh1 = 1`, pero `fecha_1DH`, `Lab_1DH`, `edad_1DH`, `CIE_DH_1DH`, `Lote_Pag_Reg_1DH` y `EESS_Ate_1DH` estan vacios.
- El cumplimiento de hemoglobina ahora se confirma desde las columnas trazables del dosaje, no solo desde `Obs_dh1`.
- Si el dosaje ya es exigible, debe existir atencion trazable y valida entre 170 y 209 dias para cumplir.
- Si el dosaje aun no es exigible y no hay atencion trazable, el componente queda `programado`; este es el caso de `94424954`, con 200 dias al corte.
- Se agregaron pruebas para `Obs_dh1 = 1` sin trazabilidad cuando el dosaje ya es exigible y para dosaje trazable valido sin depender del flag operativo.

### Ventana visible para dosaje programado MC-02
- En busqueda nominal, si hemoglobina queda `programado`, la tarjeta muestra la ventana programada del dosaje aunque el componente cumpla para paquete parcial.
- Esto permite que el personal vea el periodo exacto de atencion pendiente sin confundirlo con una atencion ya registrada.
- Para `94424954`, la vista debe mostrar la ventana `11 abr 2026 - 20 may 2026` y mantener fecha/codigo de dosaje vacios.

### Componentes observados multiples en dashboard MC-02
- En `Incumplidos por cohorte de nacimiento`, cada registro ahora expone todos los componentes no cumplidos en `components_observed`.
- El campo `component` se mantiene como compatibilidad con la primera clave tecnica, y la tabla/Excel consumen el nuevo resumen legible.
- El motivo de incumplimiento se arma por componente con el formato `Nombre del componente: motivo`, separado por saltos de linea para que la tabla y el Excel descargable sean revisables.
- El Excel `incumplidos` usa la columna `Componentes observados` y aplica ajuste de texto en componentes, alertas y motivo.
- Validacion de muestra ABANCAY: DNI `94247123` muestra neumococo, rotavirus, antipolio, pentavalente, hierro menor, hierro mayor y hemoglobina como componentes observados.
- Validacion tecnica: `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 26 pruebas y `npm run build` OK.

### Optimizacion de carga Excel MC-02
- Se agrego lectura selectiva de columnas en `backend/core/excel.py` mediante `usecols`.
- `backend/indicators/mc02/excel_loader.py` ahora construye una tabla operativa solo con columnas usadas por MC-02: datos nominales, denominador, resumen, anemia, vacunas, hierro y hemoglobina.
- El `upload-preview` de MC-02 prepara una tabla procesada `.pkl` y elimina el `.xlsx` temporal, por lo que `activate` ya no reabre ni revalida el Excel completo.
- La activacion puede recibir un `prepared_bundle` con dataframe, fecha de corte y resumen validado, manteniendo el nombre original del archivo para la vista.
- Validacion con Excel real: 5789 filas, 375 columnas disponibles, 230 columnas operativas cargadas, 0 faltantes, corte `2026-05-11`.
- Validacion funcional ABANCAY: 199 omisos y numerador total 1023, consistente con la regla actual.
- Validacion tecnica: `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 27 pruebas y `python -m compileall backend/core backend/indicators/mc02 backend/main.py` OK.

### Fase 1 PostgreSQL
- Se documento la ruta completa de migracion en `docs/README_PostgreSQL_Migration.md`.
- Se agregaron dependencias para persistencia: SQLAlchemy, Alembic, psycopg y python-dotenv.
- Se creo `backend/.env.example` con `DATABASE_URL` local para PostgreSQL.
- Se agrego el paquete `backend/db/` con base declarativa, engine, `SessionLocal` y dependencia `get_db`.
- Se configuro Alembic en `backend/alembic.ini` y `backend/alembic/` para usar la metadata de SQLAlchemy.
- Se agrego `backend/processed_uploads/`, `.env` y `backend/.env` al `.gitignore`.
- Nota tecnica: en este entorno se uso `psycopg[binary]==3.3.4` porque Python 3.14 no tenia wheel disponible para `3.2.3`.
- Validacion tecnica: instalacion con `pip install -r backend/requirements.txt` OK; imports de DB OK; `alembic -c alembic.ini heads` OK; `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 27 pruebas.

### Fase 2 PostgreSQL
- Se eligio `indicator_tracking` como nombre de base de datos en ingles para no amarrar el proyecto a MC-02 o MC-03.
- Se actualizo `DATABASE_URL` de ejemplo, configuracion Alembic y `backend/.env` local al nombre definido.
- Se crearon modelos SQLAlchemy generales para persistencia multiindicador: `IndicatorUpload`, `IndicatorActiveUpload`, `IndicatorRecord`, `ComponentResult`, `DashboardSummary` e `IndicatorOmission`.
- Se agrego la migracion inicial `backend/alembic/versions/0001_indicator_storage.py` con tablas, llaves foraneas, restricciones unicas e indices para DNI/CNV, provincia, periodo, componentes y estados.
- La documentacion de migracion quedo actualizada con comandos `createdb -U postgres indicator_tracking` y `alembic -c alembic.ini upgrade head`.
- Validacion tecnica: metadata SQLAlchemy registra 6 tablas; `alembic -c alembic.ini upgrade head --sql` genera SQL correctamente; `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 27 pruebas.

### Renombrado de base PostgreSQL
- Se adopto `indicator_tracking` como nombre en ingles para la base de datos.
- Se actualizaron `backend/.env.example`, `backend/db/session.py`, `backend/alembic.ini`, `backend/README.md` y `docs/README_PostgreSQL_Migration.md`.
- Se creo la base local `indicator_tracking` usando `psycopg`, porque `createdb`/`psql` no estaban disponibles en el PATH del entorno.
- Se aplico la migracion inicial con `alembic -c alembic.ini upgrade head` y quedaron creadas las tablas generales de persistencia.

### Fase 3 PostgreSQL MC-02
- Se agrego `backend/indicators/mc02/storage.py` como adaptador de persistencia para cargas MC-02 ya procesadas.
- La activacion de una carga MC-02 ahora guarda en PostgreSQL registros nominales, resultados por componente, resumenes de dashboard, omisos y referencia activa.
- Las lecturas actuales de busqueda por DNI, dashboard y exportacion siguen usando memoria; la migracion de lecturas queda para Fase 4 y Fase 5.
- Validacion local de persistencia MC-02: 5,789 registros, 40,523 resultados de componentes, 117 resumenes de dashboard y 728 omisos en `indicator_tracking`.
- Validacion tecnica: `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 27 pruebas; `python -m compileall backend/db backend/indicators/mc02 backend/main.py` OK.

### Fase 4 PostgreSQL MC-02
- Se agrego busqueda nominal desde carga activa PostgreSQL con `search_active_by_dni`.
- El endpoint `GET /api/search/dni/{dni}` usa PostgreSQL primero cuando `indicator=mc02` y existe carga activa; si aun no existe carga activa en BD o la BD no esta disponible en esta etapa, conserva fallback al dataframe.
- La respuesta desde BD reconstruye el mismo contrato de `SearchDNIResult`, incluyendo datos personales, componentes, alertas clinicas, tamizaje de compatibilidad y estado de paquete.
- Si existe carga activa en BD y el DNI/CNV no se encuentra en esa carga y provincia, se devuelve `404` para no mezclar resultados de memoria con otra version.
- Validacion con DNIs `94424954`, `94429011`, `94405414`, `94429279` y `94332765`: BD y dataframe coinciden en estado, cumplimiento, codigo, fecha y edad de atencion de todos los componentes.
- Validacion de endpoint directa con DNI `94405414`: neumococo `0` dosis registradas, rotavirus `0` dosis registradas y paquete incompleto.
- Validacion tecnica: `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 29 pruebas; `python -m compileall backend/db backend/indicators/mc02 backend/main.py` OK.

### Fase 5 PostgreSQL MC-02
- Se agrego `build_active_report_summary` para reconstruir el dashboard desde `dashboard_summaries` e `indicator_omissions`.
- Los endpoints `summary`, `omisos`, `incumplidos`, CSV y Excel descargable usan PostgreSQL primero para `indicator=mc02` cuando existe carga activa.
- Se centralizo la resolucion de reportes en `_report_summary_for_request`, manteniendo fallback al dataframe cuando aun no existe carga activa en BD o la BD no esta disponible.
- La cobertura mensual queda precalculada en BD y el semaforo/cumplimiento se recalcula segun la meta solicitada por el usuario.
- Validacion ABANCAY con metas 80.9 y 70.7: PostgreSQL y dataframe coinciden en 13 cohortes, 199 incumplidos, denominador, numerador, cobertura y semaforo.
- Validacion directa de endpoints: `api_report_summary` devuelve 13 cohortes, 9 cohortes cumplidas con meta 80.9, 199 omisos y corte `2026-05-11`; `api_report_incumplidos_csv` y `api_report_incumplidos_xlsx` responden con los media types esperados.
- Validacion tecnica: `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 30 pruebas; `python -m py_compile backend/main.py backend/indicators/mc02/storage.py backend/indicators/mc02/processor.py backend/indicators/mc02/__init__.py` OK.

### Fase 6 PostgreSQL MC-02
- Se formalizo la activacion versionada de MC-02 con estados `processing`, `validated`, `active`, `failed` y `superseded`.
- `persist_active_upload` crea primero el registro de carga en estado `processing`; despues de procesar registros, componentes, dashboard y omisos pasa por `validated` y finalmente activa la version.
- Si ocurre un error en procesamiento o escritura, la carga queda marcada como `failed` con `error_message` y la referencia `indicator_active_uploads` no cambia.
- Al activar una nueva version, la version previa pasa a `superseded`.
- `api_data_activate` ahora persiste MC-02 en PostgreSQL antes de actualizar la version activa en memoria, evitando que el usuario vea una version que no quedo registrada en BD.
- El estado `pending` se mantiene en `app.state.pending_uploads` entre `upload-preview` y `activate`.
- Validacion local de BD: `indicator_uploads` mantiene la carga activa existente en estado `active` y `indicator_active_uploads` apunta a esa misma version.
- Validacion tecnica: `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 31 pruebas; `python -m py_compile backend/main.py backend/indicators/mc02/storage.py backend/indicators/mc02/processor.py backend/indicators/mc02/__init__.py` OK.

### Fase 7 PostgreSQL MC-02
- Se movio la activacion pesada de MC-02 a `FastAPI BackgroundTasks`.
- `POST /api/data/activate?indicator=mc02` devuelve inmediatamente `processing=true`, `job_id`, `job_status` y `message` cuando la carga queda en segundo plano.
- Se agrego `GET /api/data/activation/{job_id}` para consultar el estado de activacion.
- La vista `DataUploadView.jsx` hace polling cada 2 segundos hasta que el trabajo queda `activated` o `failed`.
- Mientras el trabajo corre, la version activa anterior sigue disponible para busqueda, dashboard y descargas.
- Los indicadores sin persister, como MC-03 en esta etapa, mantienen activacion sincrona.
- Validacion directa del endpoint de estado: trabajo `queued` responde `processing=True`, `job_id` y mensaje de cola.
- Validacion tecnica: `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 31 pruebas; `python -m py_compile backend/main.py backend/schemas.py backend/indicators/mc02/storage.py` OK; `npm run build` OK.

### Reorganizacion MC-03
- Se refactorizo `backend/indicators/mc03/processor.py` para dejarlo como orquestador de carga, validacion, filtros, resumen y busqueda por DNI.
- La logica especializada del indicador MC-03 quedo separada en `denominator.py`, `vaccines.py`, `cred.py`, `screening.py`, `messages.py` y `utils.py`, siguiendo `MC03_sistema_seguimiento_Abancay_Codex.md`.
- `config.py` ahora centraliza constantes publicas del indicador, parametros de Excel, meses de evaluacion y columnas obligatorias.
- `rules.py` se actualizo como punto de entrada de reglas de negocio, reexportando evaluadores por componente.
- Se eliminaron los markdown redundantes `README_MC03.md`, `logic_rules.md` y `docs/indicadores/MC03_PAQUETE_RECIEN_NACIDO.md` porque quedaron reemplazados por `MC03_sistema_seguimiento_Abancay_Codex.md`.
- Validacion funcional con Excel real MC-03 ABANCAY: 2553 filas, corte `2026-05-11`, resumen mensual y busquedas de control conservan el mismo resultado previo a la reorganizacion.
- Validacion tecnica: `python -m py_compile backend/indicators/mc03/*.py` OK.

### Fase 8 PostgreSQL MC-03
- Se agrego `backend/indicators/mc03/storage.py` como adaptador de persistencia para cargas MC-03.
- El modulo MC-03 ahora expone funciones de BD compatibles con el flujo comun: `persist_active_upload`, `active_upload_id`, `search_active_by_dni` y `build_active_report_summary`.
- Al activar una carga MC-03, el backend la procesa en segundo plano y persiste registros nominales, componentes, resumenes de dashboard, omisos y referencia activa.
- Las consultas de busqueda por DNI, dashboard, incumplidos y exportaciones usan PostgreSQL primero para `indicator=mc03` cuando existe carga activa; si no existe, mantienen fallback al dataframe.
- Se valido la persistencia con el Excel MC-03 real: 2,553 registros, 15,318 resultados de componentes, 99 resumenes y 788 omisos totales.
- Validacion ABANCAY: PostgreSQL y dataframe coinciden en resumen mensual, 188 omisos, `months_met = 0` y `committed = False`.
- Validacion directa de funciones API: `api_report_summary`, `api_search_dni` y `api_data_current` responden correctamente para `indicator=mc03`.
- Nota tecnica: no se pudo usar `fastapi.testclient.TestClient` porque falta la dependencia `httpx` en el entorno; se verifico la misma logica llamando las funciones de endpoint directamente.
- Validacion tecnica: `python -m py_compile backend/indicators/mc03/storage.py backend/indicators/mc03/__init__.py backend/indicators/mc03/processor.py backend/main.py` OK; `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 31 pruebas.

### Fase 9 Seguridad y roles
- Se agrego `backend/security.py` con autenticacion por token Bearer firmado y usuarios configurables por `AUTH_USERS_JSON`.
- Se agregaron los endpoints `POST /api/auth/login` y `GET /api/auth/me`.
- Se protegieron endpoints por rol:
  - `clinical`: busqueda por DNI/CNV.
  - `supervisor`: busqueda, dashboard y descargas.
  - `admin`: busqueda, dashboard, descargas, configuracion y carga/activacion de datos.
- `AUTH_ENABLED=false` mantiene el modo desarrollo como administrador local; `AUTH_ENABLED=true` exige token.
- El frontend ahora usa `frontend/src/api/client.js`, pantalla de login, token en `localStorage`, navegacion condicionada por permisos y descargas autenticadas.
- Se documento la configuracion en `backend/.env.example` y `backend/README.md`.
- Validacion HTTP real con servidor temporal: sin token `401`; usuario clinico puede buscar y recibe `403` en dashboard; supervisor ve dashboard y recibe `403` en carga; admin accede a carga.
- Validacion tecnica: `python -m py_compile backend/security.py backend/schemas.py backend/main.py` OK; pruebas de token/roles OK; `python -m unittest backend.indicators.mc02.tests.test_mc02_rules` OK con 31 pruebas; `npm run build` OK.

### Fase 10 Auditoria y respaldo
- Se agrego la tabla `indicator_audit_events` con la migracion `0002_indicator_audit_events`.
- Se agrego `backend/db/audit.py` para registrar eventos y consultar historial de cargas.
- `upload-preview` calcula hash SHA-256 del archivo original y guarda actor de subida en la carga pendiente.
- La activacion pasa `uploaded_by`, `activated_by`, rol y hash a los persisters.
- MC-02 y MC-03 registran eventos `upload_processing_started`, `upload_activated` y `upload_failed`.
- Se agregaron endpoints admin: `GET /api/data/uploads` y `GET /api/audit/events`.
- La vista de carga muestra historial de cargas con estado, archivo, usuario que subio, usuario que activo, corte, registros y hash.
- Se agrego `backend/db/backup.py` para respaldos manuales con `pg_dump`; `backend/backups/` queda fuera de git.
- Se documentaron `BACKUP_RETENTION_DAYS` y `UPLOAD_RETENTION_DAYS`.
- Validacion local MC-03: nueva carga activa con hash y actor `admin`, historial activo OK, eventos de auditoria registrados y resumen ABANCAY mantiene 188 omisos.

### Cierre previo a nuevo indicador
- Se actualizo la documentacion de arquitectura y migracion PostgreSQL para reflejar que las fases 1 a 10 ya quedaron completadas para la base MC-02/MC-03.
- `backend/db/backup.py` ahora permite `PG_DUMP_PATH` y aplica retencion automatica de respaldos `.dump` segun `BACKUP_RETENTION_DAYS`.
- Se agrego `httpx` a dependencias backend para habilitar pruebas HTTP con `fastapi.testclient.TestClient`.

### Analisis inicial SI-02
- Se reviso la ficha tecnica SI-02 y los cuatro Excel asociados a `SI-02.01`, `SI-02.02`, `SI-02.03` y `SI-02.04`.
- Decision recomendada: implementar `SI-02` como un solo indicador publico con cuatro subindicadores internos, porque el cumplimiento del compromiso depende del conjunto, pero cada archivo tiene reglas, columnas y denominador propios.
- Se creo `backend/indicators/si02/SI02_sistema_seguimiento_Abancay_Codex.md` con contrato de archivos, reglas preliminares, columnas por subindicador, preguntas abiertas y ruta de implementacion.

### Decisiones SI-02 confirmadas
- `TA` afecta cumplimiento en `si02_01`.
- En `si02_03` y `si02_04`, `TA` es componente obligatorio y debe mostrarse en dashboard.
- En `si02_02`, `TA` queda como dato observado porque el resumen del subindicador no lo incluye como componente de cumplimiento.
- La carga semanal SI-02 llega con los cuatro Excel juntos; una version activa debe exigir paquete completo.
- El dashboard SI-02 debe tener vista global del compromiso y tabs/segmentador por subindicador.
- El sistema debe recalcular cumplimiento desde columnas de atencion desde la primera version; los estados del Excel quedan para conciliacion y pruebas.

### Fase 1 SI-02 - Contrato multiparchivo
- Se creo el paquete `backend/indicators/si02` con `config.py`, `excel_loader.py` y pruebas de contrato.
- `excel_loader.py` detecta automaticamente a que subindicador corresponde cada Excel, valida `Detalle_Ate`, fila de encabezado, celda de corte y columnas obligatorias.
- Se implemento `prepare_upload_package` / `validate_upload_package` para exigir los cuatro archivos `si02_01`, `si02_02`, `si02_03` y `si02_04`.
- La lectura usa solo columnas operativas y conserva los estados del Excel solo para conciliacion.
- Validacion con Excel reales: 4,895 filas en `si02_01`, 396 en `si02_02`, 225 en `si02_03`, 5,156 en `si02_04`; paquete total 10,672 filas.
- `python -m unittest backend.indicators.si02.tests.test_si02_excel_contract` OK con 5 pruebas.

### Fase 2 SI-02 - Evaluadores propios
- Se agregaron `evaluator.py`, `processor.py` y `utils.py` para recalcular SI-02 desde columnas de atencion.
- `TA` queda como componente obligatorio en `si02_01`, `si02_03` y `si02_04`; en `si02_02` queda observado sin afectar cumplimiento.
- Se implemento resumen inicial por subindicador/provincia/mes y busqueda por DNI/CNV sobre el paquete multiparchivo.
- Los componentes comparables contra el Excel quedan reconciliados con 0 diferencias: `si02_01` hierro/dosaje/TA; `si02_02` DH/hierro; `si02_03` hierro tratamiento, controles DH y TA; `si02_04` hierro preventivo, controles DH y TA.
- Conteo recalculado con Excel reales: `si02_01` 1,503 cumplen de 4,895; `si02_02` 93 de 396; `si02_03` 65 de 225; `si02_04` 1,281 de 5,156.
- Regla conciliada de `si02_04.hierro_preventivo`: intervalos segun codigo de entrega actual (`99199.17` 25-70 dias, `99199.19` 25-35 dias) y la sexta columna actua como cierre de esquema sin invalidar por su propio intervalo.
- Validacion tecnica: `python -m unittest backend.indicators.si02.tests.test_si02_excel_contract backend.indicators.si02.tests.test_si02_rules` OK con 8 pruebas; `python -m py_compile` OK sobre el paquete SI-02.

### Fase 3 SI-02 - Persistencia PostgreSQL
- Se agrego `backend/indicators/si02/storage.py` como adaptador de persistencia para paquete multiparchivo SI-02.
- Una carga SI-02 se persiste como una sola version activa, pero conserva `subindicator_code` en registros, componentes, resumenes, omisos y payloads.
- Los resultados de componentes se guardan con clave namespaced, por ejemplo `si02_04.hierro_preventivo`, para evitar ambiguedades entre subindicadores.
- Se agregaron consultas activas desde PostgreSQL: `active_upload_id`, `search_active_by_dni` y `build_active_report_summary`.
- La activacion registra auditoria con `upload_processing_started`, `upload_activated` y `upload_failed`.
- Validacion local con los cuatro Excel reales: 10,672 registros nominales, 49,797 resultados de componentes, 390 resumenes de dashboard y 7,730 incumplidos persistidos.
- Validacion ABANCAY desde PostgreSQL: 4 subindicadores reconstruidos, 2,589 incumplidos y busqueda por DNI `94061040` encontrada correctamente.
- `test_si02_storage.py` queda protegido por `RUN_SI02_DB_TESTS=1` porque crea una nueva version activa en PostgreSQL.
- Validacion tecnica: `python -m unittest backend.indicators.si02.tests.test_si02_excel_contract backend.indicators.si02.tests.test_si02_rules backend.indicators.si02.tests.test_si02_storage` OK con 8 pruebas y 1 omitida; `python -m py_compile` OK sobre el paquete SI-02.

### Fase 4 SI-02 - Carga multiparchivo y seleccion en la app
- Se registro `SI-02` en `backend/indicators/registry.py` y en `frontend/src/indicators/registry.js` como indicador publico con carga de paquete de 4 archivos.
- `POST /api/data/upload-preview` ahora acepta `files` para indicadores multiparchivo y mantiene `file` para cargas simples MC-02/MC-03.
- La previsualizacion SI-02 valida paquete completo, rechaza cargas parciales por subindicadores faltantes, guarda un hash combinado, procesa solo `Detalle_Ate` y devuelve resumen con archivos recibidos, esperados, subindicadores detectados/faltantes, filas y columnas operativas.
- `DataUploadView.jsx` cambia automaticamente a seleccion multiple cuando el indicador activo es SI-02 y desactiva validar hasta seleccionar exactamente 4 archivos.
- `SearchDNI.jsx` muestra SI-02 en secciones por subindicador, evitando mezclar componentes nominales entre los cuatro Excel.
- `Dashboard.jsx`, `schemas.py` y exportacion de incumplidos incorporan `subindicator_code` y `subindicator_name` para reportar el origen de los incumplimientos.
- Se compacto el resumen de provincias y meses de `excel_loader.py` para evitar listas repetidas dentro de cada subindicador.
- Validacion real de previsualizacion con los cuatro Excel SI-02: 4/4 archivos, 10,672 filas, 391 columnas operativas, subindicadores `si02_01`, `si02_02`, `si02_03`, `si02_04`, sin faltantes.
- Validacion tecnica: `python -m unittest backend.indicators.si02.tests.test_si02_excel_contract backend.indicators.si02.tests.test_si02_rules backend.indicators.si02.tests.test_si02_storage backend.indicators.mc02.tests.test_mc02_rules` OK con 40 pruebas y 1 omitida; `npm run build` OK.

### Fase 5 SI-02 - Vistas frontend por subindicador
- El dashboard de SI-02 ahora tiene selector interno para ver el compromiso global o cada subindicador `SI-02.01`, `SI-02.02`, `SI-02.03` y `SI-02.04`.
- La seleccion de subindicador actualiza meta, meses cumplidos, avance mensual, mes en evaluacion, conteo de incumplidos y tabla nominal.
- La vista global muestra columna `Subindicador`; la vista individual la omite para dejar mas espacio al motivo y componentes observados.
- `frontend/src/indicators/registry.js` centraliza los metadatos visibles de cada subindicador.
- Los endpoints de omisos/incumplidos y descargas CSV/XLSX aceptan `subindicator` para que la descarga respete la vista seleccionada.
- Validacion HTTP: global ABANCAY devuelve 2,589 incumplidos; `subindicator=si02_04` devuelve solo SI-02.04 con 1,312 incumplidos; Excel filtrado responde correctamente.
- Validacion tecnica: `npm run build` OK; `python -m py_compile backend/main.py` OK; `python -m unittest backend.indicators.si02.tests.test_si02_excel_contract backend.indicators.si02.tests.test_si02_rules backend.indicators.si02.tests.test_si02_storage backend.indicators.mc02.tests.test_mc02_rules` OK con 40 pruebas y 1 omitida.

### Fase 6 SI-02 - Validacion operativa y compromiso
- Se agrego `backend/indicators/si02/commitment.py` para calcular la lectura oficial del compromiso por verificacion:
  - mayo 2026: `SI-02.01` requiere 4 de 5 meses y `SI-02.02`/`SI-02.03`/`SI-02.04` requieren 1 mes;
  - noviembre 2026: los cuatro subindicadores requieren 5 de 6 meses.
- `build_package_summary` y `build_active_report_summary` exponen `commitment_summary`; `committed` ahora representa el cumplimiento de la verificacion vigente segun fecha de corte.
- La validacion del paquete SI-02 ahora detecta cantidad exacta de archivos, duplicados, archivos no identificados e inconsistencia de fecha de corte entre los cuatro Excel.
- `DataUploadView.jsx` muestra una grilla operativa por subindicador con archivo, corte, filas, columnas y columnas faltantes; el historial agrega desglose de filas por subindicador.
- `Dashboard.jsx` muestra un panel de compromiso SI-02 con regla aplicada y avance por subindicador.
- Se corrigio la descripcion obsoleta de `backend/indicators/si02/__init__.py`.
- Validacion tecnica: `python -m py_compile` sobre SI-02, schemas y `backend/main.py` OK; `npm run build` OK; `python -m unittest backend.indicators.si02.tests.test_si02_commitment backend.indicators.si02.tests.test_si02_excel_contract backend.indicators.si02.tests.test_si02_rules backend.indicators.si02.tests.test_si02_storage backend.indicators.mc02.tests.test_mc02_rules` OK con 34 pruebas y 3 omitidas por no encontrar Excel reales en `E:/Downloads` o pruebas protegidas de BD.

### Seguridad - usuarios, roles y permisos
- Se decidio implementar una primera capa DB-backed sobre la arquitectura actual antes de integrar un paquete mas invasivo como `fastapi-users`.
- Se agregaron tablas PostgreSQL para usuarios, roles, permisos y relaciones mediante la migracion `0003_users_roles_permissions`.
- Las contrasenas usan hash Argon2 con `pwdlib[argon2]` y los tokens usan JWT firmado con `PyJWT`.
- Roles iniciales: `clinical`, `supervisor` y `admin`; el permiso nuevo `users_admin` habilita la administracion de usuarios.
- `AUTH_USERS_JSON` queda como semilla inicial; si no hay usuarios, se crea `admin / admin123` como cuenta temporal.
- Se agrego la vista frontend **Usuarios** para crear cuentas, asignar rol, activar/desactivar y renovar contrasenas.
- Validacion local: migracion Alembic a `0003`, seed de usuarios/roles, login `admin / cambiar-admin`, endpoint `/api/security/users`, pruebas unitarias de seguridad y `npm run build` OK.
### Refactorización del Frontend y Diseño del Sistema
- Se aplicó la guía de habilidades de React (.agents/skills) para resolver la complejidad de los componentes monolíticos del frontend (`SearchDNI.jsx` y `Dashboard.jsx`).
- **Desacoplamiento de Lógica (Hooks)**:
  - Se crearon los hooks personalizados [useDniSearch.js](file:///C:/Users/USUARIO/.gemini/antigravity/worktrees/mc03-app/improve-system-design-agents/frontend/src/hooks/useDniSearch.js) y [useDashboardData.js](file:///C:/Users/USUARIO/.gemini/antigravity/worktrees/mc03-app/improve-system-design-agents/frontend/src/hooks/useDashboardData.js) para separar la lógica de negocio, llamadas de API (axios) y estados del rendering.
- **Modularización de Presentación (Componentes)**:
  - Se extrajeron a la carpeta `src/components/` los componentes funcionales: [StatusPill.jsx](file:///C:/Users/USUARIO/.gemini/antigravity/worktrees/mc03-app/improve-system-design-agents/frontend/src/components/StatusPill.jsx), [DoseDetails.jsx](file:///C:/Users/USUARIO/.gemini/antigravity/worktrees/mc03-app/improve-system-design-agents/frontend/src/components/DoseDetails.jsx), [HemoglobinDetails.jsx](file:///C:/Users/USUARIO/.gemini/antigravity/worktrees/mc03-app/improve-system-design-agents/frontend/src/components/HemoglobinDetails.jsx), [IronDetails.jsx](file:///C:/Users/USUARIO/.gemini/antigravity/worktrees/mc03-app/improve-system-design-agents/frontend/src/components/IronDetails.jsx), [PeriodBadge.jsx](file:///C:/Users/USUARIO/.gemini/antigravity/worktrees/mc03-app/improve-system-design-agents/frontend/src/components/PeriodBadge.jsx) y [SemaphoreBadge.jsx](file:///C:/Users/USUARIO/.gemini/antigravity/worktrees/mc03-app/improve-system-design-agents/frontend/src/components/SemaphoreBadge.jsx).
- **Simplificación de Vistas**:
  - [SearchDNI.jsx](file:///C:/Users/USUARIO/.gemini/antigravity/worktrees/mc03-app/improve-system-design-agents/frontend/src/SearchDNI.jsx) y [Dashboard.jsx](file:///C:/Users/USUARIO/.gemini/antigravity/worktrees/mc03-app/improve-system-design-agents/frontend/src/Dashboard.jsx) ahora consumen los nuevos hooks y delegan la renderización a los componentes modulares específicos.
- **Validación**:
  - Compilación de producción con Vite (`npm run build`) ejecutada con éxito y sin advertencias/errores.
  - Ejecución de pruebas unitarias del backend exitosa para asegurar la no regresión.

