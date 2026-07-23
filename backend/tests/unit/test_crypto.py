"""Unit tests for CryptoManager and setup_crypto utilities."""
import pytest

from app.utils.crypto import CryptoManager
from app.utils.setup_crypto import (
    encrypt_secret,
    decrypt_secret,
    get_or_create_master_key,
)


class TestCryptoManager:
    def test_encrypt_decrypt_roundtrip(self):
        cm = CryptoManager("test-secret-key")
        plaintext = "my-super-secret"
        blob = cm.encrypt_to_blob(plaintext, context="ctx")
        decrypted = cm.decrypt_from_blob(blob, context="ctx")
        assert decrypted == plaintext

    def test_decrypt_wrong_context_returns_none(self):
        cm = CryptoManager("test-secret-key")
        blob = cm.encrypt_to_blob("secret", context="ctx-a")
        assert cm.decrypt_from_blob(blob, context="ctx-b") is None

    def test_empty_plaintext(self):
        cm = CryptoManager("test-secret-key")
        assert cm.encrypt_to_blob("") is None
        assert cm.decrypt_from_blob(None) is None

    def test_password_generation(self):
        cm = CryptoManager("test-secret-key")
        password = cm.generate_password(length=16)
        assert len(password) == 16


class TestSetupCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        key = get_or_create_master_key()
        plaintext = "tenant-secret"
        blob, key_id = encrypt_secret(plaintext, key, key_id="v1")
        decrypted = decrypt_secret(blob, key, key_id=key_id)
        assert decrypted == plaintext

    def test_decrypt_with_wrong_key_fails(self):
        key = get_or_create_master_key()
        wrong_key = b"0" * 32
        blob, _ = encrypt_secret("tenant-secret", key)
        with pytest.raises(Exception):
            decrypt_secret(blob, wrong_key)
