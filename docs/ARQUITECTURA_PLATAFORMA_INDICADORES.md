# Arquitectura general para plataforma de seguimiento de indicadores

Este documento define la ruta general para evolucionar el sistema actual MC-03 hacia una plataforma multiindicador para la Red de Salud. La idea central es que cada indicador tenga sus propias reglas tecnicas, ficha, configuracion y documento especifico, pero que todos compartan la misma estructura de carga, procesamiento, dashboard, busqueda, filtros y exportacion.

Este archivo es general. Cada indicador debera tener su propio documento `.md` con sus criterios particulares.

## Objetivo del proyecto

Construir una plataforma que permita monitorear distintos indicadores de salud a partir de archivos Excel operativos, aplicando las reglas de cada ficha tecnica y entregando resultados accionables para la gestion de la Red de Salud.

El sistema debe permitir:

- Seleccionar un indicador.
- Subir el archivo Excel correspondiente.
- Validar si el archivo cumple la estructura esperada.
- Procesar denominador, numerador, cobertura e incumplidos.
- Visualizar avance mensual e historial.
- Identificar el mes en evaluacion actual.
- Filtrar poblacion objetivo.
- Buscar registros individuales.
- Descargar incumplidos en Excel.
- Mantener trazabilidad de reglas, decisiones y cambios.

## Principio de diseno

El sistema debe separar claramente dos niveles:

1. Plataforma general.
   Contiene carga de archivos, seleccion de indicador, dashboards reutilizables, filtros, exportaciones, autenticacion futura y componentes comunes.

2. Modulo de indicador.
   Contiene reglas propias de una ficha tecnica: columnas requeridas, filtros de denominador, calculo de numerador, ventanas de atencion, criterios de exclusion, mensajes de cumplimiento e incumplimiento, y estructura de detalle.

La plataforma no deberia conocer reglas especificas como BCG, CRED, tamizaje u otros criterios. Solo debe invocar al modulo del indicador seleccionado y recibir una salida estandar.

## Estructura propuesta del backend

```text
backend/
  core/
    dates.py
    excel.py
    files.py
    indicators.py
    reports.py
    storage.py

  indicators/
    mc03/
      config.py
      denominator.py
      vaccines.py
      cred.py
      screening.py
      messages.py
      utils.py
      processor.py
      rules.py
      schema.py
      MC03_sistema_seguimiento_Abancay_Codex.md

    nuevo_indicador/
      config.py
      denominator.py
      components.py
      messages.py
      utils.py
      processor.py
      rules.py
      schema.py
      README_NUEVO_INDICADOR.md

  uploads/
  processed/
  main.py
  schemas.py
```

### Responsabilidades de `core`

- Lectura y validacion base de archivos Excel.
- Manejo de fechas y formatos comunes.
- Registro de indicadores disponibles.
- Contratos comunes de reporte.
- Utilidades de exportacion.
- Persistencia de archivos subidos y fuente activa.
- Funciones compartidas para filtros, paginacion y descarga.

### Responsabilidades de `indicators`

Cada indicador debe implementar su propia logica:

- Nombre y codigo del indicador.
- Meta por defecto.
- Periodo de evaluacion.
- Hoja y celdas relevantes del Excel.
- Columnas requeridas.
- Filtros de poblacion objetivo.
- Criterios de inclusion y exclusion.
- Calculo de denominador.
- Calculo de numerador.
- Reglas de cumplimiento.
- Mensajes de incumplimiento.
- Detalle individual de atenciones.

## Contrato estandar de un indicador

Todo indicador deberia exponer una interfaz comun. Una propuesta inicial:

```python
class IndicatorProcessor:
    code: str
    name: str
    default_target: float

    def validate_file(self, file_path) -> ValidationResult:
        ...

    def load_data(self, file_path) -> DataBundle:
        ...

    def build_summary(self, data, filters, target) -> ReportSummary:
        ...

    def search_record(self, data, query, filters) -> SearchResult:
        ...

    def export_non_compliant(self, records) -> bytes:
        ...
```

La plataforma solo deberia llamar estos metodos sin conocer la logica interna del indicador.

## Salida estandar del reporte

Cada indicador deberia devolver una estructura comun:

```text
ReportSummary
- indicator_code
- indicator_name
- source_file
- cut_off_date
- target_coverage
- period_start
- period_end
- current_evaluation_month
- months_evaluated
- months_met
- committed
- monthly[]
- non_compliant[]
```

Cada elemento mensual:

```text
MonthlyCompliance
- month
- year
- month_key
- denominator
- numerator
- coverage
- status
- semaphore
- in_verification_period
- is_current_evaluation_month
```

Cada incumplido:

```text
NonCompliantRecord
- month_key
- month
- year
- document_id
- secondary_id
- birth_date
- patient_name
- province
- microred
- facility_code
- facility_name
- reason
- details
```

No todos los indicadores tendran los mismos campos clinicos, pero deberian mapear sus datos principales a este contrato comun.

## Estructura propuesta del frontend

```text
frontend/src/
  pages/
    IndicatorList.jsx
    DataUploadView.jsx
    IndicatorDashboard.jsx
    RecordSearch.jsx
    ConfigView.jsx

  components/
    MetricCard.jsx
    MonthlyTable.jsx
    NonCompliantTable.jsx
    StatusBadge.jsx
    UploadPanel.jsx
    FilterBar.jsx

  indicators/
    registry.js
    mc03.js
```

### Componentes reutilizables

- Card de metricas.
- Tabla mensual.
- Tabla de incumplidos.
- Selector de mes.
- Selector de indicador.
- Filtros de poblacion objetivo.
- Busqueda individual.
- Exportacion Excel.
- Alertas de validacion.

### Componentes especificos por indicador

Algunos indicadores pueden necesitar detalles propios. Para eso se puede permitir que cada indicador declare:

- Columnas extra para tabla de incumplidos.
- Vista de detalle individual.
- Etiquetas de atenciones.
- Mensajes personalizados.
- Filtros adicionales.

## Flujo operativo esperado

1. Usuario selecciona un indicador.
2. Usuario sube archivo Excel.
3. Sistema valida estructura, hoja, fecha de corte y columnas requeridas.
4. Sistema muestra resumen de validacion.
5. Usuario activa el archivo como fuente de datos.
6. Sistema procesa el indicador.
7. Dashboard muestra avance mensual, mes en evaluacion actual e incumplidos.
8. Usuario filtra por provincia, establecimiento, microred, seguro u otros criterios.
9. Usuario descarga Excel de incumplidos.
10. Usuario busca un registro por DNI, CNV u otro identificador.

## Manejo de archivos Excel

El sistema debe soportar carga de archivos por indicador.

Consideraciones:

- Guardar el archivo original subido.
- Registrar fecha de carga, usuario futuro, indicador y nombre original.
- Validar extension `.xlsx`.
- Validar hoja esperada.
- Validar columnas obligatorias.
- Validar fecha de corte.
- Mostrar errores claros si el archivo no corresponde.
- Permitir activar una fuente de datos.
- Mantener historial de archivos subidos.

Estructura sugerida:

```text
backend/uploads/
  mc03/
    2026-05-archivo.xlsx

backend/processed/
  mc03/
    latest.json
```

## Documentacion por indicador

Cada indicador debe tener su propio `.md` dentro de su modulo backend para mantener juntas la logica y su ficha tecnica operativa. Estructura sugerida:

```text
backend/indicators/
  mc03/
    MC03_sistema_seguimiento_Abancay_Codex.md
  mc04/
    MC04_sistema_seguimiento_Abancay_Codex.md
```

Plantilla minima para cada indicador:

```text
# Codigo y nombre del indicador

## Fuente normativa
- Ficha tecnica:
- Version:
- Archivo de referencia:

## Objetivo del indicador

## Poblacion objetivo

## Denominador

## Numerador

## Criterios de inclusion

## Criterios de exclusion

## Periodo de evaluacion

## Meta

## Columnas requeridas del Excel

## Reglas de validacion

## Reglas de cumplimiento

## Mensajes de incumplimiento

## Salida esperada

## Consideraciones operativas
```

## Migracion del MC-03 actual

MC-03 debe convertirse en el primer modulo formal del sistema. El objetivo no es cambiar su comportamiento actual, sino aislarlo.

Pasos sugeridos:

1. Crear `backend/indicators/mc03/`.
2. Mover reglas de negocio MC-03 a `rules.py`.
3. Mover configuracion MC-03 a `config.py`.
4. Mover procesamiento del indicador a `processor.py`.
5. Mantener los endpoints actuales funcionando durante la migracion.
6. Crear un registro de indicadores disponibles.
7. Adaptar endpoints para recibir `indicator_code`.
8. Adaptar frontend para seleccionar indicador.
9. Mantener el documento especifico del indicador dentro de `backend/indicators/mc03/`.

## Endpoints sugeridos a futuro

```text
GET  /api/indicators
GET  /api/indicators/{indicator_code}
GET  /api/indicators/{indicator_code}/config/options

GET  /api/indicators/{indicator_code}/data/current
POST /api/indicators/{indicator_code}/data/upload-preview
POST /api/indicators/{indicator_code}/data/activate

GET  /api/indicators/{indicator_code}/report/summary
GET  /api/indicators/{indicator_code}/report/incumplidos
GET  /api/indicators/{indicator_code}/report/incumplidos.xlsx

GET  /api/indicators/{indicator_code}/search/{document_id}
```

Durante la transicion, se pueden mantener endpoints antiguos como alias para no romper el sistema actual.

## Filtros comunes

Filtros reutilizables:

- Provincia.
- Distrito.
- Microred.
- Establecimiento.
- Mes de evaluacion.
- Tipo de seguro.
- Estado de cumplimiento.
- Indicador.

Filtros especificos:

- Dependeran de cada ficha tecnica.
- Deben definirse en el documento y configuracion del indicador.

## Exportacion Excel

Cada indicador debe poder exportar incumplidos.

Columnas comunes recomendadas:

- Mes evaluacion.
- Mes.
- Anio.
- Documento.
- Identificador secundario.
- Fecha de nacimiento, si aplica.
- Paciente.
- Provincia.
- Microred.
- Establecimiento.
- Motivo de incumplimiento.

Columnas especificas:

- Pueden agregarse por indicador segun la necesidad operativa.

## Reglas sobre fechas

El sistema debe estandarizar fechas para visualizacion y exportacion.

Frontend:

- Formato recomendado: `dd mmm yyyy`.
- Ejemplo: `04 may 2026`.

Backend:

- Mantener fechas como `date`, `datetime` o texto normalizado.
- Evitar que la hora `00:00:00` llegue como presentacion final al usuario.

Excel:

- Puede exportarse como fecha real o texto formateado, pero debe ser legible.

## Estado de desarrollo

La base multiindicador ya cuenta con:

- MC-02 modularizado y persistido en PostgreSQL.
- MC-03 modularizado y persistido en PostgreSQL.
- Registro de indicadores disponible en backend y frontend.
- Carga de archivos asociada al indicador seleccionado.
- Activacion versionada con historial.
- Dashboard, busqueda por DNI/CNV, incumplidos y descargas leyendo desde la carga activa.
- Procesamiento en segundo plano para activaciones pesadas.
- Roles `clinical`, `supervisor` y `admin`.
- Auditoria de eventos y respaldo manual de PostgreSQL.

Las fases historicas de migracion a PostgreSQL quedan documentadas en `docs/README_PostgreSQL_Migration.md`.

## Criterios para agregar un nuevo indicador

Antes de implementar un indicador nuevo se debe tener:

- Ficha tecnica oficial.
- Archivo Excel de ejemplo.
- Descripcion del denominador.
- Descripcion del numerador.
- Meta.
- Periodo de evaluacion.
- Columnas requeridas.
- Criterios de inclusion.
- Criterios de exclusion.
- Reglas de incumplimiento.
- Resultado esperado para casos de prueba.

## Recomendacion inmediata

Antes de implementar otro indicador, usar MC-02 y MC-03 como molde tecnico: crear el documento especifico del indicador, mapear columnas Excel, definir componentes, agregar pruebas nominales con DNIs/CNV reales y luego conectar el modulo al registro comun.

La prioridad no debe ser agregar muchos indicadores rapidamente, sino mantener un contrato estable para que cada indicador nuevo entre con menos riesgo y menos duplicacion.

