import os
import unittest
from unittest.mock import patch

from backend.security import (
    ROLE_ADMIN,
    ROLE_CLINICAL,
    AuthenticatedUser,
    create_access_token,
    development_user,
    hash_password,
    parse_token,
    verify_password,
)


class SecurityHelpersTest(unittest.TestCase):
    def test_password_hash_roundtrip(self):
        hashed = hash_password("clave-segura")

        self.assertTrue(verify_password("clave-segura", hashed))
        self.assertFalse(verify_password("otra-clave", hashed))

    def test_token_roundtrip_preserves_permissions(self):
        env = {
            **os.environ,
            "AUTH_ENABLED": "true",
            "AUTH_SECRET_KEY": "test-secret-with-enough-length",
            "AUTH_TOKEN_TTL_MINUTES": "30",
        }
        user = AuthenticatedUser(
            username="clinico",
            role=ROLE_CLINICAL,
            display_name="Usuario clinico",
            permissions_override=("search",),
        )

        with patch.dict(os.environ, env, clear=True):
            token = create_access_token(user)
            parsed = parse_token(token)

        self.assertEqual(parsed.username, "clinico")
        self.assertEqual(parsed.role, ROLE_CLINICAL)
        self.assertEqual(parsed.permissions, ["search"])

    def test_development_user_has_admin_permissions(self):
        user = development_user()

        self.assertEqual(user.role, ROLE_ADMIN)
        self.assertIn("users_admin", user.permissions)


if __name__ == "__main__":
    unittest.main()
