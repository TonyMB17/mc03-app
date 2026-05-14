# MC-02 - Paquete integrado menores de 12 meses

Modulo backend del indicador MC-02: porcentaje de niñas y niños menores de 12 meses de edad procedentes de distritos de quintiles 1 y 2 de pobreza departamental que recibieron el paquete integrado de servicios.

Fuente tecnica: `docs/MC-02_FT_PROCESAMIENTO_GR_241025.pdf`.

## Definicion operativa local

La ficha tecnica define el paquete integrado con cuatro componentes:

- Vacunas basicas segun edad: antipolio, pentavalente, neumococo y rotavirus.
- Entrega de hierro: gotas, jarabe o micronutrientes.
- Dosaje de hemoglobina entre los 170 y 209 dias.
- DNI emitido hasta los 30 dias de nacido.

Decision local para Red de Salud Abancay:

- El componente DNI no se evalua en la plataforma porque no corresponde al area salud.
- Los controles CRED que aparecen en el Excel operativo se omiten del calculo MC-02 actual porque no forman parte de la definicion del paquete integrado revisada para esta implementacion.
- El sistema conserva esas columnas como informacion de auditoria o uso futuro, pero no las usa para numerador.

## Fuente Excel

La primera version usa el Excel operativo ya procesado:

- Hoja principal: `Detalle_Ate`.
- Fecha de corte: celda `D9`.
- Encabezados: fila `10`.
- Filtro territorial por defecto: `provincia = ABANCAY`.
- Tipo de seguro: columna `Obs_Niño`, dentro del bloque `DATOS_GENERALES`.
- Denominador operativo: `Registros = 1`.
- Meta por defecto: `80.9%`.

## Denominador y exclusiones

El denominador operativo parte de los registros con `Registros = 1`, filtrados territorialmente por `provincia = ABANCAY` y por tipo de seguro incluido en `Obs_Niño`.

Tipos de seguro incluidos:

- `SIS`.
- `NINGUNO`.
- Celda vacia, interpretada como ningun tipo de seguro.

Adicionalmente, se evalua exclusion por condiciones de nacimiento:

- Bajo peso al nacer: `Peso < 2500`.
- Prematuridad: `Edad_Gestacional < 37`.

Tratamiento de celdas vacias:

- Si `Peso` esta vacio, el registro permanece en el denominador.
- Si `Edad_Gestacional` esta vacio, el registro permanece en el denominador.
- La exclusion solo se aplica cuando el dato existe y esta por debajo del umbral.

Esta decision evita excluir registros por ausencia de dato cuando no existe evidencia suficiente para clasificarlos como bajo peso o prematuros.

## Componentes activos para numerador

El numerador se recalcula en la plataforma a partir de marcas precalculadas por componente, evitando usar directamente `Estado` cuando pueda incluir criterios omitidos localmente.

Componentes activos:

| Componente | Marca usada |
|---|---|
| Vacuna neumococo | `obs_neu1` |
| Vacuna rotavirus | `obs_rot1` |
| Vacuna antipolio | `obs_ant1` |
| Vacuna pentavalente | `obs_pen1` |
| Hierro menor de 6 meses | `obs_suple41` |
| Hierro mayor de 6 meses | `obs_suple61` |
| Dosaje de hemoglobina | `Obs_dh1` |

Un registro cumple MC-02 cuando todos los componentes activos aplicables vienen como cumplimiento en el Excel operativo.

## Seguimiento mensual por cohorte

MC-02 no se interpreta como atenciones realizadas en un mes calendario, sino como avance acumulado de una cohorte de nacimiento.

Campo de evaluacion mensual:

- `Mes_Nac`: mes de nacimiento/cohorte del niño.

Campos usados para determinar la oportunidad:

- `Fec_Nac`: fecha de nacimiento.
- Fecha de corte del Excel: `D9`.
- `Edad_Act(dia)`: respaldo operativo cuando no se puede calcular la edad con fecha de nacimiento y fecha de corte.

La plataforma calcula la edad al corte con `Fec_Nac` y la fecha de corte. Con esa edad decide el estado de cada componente:

- `programado`: el componente aun no es exigible para la edad del niño; se informa el proximo inicio de ventana.
- `pendiente_en_plazo`: el componente ya es exigible, no cumple aun, pero la cohorte todavia esta dentro de la ventana.
- `cumple`: el componente cumple segun la marca operativa del Excel.
- `incumplimiento_fuera_plazo`: el componente no cumple y ya vencio la fecha limite de su ventana.

El dashboard agrupa numerador y denominador por `Mes_Nac`. El avance mensual representa el porcentaje acumulado de la cohorte que ya completo el paquete aplicable hasta la fecha de corte. Los motivos de incumplimiento muestran si el registro esta pendiente dentro de plazo o fuera de plazo.

## Ventanas y motivos de incumplimiento

El sistema debe explicar por que un registro no cumple. Para cada componente activo se usan dos fuentes:

- La marca precalculada del Excel (`obs_*` u `Obs_*`).
- La ventana normativa configurada en `REGLAS_NEGOCIO["VENTANAS_ATENCION"]`.

Motivos esperados:

- No se registra atencion para el componente.
- Existe atencion, pero no cumple el criterio del indicador.
- La atencion se realizo fuera de la edad o intervalo esperado.
- Falta completar dosis o entregas acumuladas para la edad actual.

Cuando el Excel trae establecimiento de la atencion (`EESS_Ate_*`), se muestra en busqueda individual y en reporte de incumplidos. El Excel MC-02 revisado no trae columnas de profesional para vacunas, hierro ni hemoglobina; por eso el campo profesional se muestra como `No disponible en Excel` para estos componentes. Las columnas `Prof_*` existen solo en CRED, componente omitido del calculo actual.

## Vacunas

Codigos de referencia segun ficha:

- Neumococo: `90670` o `90677`.
- Rotavirus: `90681`.
- Antipolio: `90712` o `90713`.
- Pentavalente: `90722` o `90723`.

Notas:

- `90723` se usa solo con fines de busqueda; el codigo vigente indicado por la ficha es `90722`.
- Rotavirus se aplica como maximo hasta los 8 meses 0 dias, equivalente a 240 dias.
- Para las vacunas con dosis sucesivas, la ficha usa reglas de edad e intervalos, principalmente desde la dosis previa +28 dias y hasta +70 dias, segun vacuna.

Ventanas configuradas:

- Neumococo: 0-119 dias no exige dosis; 120-189 dias exige 1 dosis; 190-364 dias exige 2 dosis acumuladas.
- Rotavirus: hasta 240 dias como edad maxima de aplicacion; 241-364 dias debe contar con 2 dosis acumuladas aplicadas oportunamente.
- Antipolio: 0-210 dias no exige dosis; 211-240 dias exige 1 dosis; 260-364 dias exige 3 dosis acumuladas.
- Pentavalente: 0-119 dias no exige dosis; 120-189 dias exige 1 dosis; 190-259 dias exige 2 dosis; 260-364 dias exige 3 dosis.

En busqueda por DNI, las vacunas se muestran como componente agregado y las dosis se separan en un detalle desplegable. Esto evita confundir un estado pendiente del componente acumulado con una dosis que si fue registrada.

## Dosaje de hemoglobina

Codigos de referencia:

- `85018`
- `85018.01`
- `85031`

Regla central:

- Debe registrarse dosaje de hemoglobina en sangre entre los 170 y 209 dias de edad.
- En el Excel operativo se usa la marca `Obs_dh1`.
- Desde 210 dias hasta 364 dias debe contar con 1 dosaje realizado dentro de esa ventana.

## Entrega de hierro

La ficha tecnica agrupa la entrega de hierro en gotas, jarabe o micronutrientes. Para el procesamiento se deben distinguir rutas segun edad y condicion del niño.

### Codigos validos

Tratamiento de anemia:

- Diagnosticos: `D509` o `D649`.
- CPMS de hierro: `99199.17`.

Suplementacion preventiva:

- `99199.17`: sulfato ferroso o hierro polimaltosado.
- `99199.19`: multimicronutrientes.

Exclusion comun:

- Se excluye `99499` por telemedicina.

### Reglas transversales

- Se contabiliza como maximo una misma prestacion por dia.
- Para visita familiar se consideran LAB `PO1` a `PO6`, `P01` a `P06`, `SF1` a `SF6` y numericos `1` a `6`, sin importar el orden.
- Solo se considera entrega de hierro sin LAB cuando no esta vinculada a visita familiar.
- Solo se considera entrega de hierro con LAB cuando esta vinculada a visita familiar.

### Suplementacion preventiva en esquema de 4 meses

Aplica a entregas de hierro para niños que por edad aun corresponden al esquema preventivo inicial.

Regla de cumplimiento:

- Cumple con una entrega de hierro segun edad.
- La ficha muestra el punto operativo de evaluacion desde 210 dias con al menos 1 entrega acumulada.
- Se excluye telemedicina `99499`.

En el Excel operativo, esta ruta se representa principalmente con `obs_suple41` y los bloques `SUPLEMENTACION_HIERRO_MENOR_6_MESES_*`.

### Tratamiento con hierro en niños de 6 a 11 meses

Aplica cuando existe anemia y se evalua tratamiento.

Reglas de cumplimiento:

- Cumple con al menos 3 entregas de hierro, segun edad.
- En la primera entrega se debe verificar vinculacion con anemia `D509` o `D649`.
- El diagnostico de anemia debe ser definitivo `D` en la misma cita.
- En las entregas posteriores no se vuelve a buscar diagnostico de anemia.
- Se excluye `99499` por telemedicina.
- Se excluyen registros `99199.17 + LAB TA` en la primera entrega de hierro.

En el Excel operativo, esta ruta se apoya en los bloques `TRATAMIENTO_ANEMIA_*` y la marca `Obs_Anemia`.

### Suplementacion preventiva en niños de 6 a 11 meses

Aplica cuando el niño no esta en tratamiento por anemia.

Reglas de cumplimiento:

- Cumple con al menos 2 entregas segun edad.
- Si por edad corresponde solo una entrega, cumple si recibe sulfato ferroso o hierro polimaltosado.
- Si por edad corresponden al menos 2 entregas, cumple con cualquiera de estas combinaciones:
  - 2 entregas de sulfato ferroso o hierro polimaltosado.
  - Sulfato ferroso o hierro polimaltosado + micronutrientes.
  - Micronutrientes + sulfato ferroso o hierro polimaltosado.
- En la primera entrega se verifica que no este vinculada a anemia.
- En las siguientes entregas no se vuelve a realizar esa busqueda.
- Se excluye `99499` por telemedicina.
- Se excluyen registros `99199.17 + LAB TA` en la primera entrega de hierro.

Intervalos de referencia de la ficha:

- Segunda entrega: desde primera entrega +25 dias y hasta primera entrega +70 dias.
- Tercera entrega: desde segunda entrega +25 dias y hasta segunda entrega +70 dias.

En el Excel operativo, esta ruta se representa con `obs_suple61` y los bloques `SUPLEMETACION_HIERRO_PREVENTIVO_MAYOR_6_MESES_*`.

### Esquema combinado micronutrientes mas hierro

Reglas de cumplimiento:

- Cumple con al menos 2 entregas segun edad.
- La primera entrega de micronutrientes no debe estar vinculada a anemia.
- Se excluye `99499` por telemedicina.
- Se excluyen registros `99199.19 + LAB TA` en la primera entrega.

Intervalo de referencia:

- Segunda entrega: desde primera entrega +25 dias y hasta primera entrega +35 dias.

### Esquema solo multimicronutrientes

Reglas de cumplimiento:

- Usa codigo `99199.19`.
- La primera entrega no debe estar vinculada a anemia.
- Se excluye `99499` por telemedicina.
- Se excluyen registros `99199.19 + LAB TA` en la primera entrega.

Intervalos de referencia:

- Segunda entrega: primera entrega +25 a +35 dias.
- Tercera entrega: segunda entrega +25 a +35 dias.
- Cuarta entrega: tercera entrega +25 a +35 dias.
- Quinta entrega: cuarta entrega +25 a +35 dias.
- Sexta entrega: quinta entrega +25 a +35 dias.

## Implementacion actual

La plataforma no recalcula aun cada dosis desde las atenciones crudas. En esta etapa usa las marcas precalculadas del Excel operativo:

- `obs_suple41` para hierro menor de 6 meses.
- `obs_suple61` para hierro mayor de 6 meses.
- `Obs_dh1` para dosaje de hemoglobina.
- Marcas de vacunas para el bloque de inmunizaciones.

Las columnas de detalle se conservan para auditoria, busqueda individual y mensajes explicativos. Cuando se implemente recalculo fino desde atenciones crudas, las reglas de entrega de hierro descritas arriba deben convertirse en funciones por ruta.
