#!/bin/sh
set -eu

python - <<'PY'
import os
import time
from sqlalchemy import create_engine, text

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise SystemExit("DATABASE_URL no esta configurado")

last_error = None
for _ in range(60):
    try:
        engine = create_engine(database_url, pool_pre_ping=True, future=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        break
    except Exception as exc:
        last_error = exc
        time.sleep(1)
else:
    raise SystemExit(f"No se pudo conectar a PostgreSQL: {last_error}")
PY

cd /app/backend
python -m alembic -c alembic.ini upgrade head

cd /app
python -m backend.sync_security

exec "$@"
