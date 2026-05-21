# Plan de mejora de diseno - Plataforma de indicadores de salud

Este documento define el plan de mejora visual de la plataforma MC-03 App, entendida como un sistema operativo para seguimiento de indicadores sanitarios. La prioridad no es decorar la interfaz, sino hacerla mas clara, confiable y rapida de usar por personal clinico, supervisores y administradores.

## Principios de diseno

- Claridad clinica: cada pantalla debe responder rapido que esta bien, que falta y que accion sigue.
- Confianza institucional: superficies sobrias, contraste alto, estados consistentes y lenguaje operativo.
- Densidad util: mostrar informacion suficiente sin convertir la pantalla en un tablero ruidoso.
- Accesibilidad: foco visible, estados con color + texto + icono, y lectura correcta en pantallas pequenas.
- Consistencia multiindicador: MC-02, MC-03 y SI-02 deben sentirse parte de la misma plataforma.
- Seguridad visible: roles, permisos, cargas, auditoria y usuarios deben tener jerarquia visual propia.

## Paleta y estados

- Paleta oficial: identidad visual USI.
- Base: `#F8FAFC`, `#FFFFFF`, `#E2E8F0` para pagina, tarjetas y divisores.
- Texto: `#0F172A` para lectura principal y `#64748B` para metadatos.
- Primario: azul marino institucional `#102D52` para headers, botones primarios y alta jerarquia.
- Secundario: celeste salud `#0EA5E9` para enlaces activos, iconos interactivos, hover y seleccion.
- Acento: lila Abancay `#C2A4CF` solo en detalles sutiles, fondos de baja opacidad e iconografia de apoyo.
- Regla 60-30-10: 60% neutros, 30% navy/celeste y 10% lila/estados semanticos.
- Los fondos decorativos por vista quedan evitados; las tarjetas usan base neutra y el color se reserva para marca, navegacion o estados.
- Estados:
  - Cumple: verde semantico.
  - Incumple: rojo semantico.
  - En ventana o pendiente: ambar semantico.
  - Informativo: azul semantico.

## Implementacion tecnica USI

La plataforma debe usar React, Tailwind CSS y DaisyUI como sistema visual unico. La logica existente de indicadores, busqueda, carga, seguridad y configuracion debe mantenerse; el redisenio se enfoca en composicion de componentes, estructura de layout y clases visuales.

### Tailwind y DaisyUI

- Tipografia objetivo: `Montserrat` como familia institucional, con fallback a `Inter` y `sans-serif`.
- Tema DaisyUI oficial: `usiTheme`.
- Compatibilidad del repo: mientras el codigo actual use `data-theme="clinic"`, el tema puede mantenerse como alias temporal o migrarse en un bloque controlado a `data-theme="usiTheme"`.
- Tokens obligatorios:
  - `primary`: `#102D52`.
  - `secondary`: `#0EA5E9`.
  - `accent`: `#C2A4CF`.
  - `neutral`: `#0F172A`.
  - `base-100`: `#FFFFFF`.
  - `base-200`: `#F8FAFC`.
  - `base-300`: `#E2E8F0`.
  - `success`: `#10B981`.
  - `warning`: `#F59E0B`.
  - `error`: `#EF4444`.

Configuracion de referencia para `frontend/tailwind.config.js`:

```js
import daisyui from 'daisyui';

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Montserrat', 'Inter', 'sans-serif'],
      },
      colors: {
        usi: {
          navy: '#102D52',
          celeste: '#0EA5E9',
          lilac: '#C2A4CF',
          bg: '#F8FAFC',
          dark: '#0F172A',
        },
        health: {
          success: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444',
        },
      },
    },
  },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        usiTheme: {
          primary: '#102D52',
          'primary-content': '#FFFFFF',
          secondary: '#0EA5E9',
          'secondary-content': '#FFFFFF',
          accent: '#C2A4CF',
          'accent-content': '#0F172A',
          neutral: '#0F172A',
          'neutral-content': '#F8FAFC',
          'base-100': '#FFFFFF',
          'base-200': '#F8FAFC',
          'base-300': '#E2E8F0',
          'base-content': '#0F172A',
          info: '#0EA5E9',
          success: '#10B981',
          warning: '#F59E0B',
          error: '#EF4444',
        },
      },
    ],
    darkTheme: 'usiTheme',
  },
};
```

### Componentes DaisyUI/Premium base

- `UsiCard`: wrapper sobre `card bg-base-100 border border-base-300 rounded-2xl shadow-sm`.
- `UsiStat`: wrapper sobre `stat` para metricas, triaje, carga y seguridad.
- `UsiBadge`: wrapper sobre `badge` para estados `success`, `warning`, `error`, `info` y `ghost`.
- `UsiTabs`: wrapper sobre `tabs tabs-lifted` o `tabs tabs-boxed` para flujos internos.
- `UsiAlert`: wrapper sobre `alert` para mensajes operativos y errores.
- `UsiTable`: wrapper sobre `table table-zebra` con encabezado sobrio y scroll horizontal.
- `UsiToolbar`: contenedor de acciones con `btn btn-primary`, `btn btn-secondary`, `btn-outline`.

La regla de composicion es: crear componentes pequenos y explicitos antes que seguir agregando props booleanas. Por ejemplo, preferir `UsiCard.Header`, `UsiCard.Body` y `UsiCard.Footer` antes que un `SectionPanel` con muchas variantes.

### Patron de ficha nominal

El ejemplo `PatientProfile` de la guia debe adaptarse a la plataforma como `NominalProfile` o `PatientSummaryCard` dentro de la busqueda DNI/CNV.

- Encabezado: `card`, titulo en `text-primary`, badge de estado global.
- Identidad: avatar con iniciales, nombres, DNI/CNV y metadatos de nacimiento/establecimiento.
- Triaje de indicadores: grid 2x2 con botones tipo stat para componentes, CRED, tamizaje o subindicadores SI-02.
- Estado activo: `border-primary bg-base-200 ring-2 ring-primary/20`.
- Hover: `hover:border-secondary`.
- Semantica: usar `text-success`, `text-warning`, `text-error` solo para cumplimiento, advertencias e incumplimientos.

### Patron de tabs clinicos

El ejemplo `ClinicalTabs` debe convertirse en un componente reutilizable para dividir flujos complejos sin saturar la pantalla.

- En busqueda nominal: tabs para `Resumen`, `Componentes`, `CRED`, `Tamizaje`, `Evidencia`.
- En SI-02: tabs para subindicadores cuando la vista tenga mucho detalle, manteniendo el drawer como navegacion primaria.
- En carga de datos: tabs para `Validacion`, `Errores`, `Resumen`, `Auditoria` si la vista crece.
- En seguridad: tabs para `Usuarios`, `Roles`, `Permisos`, `Auditoria` en una fase posterior.

### Layout de 3 zonas

Las paginas principales deben usar una grilla asimetrica de 12 columnas:

- Zona superior: header fijo + contexto activo.
- Zona izquierda: datos resumidos, filtros, identidad nominal o estado operativo. Usar 4 a 5 columnas en desktop.
- Zona derecha: decisiones, tablas, historiales, tabs y acciones. Usar 7 a 8 columnas en desktop.

Patron base:

```jsx
<div className="min-h-screen bg-base-200">
  <div className="mx-auto max-w-7xl p-4 lg:p-6">
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
      <aside className="space-y-6 lg:col-span-5">
        {/* resumen, filtros o ficha nominal */}
      </aside>
      <section className="space-y-6 lg:col-span-7">
        {/* tabs, tablas, detalle y acciones */}
      </section>
    </div>
  </div>
</div>
```

## Redisenio por paginas

### App shell

- Header fijo con fondo `primary`, texto blanco y chips contextuales en `base-100`.
- Drawer izquierdo en `base-100`, borde `base-300`, navegacion activa con `primary` o `secondary`.
- Tabs de modulos con `btn btn-sm`, activo en `btn-primary`, inactivo `btn-ghost`.
- El contenido principal debe vivir en `bg-base-200`, con cards blancas y bordes discretos.

### Login

- Mantener el logotipo como elemento principal.
- Panel de marca en `primary` con acentos sutiles en `secondary` y `accent`.
- Formulario en `card bg-base-100`.
- Boton principal: `btn btn-primary`.
- Mensajes de error: `alert alert-error`.

### Busqueda DNI/CNV

- Reemplazar la lectura lineal por una ficha nominal:
  - Izquierda: `PatientSummaryCard` con identidad, ubicacion, establecimiento y estado global.
  - Derecha: `ClinicalTabs` con componentes, CRED, tamizaje y evidencia.
- Los componentes evaluados deben mostrarse como tarjetas `card` con badge de estado.
- SI-02 debe usar resumen por subindicador con tabs o accordion interno solo cuando el detalle lo requiera.

### Dashboard

- Usar el layout de 12 columnas:
  - Izquierda: periodo actual, cobertura, brecha, compromiso o estado global.
  - Derecha: tabla mensual, incumplidos, filtros y acciones.
- Las metricas principales deben usar `stats` o `card compacta`.
- `Compromiso SI-02` debe mantener jerarquia ejecutiva: estado global, verificacion vigente y progreso por subindicador.
- Evitar tarjetas con fondos multicolor; usar color solo en icono, barra de progreso o badge.

### Carga de datos

- Mantener el flujo en tres pasos: seleccionar, validar y activar.
- Usar `steps` de DaisyUI si el flujo crece, o `stats` para el estado operativo.
- Validacion, errores y auditoria deben agruparse en tabs si el contenido supera una pantalla.
- Historial de cargas: `table table-zebra`, badge semantico y version activa destacada.

### Usuarios y permisos

- Cabecera en `primary` para reforzar seguridad.
- Resumen con `stats`: activos, inactivos, permisos.
- Tabla de usuarios con `table`, acciones sensibles diferenciadas:
  - Activar: `btn-outline btn-success`.
  - Desactivar: `btn-outline btn-error`.
  - Renovar contrasena: `btn-outline btn-secondary`.
- Roles como cards neutras con borde lateral de acento, no como tarjetas multicolor.

### Configuracion

- Separar parametros editables de criterios informativos.
- Provincia, meta y seguros incluidos deben mostrarse como `stats`.
- Criterios de evaluacion deben ir en cards neutras.
- La meta puede usar `progress progress-secondary` para comunicar el umbral sin introducir otro color.

### Accesibilidad

- No usar `secondary` ni `accent` para parrafos largos sobre blanco.
- Texto principal siempre en `neutral` o `base-content`.
- Todo estado debe tener color, texto e icono.
- Los controles deben mantener foco visible con ring celeste.
- Probar desktop, tablet y movil antes de cerrar cada fase visual.

## Fases de trabajo

### 1. Sistema visual base

- Definir tokens centrales en Tailwind y CSS: colores, sombras, radios, bordes, estados y foco.
- Reducir dependencia de estilos ad hoc en cada vista.
- Normalizar componentes base: paneles, campos, botones, badges y tablas.
- Reemplazar fondos decorativos por una base de plataforma sobria.

### 2. Layout general de plataforma

- Convertir el encabezado principal en una barra operativa compacta y fija.
- Ordenar selector de indicador, filtro activo, meta y usuario como controles de contexto en el header.
- Unificar navegacion por permisos con estados claros dentro de un sidebar.
- Separar encabezado de plataforma del encabezado de cada vista.

### 3. Componentes compartidos

- Consolidar componentes reutilizables:
  - `PageHeader`
  - `TopbarChip`
  - `ModuleTab`
  - `IndicatorNavItem`
  - `SectionPanel`
  - `MetricCard`
  - `DataTable`
  - `StatusBadge`
  - `EmptyState`
  - `LoadingState`
  - `ErrorState`
- Aplicar composicion explicita para evitar componentes con demasiadas variantes booleanas.

### 4. Dashboard del indicador

- Priorizar el mes en evaluacion, brecha contra meta y compromiso vigente.
- Hacer mas escaneables subindicadores SI-02, avance mensual e incumplidos.
- Mejorar tablas con encabezados pegajosos, estados consistentes y acciones visibles.
- Separar lectura global e individual por subindicador sin duplicar informacion.

### 5. Busqueda DNI/CNV

- Redisenar como ficha de seguimiento nominal.
- Mostrar identidad, ubicacion sanitaria, estado global y componentes en bloques consistentes.
- Separar alertas clinicas, ventanas normativas y evidencia registrada.
- Para SI-02, usar secciones por subindicador con jerarquia clara.

### 6. Carga de datos

- Reforzar flujo de tres pasos: seleccionar, validar y activar.
- Mostrar fuente activa, validacion, errores bloqueantes, procesamiento y auditoria.
- Hacer visible el estado de trabajos en segundo plano.
- Mejorar lectura de paquetes multiparchivo SI-02.

### 7. Usuarios y permisos

- Convertir la vista en un panel de seguridad operativo.
- Mejorar tabla de usuarios, roles, permisos y estados de cuenta.
- Diferenciar acciones sensibles como desactivar usuario o renovar contrasena.
- Mostrar permisos por rol de forma compacta y verificable.

### 8. Configuracion

- Separar parametros editables de criterios informativos del indicador.
- Hacer visibles provincia, meta, poblacion objetivo, seguros incluidos y criterios de exclusion.
- Mantener foco en decisiones operativas, no en texto explicativo largo.

### 9. Accesibilidad y validacion visual

- Revisar contraste y foco de todos los controles.
- Probar desktop, tablet y movil.
- Verificar tablas, botones, textos largos y estados vacios.
- Ejecutar `npm run build` al cerrar cada bloque grande.

## Orden de ejecucion recomendado

1. Sistema visual base.
2. Layout general de plataforma.
3. Componentes compartidos.
4. Dashboard del indicador.
5. Busqueda DNI/CNV.
6. Carga de datos.
7. Usuarios y permisos.
8. Configuracion.
9. Validacion visual integral.

## Estado

- Rama de trabajo: `codex/visual-security-improvements`.
- Fase 1 aplicada: sistema visual base.
- Fase 2 aplicada parcialmente: header fijo y drawer sidebar.
- El encabezado principal quedo fijo con indicador activo, filtro, meta y usuario.
- La navegacion principal se movio a un drawer sidebar fijo a la izquierda, minimizable y con scroll interno.
- El selector de indicadores se movio al sidebar como lista; SI-02 incluye acordeon de subindicadores conectado al dashboard.
- Los modulos principales se reubicaron en una barra horizontal fija dentro del header para mantenerlos accesibles aunque el drawer crezca.
- Fase 3 iniciada: componentes compartidos extraidos desde el layout principal (`PageHeader`, `TopbarChip`, `ModuleTab`, `IndicatorNavItem`).
- Fase 4 iniciada: dashboard con bloque superior de periodo en evaluacion, brecha contra meta y secciones basadas en `SectionPanel`.
- Ajuste SI-02: la vista global del dashboard muestra solo `Compromiso SI-02`; tablas mensual e incumplidos quedan reservadas para subindicadores seleccionados desde el drawer.
- `Compromiso SI-02` queda visible solo en la vista global y fue redisenado como panel ejecutivo de verificacion vigente con avance por subindicador.
- Fase 5 iniciada: busqueda nominal redisenada con buscador operativo, banner de estado del paquete y ficha nominal con datos personales/ubicacion.
- Fase 6 aplicada: carga de datos con estado operativo visible, flujo seleccionar-validar-activar, zona de archivo clara e historial con estados administrativos consistentes.
- Fase 7 aplicada: usuarios y permisos redisenado como panel de seguridad con resumen de cuentas, permisos por rol y tabla administrativa con estados visibles.
- Fase 8 aplicada: configuracion redisenada como pantalla de parametros operativos con provincia, meta, seguros y criterios diferenciados.
- Fase 9 aplicada: contraste global reforzado con fondo clinico tintado, paneles con gradientes suaves, header superior con color y tablas/chips menos planos.
- Ajuste de paleta aplicada: se adopto la guia visual USI (`#102D52`, `#0EA5E9`, `#C2A4CF`), se integro DaisyUI 4 compatible con Tailwind 3 y los componentes compartidos migraron a primitivas `card`, `btn`, `badge` y `stat`.
- Guia de implementacion incorporada: el siguiente redisenio de paginas debe seguir los patrones `PatientSummaryCard`, `ClinicalTabs`, layout de 3 zonas y componentes `Usi*` basados en DaisyUI/Premium.
- Inicio de redisenio USI aplicado: `tailwind.config.js` define `usiTheme`, se agregaron componentes base `UsiCard`, `UsiBadge`, `UsiStat` y `UsiTabs`, y el App shell migro a header `primary`, drawer neutro y `data-theme="usiTheme"`.
- Login redisenado con panel institucional `primary`, formulario DaisyUI, `input input-bordered`, `alert alert-error` y accion `btn btn-primary`.
- Busqueda DNI/CNV redisenada con layout de 3 zonas: ficha nominal `PatientSummaryCard` a la izquierda y tabs clinicos `UsiTabs` a la derecha para componentes, CRED, tamizaje, SI-02 y alertas.
- Dashboard redisenado con layout de 12 columnas USI: periodo, cobertura, brecha y metricas a la izquierda; seguimiento mensual e incumplidos con tablas DaisyUI a la derecha. La vista global SI-02 conserva solo el panel ejecutivo `Compromiso SI-02`.
- Ajuste de densidad aplicado: busqueda nominal usa una franja compacta de paciente activo y deja componentes/subindicadores a ancho completo; dashboard deja la tabla de incumplidos como bloque principal a todo el ancho y reduce evaluacion/avance a resumen compacto.
- Fases restantes cerradas con USI/DaisyUI: carga de datos, usuarios/permisos y configuracion migraron a superficies `base-*`, cabeceras `primary`, controles `btn/input/select/table/badge` y colores semanticos solo para estados.
- Fase 9 cerrada como validacion integral de contraste, densidad visual, tablas principales y estados vacios/error/carga.
- Validacion tecnica final: `npm run build` OK.
