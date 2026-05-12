# Sistema de Seguimiento Neonatal (Red de Salud Abancay) - Indicador MC-03

Este sistema permite el monitoreo y control de las atenciones de salud de los recién nacidos, basado en la **Ficha Técnica MC-03.01**, asegurando el cumplimiento de las metas de cobertura de vacunas, controles CRED y tamizaje neonatal.

## 📋 Criterios Técnicos Implementados (Normativa)

El sistema evalúa el cumplimiento del "Paquete Recién Nacido" bajo los siguientes parámetros:

### 1. Inmunizaciones (Dentro de las 24 horas de vida)
- **Vacuna BCG:** Código 90585.
- **Vacuna HvB:** Código 90744.

### 2. Controles CRED (0-21 días de edad)
Se deben registrar 3 controles con el código **99381.01**, respetando un intervalo mínimo de 7 días entre ellos:
- **1er CRED:** 3 a 6 días de nacido.
- **2do CRED:** 7 a 14 días de nacido.
- **3er CRED:** 15 a 21 días de nacido.

### 3. Tamizaje Neonatal (48h a 6 días de vida)
- **Pruebas:** Hipotiroidismo, Hiperplasia Suprarrenal, Fenilcetonuria y Fibrosis Quística.
- **Código:** 36416.

## 📊 Vista: Reporte de Gestión General (Cumplimiento de Meta)

Esta vista está diseñada para los directivos de la Red de Salud Abancay para monitorear el cumplimiento del Compromiso de Gestión.

### Lógica de Evaluación del Compromiso (MC-03.01):
- **Periodo de Verificación:** Única verificación en Noviembre 2026.
- **Meses evaluados:** Junio, Julio, Agosto, Setiembre, Octubre y Noviembre 2026.
- **Criterio de Éxito:** Se considera **CUMPLIDO** si la región alcanza la meta en **05 de los 06 meses** evaluados.

### Funcionalidades del Reporte:
1. **Semáforo de Cumplimiento Mensual:** Indicador visual (Rojo/Verde) por cada mes del periodo de verificación.
2. **Cálculo de Denominador Real:** Filtro automático para incluir solo niños de 29 días, con seguro SIS o Sin Seguro, excluyendo prematuros y bajo peso.
3. **Tasa de Cobertura:** Porcentaje de niños que recibieron el paquete completo (Vacunas + 3 CRED + Tamizaje) sobre el total del padrón nominal.
4. **Exportación de Omisos:** Listado descargable de niños que no completaron el paquete para intervención inmediata.

## 🛠️ Arquitectura del Sistema

- **Frontend:** React (Vite) + Tailwind CSS.
- **Backend:** FastAPI (Python 3.10+).
- **Procesamiento de Datos:** Pandas / Openpyxl (Lectura de archivos HIS y Padrón Nominal).
- **Criterios de Exclusión:** El sistema excluye automáticamente a prematuros (<37 semanas) o con bajo peso (<2500g).

## 🚀 Funcionalidades Principales

1. **Búsqueda por DNI/CNV:** Localización inmediata del recién nacido en la base de datos
2. **Tablero de Estado:** Visualización tipo semáforo del cumplimiento de vacunas, CRED y tamizaje.
3. **Calculadora de Próximas Citas:** Basado en la fecha de nacimiento del CNV, el sistema proyecta las ventanas de tiempo ideales para los próximos controles CRED.
4. **Alerta de Incumplimiento:** Notificación si el recién nacido está por superar los 21 días sin completar el esquema.

## 🔧 Instalación y Uso

### Backend
1. Instalar dependencias: `pip install fastapi uvicorn pandas openpyxl`
2. Ejecutar servidor: `uvicorn main:app --reload`

### Frontend
1. Instalar dependencias: `npm install`
2. Ejecutar aplicación: `npm run dev`

## 📄 Referencias Normativas
- NTS N° 214-MINSA/DGIESP-2024 (Atención Neonatal).
- NTS N° 238-MINSA/DGIESP-2025 (Crecimiento y Desarrollo).
- NTS N° 196-MINSA/DGIESP-2022 (Esquema Nacional de Vacunación).
- Ficha Técnica MC-03 (MIDIS/MINSA 2025).
