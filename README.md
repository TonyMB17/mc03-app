# MC-03 App - Seguimiento Neonatal

Proyecto basado en el Sistema de Seguimiento Neonatal para la Red de Salud Abancay.

## Estructura del workspace

- `backend/`: API en FastAPI para procesar datos HIS y generar reportes de cumplimiento.
- `frontend/`: App React con Vite y Tailwind para el dashboard de gestión.
- `data_samples/`: carpeta preparada para almacenar archivos de ejemplo.
- `docs/`: espacio para documentación adicional.

## Cómo arrancar

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

También puedes arrancar desde la raíz del proyecto con:

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

- El backend ya incluye un módulo `backend/config.py` con reglas MC-03.
- El frontend está configurado para hacer proxy a `/api` hacia el backend local.
