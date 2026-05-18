"""Authentication and role-based access helpers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


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
    ROLE_ADMIN: ["search", "dashboard", "downloads", "config", "data_upload"],
}

TOKEN_TYPE = "bearer"
DEFAULT_TOKEN_TTL_MINUTES = 480
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    username: str
    role: str
    display_name: str

    @property
    def permissions(self) -> list[str]:
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


def development_user() -> AuthenticatedUser:
    return AuthenticatedUser(username="development", role=ROLE_ADMIN, display_name="Desarrollo local")


def load_users() -> dict[str, dict[str, str]]:
    raw_users = os.getenv("AUTH_USERS_JSON", "").strip()
    if not raw_users:
        return {}

    try:
        parsed = json.loads(raw_users)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AUTH_USERS_JSON no es JSON valido: {exc}",
        )

    users: dict[str, dict[str, str]] = {}
    for username, user_data in parsed.items():
        if not isinstance(user_data, dict):
            continue
        role = str(user_data.get("role") or "").strip().lower()
        password = str(user_data.get("password") or "")
        if role not in ROLE_ORDER or not password:
            continue
        users[str(username)] = {
            "password": password,
            "role": role,
            "display_name": str(user_data.get("display_name") or username),
        }
    return users


def authenticate_user(username: str, password: str) -> AuthenticatedUser | None:
    users = load_users()
    user_data = users.get(username)
    if not user_data:
        return None
    if not hmac.compare_digest(user_data["password"], password):
        return None
    return AuthenticatedUser(username=username, role=user_data["role"], display_name=user_data["display_name"])


def encode_part(data: dict[str, Any]) -> str:
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def decode_part(value: str) -> dict[str, Any]:
    padding = "=" * (-len(value) % 4)
    raw = base64.urlsafe_b64decode((value + padding).encode("ascii"))
    return json.loads(raw.decode("utf-8"))


def sign(value: str) -> str:
    digest = hmac.new(auth_secret().encode("utf-8"), value.encode("ascii"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def create_access_token(user: AuthenticatedUser) -> str:
    header = encode_part({"alg": "HS256", "typ": "JWT"})
    payload = encode_part(
        {
            "sub": user.username,
            "role": user.role,
            "name": user.display_name,
            "exp": int(time.time()) + token_ttl_seconds(),
        }
    )
    unsigned = f"{header}.{payload}"
    return f"{unsigned}.{sign(unsigned)}"


def parse_token(token: str) -> AuthenticatedUser:
    try:
        header, payload, signature = token.split(".", 2)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")

    unsigned = f"{header}.{payload}"
    if not hmac.compare_digest(sign(unsigned), signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")

    try:
        data = decode_part(payload)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")

    if int(data.get("exp") or 0) < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesion expirada.")

    role = str(data.get("role") or "").lower()
    if role not in ROLE_ORDER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Rol invalido.")

    return AuthenticatedUser(
        username=str(data.get("sub") or ""),
        role=role,
        display_name=str(data.get("name") or data.get("sub") or ""),
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


def require_roles(*allowed_roles: str) -> Callable[[AuthenticatedUser], AuthenticatedUser]:
    normalized_roles = tuple(role.lower() for role in allowed_roles)

    def dependency(user: AuthenticatedUser = Depends(current_user)) -> AuthenticatedUser:
        if not has_role(user, normalized_roles):
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


__all__ = [
    "AuthenticatedUser",
    "ROLE_ADMIN",
    "ROLE_CLINICAL",
    "ROLE_SUPERVISOR",
    "TOKEN_TYPE",
    "authenticate_user",
    "auth_enabled",
    "create_access_token",
    "current_user",
    "require_roles",
    "user_response",
]
