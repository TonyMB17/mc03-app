# MC-02 - Paquete integrado de servicios en menores de 12 meses

Este documento registra los criterios especificos del indicador MC-02 dentro de la plataforma multiindicador. La documentacion general de arquitectura se encuentra en `docs/ARQUITECTURA_PLATAFORMA_INDICADORES.md`.

## Fuente normativa

- Ficha tecnica: MC-02.01.
- Nombre de la meta de cobertura: niñas y niños menores de 12 meses de edad procedentes de los quintiles 1 y 2 de pobreza departamental que reciben el paquete integrado de servicios.
- Archivo de referencia: `docs/MC-02_FT_PROCESAMIENTO_GR_241025.pdf`.
- Excel operativo revisado: `MC 02_FT MC_02 _INFANTIL.xlsx`.
- Area responsable del procesamiento: Oficina General de Tecnologias de la Informacion (OGTI) - MINSA.
- Areas tecnicas: Direccion General de Intervenciones Estrategicas en Salud Publica - MINSA, Direccion de Inmunizaciones - MINSA, Unidad Funcional de Alimentacion y Nutricion Saludable - MINSA, y Direccion de Seguimiento de la DGSEI - MIDIS.

## Definicion del indicador

Porcentaje de niñas y niños menores de 12 meses de edad procedentes de distritos de quintiles 1 y 2 de pobreza departamental que recibieron el paquete integrado de servicios.

El paquete integrado considera:

- Vacunas basicas segun edad: antineumococica, rotavirus, antipolio y pentavalente.
- Entrega de hierro: gotas, jarabe o micronutrientes, segun edad y condicion.
- Dosaje de hemoglobina entre los 170 y 209 dias.
- DNI emitido hasta los 30 dias de nacido.

Nota operativa local:

- Para la implementacion actual de la Red de Salud Abancay se omite el criterio de DNI emitido hasta los 30 dias, porque no corresponde al area salud.
- Tambien se omiten los controles CRED del calculo MC-02 actual, aunque el Excel los trae procesados. Se conservan documentados para uso futuro.

## Objetivo del indicador

Medir si las niñas y niños menores de 12 meses de los distritos Q1 y Q2 de pobreza departamental reciben oportunamente el paquete integrado de intervenciones preventivas priorizadas para el desarrollo infantil temprano y la prevencion de anemia y desnutricion cronica.

## Ambito de control

- Geografico: nacional, departamental y distrital.
- Evaluacion vinculada al ubigeo de residencia o procedencia registrado en el padron nominal.
- Se considera la atencion del niño o niña en el ubigeo de residencia registrado en el padron nominal.

## Periodicidad y verificacion

- Periodo anual: 2026.
- Verificacion: unica verificacion en noviembre 2026.
- La determinacion del corte de edad se realiza al ultimo dia del mes de medicion.

## Formula

```text
Indicador = (Numerador / Denominador) * 100
```

## Denominador

Numero de niñas y niños menores de 12 meses de edad en el mes de medicion, procedentes de distritos de quintiles 1 y 2 de pobreza departamental, registrados en el padron nominal con DNI o CNV, con tipo de seguro SIS o sin seguro.

Condiciones del denominador:

- Edad menor de 12 meses en el mes de medicion.
- Procedencia en distritos de quintil 1 o quintil 2 de pobreza departamental.
- Registro en padron nominal con DNI o CNV.
- Tipo de seguro SIS o sin seguro.
- Edad calculada al ultimo dia del mes de medicion.

Exclusiones del denominador:

- Bajo peso al nacer: menor de 2500 gramos.
- Prematuridad: menor de 37 semanas de gestacion.
- Estas exclusiones se toman de la informacion registrada en CNV.

## Numerador

Numero de niñas y niños del denominador que reciben el paquete integrado de servicios segun edad, se encuentran registrados en HIS y cuentan con DNI emitido.

Para cumplir el numerador, el registro debe cumplir los componentes aplicables por edad:

- Vacunas basicas segun edad.
- Entrega de hierro o micronutrientes segun edad, esquema y condicion.
- Dosaje de hemoglobina entre 170 y 209 dias.
- DNI emitido hasta los 30 dias de nacido.

En la implementacion local actual, el numerador operativo se calcula solo con vacunas, hierro/suplementacion y dosaje de hemoglobina. El DNI y CRED no se consideran para el cumplimiento MC-02 de la plataforma.

## Reglas generales de identificacion

- Para obtener el dato del padron nominal se toma en cuenta la variable tipo de documento DNI o, en su defecto, CNV en linea.
- Se contabiliza como maximo una misma prestacion por dia.
- Para visita familiar se consideran registros LAB `PO1` a `PO6`, `P01` a `P06`, `SF1` a `SF6` y numericos `1`, `2`, `3`, `4`, `5`, `6`, independientemente del orden de numeracion o secuencia del esquema.
- Las precisiones tecnicas se basan en la normatividad vigente.
- La trama de datos para la medicion sera definida y generada por OGTI-MINSA.

## Componente de vacunas

### Antineumococica

- Codigos HIS/CIE de busqueda: `90670` o `90677`.
- En 2026 se incorpora la vacuna antineumococica 20-valente con codigo `90677`.
- El codigo `90670` tambien se utiliza para busqueda de esta vacuna.

Reglas extraidas de la tabla 01:

| Edad del niño/a | Condicion esperada |
|---|---|
| 0 a 119 dias | Todos |
| 120 a 189 dias | 1 dosis |
| 190 a 364 dias | 2 dosis acumuladas |

Regla de intervalo:

- Para segunda dosis: debe cumplir una relacion con la primera dosis de al menos 28 dias y hasta 70 dias segun tabla tecnica.

### Rotavirus

- Codigo HIS/CIE: `90681`.
- La vacuna rotavirus se aplica como maximo hasta los 8 meses 0 dias, equivalente a 240 dias de edad.

Reglas extraidas de la tabla 02:

| Edad del niño/a | Condicion esperada |
|---|---|
| 241 a 364 dias | 2 dosis acumuladas |

Regla de intervalo:

- Segunda dosis: al menos 28 dias despues de la primera dosis.
- La segunda dosis debe respetar el limite maximo de 240 dias de edad.

Nota operativa:

- La tabla de rotavirus en el texto extraido del PDF muestra principalmente la regla de segunda dosis. Al implementar el algoritmo se debe contrastar manualmente con la ficha PDF para completar la regla de primera dosis si la trama operativa no la trae ya evaluada.

### Antipolio

- Codigos HIS/CIE: `90712` o `90713`.

Reglas extraidas de la tabla 03:

| Edad del niño/a | Condicion esperada |
|---|---|
| 0 a 210 dias | Todos |
| 211 a 240 dias | 1 dosis |
| 260 a 364 dias | 3 dosis acumuladas |

Regla de intervalo:

- Para tercera dosis: debe ser al menos 28 dias despues de la segunda dosis y hasta 70 dias despues segun tabla tecnica.

Nota operativa:

- La ficha extraida no muestra claramente el tramo de segunda dosis por el formato del PDF. Debe validarse contra la ficha original antes de codificar el algoritmo final.

### Pentavalente

- Codigo vigente: `90722`.
- Codigo historico o de busqueda: `90723`.
- La ficha indica que `90723` se utiliza solo con fines de busqueda de datos, ya que el codigo vigente es `90722`.

Reglas extraidas de la tabla 04:

| Edad del niño/a | Condicion esperada |
|---|---|
| 0 a 119 dias | Todos |
| 120 a 189 dias | 1 dosis |
| 190 a 259 dias | 2 dosis acumuladas |
| 260 a 364 dias | 3 dosis acumuladas |

Reglas de intervalo:

- Segunda dosis: al menos 28 dias despues de la primera dosis y hasta 70 dias despues.
- Tercera dosis: al menos 28 dias despues de la segunda dosis y hasta 70 dias despues.

## Componente de hierro, suplementacion y micronutrientes

### Codigos validos

Tratamiento de anemia con hierro:

- Diagnosticos: `D509`, `D649`.
- CPMS: `99199.17`.

Suplementacion preventiva:

- `99199.17`: suplementacion con hierro, sulfato ferroso o hierro polimaltosado.
- `99199.19`: suplementacion de multimicronutrientes.

Exclusion comun:

- Se excluye el codigo `99499` de telemedicina.

### Reglas generales para entregas de hierro

- Para suplementacion preventiva, cumple segun edad con una o mas entregas de hierro.
- Solo se considera entrega de hierro sin LAB cuando no esta vinculada a visita familiar.
- Solo se considera entrega de hierro con LAB cuando esta vinculada a visita familiar.
- Los multimicronutrientes aplican para entregas en niñas y niños de 170 a 364 dias.

### Suplementacion preventiva en esquema de 4 meses

Tabla 05: suplementacion preventiva, esquema de 4 meses para entregas de hierro.

Regla general extraida:

- Para la suplementacion preventiva, cumple con una entrega de hierro, segun edad.
- A partir del tramo señalado en la ficha, se espera al menos una entrega.

Nota operativa:

- La extraccion del PDF no conserva completamente la tabla de rangos. Al implementar se debe validar contra la ficha original y, si el Excel ya trae variables precalculadas, priorizar dichas variables.

### Tratamiento con hierro en niños de 6 a 11 meses

Tabla 06: tratamiento, esquema de 6 meses para entregas de hierro.

Reglas:

- Para tratamiento, cumple con al menos tres entregas de hierro, segun edad.
- En la primera entrega de hierro se busca vinculacion a un codigo de anemia `D509` o `D649`.
- El tipo de diagnostico debe ser definitivo `D` en la misma cita.
- En las siguientes entregas no se realiza nuevamente la busqueda de diagnostico de anemia.
- Se excluyen registros `99199.17 + LAB TA` en la primera entrega de hierro.
- Se excluye el codigo `99499` de telemedicina.

### Suplementacion preventiva en niños de 6 a 11 meses

Tabla 07: suplementacion preventiva, esquema de 6 meses para entregas de hierro.

Reglas:

- Cumple con al menos dos entregas de hierro, segun edad.
- Si por edad corresponde solo una entrega, cumple si recibe sulfato ferroso o hierro polimaltosado.
- Si por edad corresponden al menos dos entregas, cumple con cualquiera de estas combinaciones:
  - Dos entregas de sulfato ferroso o hierro polimaltosado.
  - Sulfato ferroso o hierro polimaltosado y micronutrientes.
  - Micronutrientes y sulfato ferroso o hierro polimaltosado.
- En la primera entrega se verifica que no este vinculada a un codigo de anemia.
- En las siguientes entregas no se realiza esa busqueda.
- Se excluyen registros `99199.17 + LAB TA` en la primera entrega de hierro.
- Se excluye el codigo `99499` de telemedicina.

Intervalos extraidos:

| Tramo | Condicion |
|---|---|
| Desde 210 dias | Al menos 1 entrega |
| Segunda entrega | Desde primera entrega +25 dias y hasta primera entrega +70 dias |
| Tercera entrega | Desde segunda entrega +25 dias y hasta segunda entrega +70 dias |

### Esquema combinado micronutrientes mas hierro

Tabla 08: suplementacion preventiva, esquema 6 meses para entregas de hierro con multimicronutrientes mas sulfato ferroso o hierro polimaltosado.

Reglas:

- Cumple con al menos dos entregas, segun edad.
- Se excluyen registros `99199.19 + LAB TA` en la primera entrega.
- Se excluye el codigo `99499` de telemedicina.
- Primera entrega desde 210 dias.
- Segunda entrega desde la primera entrega +25 dias y hasta primera entrega +35 dias.

### Esquema solo multimicronutrientes

Tabla 09: suplementacion preventiva unicamente con entregas de multimicronutrientes en niños de 6 a 11 meses.

Reglas:

- Codigo principal de multimicronutrientes: `99199.19`.
- Se excluyen registros `99199.19 + LAB TA` en la primera entrega.
- Se excluye el codigo `99499` de telemedicina.

Intervalos extraidos:

| Tramo | Condicion |
|---|---|
| Desde 210 dias | Al menos 1 entrega |
| Segunda entrega | Desde primera entrega +25 dias y hasta primera entrega +35 dias |
| Tercera entrega | Desde segunda entrega +25 dias y hasta segunda entrega +35 dias |
| Cuarta entrega | Desde tercera entrega +25 dias y hasta tercera entrega +35 dias |
| Quinta entrega | Desde cuarta entrega +25 dias y hasta cuarta entrega +35 dias |
| Sexta entrega | Desde quinta entrega +25 dias y hasta quinta entrega +35 dias |

## Dosaje de hemoglobina

Codigos identificados:

- `85018`
- `85018.01`
- `85031`

Regla:

- Haber realizado dosaje de hemoglobina en sangre entre los 170 y 209 dias de edad.

Tabla 10:

| Edad del niño/a | Condicion |
|---|---|
| 0 a 209 dias | Todos |
| 210 a 364 dias | 1 dosaje entre 170 y 209 dias |

## DNI emitido

Regla:

- Contar con DNI emitido hasta los 30 dias de nacido.

Criterio:

- El tiempo transcurrido entre la fecha de nacimiento y la fecha de emision del DNI debe ser igual o menor a 30 dias.

Tabla 11:

| Edad del niño/a | Condicion |
|---|---|
| 0 a 30 dias | Todos |
| 31 a 364 dias | Cumple si DNI fue emitido hasta los 30 dias de nacido |

## Meta

- Meta por defecto identificada en el Excel operativo: `80.9%`.
- En las hojas `Resumen_Red` y `Resumen_Ubigeo`, la meta figura como `0.809`.

Consideracion para implementacion:

- La meta debe cargarse por defecto como `80.9%`, pero mantenerse editable desde configuracion, igual que en MC-03.

## Estructura del Excel operativo

- Hoja principal: `Detalle_Ate`.
- Fecha de corte: celda `D9`.
- Fecha de corte del archivo revisado: `11 may 2026`.
- Encabezados: fila `10`.
- Filas leidas en la hoja principal: `5,789`.
- Columnas leidas en la hoja principal: `375`.
- Hojas resumen disponibles: `Resumen_Red` y `Resumen_Ubigeo`.
- Las hojas resumen contienen meses desde `2025_5` hasta `2026_5`.

### Columnas base

La lectura debe normalizar espacios en los encabezados, porque existen nombres con espacios finales.

| Uso | Columnas identificadas |
|---|---|
| Ubicacion | `Ubigeo`, `provincia`, `Distrito`, `Distrito_FED`, `Red`, `MicroRed`, `EESS`, `Renaes` |
| Identificacion | `DNI o CNV`, `NumCNV`, `Nombres`, `Ape_Paterno`, `Ape_Materno`, `Fec_Nac` |
| Contacto y familia | `NomApellMadre`, `DNIMadre`, `Celular` |
| Seguro | `Obs_Niño` |
| Nacimiento | `Peso`, `Edad_Gestacional`, `Est_Nac_CNV`, `Est_Nac_HIS` |
| Edad | `Edad_act(Mes)`, `Edad_Act(dia)`, `Mes_Nac` |
| Resultado general | `Obs_General`, `Estado`, `Registros` |

### Interpretacion del seguro

El Excel no trae una columna llamada `Seguro`. La variable operativa encontrada es `Obs_Niño`, con valores como:

- `SIS`
- `ESSALUD`
- `PRIVADO`
- vacio

Para mantener consistencia con la ficha tecnica, el sistema debe considerar como incluidos `SIS` y celdas vacias si el archivo operativo las usa como poblacion sin seguro. Los otros valores deben quedar disponibles para filtros o exclusion configurable.

### Variables de cumplimiento ya procesadas

El Excel operativo ya trae marcas de cumplimiento por componente. Esto permite una primera implementacion basada en columnas precalculadas, sin recalcular desde cero todas las reglas de atenciones.

| Componente | Texto de observacion | Marca binaria |
|---|---|---|
| Vacuna neumococo | `Obs_NEU` | `obs_neu1` |
| Vacuna rotavirus | `Obs_ROT` | `obs_rot1` |
| Vacuna antipolio | `Obs_ANT` | `obs_ant1` |
| Vacuna pentavalente | `Obs_PEN` | `obs_pen1` |
| Hierro menor de 6 meses | `Obs_Hierros` | `obs_suple41` |
| Hierro mayor de 6 meses | `OBS_SUPLE6` | `obs_suple61` |
| Anemia / hierro terapeutico | `A_Obs_AnemiaXY` | `Obs_Anemia` |
| Dosaje de hemoglobina | `Obs_Dh` | `Obs_dh1` |
| Paquete integrado | `Obs_General` | `Estado` |
| Poblacion evaluada | - | `Registros` |

Valores observados:

- `Estado = 1`: cumple paquete integrado.
- `Estado = 0`: no cumple paquete integrado.
- `Registros = 1`: registro que entra en la poblacion evaluada.
- `Obs_General = Cumple` o `No_Cumple`: estado textual del paquete.

Decision de procesamiento:

- El numerador de la plataforma ya no usa directamente `Estado`, porque puede incluir criterios que no se evaluaran en esta version local.
- El cumplimiento MC-02 se recalcula con los componentes activos: neumococo, rotavirus, antipolio, pentavalente, hierro menor de 6 meses, hierro mayor de 6 meses y dosaje de hemoglobina.
- Las marcas CRED (`obs_credRN1`, `Obs_CRED1mas`, `Cred_cumple`) quedan excluidas del calculo actual.

### Bloques de atenciones disponibles

Ademas de las marcas finales, el archivo conserva columnas de detalle para auditoria:

- Controles RN: `fecha_1RN` a `fecha_4RN`, con laboratorio, edad, CIE/CPT, lote, establecimiento y profesional.
- Controles CRED: `fecha_1CRED` a `fecha_9CRED`, con datos de edad, CIE/CPT, lote, establecimiento y profesional.
- Vacunas: bloques `NEU`, `Rot`, `ANT` y `PENT`.
- Tratamiento con hierro/anemia: bloques `fecha_1Hier` a `fecha_6Hier`, `CIE_TratHierro_*`, `CIE_Anemia_*`.
- Suplementacion preventiva: bloques `prev` y `prevhierr`, con intervalos.
- Dosaje de hemoglobina: `fecha_1DH`, `Lab_1DH`, `edad_1DH`, `CIE_DH_1DH`, `EESS_Ate_1DH`.

### Hojas resumen

Las hojas `Resumen_Red` y `Resumen_Ubigeo` ya agrupan el indicador por mes de nacimiento/evaluacion. Cada mes contiene estas metricas:

- `Total_Niños_364_Dias`
- `Control_CRED_RN.`
- `Control_CRED_1Mas.`
- `Cumple_CRED_RN_&_1mas`
- `Cumple_Vacuna_Nuemococo`
- `Cumple_Vacuna_Rotavirus`
- `Cumple_Vacuna_Antipolio`
- `Cumple_Vacuna_Penta`
- `Cumple_Hierro_Menor_6Meses`
- `Cumple_hierro_Mayor_6Meses`
- `Cumple_DosajeHemoglobina`
- `Cumple_paquete`
- `%_Cumple_paquete`

Para el dashboard propio de la plataforma se recomienda calcular los resumenes desde `Detalle_Ate`, usando `Mes_Nac`, `Registros` y `Estado`, para mantener una sola logica de filtros y descargas.

## Salidas esperadas del indicador

El modulo MC-02 debe entregar:

- Resumen mensual.
- Denominador.
- Numerador.
- Cobertura.
- Estado de cumplimiento segun meta.
- Mes en evaluacion actual.
- Registros incumplidos.
- Motivo de incumplimiento por componente:
  - Vacuna neumococo.
  - Vacuna rotavirus.
  - Vacuna antipolio.
  - Vacuna pentavalente.
  - Hierro o micronutrientes.
  - Dosaje de hemoglobina.
- Busqueda individual por DNI o CNV.
- Exportacion Excel de incumplidos.

## Consideraciones para implementacion

- Este indicador es mas extenso que MC-03 y debe implementarse por componentes.
- La primera version debe priorizar leer el Excel operativo y verificar si las reglas ya vienen precalculadas en columnas de observacion o evaluacion.
- Si el Excel ya trae marcas de cumplimiento por componente, el sistema debe aprovecharlas antes de recalcular todo desde atenciones crudas.
- Si el Excel trae atenciones crudas, sera necesario construir reglas por dosis, edad e intervalos.
- Las tablas de suplementacion requieren revision manual junto al PDF porque la extraccion textual no conserva perfectamente todos los rangos.
- El sistema debe mostrar mensajes claros de incumplimiento por componente y no solo un incumplimiento general.
- Los bloques CRED se mantienen disponibles como informacion historica/auditoria, pero no participan en el calculo del indicador MC-02 actual.
- El criterio DNI se mantiene como referencia de ficha tecnica, pero no participa en el calculo operativo de salud.

## Referencias bibliograficas citadas en la ficha

- NTS N. 238-MINSA/DGIESP-2025: Norma Tecnica de Salud para el Control del Crecimiento y Desarrollo del Niño.
- ENDES 2024.
- Manual de registro y codificacion de la prevencion y control de la anemia por deficiencia de hierro en el niño y la niña, adolescente, mujeres en edad fertil, gestantes y puerperas 2024.
- NTS N. 213-MINSA/DGIESP-2024: Prevencion y control de la anemia por deficiencia de hierro.
- NTS N. 196-MINSA/DGIESP-2022: Esquema Nacional de Vacunacion.
- Manual de Registro y Codificacion de la Atencion. Etapa de Vida Niño / Sistema de Informacion HIS.
