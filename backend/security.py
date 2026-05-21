"""Authentication and permission-based access helpers."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

try:
    from .db.models import AppPermission, AppRole, AppRolePermission, AppUser, AppUserRole
    from .db.session import get_db
except ImportError:
    from db.models import AppPermission, AppRole, AppRolePermission, AppUser, AppUserRole
    from db.session import get_db


ROLE_CLINICAL = "clinical"
ROLE_SUPERVISOR = "supervisor"
ROLE_ADMIN = "admin"
ROLE_ORDER = {
    ROLE_CLINICAL: 1,
    ROLE_SUPERVISOR: 2,
    ROLE_ADMIN: 3,
}
ROLE_LABELS = {
    ROLE_CLINICAL: "Usuario clinico",
    ROLE_SUPERVISOR: "Usuario supervisor",
    ROLE_ADMIN: "Administrador",
}
ROLE_PERMISSIONS = {
    ROLE_CLINICAL: ["search"],
    ROLE_SUPERVISOR: ["search", "dashboard", "downloads"],
    ROLE_ADMIN: ["search", "dashboard", "downloads", "config", "data_upload", "users_admin"],
}
PERMISSION_LABELS = {
    "search": "Busqueda por DNI/CNV",
    "dashboard": "Dashboard",
    "downloads": "Descargas",
    "config": "Configuracion",
    "data_upload": "Carga de datos",
    "users_admin": "Administracion de usuarios",
}

TOKEN_TYPE = "bearer"
JWT_ALGORITHM = "HS256"
DEFAULT_TOKEN_TTL_MINUTES = 480
bearer_scheme = HTTPBearer(auto_error=False)
password_hash = PasswordHash.recommended()


@dataclass(frozen=True)
class AuthenticatedUser:
    username: str
    role: str
    display_name: str
    permissions_override: tuple[str, ...] | None = None

    @property
    def permissions(self) -> list[str]:
        if self.permissions_override is not None:
            return list(self.permissions_override)
        return ROLE_PERMISSIONS.get(self.role, [])


def auth_enabled() -> bool:
    return os.getenv("AUTH_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}


def token_ttl_seconds() -> int:
    raw_value = os.getenv("AUTH_TOKEN_TTL_MINUTES", str(DEFAULT_TOKEN_TTL_MINUTES))
    try:
        minutes = int(raw_value)
    except ValueError:
        minutes = DEFAULT_TOKEN_TTL_MINUTES
    return max(5, minutes) * 60


def auth_secret() -> str:
    secret = os.getenv("AUTH_SECRET_KEY", "")
    if auth_enabled() and not secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AUTH_SECRET_KEY no esta configurado.",
        )
    return secret or "development-only-secret"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(password, hashed_password)
    except Exception:
        return False


def development_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        username="development",
        role=ROLE_ADMIN,
        display_name="Desarrollo local",
        permissions_override=tuple(ROLE_PERMISSIONS[ROLE_ADMIN]),
    )


def authenticate_user(db: Session, username: str, password: str) -> AuthenticatedUser | None:
    user = get_user_by_username(db, username)
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    return authenticated_user_from_model(user)


def create_access_token(user: AuthenticatedUser) -> str:
    payload = {
        "sub": user.username,
        "role": user.role,
        "name": user.display_name,
        "permissions": user.permissions,
        "exp": int(time.time()) + token_ttl_seconds(),
        "iat": int(time.time()),
    }
    return jwt.encode(payload, auth_secret(), algorithm=JWT_ALGORITHM)


def parse_token(token: str) -> AuthenticatedUser:
    try:
        data = jwt.decode(token, auth_secret(), algorithms=[JWT_ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")

    role = str(data.get("role") or "").lower()
    if role not in ROLE_ORDER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Rol invalido.")
    username = str(data.get("sub") or "").strip()
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")

    permissions = tuple(str(item) for item in data.get("permissions") or ROLE_PERMISSIONS.get(role, []))
    return AuthenticatedUser(
        username=username,
        role=role,
        display_name=str(data.get("name") or username),
        permissions_override=permissions,
    )


def current_user(
    _request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser:
    if not auth_enabled():
        return development_user()

    if credentials is None or credentials.scheme.lower() != TOKEN_TYPE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticacion requerida.")
    return parse_token(credentials.credentials)


def has_role(user: AuthenticatedUser, allowed_roles: tuple[str, ...]) -> bool:
    user_level = ROLE_ORDER.get(user.role, 0)
    allowed_levels = [ROLE_ORDER.get(role, 999) for role in allowed_roles]
    return user_level >= min(allowed_levels)


def has_permission(user: AuthenticatedUser, permission: str) -> bool:
    return permission in user.permissions


def require_roles(*allowed_roles: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    normalized_roles = tuple(role.lower() for role in allowed_roles)

    def dependency(user: AuthenticatedUser = Depends(current_user)) -> AuthenticatedUser:
        if not has_role(user, normalized_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para esta accion.")
        return user

    return dependency


def require_permissions(*permissions: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    requested = tuple(permissions)

    def dependency(user: AuthenticatedUser = Depends(current_user)) -> AuthenticatedUser:
        if not all(has_permission(user, permission) for permission in requested):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para esta accion.")
        return user

    return dependency


def user_response(user: AuthenticatedUser) -> dict[str, Any]:
    return {
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
        "role_label": ROLE_LABELS.get(user.role, user.role),
        "permissions": user.permissions,
        "auth_enabled": auth_enabled(),
    }


def get_user_by_username(db: Session, username: str) -> AppUser | None:
    username = normalize_username(username)
    statement = (
        select(AppUser)
        .options(
            selectinload(AppUser.roles).selectinload(AppUserRole.role).selectinload(AppRole.permissions).selectinload(AppRolePermission.permission)
        )
        .where(AppUser.username == username)
    )
    return db.execute(statement).scalars().first()


def authenticated_user_from_model(user: AppUser) -> AuthenticatedUser:
    role_codes = [item.role.code for item in user.roles if item.role]
    role = highest_role(role_codes)
    permissions = sorted(
        {
            permission.permission.code
            for user_role in user.roles
            for permission in user_role.role.permissions
            if permission.permission
        }
    )
    return AuthenticatedUser(
        username=user.username,
        role=role,
        display_name=user.display_name,
        permissions_override=tuple(permissions or ROLE_PERMISSIONS.get(role, [])),
    )


def highest_role(role_codes: list[str]) -> str:
    if not role_codes:
        return ROLE_CLINICAL
    return max(role_codes, key=lambda code: ROLE_ORDER.get(code, 0))


def ensure_security_defaults(db: Session) -> None:
    permissions = ensure_permissions(db)
    roles = ensure_roles(db)
    ensure_role_permissions(db, roles, permissions)
    ensure_bootstrap_users(db, roles)
    db.commit()


def ensure_permissions(db: Session) -> dict[str, AppPermission]:
    existing = {item.code: item for item in db.execute(select(AppPermission)).scalars().all()}
    for code, label in PERMISSION_LABELS.items():
        permission = existing.get(code)
        if permission is None:
            permission = AppPermission(code=code, label=label, is_system=True)
            db.add(permission)
            existing[code] = permission
        else:
            permission.label = label
            permission.is_system = True
    db.flush()
    return existing


def ensure_roles(db: Session) -> dict[str, AppRole]:
    existing = {item.code: item for item in db.execute(select(AppRole)).scalars().all()}
    for code, label in ROLE_LABELS.items():
        role = existing.get(code)
        if role is None:
            role = AppRole(code=code, label=label, is_system=True)
            db.add(role)
            existing[code] = role
        else:
            role.label = label
            role.is_system = True
    db.flush()
    return existing


def ensure_role_permissions(db: Session, roles: dict[str, AppRole], permissions: dict[str, AppPermission]) -> None:
    existing_pairs = {
        (item.role_id, item.permission_id)
        for item in db.execute(select(AppRolePermission)).scalars().all()
    }
    for role_code, permission_codes in ROLE_PERMISSIONS.items():
        role = roles[role_code]
        for permission_code in permission_codes:
            permission = permissions[permission_code]
            pair = (role.id, permission.id)
            if pair not in existing_pairs:
                db.add(AppRolePermission(role_id=role.id, permission_id=permission.id))
                existing_pairs.add(pair)


def ensure_bootstrap_users(db: Session, roles: dict[str, AppRole]) -> None:
    users = bootstrap_users_from_env()
    if not users and db.execute(select(AppUser.id).limit(1)).first() is None:
        users = {
            "admin": {
                "password": "admin123",
                "role": ROLE_ADMIN,
                "display_name": "Administrador",
                "must_change_password": True,
            }
        }

    for username, data in users.items():
        username = normalize_username(username)
        role_code = str(data.get("role") or ROLE_CLINICAL).lower()
        role = roles.get(role_code) or roles[ROLE_CLINICAL]
        existing_user = get_user_by_username(db, username)
        if existing_user is not None:
            existing_user.display_name = str(data.get("display_name") or username)
            existing_user.password_hash = hash_password(str(data["password"]))
            existing_user.is_active = bool(data.get("is_active", True))
            existing_user.must_change_password = bool(data.get("must_change_password", False))
            sync_user_role(db, existing_user, role)
            continue

        user = AppUser(
            username=username,
            display_name=str(data.get("display_name") or username),
            password_hash=hash_password(str(data["password"])),
            is_active=bool(data.get("is_active", True)),
            must_change_password=bool(data.get("must_change_password", False)),
        )
        db.add(user)
        db.flush()
        db.add(AppUserRole(user_id=user.id, role_id=role.id))


def sync_user_role(db: Session, user: AppUser, role: AppRole) -> None:
    current_roles = db.execute(select(AppUserRole).where(AppUserRole.user_id == user.id)).scalars().all()
    has_target_role = False
    for current_role in current_roles:
        if current_role.role_id == role.id:
            has_target_role = True
            continue
        db.delete(current_role)
    if not has_target_role:
        db.add(AppUserRole(user_id=user.id, role_id=role.id))


def bootstrap_users_from_env() -> dict[str, dict[str, Any]]:
    raw_users = os.getenv("AUTH_USERS_JSON", "").strip()
    if not raw_users:
        return {}
    try:
        parsed = json.loads(raw_users)
    except json.JSONDecodeError:
        return {}

    users: dict[str, dict[str, Any]] = {}
    for username, user_data in parsed.items():
        if not isinstance(user_data, dict):
            continue
        password = str(user_data.get("password") or "")
        role = str(user_data.get("role") or "").strip().lower()
        if not password or role not in ROLE_ORDER:
            continue
        normalized_username = normalize_username(str(username))
        if not normalized_username:
            continue
        users[normalized_username] = {
            "password": password,
            "role": role,
            "display_name": str(user_data.get("display_name") or username),
            "is_active": bool(user_data.get("is_active", True)),
            "must_change_password": bool(user_data.get("must_change_password", False)),
        }
    return users


def list_users(db: Session) -> list[dict[str, Any]]:
    statement = (
        select(AppUser)
        .options(selectinload(AppUser.roles).selectinload(AppUserRole.role))
        .order_by(AppUser.username)
    )
    return [user_admin_response(user) for user in db.execute(statement).scalars().all()]


def list_roles(db: Session) -> list[dict[str, Any]]:
    statement = select(AppRole).options(selectinload(AppRole.permissions).selectinload(AppRolePermission.permission)).order_by(AppRole.code)
    roles = []
    for role in db.execute(statement).scalars().all():
        roles.append(
            {
                "code": role.code,
                "label": role.label,
                "description": role.description,
                "permissions": sorted(item.permission.code for item in role.permissions if item.permission),
                "is_system": role.is_system,
            }
        )
    return roles


def create_user(db: Session, username: str, password: str, display_name: str, role: str, is_active: bool = True) -> dict[str, Any]:
    username = normalize_username(username)
    display_name = display_name.strip()
    role = role.strip().lower()
    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario es obligatorio.")
    if len(password or "") < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contrasena debe tener al menos 6 caracteres.")
    if not display_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre visible es obligatorio.")
    if get_user_by_username(db, username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya existe.")
    role_model = db.execute(select(AppRole).where(AppRole.code == role)).scalars().first()
    if role_model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol no valido.")
    user = AppUser(
        username=username,
        display_name=display_name,
        password_hash=hash_password(password),
        is_active=is_active,
    )
    db.add(user)
    db.flush()
    db.add(AppUserRole(user_id=user.id, role_id=role_model.id))
    db.commit()
    db.refresh(user)
    return user_admin_response(get_user_by_username(db, username) or user)


def update_user(db: Session, username: str, payload: dict[str, Any]) -> dict[str, Any]:
    username = normalize_username(username)
    user = get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    if "display_name" in payload and payload["display_name"]:
        user.display_name = str(payload["display_name"])
    if "is_active" in payload and payload["is_active"] is not None:
        user.is_active = bool(payload["is_active"])
    if payload.get("password"):
        if len(str(payload["password"])) < 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La contrasena debe tener al menos 6 caracteres.")
        user.password_hash = hash_password(str(payload["password"]))
        user.must_change_password = False
    if payload.get("role"):
        role = db.execute(select(AppRole).where(AppRole.code == str(payload["role"]).strip().lower())).scalars().first()
        if role is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol no valido.")
        user.roles.clear()
        db.flush()
        db.add(AppUserRole(user_id=user.id, role_id=role.id))
    db.commit()
    return user_admin_response(get_user_by_username(db, username) or user)


def user_admin_response(user: AppUser) -> dict[str, Any]:
    role_codes = sorted(item.role.code for item in user.roles if item.role)
    return {
        "username": user.username,
        "display_name": user.display_name,
        "roles": role_codes,
        "role": highest_role(role_codes),
        "is_active": user.is_active,
        "must_change_password": user.must_change_password,
        "last_login_at": user.last_login_at,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def normalize_username(username: str) -> str:
    return str(username or "").strip().lower()


__all__ = [
    "AuthenticatedUser",
    "ROLE_ADMIN",
    "ROLE_CLINICAL",
    "ROLE_SUPERVISOR",
    "TOKEN_TYPE",
    "authenticate_user",
    "auth_enabled",
    "create_access_token",
    "create_user",
    "current_user",
    "ensure_security_defaults",
    "list_roles",
    "list_users",
    "require_permissions",
    "require_roles",
    "update_user",
    "user_response",
]
