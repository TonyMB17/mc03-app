# Sistema de Seguimiento — Indicador MC-03.01
## Red de Salud Abancay — Versión Codex-friendly

> **Objetivo del documento:** servir como base técnica para que Codex implemente, refactorice o corrija el módulo del indicador **MC-03.01** en el sistema de seguimiento de la Red de Salud Abancay.  
> **Fuente normativa principal:** Ficha Técnica MC-03 — Paquete Recién Nacido, procesamiento GORE, versión revisada octubre 2025.  
> **Documentacion consolidada:** este archivo reemplaza los antiguos `logic_rules.md` y `README_MC03.md`; `config.py` conserva la configuracion operativa.  
> **Principio de implementación:** cuando exista conflicto entre archivos locales y ficha técnica, prevalece la ficha técnica. Cuando exista conflicto entre ficha técnica y configuración operativa local, dejar la regla parametrizable y documentar la decisión.

---

# 1. Identificación del indicador

| Campo | Valor |
|---|---|
| Código de meta | `MC-03` |
| Código de indicador | `MC-03.01` |
| Nombre | Porcentaje de recién nacidos del departamento que reciben vacunas BCG, HvB, controles CRED y tamizaje neonatal |
| Meta de cobertura | Recién nacidos del departamento reciben vacunas BCG, HvB, controles CRED y tamizaje neonatal |
| Periodicidad | Mensual |
| Periodo de medición | Desde el primer día hasta el último día del mes |
| Verificación 2026 | Noviembre 2026, considerando los meses de junio, julio, agosto, setiembre, octubre y noviembre 2026 |
| Criterio de cumplimiento del compromiso | La región cumple cuando alcanza la meta en 5 de los 6 meses del periodo de verificación |
| Niveles de desagregación | Nacional, departamental, provincial y distrital |
| Fuente numerador | HIS MINSA |
| Fuente denominador | Padrón Nominal de niñas y niños menores de 6 años y CNV en línea |
| Instrumento | Registro Diario de Atención y Otras Actividades de Salud — HIS |

---

# 2. Definición operativa local para Red de Salud Abancay

El sistema debe evaluar recién nacidos pertenecientes al ámbito de la **Red de Salud Abancay**.

## 2.1 Filtro territorial local

Para la implementación local, usar filtros configurables:

```python
FILTRO_TERRITORIAL_DEFAULT = {
    "provincia": "ABANCAY"
}
```

Regla recomendada:

1. Si el Excel trae `Desc_prov`, filtrar por `ABANCAY`.
2. Si el sistema se usa a nivel regional, no quemar el filtro territorial en el código; exponerlo como parámetro.

---

# 3. Fórmula de cálculo

```text
MC-03.01 (%) = (Numerador / Denominador) × 100
```

## 3.1 Denominador

Cantidad de recién nacidos que:

1. Cumplen **29 días de vida** dentro del mes de medición.
2. Están registrados en el Padrón Nominal con `DNI` o `CNV en línea`.
3. Cuentan con registro en `CNV en línea`.
4. Tienen tipo de seguro `SIS` o `Sin seguro`.
5. No están excluidos por bajo peso al nacer o prematuridad.

## 3.2 Numerador

Cantidad de recién nacidos del denominador que cumplen **todos** los componentes:

1. Vacuna BCG dentro de las 24 horas de nacido.
2. Vacuna HvB dentro de las 24 horas de nacido.
3. Tres controles CRED dentro de las ventanas normativas.
4. Tamizaje neonatal desde las 48 horas hasta los 6 días de nacido.

---

# 4. Denominador detallado

## 4.1 Regla de edad: cumple 29 días en el mes

Un recién nacido pertenece al denominador del mes si:

```python
fecha_29_dias = fecha_nacimiento + timedelta(days=29)
inicio_mes <= fecha_29_dias <= fin_mes
```

Ejemplo:

| Fecha de nacimiento | Fecha en que cumple 29 días | Mes de medición |
|---|---:|---|
| 2026-06-01 | 2026-06-30 | Junio 2026 |
| 2026-06-02 | 2026-07-01 | Julio 2026 |
| 2026-10-31 | 2026-11-29 | Noviembre 2026 |

> No usar simplemente `Mes_eva` si se puede calcular con `fec_Nac`. `Mes_eva` puede usarse como respaldo operativo cuando el Excel ya viene preprocesado.

## 4.2 Seguros incluidos

Normalizar el texto antes de comparar.

```python
SEGUROS_INCLUIDOS = {
    "SIS",
    "SIN SEGURO",
    "SIN_SEGURO",
    "NINGUNO",
    ""
}
```

Regla:

- `SIS` cuenta.
- `SIN SEGURO`, `SIN_SEGURO`, `NINGUNO` y celda vacía pueden interpretarse como sin seguro, según decisión operativa local.
- Otros seguros no forman parte del denominador.

## 4.3 Exclusiones

Excluir del denominador si existe evidencia de:

| Criterio | Regla |
|---|---|
| Bajo peso al nacer | `peso < 2500` gramos |
| Prematuridad | `edad_gestacional < 37` semanas |

Tratamiento recomendado para datos vacíos:

- Si `peso` está vacío, **no excluir automáticamente**; marcar `dato_peso_faltante`.
- Si `edad_gestacional` está vacío, **no excluir automáticamente**; marcar `dato_gestacional_faltante`.
- La exclusión debe aplicarse solo cuando el dato existe y está bajo el umbral.
- Agregar alertas de calidad de datos para revisión operativa.

Estados sugeridos para denominador:

```text
incluido_denominador
fuera_denominador_edad
fuera_denominador_seguro
excluido_bajo_peso
excluido_prematuro
dato_incompleto_nacimiento
```

---

# 5. Componentes del numerador

Un recién nacido cumple MC-03.01 si cumple los cuatro bloques:

```text
cumple_mc03 = cumple_bcg
           AND cumple_hvb
           AND cumple_cred_1
           AND cumple_cred_2
           AND cumple_cred_3
           AND cumple_tamizaje
```

No usar `Obs_General` como única fuente del numerador. El sistema debe recalcular o validar el cumplimiento desde los componentes. Las columnas `Obs_*` pueden usarse para auditoría, comparación o explicación.

---

## 5.1 Componente A — Vacuna BCG

| Campo | Valor |
|---|---|
| Código HIS | `90585` |
| Plazo | Dentro de las 24 horas de nacido |
| Fuente operativa Excel | `fec1_BCG`, `Edad_ate1_BCG`, `BCG_1_1`, `reg_BCG1`, `eess_BCG1`, `Obs_BCG` |

### Regla principal

Con fecha y hora:

```python
edad_horas = fecha_hora_atencion - fecha_hora_nacimiento
cumple_bcg = codigo == "90585" and 0 <= edad_horas <= 24
```

Con solo fechas:

```python
edad_dias = fecha_atencion.date() - fecha_nacimiento.date()
cumple_bcg = codigo == "90585" and edad_dias in [0, 1]
```

> Si solo existe edad en días, documentar que se aplica aproximación por día calendario. El sistema debe preferir fecha/hora cuando esté disponible.

### Motivos de incumplimiento

| Código | Motivo |
|---|---|
| `BCG-01` | No registra vacuna BCG |
| `BCG-02` | Registra BCG fuera de las 24 horas |
| `BCG-03` | Código BCG inválido o no corresponde a `90585` |
| `BCG-04` | Fecha de BCG inválida o menor a fecha de nacimiento |

---

## 5.2 Componente B — Vacuna HvB

| Campo | Valor |
|---|---|
| Código HIS | `90744` |
| Plazo | Dentro de las 24 horas de nacido |
| Fuente operativa Excel | `fecHVB`, `Edad_ateHVB`, `sg_HVB`, `reg_HVB`, `eess_HVB`, `Obs_HVB` |

### Regla principal

Con fecha y hora:

```python
edad_horas = fecha_hora_atencion - fecha_hora_nacimiento
cumple_hvb = codigo == "90744" and 0 <= edad_horas <= 24
```

Con solo fechas:

```python
edad_dias = fecha_atencion.date() - fecha_nacimiento.date()
cumple_hvb = codigo == "90744" and edad_dias in [0, 1]
```

### Motivos de incumplimiento

| Código | Motivo |
|---|---|
| `HVB-01` | No registra vacuna HvB |
| `HVB-02` | Registra HvB fuera de las 24 horas |
| `HVB-03` | Código HvB inválido o no corresponde a `90744` |
| `HVB-04` | Fecha de HvB inválida o menor a fecha de nacimiento |

---

## 5.3 Componente C — Controles CRED neonatal

| Campo | Valor |
|---|---|
| Código HIS vigente | `99381.01` |
| Cantidad requerida | 3 controles |
| Edad máxima | Hasta los 21 días de nacido |
| LAB | Se evalúa independiente del LAB |
| Intervalo mínimo | 7 días entre controles |
| Control adicional | `CRED_4` puede conservarse para auditoría, pero no suma al numerador principal |

### Ventanas normativas

| Control | Ventana de edad | Regla |
|---|---:|---|
| 1er CRED | 3 a 6 días | `3 <= edad_dias <= 6` |
| 2do CRED | 7 a 14 días | `7 <= edad_dias <= 14` |
| 3er CRED | 15 a 21 días | `15 <= edad_dias <= 21` |

### Regla de intervalo mínimo

Además de la ventana, debe cumplirse:

```python
fecha_cred_2 - fecha_cred_1 >= 7 días
fecha_cred_3 - fecha_cred_2 >= 7 días
```

### Asignación recomendada de controles

Si el Excel trae CRED preclasificados (`CRED_1`, `CRED_2`, `CRED_3`), validar cada bloque.

Si se procesa HIS crudo:

1. Filtrar atenciones del niño con código `99381.01`.
2. Eliminar duplicados de la misma prestación en la misma fecha.
3. Calcular edad en días en cada atención.
4. Asignar cada atención a la ventana correspondiente.
5. Elegir la primera atención válida por ventana.
6. Verificar intervalo mínimo de 7 días entre los controles seleccionados.
7. No usar LAB para invalidar CRED.

### Motivos de incumplimiento

| Código | Motivo |
|---|---|
| `CRED-01` | No registra 1er CRED entre 3 y 6 días |
| `CRED-02` | No registra 2do CRED entre 7 y 14 días |
| `CRED-03` | No registra 3er CRED entre 15 y 21 días |
| `CRED-04` | Algún CRED tiene código distinto de `99381.01` |
| `CRED-05` | Intervalo menor a 7 días entre controles |
| `CRED-06` | Fecha de CRED inválida o menor a fecha de nacimiento |
| `CRED-07` | Registro duplicado en la misma fecha; se contabilizó solo una prestación |
| `CRED-08` | Tiene CRED fuera de ventana, no válido para numerador |

---

## 5.4 Componente D — Tamizaje neonatal

| Campo | Valor |
|---|---|
| Código HIS | `36416` |
| Ventana | Desde las 48 horas hasta los 6 días de nacido |
| Edad equivalente con solo fechas | 2 a 6 días |
| Pruebas consideradas | Hipotiroidismo congénito, hiperplasia suprarrenal congénita, fenilcetonuria y fibrosis quística |
| Fuente operativa Excel | `Fecha_Atencion_TN`, `Lab_TN`, `Edad_Atencion_TN`, `Codigo_HIS_TN`, `Registro_TN`, `EESS_Atencion_TN`, `Obs_TM` |

### Regla principal

Con fecha y hora:

```python
edad_horas = fecha_hora_tamizaje - fecha_hora_nacimiento
cumple_tamizaje = codigo == "36416" and 48 <= edad_horas <= 144
```

Con solo fechas:

```python
edad_dias = fecha_tamizaje.date() - fecha_nacimiento.date()
cumple_tamizaje = codigo == "36416" and 2 <= edad_dias <= 6
```

### Motivos de incumplimiento

| Código | Motivo |
|---|---|
| `TAM-01` | No registra tamizaje neonatal |
| `TAM-02` | Tamizaje realizado antes de las 48 horas |
| `TAM-03` | Tamizaje realizado después de los 6 días |
| `TAM-04` | Código de tamizaje inválido o no corresponde a `36416` |
| `TAM-05` | Fecha de tamizaje inválida o menor a fecha de nacimiento |

---

# 6. Reglas transversales de procesamiento

## 6.1 Cálculo de edad

Implementar una utilidad única:

```python
def edad_dias(fecha_nacimiento, fecha_atencion) -> int:
    return (to_date(fecha_atencion) - to_date(fecha_nacimiento)).days
```

Para vacunas y tamizaje, si se tiene fecha/hora:

```python
def edad_horas(fecha_hora_nacimiento, fecha_hora_atencion) -> float:
    return (to_datetime(fecha_hora_atencion) - to_datetime(fecha_hora_nacimiento)).total_seconds() / 3600
```

## 6.2 Normalización de texto

Antes de comparar columnas de seguro, provincia, red, resultado u observaciones:

```python
def normalizar_texto(valor: object) -> str:
    if valor is None:
        return ""
    return str(valor).strip().upper()
```

## 6.3 Unicidad por prestación y día

Para HIS crudo:

```text
Un mismo paciente no debe contar dos veces la misma prestación en la misma fecha.
Clave sugerida: paciente_id + codigo_his + fecha_atencion
```

Para Excel preprocesado:

- Si hay columnas separadas por componente, no duplicar.
- Si se detectan múltiples registros de un mismo paciente, consolidar antes de calcular el numerador.

## 6.4 Estado de componente

Usar un contrato común para cada componente:

```json
{
  "componente": "BCG",
  "cumple": true,
  "estado": "cumple",
  "codigo_motivo": null,
  "mensaje": "BCG registrada oportunamente",
  "fecha_atencion": "2026-06-02",
  "edad_dias": 0,
  "edad_horas": 5.5,
  "codigo_his": "90585",
  "eess": "..."
}
```

Estados permitidos:

```text
cumple
no_cumple
pendiente_en_plazo
incumplimiento_fuera_plazo
dato_incompleto
no_aplica
```

Para el indicador oficial mensual, cuando el niño ya pertenece al denominador porque cumplió 29 días en el mes, todos los componentes ya deberían estar cerrados. Sin embargo, `pendiente_en_plazo` puede usarse en seguimiento operativo antes de finalizar el mes o cuando la fecha de corte aún no alcanza el vencimiento.

---

# 7. Estructura de datos esperada

## 7.1 Campos mínimos de paciente

| Campo canónico | Columnas posibles en Excel | Tipo | Uso |
|---|---|---|---|
| `id_paciente` | `afi_DNI`, `NumCNV`, `his_cli` | texto | Identificador principal |
| `dni` | `afi_DNI` | texto | Documento del niño |
| `cnv` | `NumCNV` | texto | CNV |
| `nombres` | `afi_nombres` | texto | Búsqueda nominal |
| `apellido_paterno` | `afi_appaterno` | texto | Búsqueda nominal |
| `apellido_materno` | `afi_apmaterno` | texto | Búsqueda nominal |
| `fecha_nacimiento` | `fec_Nac`, `Est_Nac` | fecha | Edad y denominador |
| `peso_nacer` | `peso` | número | Exclusión |
| `edad_gestacional` | `edadGEst` | número | Exclusión |
| `tipo_seguro` | `Obs_Eval`, `Esta_pac` o campo operativo equivalente | texto | Denominador |
| `provincia` | `Desc_prov` | texto | Filtro territorial |
| `distrito` | `Desc_Dist` | texto | Desagregación |
| `red` | `Des_Red` | texto | Filtro territorial |
| `microred` | `Des_MicroRed` | texto | Filtro |
| `eess_adscripcion` | `Des_EESS`, `pre_CodigoRENAES` | texto | Reporte |

> Revisar en el Excel real cuál columna contiene exactamente el tipo de seguro. En el `config.py` actual no aparece una columna llamada explícitamente `tipo_seguro`; Codex debe localizarla o dejarla parametrizable.

## 7.2 Campos de evaluación

| Componente | Columnas esperadas |
|---|---|
| Evaluación general | `Mes_eva`, `Obs_Eval`, `Obs_CRED`, `Obs_General` |
| BCG | `fec1_BCG`, `resul1_BCG`, `Edad_ate1_BCG`, `BCG_1_1`, `reg_BCG1`, `eess_BCG1`, `Obs_BCG` |
| HvB | `fecHVB`, `resulHVB`, `Edad_ateHVB`, `sg_HVB`, `reg_HVB`, `eess_HVB`, `Obs_HVB` |
| CRED 1 | `Fecha_Atencion_1`, `Lab_1`, `Edad_Atencion_1`, `CIE10_1`, `Codigo_HIS_1`, `Registro_1`, `EESS_Atencion_1` |
| CRED 2 | `Fecha_Atencion_2`, `Lab_2`, `Edad_Atencion_2`, `CIE10_2`, `Codigo_HIS_2`, `Registro_2`, `EESS_Atencion2`, `Intervalo_2` |
| CRED 3 | `Fecha_Atencion_3`, `Lab_3`, `Edad_Atencion_3`, `CIE10_3`, `Codigo_HIS_3`, `Registro_3`, `EESS_Atencion_3`, `Intervalo_3` |
| CRED 4 | `Fecha_Atencion_4`, `lab_4`, `Edad_Atencion_4`, `CIE10_4`, `Codigo_HIS_4`, `Registro_4`, `EESS_Atencion_4`, `Intervalo_4` |
| Tamizaje | `Fecha_Atencion_TN`, `Lab_TN`, `Edad_Atencion_TN`, `Codigo_HIS_TN`, `Registro_TN`, `EESS_Atencion_TN`, `Obs_TM` |

---

# 8. Constantes sugeridas para `config.py`

```python
CODIGOS_HIS_MC03 = {
    "BCG": {"90585"},
    "HVB": {"90744"},
    "CRED": {"99381.01"},
    "TAMIZAJE": {"36416"},
}

REGLAS_MC03 = {
    "META_COBERTURA_MENSUAL": 70.7,  # Meta operativa local actual; mantener parametrizable.
    "PERIODO_VERIFICACION_2026": {
        "inicio": "2026-06-01",
        "fin": "2026-11-30",
        "meses_requeridos_cumplidos": 5,
        "meses_totales": 6,
    },
    "DENOMINADOR": {
        "edad_dias_referencia": 29,
        "seguros_incluidos": {"SIS", "SIN SEGURO", "SIN_SEGURO", "NINGUNO", ""},
        "peso_minimo": 2500,
        "edad_gestacional_minima": 37,
    },
    "VACUNAS": {
        "plazo_max_horas": 24,
        "fallback_edad_dias_validos": {0, 1},
    },
    "CRED": {
        "codigo": "99381.01",
        "evaluar_lab": False,
        "intervalo_min_dias": 7,
        "ventanas": {
            "cred_1": {"inicio_dia": 3, "fin_dia": 6},
            "cred_2": {"inicio_dia": 7, "fin_dia": 14},
            "cred_3": {"inicio_dia": 15, "fin_dia": 21},
        },
    },
    "TAMIZAJE": {
        "codigo": "36416",
        "inicio_horas": 48,
        "fin_horas": 144,
        "fallback_inicio_dia": 2,
        "fallback_fin_dia": 6,
    },
}
```

---

# 9. Arquitectura sugerida del módulo

Estructura recomendada:

```text
backend/
└── indicators/
    └── mc03/
        ├── __init__.py
        ├── config.py
        ├── processor.py
        ├── denominator.py
        ├── vaccines.py
        ├── cred.py
        ├── screening.py
        ├── messages.py
        ├── schema.py
        └── utils.py
```

## 9.1 Responsabilidades

| Archivo | Responsabilidad |
|---|---|
| `config.py` | Códigos HIS, columnas Excel, reglas de negocio y meta mensual |
| `processor.py` | Orquestar carga de Excel, validación, filtros, dashboard, búsqueda y exportación |
| `denominator.py` | Calcular si el RN pertenece al denominador mensual |
| `vaccines.py` | Evaluar BCG y HvB |
| `cred.py` | Evaluar tres controles CRED, ventanas e intervalo mínimo |
| `screening.py` | Evaluar tamizaje neonatal |
| `messages.py` | Centralizar códigos y mensajes de incumplimiento |
| `schema.py` | Definir modelos de respuesta para API |
| `utils.py` | Fechas, normalización, conversión numérica, deduplicación |

---

# 10. Algoritmo general de evaluación

```text
Para cada registro de recién nacido:

1. Normalizar campos.
2. Determinar ID del paciente:
   - Preferir DNI si existe.
   - Si no existe DNI, usar CNV.
   - Si ninguno existe, marcar dato_incompleto_documento.

3. Calcular fecha_29_dias = fecha_nacimiento + 29 días.

4. Evaluar denominador:
   a. fecha_29_dias dentro del mes de medición.
   b. seguro incluido.
   c. territorio incluido.
   d. peso >= 2500 si existe.
   e. edad_gestacional >= 37 si existe.

5. Si no pertenece al denominador:
   - Excluir del cálculo.
   - Registrar motivo de exclusión.

6. Si pertenece al denominador:
   a. Evaluar BCG.
   b. Evaluar HvB.
   c. Evaluar CRED 1.
   d. Evaluar CRED 2.
   e. Evaluar CRED 3.
   f. Evaluar tamizaje neonatal.

7. Numerador:
   - Cumple si todos los componentes requeridos cumplen.
   - No cumple si al menos un componente falla.

8. Generar respuesta:
   - Estado general.
   - Componentes cumplidos.
   - Componentes incumplidos.
   - Motivos codificados.
   - Fechas y edades de atención.
   - EESS donde se registró cada prestación.
```

---

# 11. Dashboard y reportes

## 11.1 Indicadores mínimos

El dashboard debe mostrar:

| Métrica | Descripción |
|---|---|
| Denominador | RN que cumplen 29 días en el mes y pasan filtros |
| Numerador | RN del denominador con paquete completo |
| Avance porcentual | `(numerador / denominador) × 100` |
| Meta mensual | `70.7%` parametrizable |
| Brecha | `meta - avance` |
| Cumple meta | `avance >= meta` |
| Incumplidos | RN del denominador que no completan paquete |
| Excluidos | RN fuera del denominador por peso, prematuridad, seguro o edad |

## 11.2 Agrupaciones recomendadas

- Mes de evaluación.
- Provincia.
- Distrito.
- Red.
- Microred.
- Establecimiento.
- Componente incumplido.
- Motivo de incumplimiento.
- Seguro.
- Estado del paquete.

## 11.3 Reporte de incumplidos

Columnas sugeridas:

| Columna | Descripción |
|---|---|
| `id_paciente` | DNI o CNV |
| `dni` | DNI |
| `cnv` | CNV |
| `nombre_completo` | Nombre del RN |
| `madre` | Nombre de madre |
| `dni_madre` | DNI madre |
| `celular` | Celular |
| `fecha_nacimiento` | Fecha nacimiento |
| `fecha_29_dias` | Fecha en que cumple 29 días |
| `edad_gestacional` | Semanas gestacionales |
| `peso_nacer` | Peso al nacer |
| `provincia` | Provincia |
| `distrito` | Distrito |
| `eess_adscripcion` | EESS |
| `cumple_bcg` | Sí/No |
| `motivo_bcg` | Código motivo |
| `cumple_hvb` | Sí/No |
| `motivo_hvb` | Código motivo |
| `cumple_cred_1` | Sí/No |
| `cumple_cred_2` | Sí/No |
| `cumple_cred_3` | Sí/No |
| `motivo_cred` | Código motivo |
| `cumple_tamizaje` | Sí/No |
| `motivo_tamizaje` | Código motivo |
| `cumple_mc03` | Sí/No |
| `motivos_resumen` | Lista de motivos |

---

# 12. Búsqueda por DNI/CNV

La búsqueda individual debe devolver:

```json
{
  "paciente": {
    "id_paciente": "12345678",
    "dni": "12345678",
    "cnv": "CNV123",
    "nombre_completo": "NOMBRES APELLIDOS",
    "fecha_nacimiento": "2026-06-01",
    "fecha_29_dias": "2026-06-30",
    "distrito": "ABANCAY",
    "eess_adscripcion": "..."
  },
  "denominador": {
    "incluido": true,
    "motivo": null
  },
  "resultado": {
    "cumple_mc03": false,
    "estado": "no_cumple",
    "componentes_cumplidos": 4,
    "componentes_requeridos": 6,
    "porcentaje_componentes": 66.67
  },
  "componentes": [
    {
      "codigo": "BCG",
      "nombre": "Vacuna BCG",
      "cumple": true,
      "fecha_atencion": "2026-06-01",
      "edad_dias": 0,
      "codigo_his": "90585",
      "eess": "..."
    },
    {
      "codigo": "TAMIZAJE",
      "nombre": "Tamizaje neonatal",
      "cumple": false,
      "codigo_motivo": "TAM-01",
      "mensaje": "No registra tamizaje neonatal"
    }
  ]
}
```

---

# 13. Reglas de compatibilidad con la implementación actual

El contrato publico actual del modulo expone:

```text
load_sample_data
validate_data_file
get_filter_options
build_report_summary
search_by_dni
```

Codex debe mantener compatibilidad con estas funciones mientras se refactoriza.

## 13.1 No romper endpoints actuales

Si `backend/main.py` ya consume `backend/services.py` o `backend/config.py`, mantener fachadas de compatibilidad:

```python
# backend/services.py
from backend.indicators.mc03.processor import (
    load_sample_data,
    validate_data_file,
    get_filter_options,
    build_report_summary,
    search_by_dni,
)
```

## 13.2 Evitar lógica monolítica

No concentrar todas las reglas en `processor.py`. Separar en módulos especializados para facilitar pruebas unitarias.

---

# 14. Correcciones y mejoras frente a la implementacion actual

Los antiguos `logic_rules.md` y `README_MC03.md` quedaron consolidados en este documento para evitar reglas duplicadas o desactualizadas.

## 14.1 `config.py`

El archivo actual contiene una buena base de códigos y columnas. Mejoras recomendadas:

1. Renombrar `CODIGOS_ESTANDAR` a `CODIGOS_HIS_MC03`.
2. Separar reglas de denominador, vacunas, CRED y tamizaje.
3. Agregar `PERIODO_VERIFICACION_2026`.
4. Agregar `fallback_edad_dias_validos` para vacunas.
5. Agregar reglas explícitas para datos faltantes.
6. Revisar y parametrizar columna de seguro.
7. Mantener `CRED_4` solo como auditoría.

---

# 15. Pruebas mínimas de aceptación

Codex debe crear pruebas unitarias para estas reglas.

## 15.1 Denominador

| Caso | Entrada | Esperado |
|---|---|---|
| RN cumple 29 días en junio | `fec_Nac=2026-06-01`, mes junio | Incluido |
| RN cumple 29 días en julio | `fec_Nac=2026-06-02`, mes junio | Fuera denominador junio |
| Peso 2499 | `peso=2499` | Excluido bajo peso |
| Peso 2500 | `peso=2500` | Incluido |
| Edad gestacional 36 | `edadGEst=36` | Excluido prematuro |
| Edad gestacional 37 | `edadGEst=37` | Incluido |
| Seguro SIS | `seguro=SIS` | Incluido |
| Seguro ESSALUD | `seguro=ESSALUD` | Fuera denominador |
| Peso vacío | `peso=None` | Incluido con alerta |

## 15.2 BCG/HvB

| Caso | Entrada | Esperado |
|---|---|---|
| BCG a las 12 horas | código `90585`, edad 12h | Cumple |
| BCG a las 25 horas | código `90585`, edad 25h | No cumple |
| HvB mismo día | código `90744`, edad día 0 | Cumple con fallback |
| HvB día 2 | código `90744`, edad día 2 | No cumple |
| Código incorrecto | código distinto | No cumple |

## 15.3 CRED

| Caso | Entrada | Esperado |
|---|---|---|
| CRED días 3, 10, 17 | código `99381.01` | Cumple |
| CRED días 6, 10, 17 | intervalo CRED1-CRED2 = 4 | No cumple por intervalo |
| Falta 2do CRED | días 3 y 17 | No cumple |
| CRED1 día 2 | fuera ventana | No cumple |
| CRED3 día 22 | fuera ventana | No cumple |
| CRED con LAB vacío | código válido | Cumple si ventana e intervalo son válidos |

## 15.4 Tamizaje

| Caso | Entrada | Esperado |
|---|---|---|
| Tamizaje 48 horas | código `36416` | Cumple |
| Tamizaje día 2 | código `36416` | Cumple con fallback |
| Tamizaje antes de 48h | código `36416` | No cumple |
| Tamizaje día 7 | código `36416` | No cumple |
| Código incorrecto | código distinto | No cumple |

## 15.5 Numerador

| Caso | Entrada | Esperado |
|---|---|---|
| Todos los componentes cumplen | BCG, HvB, 3 CRED, tamizaje válidos | Cumple MC-03 |
| Falta un componente | Falta tamizaje | No cumple MC-03 |
| No pertenece al denominador | ESSALUD | No entra al cálculo |

---

# 16. Checklist para Codex

Antes de finalizar implementación, Codex debe verificar:

- [ ] Se calcula denominador por `fecha_nacimiento + 29 días`.
- [ ] Se filtra por seguro SIS o sin seguro.
- [ ] Se excluye peso menor a 2500 g.
- [ ] Se excluye edad gestacional menor a 37 semanas.
- [ ] BCG usa código `90585`.
- [ ] HvB usa código `90744`.
- [ ] BCG y HvB validan plazo máximo de 24 horas.
- [ ] Si no hay hora, se usa fallback `edad_dias in [0, 1]`.
- [ ] CRED usa código `99381.01`.
- [ ] CRED se evalúa independiente del LAB.
- [ ] CRED 1 se evalúa entre 3 y 6 días.
- [ ] CRED 2 se evalúa entre 7 y 14 días.
- [ ] CRED 3 se evalúa entre 15 y 21 días.
- [ ] Se valida intervalo mínimo de 7 días entre controles CRED.
- [ ] Tamizaje usa código `36416`.
- [ ] Tamizaje se evalúa desde 48 horas hasta 6 días.
- [ ] `CRED_4` no cuenta para numerador.
- [ ] No se usa `Obs_General` como única fuente de cumplimiento.
- [ ] Se generan motivos de incumplimiento codificados.
- [ ] Se mantiene compatibilidad con funciones públicas actuales.
- [ ] La meta mensual `70.7` queda parametrizable.
- [ ] Se agregan pruebas unitarias.

---

# 17. Prompt sugerido para usar en Codex

```text
Necesito refactorizar el módulo del indicador MC-03.01 para la Red de Salud Abancay usando este markdown como fuente principal.

Objetivo:
Implementar un sistema de evaluación del indicador MC-03.01: recién nacidos que reciben BCG, HvB, 3 controles CRED y tamizaje neonatal.

Reglas clave:
- Denominador: recién nacidos que cumplen 29 días en el mes de medición, registrados con DNI o CNV/CNV en línea, seguro SIS o sin seguro.
- Excluir bajo peso al nacer: peso < 2500 g.
- Excluir prematuridad: edad gestacional < 37 semanas.
- BCG: código 90585, dentro de 24 horas de nacido.
- HvB: código 90744, dentro de 24 horas de nacido.
- CRED: código 99381.01, 3 controles:
  - 1er CRED: 3 a 6 días.
  - 2do CRED: 7 a 14 días.
  - 3er CRED: 15 a 21 días.
  - Intervalo mínimo entre controles: 7 días.
  - Evaluar independiente del LAB.
- Tamizaje neonatal: código 36416, desde 48 horas hasta 6 días.
- No usar CRED_4 para numerador.
- No usar Obs_General como única fuente del resultado.
- Mantener compatibilidad con las funciones actuales:
  load_sample_data, validate_data_file, get_filter_options, build_report_summary, search_by_dni.

Tareas:
1. Revisar el módulo actual `backend/indicators/mc03`.
2. Separar lógica en `denominator.py`, `vaccines.py`, `cred.py`, `screening.py`, `utils.py`, `messages.py` y `processor.py`.
3. Crear constantes limpias en `config.py`.
4. Implementar estados y motivos de incumplimiento codificados.
5. Mantener compatibilidad con endpoints existentes.
6. Agregar pruebas unitarias para denominador, BCG/HvB, CRED, tamizaje y numerador.
7. Documentar cualquier decisión operativa cuando el Excel no tenga fecha/hora exacta y se use edad en días como fallback.
```

---

# 18. Notas finales de implementación

1. El indicador MC-03 es **mensual**, no acumulado anual como MC-02.
2. El denominador se basa en recién nacidos que cumplen 29 días en el mes.
3. El paquete completo se considera cerrado antes de los 29 días porque los componentes vencen como máximo al día 21, excepto vacunas/tamizaje que vencen antes.
4. La búsqueda por DNI/CNV debe mostrar el detalle por componente, no solo el estado general.
5. Las observaciones del Excel (`Obs_*`) deben servir para auditoría y explicación, pero la lógica debe estar centralizada en funciones evaluadoras.
6. La implementación debe permitir recalcular desde HIS crudo en una fase posterior, sin depender permanentemente de marcas precalculadas.
