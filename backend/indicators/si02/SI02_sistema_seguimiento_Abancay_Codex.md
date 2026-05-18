# Sistema de Seguimiento - Indicador SI-02
## Red de Salud Abancay - Version Codex-friendly

> Objetivo del documento: servir como base tecnica para implementar el compromiso **SI-02** en la plataforma multiindicador, sin volver a descifrar la ficha tecnica ni los Excel semanales en cada iteracion.
>
> Fuente normativa principal: ficha tecnica **SI-02 - Hierro nino GORE, procesamiento octubre 2025**.
>
> Principio de implementacion: SI-02 debe tratarse como un indicador compuesto con cuatro subindicadores. El sistema debe conservar una vista integrada del compromiso y, al mismo tiempo, permitir evaluar, cargar, auditar y explicar cada subindicador por separado.

---

# 1. Identificacion del compromiso

| Campo | Valor |
|---|---|
| Codigo de compromiso | `SI-02` |
| Nombre | Ninas y ninos de doce meses del departamento que reciben tratamiento o suplementacion preventiva con hierro, y dosajes de hemoglobina |
| Periodicidad | Mensual |
| Fuente numerador | HIS MINSA |
| Fuente denominador | Padron nominal de ninas y ninos menores de 6 anos; para SI-02.02 tambien CNV en linea |
| Instrumento | Registro Diario de Atencion y Otras Actividades de Salud - HIS |
| Ambito local recomendado | Provincia `ABANCAY`, configurable |
| Fecha de corte observada en archivos | `2026-05-11` |

## 1.1 Subindicadores

| Subindicador | Nombre operativo | Poblacion | Edad de medicion | Meta observada |
|---|---|---|---|---|
| `si02_01` | Condicion previa: hierro 4 meses + dosaje 6 meses | Ninos de 6 meses, sin BPN/prematuridad | 209 dias | 92.0% |
| `si02_02` | Prematuros y/o bajo peso al nacer | Ninos de 6 meses prematuros leves y/o BPN, sin anemia | 209 dias | 60.3% |
| `si02_03` | Ninos de 12 meses con anemia | Ninos con diagnostico definitivo de anemia a los 6 meses | 394 dias | 55.0% |
| `si02_04` | Ninos de 12 meses sin anemia | Ninos sin diagnostico de anemia a los 6 meses | 394 dias | 65.0% |

## 1.2 Cumplimiento del compromiso

Primera verificacion, mayo 2026:

- `si02_01`: cumple si la region alcanza la meta en 4 de 5 meses.
- `si02_02`: cumple si alcanza la meta en 1 mes.
- `si02_03`: cumple si alcanza la meta en 1 mes.
- `si02_04`: cumple si alcanza la meta en 1 mes.

Segunda verificacion, noviembre 2026:

- Cada subindicador cumple si alcanza la meta en 5 de 6 meses.
- El compromiso SI-02 se considera cumplido cuando se cumplen los cuatro subindicadores.

---

# 2. Recomendacion de arquitectura

Implementar **un solo modulo publico**:

```text
backend/indicators/si02/
```

con **cuatro submodulos internos**:

```text
backend/indicators/si02/subindicators/si0201.py
backend/indicators/si02/subindicators/si0202.py
backend/indicators/si02/subindicators/si0203.py
backend/indicators/si02/subindicators/si0204.py
```

## 2.1 Por que no separarlos como cuatro indicadores independientes

No conviene exponerlos como cuatro indicadores totalmente separados porque:

- La ficha define un compromiso unico `SI-02`.
- El cumplimiento final depende de los cuatro subindicadores.
- Comparten poblacion, codigos HIS, reglas de anemia, reglas de hierro, dosajes, corte mensual y filtros territoriales.
- En busqueda por DNI conviene mostrar la trayectoria SI-02 del nino en una sola vista.
- En dashboard conviene ver avance global y avance por subindicador.

## 2.2 Como separarlos internamente

Si conviene separarlos internamente porque:

- Cada subindicador usa un Excel distinto.
- Las columnas y filas de encabezado cambian.
- Las reglas de denominador cambian.
- Los componentes exigidos cambian.
- Los mensajes de incumplimiento deben explicar motivos distintos.

Modelo recomendado:

```text
si02
|-- config.py
|-- excel_loader.py
|-- processor.py
|-- dashboard.py
|-- schema.py
|-- storage.py
|-- components/
|   |-- anemia.py
|   |-- hemoglobin.py
|   |-- iron.py
|   |-- intervals.py
|-- subindicators/
|   |-- si0201.py
|   |-- si0202.py
|   |-- si0203.py
|   |-- si0204.py
|-- tests/
|   |-- test_si02_excel_contract.py
|   |-- test_si02_rules.py
```

---

# 3. Estrategia de carga de datos

SI-02 debe cargarse como un **paquete de cuatro archivos**.

Flujo recomendado:

```text
4 Excel SI-02
-> validacion de presencia y estructura por subindicador
-> lectura solo de hoja Detalle_Ate
-> procesamiento por subindicador
-> conciliacion opcional contra Resumen_Red / Resumen_Ubigeo
-> persistencia como una version activa SI-02
```

Reglas de carga:

- La activacion completa de `SI-02` debe requerir los cuatro archivos.
- La carga semanal llega como paquete completo de cuatro Excel; no se debe activar una version SI-02 incompleta.
- `Resumen_Red` y `Resumen_Ubigeo` deben usarse para validacion y conciliacion, no como fuente principal de busqueda.
- La busqueda por DNI debe leer datos procesados de `Detalle_Ate`.
- La tabla de dashboard puede usar resumen precalculado por subindicador.
- En PostgreSQL, usar `indicator_code = "si02"` y guardar `subindicator_code` en `record_payload`, `component_results.detail` y `indicator_omissions.detail`.
- Si se permite carga parcial para pruebas, no debe reemplazar la version activa completa.

---

# 4. Archivos Excel revisados

| Subindicador | Archivo | Hoja detalle | Fila de encabezado | Filas detalle | Columnas |
|---|---|---:|---:|---:|---:|
| `si02_01` | `SI_02_01_Ninos de 209 dias Con Hierro_DosajeHemoglobina` | `Detalle_Ate` | 11 | 4,895 | 62 |
| `si02_02` | `SI_02_02_Ninos BPN_Prematuridad 209 dias Con Hierro_DosajeHemoglobina` | `Detalle_Ate` | 10 | 396 | 85 |
| `si02_03` | `SI_02_03_Ninos de 394dias DX_Anemia con Hierro_DosajeHemoglobina` | `Detalle_Ate` | 9 | 225 | 135 |
| `si02_04` | `SI_02_04_Ninos de 394dias sin_DX_Anemia con Hierro_DosajeHemoglobina` | `Detalle_Ate` | 9 | 5,156 | 109 |

Hojas comunes:

- `Detalle_Ate`: fuente nominal principal.
- `Resumen_Red`: resumen mensual por red/provincia.
- `Resumen_Ubigeo`: resumen mensual por ubigeo/provincia.

Notas de estructura:

- La columna de provincia cambia de mayusculas: `PROVINCIA` en `si02_01`, `provincia` en los demas.
- La fila de corte esta en la cabecera del Excel, pero cambia de posicion: `si02_01` la trae en fila 9; los demas en fila 8.
- `si02_01` muestra en cabecera "Indicador MC 01", aunque el archivo pertenece a SI-02. Esto debe tratarse como rotulo inconsistente del Excel, no como codigo del indicador.

---

# 5. Columnas comunes minimas

Las cuatro hojas `Detalle_Ate` comparten un bloque nominal:

```text
UBIGEO
provincia / PROVINCIA
distrito
des_red
des_micro
Renaes_ate
EESS
afi_dni
NUMCNV
NOMBRE
APELLPAT
APEMAT
FEC_NAC
EESS_NAC
APELLNOM_MADRE
DNI_MADRE
CELULAR
TIPO_SEGURO
Peso
SEMANAGESTACION
obs_Cnv
EdadDias
mes_eva
ano
registros
```

Campos de identidad para busqueda:

- DNI: `afi_dni`
- CNV: `NUMCNV`
- Nombre completo: `NOMBRE`, `APELLPAT`, `APEMAT`
- Fecha de nacimiento: `FEC_NAC`

Reglas de normalizacion:

- Mantener DNI/CNV como texto para no perder ceros.
- Normalizar provincia con `str.upper().strip()`.
- Convertir fechas con parser tolerante de Excel.
- Tratar vacios, guiones y `NaN` como ausencia real de atencion.

---

# 6. Codigos y reglas transversales

## 6.1 Dosaje de hemoglobina

Codigos validos:

```text
85018
85018.01
85031
```

## 6.2 Diagnostico de anemia

Codigos:

```text
D509
D649
```

Regla:

- Para clasificar anemia se debe exigir diagnostico definitivo `D` cuando el Excel exponga tipo de diagnostico o LAB aplicable.
- `si02_02` excluye anemia entre 0 y 169 dias.
- `si02_03` exige anemia a los 6 meses, entre 170 y 209 dias, a partir del primer dosaje.
- `si02_04` exige ausencia de anemia a los 6 meses y excluye diagnosticos D509/D649 entre 210 y 364 dias.

## 6.3 Entrega de hierro

Codigos:

```text
99199.17
99199.19
```

Uso:

- `99199.17`: hierro / sulfato ferroso / polimaltosado segun ficha y Excel.
- `99199.19`: multimicronutriente, usado en reglas de `si02_04`.

## 6.4 Exclusiones generales

Excluir atenciones de telemedicina:

```text
99499
```

Regla de LAB para visita familiar:

- Se consideran LAB `PO1-PO6`, `P01-P06`, `SF1-SF6` y numericos `1` a `6`.
- Aplica solo para visita familiar, segun ficha tecnica.

---

# 7. Reglas por subindicador

## 7.1 SI-02.01 - Condicion previa

Denominador:

- Ninas y ninos de 6 meses de edad, 209 dias.
- Registrados en padron nominal con DNI o CNV.
- Tipo de seguro SIS o Sin seguro.
- Excluir prematuros menores de 37 semanas y BPN menor de 2500 g desde CNV en linea.

Numerador segun ficha:

1. Una entrega de hierro a los 4 meses.
   - Ventana: 110 a 130 dias.
   - Codigo: `99199.17`.
2. Un dosaje de hemoglobina a los 6 meses.
   - Ventana: 170 a 209 dias.
   - Codigos: `85018`, `85018.01`, `85031`.

Columnas observadas:

| Componente | Fecha | Codigo | LAB | Edad/intervalo | Estado |
|---|---|---|---|---|---|
| Hierro 4 meses | `Fec_H2` | `Cie_H2` | `Lab_H2` | `Intervalo3` | `Obs_hierro`, `Obs_hierro1` |
| Dosaje 6 meses | `Fec_Dh3` | `Cie_Dh3` | `Lab_Dh3` | `Intervalo5` | `Obs_DH`, `Obs_DH1` |
| TA del Excel | `Fec_TA3` | `Cie_TA3` | `Lab_TA3` | `Intervalo6` | `Obs_TA`, `Obs_TA1` |
| Resultado general | - | - | - | - | `Obs_General`, `Obs_General1` |

Decision local confirmada:

- `TA` / `Termino_Tratamiento` afecta el cumplimiento de `si02_01`.
- El estado general de `si02_01` debe exigir hierro, dosaje y TA cuando el registro es evaluable.

## 7.2 SI-02.02 - Prematuros y/o bajo peso

Denominador:

- Ninas y ninos de 6 meses, 209 dias.
- Prematuridad leve: 34 a 36 semanas.
- Bajo peso al nacer: 1500 a 2499 g.
- Registrados con DNI o CNV.
- Tipo de seguro SIS o Sin seguro.
- Sin diagnostico de anemia entre 0 y 169 dias.

Numerador:

1. Primer dosaje a 30 dias.
   - Ventana: 30 a 59 dias.
2. Primera entrega de hierro a 30 dias.
   - Ventana: 30 a 59 dias.
   - Codigo: `99199.17`.
3. Segunda entrega de hierro entre tercer y cuarto mes.
   - Ventana: 80 a 130 dias.
   - Codigo: `99199.17`.
4. Segundo dosaje a los 3 meses de iniciada la suplementacion.
   - Ventana: 80 a 119 dias.
5. Tercer dosaje a 6 meses.
   - Ventana: 170 a 209 dias.

Columnas observadas:

| Componente | Fecha | Codigo | LAB | Edad/intervalo | Estado |
|---|---|---|---|---|---|
| Prematuridad/BPN | `fec_premat` | - | - | - | `obs_Cnv` |
| DH 1 mes | `Fec_Dh1` | `Cie_Dh1` | `lab_Dh1` | `Intervalo1` | `DH_1Mes` |
| Hierro 1 mes | `Fec_H1` | `Cie_H1` | `Lab_H1` | `Intervalo2` | `H1_1Mes` |
| Hierro 4 meses | `Fec_H2` | `Cie_H2` | `Lab_H2` | `Intervalo3` | `H2_4Mes` |
| DH 3 meses | `Fec_Dh2` | `Cie_Dh2` | `Lab_Dh2` | `Intervalo4` | `DH2_3Mes` |
| DH 6 meses | `Fec_Dh3` | `Cie_Dh3` | `Lab_Dh3` | `Intervalo5` | `DH3_6Mes` |
| TA del Excel | `Fec_TA3` | `Cie_TA3` | `Lab_TA3` | `Intervalo6` | - |
| Resultado general | - | - | - | - | `obser_Cumple`, `estado` |

## 7.3 SI-02.03 - Doce meses con anemia

Denominador:

- Ninas y ninos de 12 meses 29 dias, 394 dias.
- Registrados con DNI o CNV.
- Tipo de seguro SIS o Sin seguro.
- Primer dosaje a los 6 meses entre 170 y 209 dias.
- Diagnostico definitivo de anemia entre 170 y 209 dias, a partir del primer dosaje.

Numerador:

1. Tres entregas de hierro de tratamiento.
   - Primera entrega el mismo dia del diagnostico.
   - Segunda entrega: 25 a 70 dias despues de la primera.
   - Tercera entrega: 25 a 70 dias despues de la segunda.
   - Codigo: `99199.17`.
2. Dosaje de control al mes de tratamiento.
   - Ventana: 25 a 59 dias.
3. Dosaje de control a los 2 meses.
   - Ventana: 55 a 89 dias.
4. Dosaje de control a los 3 meses.
   - Ventana: 85 a 119 dias.
5. Dosaje de control a los 6 meses.
   - Ventana: 170 a 209 dias.

Columnas observadas:

| Componente | Columnas principales | Estado |
|---|---|---|
| Anemia denominador | `fec_Anemia`, `Ci10_Anemia`, `Lab_Anemia`, `reg_Anemia`, `EESS_Anemia`, `Prof_Anemia`, `Obser_Anemia` | `Con_Anemia` |
| Primer DH denominador | `fec_DH`, `Ci10_Dh`, `lab_Dh`, `reg_dh` | `Cumple_6Meses` |
| Hierro tratamiento | `Fec_hierro1` a `Fec_hierro6`, `Cie10_Hierro1` a `Cie10_Hierro6`, `lab_hierro1` a `lab_hierro6` | `Obs_Hierro`, `Esta_Hierro` |
| DH control 1 mes | `Fec_DH1`, `Cie_Dh1`, `Lab_Dh1`, `intervaloDh1` | `Obse_Dh1m`, `Esta_DH1` |
| DH control 2 meses | `Fec_DH2`, `Cie_Dh2`, `Lab_Dh2`, `intervaloDh2` | `Obse_Dh2m`, `Esta_Dh2` |
| DH control 3 meses | `Fec_DH3`, `Cie_Dh3`, `Lab_Dh3`, `intervaloDh3` | `Obse_Dh3m`, `Esta_DH3` |
| TA | `Fec_TA1`, `Cie10_TA1`, `lab_TA1`, `intervaloTA` | `Obse_TA`, `Esta_TA` |
| DH 12 meses | `Fec_DH12m`, `Cie_Dh12m`, `Lab_Dh12m`, `intervaloDh12m` | `Obse_Dh12m`, `Esta_Dh12m` |
| Resultado general | - | `Cumple_General`, `estado` |

Reglas adicionales:

- Excluir registros `99199.17 + LAB TA` en la primera entrega de hierro.
- En la primera entrega se debe buscar vinculacion con anemia `D509` o `D649`; en las siguientes entregas no.
- Entre segundo, tercero y cuarto dosaje el intervalo minimo es 25 dias.
- Entre cuarto y quinto dosaje el intervalo minimo es 85 dias.

## 7.4 SI-02.04 - Doce meses sin anemia

Denominador:

- Ninas y ninos de 12 meses 29 dias, 394 dias.
- Registrados con DNI o CNV.
- Tipo de seguro SIS o Sin seguro.
- Primer dosaje a los 6 meses entre 170 y 209 dias.
- Sin diagnostico definitivo de anemia entre 170 y 209 dias a partir del primer dosaje.
- Excluir diagnosticos D509/D649 entre 210 y 364 dias.

Numerador:

1. Al menos dos entregas de suplemento de hierro.
   - Primera entrega el mismo dia del primer dosaje.
   - Codigos: `99199.17` o `99199.19`.
   - Si es sulfato ferroso/polimaltosado: intervalo 25 a 70 dias.
   - Si continua multimicronutriente: 6 entregas con intervalo 25 a 35 dias.
   - Si cambia entre hierro y multimicronutriente: aplicar intervalo segun tipo inicial, como indica ficha.
2. Dos dosajes de hemoglobina.
   - Primer control: 85 a 119 dias desde la primera entrega.
   - Segundo control: 170 a 209 dias desde la primera entrega.

Columnas observadas:

| Componente | Columnas principales | Estado |
|---|---|---|
| Anemia denominador | `fec_Anemia`, `Ci10_Anemia`, `Lab_Anemia`, `reg_Anemia`, `Obser_Anemia` | `Sin_Anemia` |
| Primer DH denominador | `fec_DH`, `Ci10_Dh`, `lab_Dh`, `reg_dh` | `Cumple_6Meses` |
| Hierro preventivo | `Fec_hierro1` a `Fec_hierro6`, `Cie10_Hierro1` a `Cie10_Hierro6`, `lab_hierro1` a `lab_hierro6` | `Obs_Hierro`, `Esta_Hierro` |
| DH control 3 meses | `Fec_DH1`, `Cie_Dh1`, `Lab_Dh1`, `intervaloDh1` | `Obse_Dh1m`, `Esta_DH1` |
| TA del Excel | `Fec_TA1`, `Cie10_TA1`, `lab_TA1`, `intervaloTA` | `Obse_TA`, `Esta_TA` |
| DH 12 meses | `Fec_DH12m`, `Cie_Dh12m`, `Lab_Dh12m`, `intervaloDh12m` | `Obse_Dh12m`, `Esta_Dh12m` |
| Resultado general | - | `Cumple_General`, `estado` |

Reglas adicionales:

- Excluir telemedicina `99499`.
- Excluir registros con `99199.17 + LAB TA` o `99199.19 + LAB TA` en la primera entrega de hierro.
- Solo en la primera entrega se valida que no este vinculada a codigo de anemia; en las siguientes no se realiza esa busqueda.

---

# 8. Estados y componentes recomendados

Estados internos:

```text
cumple
no_cumple
no_evaluado
no_exigible
dato_insuficiente
```

Mapeo desde Excel:

- `Cumple`, `1` -> `cumple`
- `No_Cumple`, `0` -> `no_cumple`
- `No_Evaluado` -> `no_evaluado`
- Vacio en atencion -> ausencia real de registro

Componentes persistidos obligatorios:

```text
si02_01.hierro_4m
si02_01.dosaje_6m
si02_01.ta

si02_02.dh_1m
si02_02.hierro_1m
si02_02.hierro_4m
si02_02.dh_3m
si02_02.dh_6m

si02_03.anemia_6m
si02_03.hierro_tratamiento
si02_03.ta
si02_03.dh_1m
si02_03.dh_2m
si02_03.dh_3m
si02_03.dh_6m

si02_04.dh_6m_denominador
si02_04.hierro_preventivo
si02_04.ta
si02_04.dh_3m
si02_04.dh_12m
```

`TA` debe tratarse como componente obligatorio y visible en dashboard para `si02_01`, `si02_03` y `si02_04`. Para `si02_02`, el Excel trae columnas `Fec_TA3` / `Cie_TA3`, pero el resumen del subindicador no lo incluye como componente de cumplimiento; debe conservarse solo como dato observado para trazabilidad.

---

# 9. Dashboard y busqueda por DNI

## 9.1 Dashboard

Vista recomendada:

- Selector de indicador `SI-02`.
- Cards de cumplimiento global del compromiso.
- Resumen global con estado de los cuatro subindicadores y cumplimiento del compromiso.
- Tabs o segmentador por subindicador:
  - SI-02.01
  - SI-02.02
  - SI-02.03
  - SI-02.04
- Tabla mensual por subindicador.
- Tabla de incumplidos con columnas:
  - DNI/CNV
  - Nombre
  - Provincia/distrito/EESS
  - Subindicador
  - Componentes observados
  - Motivos
  - Mes de evaluacion

## 9.2 Busqueda por DNI/CNV

La respuesta debe mostrar una ficha SI-02 integrada:

```text
Datos personales
Subindicadores donde aparece el nino
Componentes exigibles por subindicador
Atenciones registradas
Motivos de incumplimiento
Estado final por subindicador
```

Si un nino aparece en mas de un archivo, se deben mostrar secciones separadas por subindicador, no mezclar componentes.

---

# 10. Pruebas minimas recomendadas

## 10.1 Contrato Excel

Validar:

- Cada archivo requerido existe en la carga.
- Existe hoja `Detalle_Ate`.
- La fila de encabezado coincide:
  - `si02_01`: 11
  - `si02_02`: 10
  - `si02_03`: 9
  - `si02_04`: 9
- Columnas minimas presentes por subindicador.
- La fecha de corte se detecta.

## 10.2 Conciliacion con archivos de ejemplo

Conteos esperados en los Excel revisados:

| Subindicador | Filas | ABANCAY | Cumplen segun estado general | No cumplen segun estado general |
|---|---:|---:|---:|---:|
| `si02_01` | 4,895 | 1,543 | 1,593 | 3,302 |
| `si02_02` | 396 | 124 | 96 | 300 |
| `si02_03` | 225 | 58 | 73 | 152 |
| `si02_04` | 5,156 | 1,604 | 1,345 | 3,811 |

## 10.3 Reglas nominales

Crear casos de prueba por subindicador:

- Un nino que cumple todos los componentes.
- Un nino sin entrega de hierro.
- Un nino sin dosaje.
- Un nino con atencion fuera de ventana.
- Un nino con anemia que debe ir a `si02_03`.
- Un nino sin anemia que debe ir a `si02_04`.
- Un prematuro/BPN que debe ir a `si02_02`.
- Un registro `No_Evaluado`.

---

# 11. Decisiones confirmadas para implementacion

1. `TA` debe afectar el cumplimiento de `si02_01`.
2. En `si02_03` y `si02_04`, `TA` debe tratarse como componente obligatorio y visible en dashboard.
3. La carga semanal SI-02 llega con los cuatro Excel juntos; la activacion debe exigir paquete completo.
4. El dashboard debe tener una vista global del compromiso SI-02 y tabs/segmentador por subindicador.
5. El sistema debe recalcular el cumplimiento desde las columnas de atencion desde la primera version, siguiendo el patron usado en MC-02 y MC-03. Los estados generales del Excel se usan para conciliacion y pruebas, no como fuente final de verdad.

---

# 12. Ruta de implementacion sugerida

1. Crear modulo `si02` con loader multiparchivo.
2. Implementar validacion de contrato Excel.
3. Persistir el paquete SI-02 en PostgreSQL como una version activa unica.
4. Implementar dashboard por subindicador usando los resumos precalculados.
5. Implementar busqueda por DNI/CNV con secciones por subindicador.
6. Recalcular reglas finas componente por componente.
7. Conciliar resultados contra `Resumen_Red` y `Resumen_Ubigeo`.
8. Agregar exportacion de incumplidos con subindicador, componente y motivo.

Primera implementacion recomendada:

- Usar `Detalle_Ate` como fuente nominal.
- Recalcular los estados desde columnas de atencion desde el inicio.
- Usar los estados calculados por el Excel solo como referencia de conciliacion.
- Implementar primero el contrato multiparchivo y luego los evaluadores propios, empezando por `si02_01` y `si02_02`, que tienen menor complejidad que los subindicadores de 12 meses.

---

# 13. Estado de implementacion

## Fase 1 completada - contrato multiparchivo

Archivos creados:

- `backend/indicators/si02/config.py`
- `backend/indicators/si02/excel_loader.py`
- `backend/indicators/si02/__init__.py`
- `backend/indicators/si02/tests/test_si02_excel_contract.py`

Capacidades implementadas:

- Configuracion de los cuatro subindicadores `si02_01`, `si02_02`, `si02_03` y `si02_04`.
- Deteccion automatica del subindicador a partir de la estructura real del Excel.
- Validacion de hoja `Detalle_Ate`, fila de encabezado, celda de corte y columnas obligatorias.
- Lectura optimizada solo de columnas operativas.
- Validacion de paquete completo de cuatro archivos.
- Pruebas contra los Excel reales ubicados en `E:/Downloads`.

Validaciones ejecutadas:

```powershell
backend\.venv\Scripts\python.exe -m unittest backend.indicators.si02.tests.test_si02_excel_contract
backend\.venv\Scripts\python.exe -m py_compile backend\indicators\si02\__init__.py backend\indicators\si02\config.py backend\indicators\si02\excel_loader.py backend\indicators\si02\tests\test_si02_excel_contract.py
```

Nota tecnica:

- SI-02 aun no se registra en `backend/indicators/registry.py` ni en el selector frontend. Esto es intencional hasta que el flujo de carga multiparchivo y la persistencia esten conectados.

## Fase 2 completada - evaluadores propios y resumen inicial

Archivos agregados:

- `backend/indicators/si02/evaluator.py`
- `backend/indicators/si02/processor.py`
- `backend/indicators/si02/utils.py`
- `backend/indicators/si02/tests/test_si02_rules.py`

Capacidades implementadas:

- Recalculo de cumplimiento desde columnas de atencion para los cuatro subindicadores.
- `TA` obligatorio en `si02_01`, `si02_03` y `si02_04`; observado sin afectar cumplimiento en `si02_02`.
- Evaluacion de busqueda por DNI/CNV sobre paquete multiparchivo.
- Resumen inicial por subindicador, provincia y mes para dashboard global SI-02.
- Exportacion interna de motivos y componentes observados por registro omiso.

Conteos recalculados con los Excel de referencia:

| Subindicador | Total | Cumplen recalculado | Componentes conciliados contra Excel |
|---|---:|---:|---|
| `si02_01` | 4,895 | 1,503 | `hierro_4m`, `dosaje_6m`, `ta` con 0 diferencias |
| `si02_02` | 396 | 93 | `dh_1m`, `hierro_1m`, `hierro_4m`, `dh_3m`, `dh_6m` con 0 diferencias |
| `si02_03` | 225 | 65 | `hierro_tratamiento`, `dh_1m`, `dh_2m`, `dh_3m`, `ta`, `dh_6m` con 0 diferencias |
| `si02_04` | 5,156 | 1,281 | `hierro_preventivo`, `dh_3m`, `ta`, `dh_12m` con 0 diferencias |

Detalle tecnico importante:

- En `si02_04.hierro_preventivo`, la conciliacion del Excel confirma que el intervalo se valida segun el codigo de la entrega actual:
  - `99199.17`: 25 a 70 dias.
  - `99199.19`: 25 a 35 dias.
- Cuando el esquema llega a sexta columna de hierro, el Excel la trata como cierre de esquema y no usa su intervalo para invalidar el componente. Esta regla quedo documentada en pruebas con casos reales.

Validaciones ejecutadas:

```powershell
backend\.venv\Scripts\python.exe -m unittest backend.indicators.si02.tests.test_si02_excel_contract backend.indicators.si02.tests.test_si02_rules
backend\.venv\Scripts\python.exe -m py_compile backend\indicators\si02\__init__.py backend\indicators\si02\config.py backend\indicators\si02\excel_loader.py backend\indicators\si02\evaluator.py backend\indicators\si02\processor.py backend\indicators\si02\utils.py backend\indicators\si02\tests\test_si02_excel_contract.py backend\indicators\si02\tests\test_si02_rules.py
```

Nota tecnica:

- SI-02 sigue sin registrarse en `backend/indicators/registry.py` ni en el frontend. La siguiente fase debe conectar el paquete SI-02 al flujo de carga multiparchivo y a la persistencia PostgreSQL.

## Fase 3 completada - persistencia PostgreSQL del paquete SI-02

Archivos agregados o actualizados:

- `backend/indicators/si02/storage.py`
- `backend/indicators/si02/__init__.py`
- `backend/indicators/si02/tests/test_si02_storage.py`

Capacidades implementadas:

- Persistencia versionada de una carga SI-02 completa como una sola version activa.
- Registro nominal por fila y subindicador en `indicator_records`.
- Resultados por componente en `component_results`, con clave namespaced (`si02_04.hierro_preventivo`, por ejemplo) para evitar ambiguedades entre subindicadores.
- Resumen mensual por provincia, subindicador y mes en `dashboard_summaries`.
- Incumplidos nominales por subindicador en `indicator_omissions`.
- Eventos de auditoria `upload_processing_started`, `upload_activated` y `upload_failed`.
- Consulta activa por DNI/CNV desde PostgreSQL, devolviendo las secciones SI-02 encontradas para el nino.
- Reconstruccion de resumen activo desde PostgreSQL con detalle por subindicador.

Validacion local con PostgreSQL:

| Elemento persistido | Conteo |
|---|---:|
| Registros nominales | 10,672 |
| Resultados de componentes | 49,797 |
| Resumenes dashboard | 390 |
| Incumplidos | 7,730 |

Validacion ABANCAY desde PostgreSQL:

- Subindicadores reconstruidos: `si02_01`, `si02_02`, `si02_03`, `si02_04`.
- Incumplidos ABANCAY reconstruidos: 2,589.
- Busqueda por DNI `94061040`: encontrada correctamente en la carga activa.

Validaciones ejecutadas:

```powershell
backend\.venv\Scripts\python.exe -m unittest backend.indicators.si02.tests.test_si02_excel_contract backend.indicators.si02.tests.test_si02_rules backend.indicators.si02.tests.test_si02_storage
backend\.venv\Scripts\python.exe -m py_compile backend\indicators\si02\__init__.py backend\indicators\si02\config.py backend\indicators\si02\excel_loader.py backend\indicators\si02\evaluator.py backend\indicators\si02\processor.py backend\indicators\si02\storage.py backend\indicators\si02\utils.py backend\indicators\si02\tests\test_si02_excel_contract.py backend\indicators\si02\tests\test_si02_rules.py backend\indicators\si02\tests\test_si02_storage.py
```

Nota de pruebas:

- `test_si02_storage.py` queda protegido por `RUN_SI02_DB_TESTS=1` porque crea una nueva version activa en PostgreSQL. La validacion real se ejecuto manualmente contra `indicator_tracking`.

Nota tecnica:

- Esta fase dejo lista la persistencia, pero la exposicion publica del indicador queda conectada en la fase 4 mediante registro en el backend, carga multiparchivo en API/frontend y vistas de consulta.

## Fase 4 completada - carga multiparchivo y seleccion SI-02

Archivos actualizados:

- `backend/indicators/registry.py`
- `backend/main.py`
- `backend/schemas.py`
- `backend/indicators/si02/__init__.py`
- `backend/indicators/si02/excel_loader.py`
- `backend/indicators/si02/processor.py`
- `frontend/src/indicators/registry.js`
- `frontend/src/DataUploadView.jsx`
- `frontend/src/Dashboard.jsx`
- `frontend/src/SearchDNI.jsx`

Capacidades implementadas:

- Registro publico de `SI-02` en el registry multiindicador.
- `upload-preview` acepta paquetes multiparchivo mediante el campo `files` cuando el indicador lo soporta.
- SI-02 valida y procesa los cuatro Excel como una sola carga pendiente, con hash combinado y resumen de paquete; una carga parcial queda invalida por subindicadores faltantes.
- El resumen de carga expone `files_received`, `expected_files`, `subindicators_found`, `missing_subindicators`, `total_loaded_columns` y detalle por subindicador.
- La vista de carga cambia automaticamente a seleccion multiple para `SI-02`, exige exactamente 4 archivos para validar y mantiene carga simple para MC-02/MC-03.
- La busqueda por DNI/CNV puede mostrar una ficha SI-02 integrada, separada por subindicador, sin mezclar componentes entre archivos.
- Dashboard y exportacion de incumplidos reciben `subindicator_code` y `subindicator_name` para diferenciar el origen del incumplimiento.
- Se compacto el resumen de provincias y meses por subindicador para evitar payloads grandes con valores repetidos.

Validacion con los cuatro Excel reales:

| Campo | Resultado |
|---|---:|
| Estado HTTP de previsualizacion | 200 |
| Valido | Si |
| Archivos recibidos | 4 |
| Archivos esperados | 4 |
| Subindicadores detectados | `si02_01`, `si02_02`, `si02_03`, `si02_04` |
| Subindicadores faltantes | 0 |
| Filas totales | 10,672 |
| Columnas operativas cargadas | 391 |

Detalle por subindicador:

| Subindicador | Filas | Columnas operativas | Provincias | Meses |
|---|---:|---:|---:|---:|
| `si02_01` | 4,895 | 62 | 8 | 12 |
| `si02_02` | 396 | 85 | 8 | 12 |
| `si02_03` | 225 | 135 | 8 | 12 |
| `si02_04` | 5,156 | 109 | 8 | 12 |

Validaciones ejecutadas:

```powershell
backend\.venv\Scripts\python.exe -m py_compile backend\main.py backend\schemas.py backend\indicators\registry.py backend\indicators\si02\__init__.py backend\indicators\si02\config.py backend\indicators\si02\excel_loader.py backend\indicators\si02\processor.py backend\indicators\si02\storage.py
backend\.venv\Scripts\python.exe -m unittest backend.indicators.si02.tests.test_si02_excel_contract backend.indicators.si02.tests.test_si02_rules backend.indicators.si02.tests.test_si02_storage backend.indicators.mc02.tests.test_mc02_rules
npm run build
```

Nota de pruebas:

- `test_si02_storage.py` sigue protegido por `RUN_SI02_DB_TESTS=1`; en la corrida normal se omite la prueba que escribe en PostgreSQL real.
- Se valido ademas `POST /api/data/upload-preview?indicator=si02` con `fastapi.testclient.TestClient` y los cuatro Excel reales desde `E:/Downloads`.

## Fase 5 completada - vistas frontend por subindicador

Archivos actualizados:

- `frontend/src/Dashboard.jsx`
- `frontend/src/indicators/registry.js`
- `backend/main.py`

Capacidades implementadas:

- El dashboard de `SI-02` mantiene una vista global del compromiso y agrega selector interno por subindicador:
  - `SI-02.01`
  - `SI-02.02`
  - `SI-02.03`
  - `SI-02.04`
- Al seleccionar un subindicador, se actualizan:
  - meta de la vista,
  - meses cumplidos,
  - avance mensual,
  - mes en evaluacion,
  - tabla de incumplidos,
  - conteo de omisos,
  - descarga Excel.
- La vista global conserva todos los subindicadores y muestra una columna `Subindicador` en la tabla de incumplidos.
- La vista por subindicador oculta la columna redundante y deja mas espacio para componentes observados y motivo.
- El backend acepta `subindicator` en endpoints de omisos/incumplidos y en descarga CSV/XLSX para que el archivo descargado respete la vista seleccionada.

Validaciones ejecutadas:

```powershell
npm run build
backend\.venv\Scripts\python.exe -m py_compile backend\main.py
backend\.venv\Scripts\python.exe -m unittest backend.indicators.si02.tests.test_si02_excel_contract backend.indicators.si02.tests.test_si02_rules backend.indicators.si02.tests.test_si02_storage backend.indicators.mc02.tests.test_mc02_rules
```

Validacion HTTP:

- `GET /api/report/incumplidos?indicator=si02&province=ABANCAY` devuelve 2,589 incumplidos.
- `GET /api/report/incumplidos?indicator=si02&province=ABANCAY&subindicator=si02_04` devuelve solo `si02_04`, con 1,312 incumplidos.
- `GET /api/report/incumplidos.xlsx?indicator=si02&province=ABANCAY&subindicator=si02_04&month=2026_5` responde Excel con nombre `incumplidos_si02_si02_04_2026_5.xlsx`.

Validacion visual:

- En navegador local, `SI-02` muestra el selector de subindicadores en dashboard.
- Al elegir `SI-02.04`, la vista cambia a `Incumplidos - SI-02.04` sin errores de consola.

## Fase 6 completada - validacion operativa y compromiso SI-02

Archivos actualizados:

- `backend/indicators/si02/commitment.py`
- `backend/indicators/si02/excel_loader.py`
- `backend/indicators/si02/processor.py`
- `backend/indicators/si02/storage.py`
- `backend/indicators/si02/__init__.py`
- `backend/schemas.py`
- `frontend/src/DataUploadView.jsx`
- `frontend/src/Dashboard.jsx`
- `backend/indicators/si02/tests/test_si02_commitment.py`

Capacidades implementadas:

- Se agrego calculo explicito del compromiso SI-02 por verificacion:
  - Primera verificacion mayo 2026: `SI-02.01` requiere 4 de 5 meses; `SI-02.02`, `SI-02.03` y `SI-02.04` requieren 1 mes.
  - Segunda verificacion noviembre 2026: los cuatro subindicadores requieren 5 de 6 meses.
- El resumen del dashboard ahora expone `commitment_summary` y `committed` refleja la verificacion vigente segun fecha de corte.
- La vista Dashboard muestra un panel de compromiso SI-02 con estado global, regla aplicada y avance de cada subindicador.
- La validacion del paquete SI-02 ahora informa:
  - cantidad exacta de archivos esperados/recibidos,
  - archivos faltantes,
  - subindicadores duplicados,
  - archivos no identificados,
  - detalle por archivo/subindicador,
  - inconsistencia de fechas de corte entre los cuatro Excel.
- La vista de carga muestra una grilla de estado del paquete, con archivo, corte, registros, columnas y columnas faltantes por subindicador.
- El historial de cargas muestra, cuando aplica, el desglose de filas por subindicador.
- Se corrigio la descripcion obsoleta de `backend/indicators/si02/__init__.py`, que aun indicaba que SI-02 no estaba registrado.

Validaciones ejecutadas:

```powershell
python -m py_compile backend\indicators\si02\commitment.py backend\indicators\si02\processor.py backend\indicators\si02\storage.py backend\indicators\si02\excel_loader.py backend\schemas.py
npm run build
python -m unittest backend.indicators.si02.tests.test_si02_commitment backend.indicators.si02.tests.test_si02_excel_contract backend.indicators.si02.tests.test_si02_rules backend.indicators.si02.tests.test_si02_storage backend.indicators.mc02.tests.test_mc02_rules
```
