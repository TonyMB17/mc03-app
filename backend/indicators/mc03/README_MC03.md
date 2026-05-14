# Indicador MC-03 - Paquete recien nacido

Este modulo contiene la implementacion tecnica del indicador MC-03. En la fase 1 de la plataforma multiindicador, la logica existente se traslado a esta carpeta sin cambiar el comportamiento de los endpoints actuales.

## Archivos del modulo

- `config.py`: codigos estandar, columnas del Excel y reglas de negocio propias de MC-03.
- `processor.py`: lectura del Excel, validacion de estructura, filtros, calculo de denominador/numerador, busqueda por DNI y construccion de incumplidos.
- `schema.py`: limite reservado para futuros modelos especificos de MC-03.
- `__init__.py`: expone los metodos principales del modulo.

## Superficie publica

El modulo expone:

- `load_sample_data`
- `validate_data_file`
- `get_filter_options`
- `build_report_summary`
- `search_by_dni`

## Compatibilidad

Los archivos antiguos `backend/services.py` y `backend/config.py` siguen existiendo como fachadas de compatibilidad. Esto permite que `backend/main.py` y los endpoints actuales sigan funcionando mientras se completa la migracion a rutas multiindicador.

## Siguiente paso

Cuando la plataforma incorpore el registro general de indicadores, este modulo debera adaptarse a una interfaz comun para que otros indicadores puedan implementar el mismo contrato.
