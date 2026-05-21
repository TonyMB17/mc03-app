"""Synchronize roles and bootstrap users after database migrations."""

from __future__ import annotations

try:
    from .db.session import SessionLocal
    from .security import ensure_security_defaults
except ImportError:
    from db.session import SessionLocal
    from security import ensure_security_defaults


def main() -> None:
    with SessionLocal() as db:
        ensure_security_defaults(db)


if __name__ == "__main__":
    main()
