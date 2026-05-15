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
