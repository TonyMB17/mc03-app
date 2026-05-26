# Promocion controlada a main

Este proyecto usa la rama de desarrollo para conservar documentacion, decisiones y archivos auxiliares. La rama `main` debe mantenerse como rama de produccion, con solo los archivos necesarios para construir y ejecutar el sistema.

## Regla general

- La rama de desarrollo conserva la documentacion completa: `backend/README.md`, `docs/` y notas de implementacion.
- La rama `main` recibe codigo, configuracion, migraciones, assets versionados y archivos necesarios para despliegue.
- `README.md` es la unica documentacion permitida en `main`; debe ser una guia breve para levantar el proyecto en produccion/despliegue.
- No promover a `main` documentacion de trabajo, bitacoras, pruebas exploratorias ni archivos temporales.

## Flujo recomendado

1. Trabajar y documentar en la rama de desarrollo.
2. Ejecutar pruebas y build.
3. Hacer commit y push de la rama de desarrollo.
4. Actualizar `main` desde `origin/main`.
5. Copiar hacia `main` solo las rutas de produccion desde la rama de desarrollo.
6. Verificar build/pruebas minimas en `main`.
7. Commit y push de `main`.

## Rutas que normalmente si se promueven

- `backend/`
- `frontend/src/`
- `frontend/dist/`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/index.html`
- `frontend/Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `.gitignore`
- `README.md`
- `alembic.ini`

Excluir de esta lista archivos de documentacion o pruebas si estan dentro de esas rutas y no son necesarios para ejecutar produccion. La unica excepcion documental es `README.md`.

## Rutas que no deben promoverse a main

- `backend/README.md`
- `docs/`
- `backend/tests/`
- Archivos de notas, decisiones o readmes creados para desarrollo.

## Comandos base

```powershell
git checkout main
git pull --ff-only origin main

# Ejemplo: traer solo rutas de produccion desde la rama de desarrollo.
git checkout codex/visual-security-improvements -- backend frontend/src frontend/dist docker-compose.yml

# Retirar rutas de documentacion o pruebas si entraron por estar dentro de una carpeta amplia.
git restore --staged backend/README.md docs backend/tests
git restore backend/README.md docs backend/tests

git status --short
npm run build --prefix frontend
backend\.venv\Scripts\python.exe -m py_compile backend\main.py

git add <rutas-produccion>
git commit -m "chore: promote production changes"
git push origin main
```

## Nota

Si un cambio de infraestructura requiere documentacion para operar produccion, mantener esa guia en la rama de desarrollo y copiar a `main` solo variables, scripts o configuraciones que el despliegue necesite realmente.
