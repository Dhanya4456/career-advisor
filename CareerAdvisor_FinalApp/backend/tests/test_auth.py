import sys
import unittest
from pathlib import Path

from fastapi import HTTPException
from jose import jwt
from pymongo.errors import DuplicateKeyError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.services.auth import JWT_ALGORITHM, login_user, register_user


class MemoryUsers:
    def __init__(self):
        self.documents = {}

    async def insert_one(self, document):
        if document["email"] in self.documents:
            raise DuplicateKeyError("duplicate email")
        self.documents[document["email"]] = dict(document)

    async def find_one(self, query):
        return self.documents.get(query["email"])


class MemoryDatabase:
    def __init__(self):
        self.users = MemoryUsers()


class AuthServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.database = MemoryDatabase()

    async def test_register_login_and_verify_token(self):
        created = await register_user(
            self.database, "Student@Example.com", "correct horse battery", "Student"
        )
        signed_in = await login_user(
            self.database, "student@example.com", "correct horse battery"
        )
        payload = jwt.decode(
            signed_in["access_token"], get_settings().jwt_secret, algorithms=[JWT_ALGORITHM]
        )
        self.assertEqual(created["user_id"], signed_in["user_id"])
        self.assertEqual(payload["sub"], created["user_id"])
        self.assertNotEqual(
            self.database.users.documents["student@example.com"]["password_hash"],
            "correct horse battery",
        )

    async def test_duplicate_email_is_rejected(self):
        await register_user(self.database, "student@example.com", "correct horse battery", "Student")
        with self.assertRaises(HTTPException) as error:
            await register_user(self.database, "student@example.com", "another password", "Other")
        self.assertEqual(error.exception.status_code, 409)

    async def test_wrong_password_is_rejected(self):
        await register_user(self.database, "student@example.com", "correct horse battery", "Student")
        with self.assertRaises(HTTPException) as error:
            await login_user(self.database, "student@example.com", "wrong password")
        self.assertEqual(error.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
