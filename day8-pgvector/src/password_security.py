"""Password validation and Argon2id password hashing for Day 16."""

from argon2 import PasswordHasher, Type
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

MIN_PASSWORD_LENGTH = 15
MAX_PASSWORD_LENGTH = 1024

# A small local blocklist for this learning build.
# A production system should use a substantially larger breached-password list.
BLOCKLIST = {
    "password1234567",
    "qwertyuiopasdfg",
    "letmeinletmein!",
    "123456789012345",
    "passwordpassword",
    "correcthorsebatterystaple",
}

password_hasher = PasswordHasher(type=Type.ID)


def validate_password(password: str) -> None:
    """Enforce length and blocklist rules without composition requirements."""
    if not isinstance(password, str):
        raise ValueError("Password must be text.")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError("Password must contain at least 15 characters.")

    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError("Password is too long.")

    if password.casefold() in BLOCKLIST:
        raise ValueError("This password is too common or easily guessed.")


def hash_password(password: str) -> str:
    """Validate and securely hash a password using Argon2id."""
    validate_password(password)
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password without exposing hashing errors to callers."""
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError, VerificationError, InvalidHashError:
        return False


def password_hash_needs_update(password_hash: str) -> bool:
    """Check whether the stored Argon2 parameters need updating."""
    try:
        return password_hasher.check_needs_rehash(password_hash)
    except VerificationError, InvalidHashError:
        return True
