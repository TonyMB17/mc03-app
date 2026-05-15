# MC-02.01 - Sistema de Seguimiento del Paquete Integrado
## Red de Salud Abancay

> **Archivo para Codex:** usar este markdown como fuente funcional para implementar, refactorizar o validar el sistema MC-02.01.  
> **Versión:** 2.0 - corregida y optimizada para desarrollo.  
> **Ámbito local:** Red de Salud Abancay.  
> **Indicador:** MC-02.01.  
> **Medición oficial:** anual 2026, única verificación en noviembre 2026.  
> **Decisión local:** el componente DNI no se evalúa en el sistema porque corresponde a RENIEC/identificación civil, no al área salud.  
> **Regla de prioridad:** si existe conflicto entre el README antiguo y este documento, usar este documento. Si existe conflicto entre este documento y la ficha técnica oficial, prevalece la ficha técnica oficial, excepto la exclusión local documentada del componente DNI.

---

## 0. Objetivo para Codex

Implementar o corregir un sistema que permita hacer seguimiento nominal, por niño/a y por cohorte, del cumplimiento del indicador **MC-02.01** para la Red de Salud Abancay.

El sistema debe permitir:

1. Cargar el Excel operativo MC-02 ya procesado.
2. Calcular denominador local.
3. Recalcular numerador local sin usar directamente la columna `Estado`.
4. Evaluar componentes activos: neumococo, rotavirus, antipolio, pentavalente, hierro 4 meses, hierro 6 meses y dosaje de hemoglobina.
5. Excluir del cálculo local el componente DNI.
6. Omitir controles CRED del numerador MC-02 actual.
7. Mostrar avance por cohorte de nacimiento (`Mes_Nac`) y por establecimiento/distrito cuando existan columnas disponibles.
8. Permitir búsqueda nominal por DNI/CNV.
9. Explicar por qué un niño/a no cumple: componente faltante, fuera de plazo, no exigible, pendiente o dato insuficiente.
10. Preparar la arquitectura para una fase futura en la que las reglas se recalculen desde HIS crudo y padrón nominal, no solo desde marcas precalculadas del Excel.

---

## 1. Definición del indicador

| Campo | Valor |
|---|---|
| Código | `MC-02.01` |
| Nombre | Porcentaje de niñas y niños menores de 12 meses de edad procedentes de distritos de quintiles 1 y 2 de pobreza departamental que recibieron el paquete integrado de servicios. |
| Tipo | Eficacia / Resultado |
| Periodicidad oficial | Anual 2026 |
| Verificación oficial | Noviembre 2026 |
| Niveles de desagregación | Nacional, departamental y distrital |
| Fuentes oficiales | HIS MINSA, RENIEC, Padrón Nominal de niños/as menores de 6 años y CNV en línea |
| Instrumento HIS | Registro Diario de Atención y Otras Actividades de Salud - HIS |

### 1.1 Fórmula oficial

```text
MC-02.01 (%) = (Numerador / Denominador) * 100
```

### 1.2 Denominador oficial

Niñas y niños menores de 12 meses de edad en el mes de medición, procedentes de distritos de quintiles 1 y 2 de pobreza departamental, registrados en el padrón nominal con DNI o CNV, con tipo de seguro SIS o sin seguro.

### 1.3 Numerador oficial

Niñas y niños del denominador que reciben el paquete integrado de servicios según edad, registrados en HIS y con DNI emitido.

### 1.4 Numerador local Abancay

Para este sistema local, el numerador se calcula con los componentes sanitarios del paquete integrado:

- Vacuna antineumocócica.
- Vacuna contra rotavirus.
- Vacuna antipolio.
- Vacuna pentavalente.
- Entrega de hierro de 4 meses, cuando corresponde por edad.
- Entrega de hierro de 6 meses, cuando corresponde por edad.
- Dosaje de hemoglobina, cuando corresponde por edad.

No se evalúa el componente DNI, aunque se documenta en este archivo como criterio oficial excluido localmente.

---

## 2. Decisiones funcionales locales

Estas decisiones deben respetarse en el código.

| Decisión | Regla |
|---|---|
| `DNI` | No evaluar como componente de cumplimiento local. No debe afectar el numerador local. |
| `CRED` | No usar controles CRED para numerador MC-02 actual. Pueden conservarse como auditoría o futura mejora. |
| `Estado` del Excel | No usar directamente para numerador, porque puede incluir criterios omitidos localmente. |
| Marcas `obs_*` del Excel | Usarlas en fase 1 como fuente operativa de cumplimiento por componente. |
| HIS crudo | Preparar módulos para recalcular en fase 2. |
| Duplicados | Contabilizar como máximo una misma prestación por día por paciente. |
| Corte de edad | Usar el último día del mes de medición o la fecha de corte del Excel cuando esté disponible. |
| Componentes no exigibles por edad | No deben generar incumplimiento; para el paquete parcial al corte se consideran `programado` o `no_exigible`. |

---

## 3. Fuente Excel operativa - fase 1

La primera implementación usa el Excel operativo ya procesado.

| Elemento | Regla esperada |
|---|---|
| Hoja principal | `Detalle_Ate` |
| Fecha de corte | Celda `D9` |
| Encabezados | Fila `10` |
| Filtro territorial por defecto | `provincia = ABANCAY` |
| Denominador operativo | `Registros = 1` |
| Seguro operativo | Columna `Obs_Niño`, bloque `DATOS_GENERALES` |
| Meta por defecto | `80.9%` |

### 3.1 Columnas mínimas esperadas

El sistema debe tolerar columnas faltantes y reportarlas como advertencias, no romper el proceso sin explicación.

```text
DATOS_GENERALES:
- Registros
- Provincia / provincia
- Distrito / distrito
- DNI o CNV / id_paciente
- Fec_Nac
- Mes_Nac
- Edad_Act(dia)
- Obs_Niño
- Peso
- Edad_Gestacional

MARCAS DE COMPONENTES:
- obs_neu1
- obs_rot1
- obs_ant1
- obs_pen1
- obs_suple41
- obs_suple61
- Obs_dh1

CAMPOS DE APOYO / AUDITORÍA, SI EXISTEN:
- EESS_Ate_*
- fecha_* / Fec_*
- Obs_Anemia
- Dx_Anemia
- CIE_Anemia_1Hier
- fecha_1Hier
- Fec_Anemia
```

### 3.2 Normalización de marcas de cumplimiento

Crear una función única para interpretar marcas del Excel.

```python
def normalizar_flag_cumple(valor):
    """
    Retorna True si el valor representa cumplimiento.
    Retorna False si representa incumplimiento, vacío, no registrado o no.
    Debe ser configurable porque el Excel puede variar entre versiones.
    """
```

Valores sugeridos inicialmente como cumplimiento, previa validación con el Excel real:

```text
CUMPLE, CUMPLE CON PAQUETE, SI, SÍ, 1, TRUE, VERDADERO, OK
```

Valores sugeridos como no cumplimiento:

```text
NO CUMPLE, NO, 0, FALSE, FALTA, PENDIENTE, OBSERVADO, vacío, null
```

No duplicar esta lógica en varios módulos.

---

## 4. Denominador local

Un niño/a pertenece al denominador si cumple todos los criterios siguientes.

### 4.1 Inclusión

| Criterio | Regla |
|---|---|
| Edad | Menor de 12 meses al corte: `0 <= edad_dias <= 364`. |
| Territorio | Procede/reside en distrito de quintil 1 o 2 del ámbito de la Red de Salud Abancay. En fase Excel, aplicar por defecto `provincia = ABANCAY` y permitir filtro configurable por distrito/quintil. |
| Padrón | Registrado con DNI o CNV. |
| Seguro | SIS o sin seguro. En Excel: aceptar `SIS`, `NINGUNO`, `SIN SEGURO` o celda vacía como sin seguro, según configuración. |
| Registro operativo | `Registros = 1`, en fase Excel. |

### 4.2 Exclusión

Excluir del denominador solo si existe evidencia explícita en CNV o campos equivalentes:

| Criterio | Regla |
|---|---|
| Bajo peso al nacer | `Peso < 2500` gramos. |
| Prematuridad | `Edad_Gestacional < 37` semanas. |

### 4.3 Tratamiento de datos vacíos

- Si `Peso` está vacío, no excluir por bajo peso.
- Si `Edad_Gestacional` está vacío, no excluir por prematuridad.
- Si falta fecha de nacimiento, usar `Edad_Act(dia)` como respaldo y registrar advertencia.
- Si no se puede calcular edad por ninguna fuente, marcar como `dato_insuficiente` y excluir del cálculo hasta corregir el dato.

---

## 5. Cálculo de edad y fechas

### 5.1 Edad al corte

```python
edad_dias = (fecha_corte - fecha_nacimiento).days
```

Reglas:

- Nacimiento el mismo día del corte: `edad_dias = 0`.
- Todos los rangos de edad son inclusivos.
- Si la fecha de corte del Excel existe en `D9`, usarla como fecha principal.
- Si no existe, usar el último día del mes de medición indicado por el usuario o configuración.

### 5.2 Edad al momento de la atención

```python
edad_atencion_dias = (fecha_atencion - fecha_nacimiento).days
```

Se usa para validar ventanas de vacunas, hierro y hemoglobina cuando existan fechas de atención.

---

## 6. Componentes activos para numerador local

En fase Excel, el numerador se recalcula con marcas precalculadas. No usar directamente `Estado`.

| Código interno | Componente | Marca Excel | Aplica desde edad al corte | Observación |
|---|---|---|---:|---|
| `neumococo` | Vacuna antineumocócica | `obs_neu1` | 120 días | 2 dosis acumuladas desde 190 días. |
| `rotavirus` | Vacuna rotavirus | `obs_rot1` | 211 días | Corregido: no empieza a los 120 días. |
| `antipolio` | Vacuna antipolio | `obs_ant1` | 120 días | 3 dosis acumuladas desde 260 días. |
| `pentavalente` | Vacuna pentavalente | `obs_pen1` | 120 días | 3 dosis acumuladas desde 260 días. |
| `hierro_4m` | Entrega preventiva de hierro 4 meses | `obs_suple41` | 131 días | Entrega válida entre 110 y 130 días. |
| `hierro_6m` | Hierro 6 a 11 meses: prevención o tratamiento | `obs_suple61` | 210 días | Según ruta preventiva, combinada, micronutrientes o tratamiento. |
| `hemoglobina` | Dosaje de hemoglobina | `Obs_dh1` | 210 días | Dosaje realizado entre 170 y 209 días. |

### 6.1 Regla del paquete local

```python
cumple_paquete_local = all(componentes_exigibles_cumplen)
```

Un componente es exigible si el niño/a ya alcanzó el rango de edad en el que la ficha técnica exige el cumplimiento. Si el componente aún no es exigible, debe mostrarse como `programado` o `no_exigible`, pero no debe causar incumplimiento del paquete parcial al corte.

### 6.2 Regla para niños con prestaciones anticipadas

Si un componente aún no es exigible por edad, pero el niño/a ya tiene una prestación válida y completa, puede mostrarse como `cumple`.

Si existe una prestación registrada antes de tiempo o fuera de intervalo, se debe auditar como `fuera_de_ventana`. En fase Excel, esta validación fina depende de disponibilidad de fechas; si solo existe marca precalculada, usar la marca y mostrar advertencia de que no se recalculó desde HIS crudo.

---

## 7. Reglas oficiales por componente - fuente de verdad para fase 2

Todas las fechas/rangos son inclusivos.

---

### 7.1 Vacuna antineumocócica

| Campo | Valor |
|---|---|
| Código interno | `neumococo` |
| Códigos HIS | `90670`, `90677` |
| Nota 2026 | Se incorpora vacuna antineumocócica 20-valente con código `90677`; `90670` se mantiene para búsqueda. |

| Edad al corte | Exigencia | Condición de dosis |
|---|---|---|
| `0-119` | No exige dosis | `programado` / cumple para paquete parcial. |
| `120-189` | 1 dosis | Primera dosis aplicada con edad de atención `55-119` días. |
| `190-364` | 2 dosis | Segunda dosis con intervalo `28-70` días después de la primera. |

Motivos:

| Código | Descripción |
|---|---|
| `NEUM-01` | Sin primera dosis exigible. |
| `NEUM-02` | Sin segunda dosis exigible. |
| `NEUM-03` | Segunda dosis fuera del intervalo permitido. |

---

### 7.2 Vacuna rotavirus

| Campo | Valor |
|---|---|
| Código interno | `rotavirus` |
| Código HIS | `90681` |
| Edad máxima de aplicación | `240` días. |

> **Corrección importante:** rotavirus no usa la misma ventana de neumococo/pentavalente. La ficha establece `0-210` como no exigible, `211-240` para una dosis y `241-364` para dos dosis acumuladas.

| Edad al corte | Exigencia | Condición de dosis |
|---|---|---|
| `0-210` | No exige dosis | `programado` / cumple para paquete parcial. |
| `211-240` | 1 dosis | Primera dosis aplicada con edad de atención `55-210` días. |
| `241-364` | 2 dosis | Segunda dosis con intervalo mínimo de `28` días después de la primera y edad de atención `<=240` días. |

Motivos:

| Código | Descripción |
|---|---|
| `ROTA-01` | Sin primera dosis exigible para niño/a de `211-240` días. |
| `ROTA-02` | Sin segunda dosis exigible para niño/a de `241-364` días. |
| `ROTA-03` | Dosis registrada luego de los 240 días o fuera de ventana. |

---

### 7.3 Vacuna antipolio

| Campo | Valor |
|---|---|
| Código interno | `antipolio` |
| Códigos HIS | `90712`, `90713` |

> **Corrección importante:** antipolio usa la ventana `0-119`, `120-189`, `190-259`, `260-364`. No debe usar la ventana de rotavirus `0-210`, `211-240`, `241-364`.

| Edad al corte | Exigencia | Condición de dosis |
|---|---|---|
| `0-119` | No exige dosis | `programado` / cumple para paquete parcial. |
| `120-189` | 1 dosis | Primera dosis aplicada con edad de atención `55-119` días. |
| `190-259` | 2 dosis | Segunda dosis con intervalo `28-70` días después de la primera. |
| `260-364` | 3 dosis | Tercera dosis con intervalo `28-70` días después de la segunda. |

Motivos:

| Código | Descripción |
|---|---|
| `POLIO-01` | Sin primera dosis exigible. |
| `POLIO-02` | Sin segunda dosis exigible. |
| `POLIO-03` | Sin tercera dosis exigible. |
| `POLIO-04` | Dosis fuera del intervalo permitido. |

---

### 7.4 Vacuna pentavalente

| Campo | Valor |
|---|---|
| Código interno | `pentavalente` |
| Códigos HIS | `90722`, `90723` |
| Nota | `90723` se usa solo con fines de búsqueda; el código vigente es `90722`. |

| Edad al corte | Exigencia | Condición de dosis |
|---|---|---|
| `0-119` | No exige dosis | `programado` / cumple para paquete parcial. |
| `120-189` | 1 dosis | Primera dosis aplicada con edad de atención `55-119` días. |
| `190-259` | 2 dosis | Segunda dosis con intervalo `28-70` días después de la primera. |
| `260-364` | 3 dosis | Tercera dosis con intervalo `28-70` días después de la segunda. |

Motivos:

| Código | Descripción |
|---|---|
| `PENTA-01` | Sin primera dosis exigible. |
| `PENTA-02` | Sin segunda dosis exigible. |
| `PENTA-03` | Sin tercera dosis exigible. |
| `PENTA-04` | Dosis fuera del intervalo permitido. |

---

### 7.5 Entrega de hierro

El componente de hierro debe dividirse internamente en dos subcomponentes para seguimiento operativo:

1. `hierro_4m`: suplementación preventiva de 4 meses.
2. `hierro_6m`: suplementación/tratamiento de 6 a 11 meses.

Para cumplir el paquete local:

- Si `edad_dias < 131`: no se exige hierro.
- Si `131 <= edad_dias <= 209`: se exige `hierro_4m`.
- Si `210 <= edad_dias <= 364`: se exige `hierro_4m` y también `hierro_6m`.

#### 7.5.1 Códigos y exclusiones

| Tipo | Códigos/reglas |
|---|---|
| Suplementación con hierro | `99199.17` |
| Suplementación con multimicronutrientes | `99199.19` |
| Tratamiento de anemia | Diagnóstico `D509` o `D649` + CPMS `99199.17` |
| Exclusión común | Excluir registros con `99499` telemedicina. |
| LAB visita familiar | Válidos: `PO1-PO6`, `P01-P06`, `SF1-SF6`, `1-6`. |

Reglas LAB:

- Entrega sin LAB: válida solo cuando no está vinculada a visita familiar.
- Entrega con LAB: válida solo cuando está vinculada a visita familiar.
- En la primera entrega preventiva, buscar que no esté vinculada a diagnóstico de anemia.
- En la primera entrega de tratamiento, buscar que sí esté vinculada a diagnóstico `D509` o `D649`, con diagnóstico definitivo `D` en la misma cita.
- En las siguientes entregas de tratamiento no se vuelve a exigir diagnóstico de anemia.

#### 7.5.2 `hierro_4m` - suplementación preventiva 4 meses

| Edad al corte | Exigencia | Ventana de atención |
|---|---|---|
| `0-130` | No exige entrega | `programado` / cumple para paquete parcial. |
| `131-364` | 1 entrega | Entrega entre `110-130` días de edad. |

En fase Excel se usa `obs_suple41`.

Motivos:

| Código | Descripción |
|---|---|
| `HIERRO4-01` | Niño/a de 131 días o más sin entrega preventiva de 4 meses. |
| `HIERRO4-02` | Entrega de 4 meses fuera de edad `110-130` días. |
| `HIERRO4-03` | Registro excluido por telemedicina `99499`. |

#### 7.5.3 `hierro_6m` - tratamiento de anemia

Aplicar esta ruta cuando existe anemia registrada para la primera entrega.

| Edad al corte | Exigencia acumulada | Ventana/intervalo |
|---|---:|---|
| `0-209` | No exige entrega de 6 meses | `programado` / cumple para paquete parcial. |
| `210-279` | 1 entrega | Primera entrega entre `170-209` días. |
| `280-349` | 2 entregas | Segunda entrega `25-70` días después de la primera. |
| `350-364` | 3 entregas | Tercera entrega `25-70` días después de la segunda. |

Reglas adicionales:

- Primera entrega: `D509` o `D649` + `99199.17` en la misma cita.
- Diagnóstico de anemia debe ser definitivo `D` cuando el campo exista.
- Excluir `99199.17 + LAB TA` en la primera entrega.
- Excluir `99499` telemedicina.

Motivos:

| Código | Descripción |
|---|---|
| `HIERRO6T-01` | Sin primera entrega de tratamiento exigible. |
| `HIERRO6T-02` | Tratamiento con menos entregas acumuladas de las requeridas por edad. |
| `HIERRO6T-03` | Primera entrega sin diagnóstico `D509`/`D649`. |
| `HIERRO6T-04` | Intervalo entre entregas fuera de `25-70` días. |
| `HIERRO6T-05` | Registro excluido por telemedicina o LAB TA en primera entrega. |

#### 7.5.4 `hierro_6m` - suplementación preventiva solo hierro

Aplicar cuando no existe ruta de tratamiento por anemia.

| Edad al corte | Exigencia acumulada | Ventana/intervalo |
|---|---:|---|
| `0-209` | No exige entrega de 6 meses | `programado` / cumple para paquete parcial. |
| `210-279` | 1 entrega | Primera entrega entre `170-209` días. |
| `280-364` | 2 entregas | Segunda entrega `25-70` días después de la primera. |

Reglas adicionales:

- Usa `99199.17`.
- Primera entrega no debe estar vinculada a diagnóstico de anemia.
- Excluir `99199.17 + LAB TA` en la primera entrega.
- Excluir `99499` telemedicina.

#### 7.5.5 `hierro_6m` - suplementación combinada hierro + multimicronutrientes

| Edad al corte | Exigencia acumulada | Ventana/intervalo |
|---|---:|---|
| `0-209` | No exige entrega de 6 meses | `programado` / cumple para paquete parcial. |
| `210-244` | 1 entrega | Primera entrega entre `170-209` días. |
| `245-364` | 2 entregas | Segunda entrega `25-35` días después de la primera. |

Reglas adicionales:

- Combinación válida: `99199.19` + `99199.17`, en cualquier orden válido según ficha.
- Si la primera entrega es micronutriente, no debe estar vinculada a anemia.
- Excluir `99199.19 + LAB TA` en primera entrega cuando corresponda.
- Excluir `99499` telemedicina.

#### 7.5.6 `hierro_6m` - solo multimicronutrientes

| Edad al corte | Exigencia acumulada | Ventana/intervalo |
|---|---:|---|
| `0-209` | No exige entrega de 6 meses | `programado` / cumple para paquete parcial. |
| `210-244` | 1 entrega | Primera entrega entre `170-209` días. |
| `245-279` | 2 entregas | Segunda entrega `25-35` días después de la primera. |
| `280-314` | 3 entregas | Tercera entrega `25-35` días después de la segunda. |
| `315-349` | 4 entregas | Cuarta entrega `25-35` días después de la tercera. |
| `350-363` | 5 entregas | Quinta entrega `25-35` días después de la cuarta. |
| `364` | 6 entregas | Sexta entrega `25-35` días después de la quinta. |

Reglas adicionales:

- Usa `99199.19`.
- Primera entrega no debe estar vinculada a diagnóstico de anemia.
- Excluir `99199.19 + LAB TA` en primera entrega.
- Excluir `99499` telemedicina.

#### 7.5.7 Evaluación final de hierro 6 meses

```python
hierro_6m_cumple = tratamiento_anemia_cumple or preventivo_hierro_cumple or combinado_cumple or solo_micronutrientes_cumple
```

En fase Excel se usa `obs_suple61`, pero el sistema debe conservar datos de anemia como alerta de auditoría.

---

### 7.6 Dosaje de hemoglobina

| Campo | Valor |
|---|---|
| Código interno | `hemoglobina` |
| Códigos HIS | `85018`, `85018.01`, `85031` |
| Marca Excel | `Obs_dh1` |

| Edad al corte | Exigencia | Ventana de atención |
|---|---|---|
| `0-209` | No exige dosaje vencido | Programado. Si existe dosaje válido entre 170-209, mostrar `cumple`. |
| `210-364` | 1 dosaje | Dosaje registrado cuando el niño/a tenía `170-209` días. |

Motivos:

| Código | Descripción |
|---|---|
| `HEMO-01` | Niño/a de 210 días o más sin dosaje. |
| `HEMO-02` | Dosaje registrado fuera de edad `170-209` días. |
| `HEMO-03` | Código de dosaje no válido. |

---

### 7.7 DNI emitido - criterio oficial no evaluado localmente

La ficha oficial considera DNI emitido hasta los 30 días de nacido.

| Edad al corte oficial | Exigencia oficial |
|---|---|
| `0-30` | No exige vencimiento. |
| `31-364` | DNI emitido con diferencia `0-30` días desde fecha de nacimiento. |

**Implementación local:** no evaluar este componente. No crear incumplimientos por DNI. Puede mostrarse únicamente como dato informativo si existe fuente RENIEC.

---

## 8. Estados estándar del sistema

Usar estos valores de estado para todos los componentes.

| Estado | Uso |
|---|---|
| `cumple` | Cumple el componente según edad y regla. |
| `programado` | Aún no es exigible por edad; no penaliza numerador parcial. |
| `pendiente_en_plazo` | Ya inició la ventana de cumplimiento, todavía puede completarse dentro del plazo. |
| `incumplimiento_fuera_plazo` | No cumple y ya venció la ventana normativa. |
| `fuera_de_ventana` | Existe atención, pero fuera de edad/intervalo permitido. |
| `dato_insuficiente` | Falta dato mínimo para evaluar. |
| `excluido_denominador` | No entra al denominador. |

---

## 9. Algoritmo general de evaluación

```python
def evaluar_mc02_paciente(paciente, atenciones, fecha_corte):
    resultado = {
        "id_paciente": paciente.id,
        "edad_dias": calcular_edad(paciente.fecha_nacimiento, fecha_corte),
        "denominador": False,
        "numerador_local": False,
        "componentes": {},
        "motivos": [],
        "alertas": [],
    }

    denominador = evaluar_denominador(paciente, fecha_corte)
    resultado["denominador"] = denominador.incluido
    resultado["motivos"].extend(denominador.motivos)

    if not denominador.incluido:
        return resultado

    eventos = deduplicar_misma_prestacion_por_dia(atenciones)

    componentes = {
        "neumococo": evaluar_neumococo(paciente, eventos, fecha_corte),
        "rotavirus": evaluar_rotavirus(paciente, eventos, fecha_corte),
        "antipolio": evaluar_antipolio(paciente, eventos, fecha_corte),
        "pentavalente": evaluar_pentavalente(paciente, eventos, fecha_corte),
        "hierro_4m": evaluar_hierro_4m(paciente, eventos, fecha_corte),
        "hierro_6m": evaluar_hierro_6m(paciente, eventos, fecha_corte),
        "hemoglobina": evaluar_hemoglobina(paciente, eventos, fecha_corte),
    }

    resultado["componentes"] = componentes
    resultado["numerador_local"] = all(
        c.cumple_para_paquete for c in componentes.values()
    )

    for codigo, componente in componentes.items():
        if not componente.cumple_para_paquete:
            resultado["motivos"].extend(componente.motivos)

    return resultado
```

### 9.1 Regla `cumple_para_paquete`

```python
cumple_para_paquete = estado in ["cumple", "programado"]
```

Solo cuando `programado` significa realmente no exigible por edad. Si el componente ya es exigible y no cumple, debe ser `pendiente_en_plazo` o `incumplimiento_fuera_plazo`, según corresponda.

---

## 10. Deduplicación de prestaciones

Se contabiliza como máximo una misma prestación por día.

Regla recomendada:

```python
clave = (id_paciente, fecha_atencion, codigo_his_normalizado)
```

Si hay duplicados con la misma clave:

1. Conservar uno para conteo.
2. Mantener todos en auditoría si se necesita trazabilidad.
3. Registrar advertencia `DUP-01` cuando el duplicado afecte una evaluación.

Dosis distintas el mismo día con códigos distintos no se eliminan entre sí.

---

## 11. Resultado esperado por paciente

La API o función principal debe devolver una estructura similar a esta.

```json
{
  "id_paciente": "string",
  "tipo_documento": "DNI|CNV",
  "nombres": "string|null",
  "fecha_nacimiento": "YYYY-MM-DD",
  "edad_dias_corte": 0,
  "mes_nac": "YYYY-MM|null",
  "provincia": "ABANCAY",
  "distrito": "string|null",
  "establecimiento": "string|null",
  "denominador": true,
  "numerador_local": false,
  "porcentaje_paquete": 0,
  "componentes": {
    "neumococo": {"estado": "cumple", "cumple_para_paquete": true, "motivos": []},
    "rotavirus": {"estado": "programado", "cumple_para_paquete": true, "motivos": []},
    "antipolio": {"estado": "incumplimiento_fuera_plazo", "cumple_para_paquete": false, "motivos": ["POLIO-03"]},
    "pentavalente": {"estado": "cumple", "cumple_para_paquete": true, "motivos": []},
    "hierro_4m": {"estado": "cumple", "cumple_para_paquete": true, "motivos": []},
    "hierro_6m": {"estado": "pendiente_en_plazo", "cumple_para_paquete": false, "motivos": ["HIERRO6P-01"]},
    "hemoglobina": {"estado": "programado", "cumple_para_paquete": true, "motivos": []}
  },
  "motivos_resumen": ["POLIO-03", "HIERRO6P-01"],
  "alertas": ["No se evaluó DNI por decisión local"],
  "fuente": "excel_operativo|his_crudo"
}
```

---

## 12. Dashboard esperado

### 12.1 Indicadores principales

| Indicador | Cálculo |
|---|---|
| Denominador | Total de niños/as incluidos. |
| Numerador local | Total de niños/as del denominador que cumplen paquete local. |
| Avance local | `numerador_local / denominador * 100`. |
| Brecha | `denominador - numerador_local`. |
| Meta | `80.9%` por defecto, configurable. |

### 12.2 Agrupaciones recomendadas

- Por `Mes_Nac` / cohorte de nacimiento.
- Por distrito.
- Por establecimiento, si existe campo confiable.
- Por componente incumplido.
- Por edad actual en días o tramo de edad.
- Por tipo de seguro.
- Por condición de alerta de anemia.

### 12.3 Interpretación por cohorte

MC-02 no debe interpretarse como atenciones realizadas solo en el mes calendario. El avance mensual por `Mes_Nac` representa el cumplimiento acumulado de una cohorte de nacimiento al corte de evaluación.

---

## 13. Arquitectura sugerida de backend

Estructura recomendada:

```text
backend/
  indicators/
    mc02/
      __init__.py
      config.py
      constants.py
      schema.py
      rules.py
      utils.py
      excel_loader.py
      denominator.py
      evaluator.py
      vaccines.py
      iron.py
      hemoglobin.py
      messages.py
      dashboard.py
      processor.py
      tests/
        test_mc02_rules.py
```

### 13.1 Responsabilidades por módulo

| Módulo | Responsabilidad |
|---|---|
| `config.py` | Contrato del Excel operativo, columnas, reglas de negocio y valores por defecto. |
| `constants.py` | Códigos HIS, rangos de edad, ventanas, estados, motivos. |
| `schema.py` | Modelos o notas de contrato especificas del indicador cuando no correspondan al esquema global. |
| `rules.py` | Alias operativos de reglas usadas por procesadores y validadores. |
| `utils.py` | Fechas, normalización de texto, normalización de flags, conversión numérica. |
| `excel_loader.py` | Lectura de Excel, hoja `Detalle_Ate`, fecha `D9`, encabezados fila 10. |
| `denominator.py` | Inclusión/exclusión del denominador. |
| `vaccines.py` | Neumococo, rotavirus, antipolio y pentavalente. |
| `iron.py` | Hierro 4m, hierro 6m, prevención, tratamiento, micronutrientes. |
| `hemoglobin.py` | Dosaje de hemoglobina. |
| `evaluator.py` | Orquestación por paciente. |
| `dashboard.py` | Agregaciones, avance, brechas y motivos. |
| `messages.py` | Diccionario de mensajes de incumplimiento y alertas. |
| `processor.py` | Fachada publica del indicador para la plataforma multiindicador. |

---

## 14. Constantes recomendadas

```python
CODIGOS = {
    "neumococo": ["90670", "90677"],
    "rotavirus": ["90681"],
    "antipolio": ["90712", "90713"],
    "pentavalente": ["90722", "90723"],
    "hierro": ["99199.17"],
    "micronutrientes": ["99199.19"],
    "telemedicina_excluir": ["99499"],
    "anemia_dx": ["D509", "D649"],
    "hemoglobina": ["85018", "85018.01", "85031"],
}

VENTANAS_VACUNAS = {
    "neumococo": [
        {"edad_corte": [0, 119], "dosis_requeridas": 0},
        {"edad_corte": [120, 189], "dosis_requeridas": 1, "edad_dosis_1": [55, 119]},
        {"edad_corte": [190, 364], "dosis_requeridas": 2, "intervalo": [28, 70]},
    ],
    "rotavirus": [
        {"edad_corte": [0, 210], "dosis_requeridas": 0},
        {"edad_corte": [211, 240], "dosis_requeridas": 1, "edad_dosis_1": [55, 210]},
        {"edad_corte": [241, 364], "dosis_requeridas": 2, "intervalo_min": 28, "edad_max_dosis": 240},
    ],
    "antipolio": [
        {"edad_corte": [0, 119], "dosis_requeridas": 0},
        {"edad_corte": [120, 189], "dosis_requeridas": 1, "edad_dosis_1": [55, 119]},
        {"edad_corte": [190, 259], "dosis_requeridas": 2, "intervalo": [28, 70]},
        {"edad_corte": [260, 364], "dosis_requeridas": 3, "intervalo": [28, 70]},
    ],
    "pentavalente": [
        {"edad_corte": [0, 119], "dosis_requeridas": 0},
        {"edad_corte": [120, 189], "dosis_requeridas": 1, "edad_dosis_1": [55, 119]},
        {"edad_corte": [190, 259], "dosis_requeridas": 2, "intervalo": [28, 70]},
        {"edad_corte": [260, 364], "dosis_requeridas": 3, "intervalo": [28, 70]},
    ],
}
```

---

## 15. Pruebas mínimas de aceptación

Crear pruebas unitarias para estos casos.

### 15.1 Denominador

| Caso | Esperado |
|---|---|
| Niño 364 días, SIS, ABANCAY, Registros=1 | Incluido. |
| Niño 365 días | Excluido por edad. |
| Peso 2499 | Excluido por bajo peso. |
| Peso vacío | No excluir por bajo peso. |
| Edad gestacional 36 | Excluido por prematuridad. |
| Edad gestacional vacía | No excluir por prematuridad. |
| Seguro SIS | Incluido. |
| Seguro NINGUNO o vacío | Incluido como sin seguro. |

### 15.2 Vacunas

| Caso | Esperado |
|---|---|
| Rotavirus, niño 150 días sin dosis | `programado`, no incumple. |
| Rotavirus, niño 220 días sin dosis | Incumple primera dosis: `ROTA-01`. |
| Rotavirus, segunda dosis a edad 245 días | Fuera de ventana: `ROTA-03`. |
| Antipolio, niño 150 días sin dosis | Incumple primera dosis: `POLIO-01`. |
| Antipolio, niño 220 días con 1 dosis | Incumple segunda dosis. |
| Pentavalente, niño 270 días con 2 dosis | Incumple tercera dosis: `PENTA-03`. |
| Neumococo, segunda dosis 20 días después de primera | Fuera de intervalo: `NEUM-03`. |

### 15.3 Hierro

| Caso | Esperado |
|---|---|
| Niño 120 días sin hierro 4m | `programado`. |
| Niño 150 días sin hierro 4m | Incumple `HIERRO4-01`. |
| Hierro 4m entregado a 100 días | Fuera de ventana `HIERRO4-02`. |
| Niño 230 días sin hierro 6m | Incumple primera entrega de 6m. |
| Tratamiento anemia con primera entrega sin D509/D649 | Incumple `HIERRO6T-03`. |
| Micronutrientes segunda entrega 15 días después | Fuera de intervalo. |
| Registro 99499 telemedicina | No cuenta. |

### 15.4 Hemoglobina

| Caso | Esperado |
|---|---|
| Niño 190 días sin dosaje | `programado` o pendiente informativo, no incumple como vencido. |
| Niño 230 días sin dosaje | Incumple `HEMO-01`. |
| Dosaje a 160 días | Fuera de ventana `HEMO-02`. |
| Dosaje a 180 días | Cumple. |

---

## 16. Errores detectados en versiones anteriores y correcciones aplicadas

| Tema | Problema detectado | Corrección en este documento |
|---|---|---|
| Rotavirus | Se documentó con ventana similar a neumococo/pentavalente. | Se corrigió a `0-210`, `211-240`, `241-364`, con máximo de aplicación 240 días. |
| Antipolio | En el markdown actual aparecía con ventana de rotavirus. | Se corrigió a `0-119`, `120-189`, `190-259`, `260-364`. |
| Hierro 4 meses | Se describió como aplicable hasta 209 días. | Se corrigió: no exigible `0-130`, exige una entrega desde `131-364`, con atención entre `110-130`. |
| Hierro 6 meses | Faltaban rangos etarios acumulados completos. | Se separó tratamiento, preventivo solo hierro, combinado y solo micronutrientes. |
| DNI | Aparece en la ficha oficial. | Se mantiene documentado como criterio oficial, pero excluido localmente del numerador. |
| CRED | Aparece en Excel operativo, pero no en definición del paquete MC-02 revisado. | Se omite del cálculo y queda solo como auditoría/futuro. |
| `Estado` Excel | Podría incluir DNI u otros criterios. | No usar directamente para numerador local. |

---

## 17. Instrucciones explícitas para Codex

Cuando Codex modifique el sistema:

1. No debe inventar nuevas reglas de negocio.
2. No debe usar `Estado` como numerador final local.
3. No debe considerar DNI como incumplimiento local.
4. No debe incluir CRED en el numerador MC-02 actual.
5. Debe centralizar rangos, códigos HIS y motivos en constantes.
6. Debe escribir pruebas para los límites de edad: 119, 120, 130, 131, 189, 190, 209, 210, 211, 240, 241, 259, 260, 279, 280, 349, 350, 363, 364 y 365 días.
7. Debe tratar todos los rangos como inclusivos.
8. Debe devolver motivos de incumplimiento legibles y códigos internos.
9. Debe dejar advertencias cuando una columna necesaria del Excel no exista.
10. Debe mantener separada la lógica de fase Excel y la lógica futura de HIS crudo.

---

## 18. Prompt sugerido para usar en Codex

```text
Usa el archivo MC02_sistema_seguimiento_Abancay_Codex.md como fuente funcional del indicador MC-02.01.

Objetivo:
Corregir/refactorizar el backend para calcular el denominador, numerador local y seguimiento nominal del indicador MC-02.01 para la Red de Salud Abancay.

Restricciones:
- No uses la columna Estado para el numerador local.
- No evalúes DNI como componente local.
- No incluyas CRED en el numerador MC-02.
- Usa las marcas precalculadas del Excel en fase 1.
- Deja preparada la arquitectura para recalcular desde HIS crudo en fase 2.
- Centraliza reglas en constantes.
- Agrega pruebas unitarias para límites de edad y ventanas.

Primero revisa el código actual, identifica dónde se calcula MC-02 y luego aplica los cambios de forma incremental.
Antes de modificar, enumera los archivos que vas a tocar y la razón.
Después de modificar, ejecuta o propone pruebas.
```

---

## 19. Checklist final de implementación

- [ ] Carga Excel `Detalle_Ate` con encabezados fila 10.
- [ ] Obtiene fecha de corte desde `D9`.
- [ ] Filtra `provincia = ABANCAY` por defecto.
- [ ] Calcula edad al corte.
- [ ] Evalúa denominador con seguro SIS/sin seguro.
- [ ] Excluye bajo peso y prematuridad solo con evidencia explícita.
- [ ] Recalcula numerador desde componentes, no desde `Estado`.
- [ ] Omite DNI del numerador local.
- [ ] Omite CRED del numerador actual.
- [ ] Corrige rotavirus con ventana `0-210`, `211-240`, `241-364`.
- [ ] Corrige antipolio con ventana `0-119`, `120-189`, `190-259`, `260-364`.
- [ ] Corrige hierro 4m desde `131-364`, atención `110-130`.
- [ ] Evalúa hierro 6m por rutas.
- [ ] Evalúa hemoglobina `170-209`, exigible desde 210.
- [ ] Deduplica misma prestación por día.
- [ ] Muestra motivos nominales de incumplimiento.
- [ ] Agrupa dashboard por `Mes_Nac`.
- [ ] Incluye pruebas unitarias de límites.
