# MC-03 App - Seguimiento Neonatal

Proyecto basado en el Sistema de Seguimiento Neonatal para la Red de Salud Abancay.

## Estructura del workspace

- `backend/`: API en FastAPI para procesar datos HIS y generar reportes de cumplimiento.
- `frontend/`: App React con Vite y Tailwind para el dashboard de gestion.
- `data_samples/`: carpeta preparada para almacenar archivos de ejemplo.
- `docs/`: espacio para documentacion adicional.

## Como arrancar

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Tambien puedes arrancar desde la raiz del proyecto con:

```powershell
uvicorn backend.main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Notas

- El backend ya incluye un modulo `backend/config.py` con reglas MC-03.
- El frontend esta configurado para hacer proxy a `/api` hacia el backend local.

## Criterio de diseno frontend con daisyUI

Se puede usar `daisyUI` para acelerar el desarrollo de componentes comunes, manteniendo la identidad visual sobria y profesional del sistema MC-03.

### Uso recomendado

- Usar daisyUI de forma selectiva para componentes base: `btn`, `alert`, `badge`, `modal`, `tabs`, `input`, `select`, `table`, `loading` y estados de formulario.
- Mantener diseno propio para layouts principales, dashboard, tablas de seguimiento, semaforizacion, cabecera institucional y vistas operativas.
- Priorizar una interfaz clara para salud: buen contraste, lectura rapida, estados verde/rojo consistentes y superficies sobrias.
- Combinar clases daisyUI con utilidades Tailwind cuando sea necesario, por ejemplo `btn btn-primary gap-2`.
- Usar iconos de `lucide-react` dentro de botones y acciones cuando aporten claridad.

### Precauciones

- No convertir toda la app a una plantilla generica de daisyUI; la identidad del sistema debe seguir siendo MC-03 / Red de Salud Abancay.
- Evitar `hero`, cards decorativas excesivas o temas visuales muy llamativos en vistas operativas.
- Revisar contraste antes de cerrar una vista, especialmente en badges, alertas, botones secundarios y tablas.
- No usar `!` para forzar estilos salvo que sea realmente necesario.
- No reemplazar semaforos clinicos existentes si el cambio reduce claridad.

### Compatibilidad

La documentacion actual de daisyUI 5 indica que requiere Tailwind CSS 4 y se configura desde CSS con `@plugin "daisyui";`. Este proyecto actualmente usa Tailwind CSS 3 con `tailwind.config.js`.

Por eso hay dos caminos posibles:

1. Mantener Tailwind 3 e instalar una version compatible de daisyUI 4.
2. Migrar a Tailwind 4 y usar daisyUI 5 siguiendo la documentacion actual.

Para avanzar con menor riesgo, se recomienda primero usar daisyUI compatible con Tailwind 3 y aplicarlo gradualmente en componentes nuevos o refactors pequenos.

Referencia revisada: https://daisyui.com/llms.txt
