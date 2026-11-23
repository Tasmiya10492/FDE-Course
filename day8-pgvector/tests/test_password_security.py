import pytest
from argon2 import extract_parameters
from argon2.low_level import Type
from src.password_security import (
    hash_password,
    password_hash_needs_update,
    validate_password,
    verify_password,
)


def test_rejects_password_shorter_than_15_characters():
    with pytest.raises(ValueError, match="at least 15"):
        validate_password("Short123!")


def test_accepts_password_of_15_characters():
    validate_password("MyLongPassphrase")


def test_accepts_password_of_64_characters():
    validate_password("a" * 64)


def test_rejects_blocklisted_password():
    with pytest.raises(ValueError, match="common"):
        validate_password("password1234567")


def test_does_not_require_character_composition():
    validate_password("aaaaaaaaaaaaaaa")


def test_hash_is_argon2id_and_not_plain_text():
    candidate = "A long and secure passphrase"
    password_hash = hash_password(candidate)

    assert password_hash != candidate
    assert extract_parameters(password_hash).type == Type.ID


def test_correct_password_verifies():
    candidate = "A different secure passphrase"
    password_hash = hash_password(candidate)

    assert verify_password(candidate, password_hash) is True


def test_incorrect_password_does_not_verify():
    password_hash = hash_password("A secure passphrase for testing")

    assert verify_password("An incorrect passphrase", password_hash) is False


def test_invalid_hash_does_not_verify():
    assert verify_password("Any password here", "not-a-valid-hash") is False


def test_hash_rehash_check_works():
    password_hash = hash_password("Another secure passphrase")

    assert password_hash_needs_update(password_hash) is False
