# MC-03 - Paquete recien nacido

Este documento registra los criterios especificos del indicador MC-03 dentro de la plataforma multiindicador. La documentacion general de arquitectura se encuentra en `docs/ARQUITECTURA_PLATAFORMA_INDICADORES.md`.

## Fuente normativa

- Ficha tecnica: MC-03 FT Paquete Recien Nacido.
- Archivo de referencia inicial: `docs/MC-03 FT_PAQUETE RECIEN NACIDO.pdf`.
- Archivo operativo actual: Excel con hoja `Detalle_Ate`.

## Objetivo del indicador

Medir el cumplimiento del paquete de atenciones del recien nacido, incluyendo vacunas, controles CRED y tamizaje neonatal, segun las reglas definidas en la ficha tecnica.

## Poblacion objetivo

Registros que entran a evaluacion del indicador segun la columna `Obs_Eval`.

Actualmente:

- Incluye: `Evaluado`.
- Excluye: `No_Evaluado`.

La columna `Obs_Eval` ya incorpora criterios como peso al nacer y edad gestacional, por lo que el sistema no recalcula esas exclusiones.

## Denominador

Registros del mes de evaluacion que cumplen:

- `Mes_eva` igual al mes evaluado.
- `Obs_Eval` igual a `Evaluado`.
- Tipo de seguro incluido en la configuracion del indicador.

Tipos de seguro incluidos:

- `SIS`
- `NINGUNO`
- `SIN SEGURO`
- `SIN_SEGURO`
- Celda vacia, considerada como sin seguro.

## Numerador

Registros del denominador que completan el paquete del recien nacido:

- Vacuna BCG dentro del plazo.
- Vacuna HvB dentro del plazo.
- Tres controles CRED dentro de ventana normativa.
- Tamizaje neonatal dentro de ventana normativa.

## Reglas de vacunas

### BCG

- Codigo: `90585`.
- Plazo: dentro de las primeras 24 horas de vida.

### HvB

- Codigo: `90744`.
- Plazo: dentro de las primeras 24 horas de vida.

## Reglas CRED

Codigo esperado: `99381.01`.

Ventanas:

- 1er CRED: dias 3 a 6.
- 2do CRED: dias 7 a 14.
- 3er CRED: dias 15 a 21.

Regla adicional:

- Intervalo minimo entre controles: 7 dias.

## Reglas de tamizaje neonatal

- Codigo: `36416`.
- Ventana: desde el dia 2 hasta el dia 6 de vida.

## Meta

Meta mensual por defecto:

- `70.7%`

Semaforo:

- `Cumple`: cobertura mayor o igual a la meta.
- `No cumple`: cobertura menor a la meta.

## Periodo de evaluacion

Periodo oficial de verificacion:

- Junio a noviembre 2026.

El dashboard tambien muestra meses previos con datos para seguimiento historico operativo.

## Mes en evaluacion actual

El mes en evaluacion se identifica a partir de la fecha de corte del archivo Excel.

El sistema debe indicar:

- Mes actual en evaluacion.
- Numerador actual.
- Denominador actual.
- Cobertura acumulada hasta el corte.
- Registros faltantes para alcanzar la meta.

## Columnas requeridas del Excel

Columnas principales:

- `Mes_eva`
- `Obs_Eval`
- `Esta_pac`
- `Desc_prov`
- `afi_DNI`
- `NumCNV`
- `fec_Nac`
- `fec1_BCG`
- `resul1_BCG`
- `Edad_ate1_BCG`
- `fecHVB`
- `resulHVB`
- `Edad_ateHVB`
- `Fecha_Atencion_1`
- `Codigo_HIS_1`
- `Edad_Atencion_1`
- `Fecha_Atencion_2`
- `Codigo_HIS_2`
- `Edad_Atencion_2`
- `Intervalo_2`
- `Fecha_Atencion_3`
- `Codigo_HIS_3`
- `Edad_Atencion_3`
- `Intervalo_3`
- `Fecha_Atencion_TN`
- `Codigo_HIS_TN`
- `Edad_Atencion_TN`

## Salidas del indicador

El modulo MC-03 debe entregar:

- Resumen mensual.
- Numerador y denominador.
- Cobertura.
- Estado de cumplimiento.
- Incumplidos por mes.
- Motivo de incumplimiento.
- Busqueda individual por DNI.
- Exportacion Excel de incumplidos.

## Consideraciones operativas

- La provincia por defecto para la Red de Salud es `ABANCAY`.
- Debe existir opcion para mostrar todos los datos.
- Las fechas visibles deben mostrarse en formato `dd mmm yyyy`.
- En el Excel de incumplidos debe incluirse la fecha de nacimiento.
- En la tabla de incumplidos no se muestra codigo RENAES, pero puede conservarse internamente si se requiere.
