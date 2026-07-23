"""
Sistema Financiero - Setup Module Tests
Basic unit tests for the credential validators.
"""
from app.modules.setup.service import (
    _validate_gemini_shape,
    _validate_telegram_shape,
)


class TestTelegramShape:
    def test_accepts_valid_format(self):
        token = "1234567890:AAEhBO3eP8dB4xKb5lN6m7o8p9q0r1s2t3u4v"
        assert _validate_telegram_shape(token) is None

    def test_rejects_short_id(self):
        token = "123:AAEhBO3eP8dB4xKb5lN6m7o8p9q0r1s2t3u4v"
        assert _validate_telegram_shape(token) is not None

    def test_rejects_wrong_secret_length(self):
        token = "1234567890:short"
        assert _validate_telegram_shape(token) is not None

    def test_rejects_no_colon(self):
        token = "1234567890AAEhBO3eP8dB4xKb5lN6m7o8p9q0r1s2t3u4v"
        assert _validate_telegram_shape(token) is not None


class TestGeminiShape:
    def test_accepts_valid_key(self):
        key = "AIzaSyA" + "a" * 32
        assert _validate_gemini_shape(key) is None

    def test_rejects_wrong_prefix(self):
        key = "sk-" + "a" * 40
        assert _validate_gemini_shape(key) is not None

    def test_rejects_too_short(self):
        key = "AIza"
        assert _validate_gemini_shape(key) is not None
