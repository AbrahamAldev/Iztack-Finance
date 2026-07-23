"""
Sistema Financiero - File Hashing Utilities
SHA-256 hashing for file deduplication + password hashing.
"""
import hashlib

import bcrypt


class FileHasher:
    """File hashing utilities for deduplication."""

    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """Generate SHA-256 hash from bytes."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def hash_file(filepath: str, chunk_size: int = 8192) -> str:
        """Generate SHA-256 hash of a file (streaming for large files)."""
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def hash_string(text: str) -> str:
        """Generate SHA-256 hash from string."""
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def hash_metadata(store_name: str, receipt_number: str, total: float, date: str) -> str:
        """
        Generate a deterministic hash from ticket metadata for quick dedup check.
        This allows checking if a ticket was already processed without re-hashing files.
        """
        content = f"{store_name}|{receipt_number}|{total}|{date}"
        return FileHasher.hash_string(content)

    @staticmethod
    def verify_hash(filepath: str, expected_hash: str) -> bool:
        """Verify a file's hash matches expected value."""
        actual_hash = FileHasher.hash_file(filepath)
        return actual_hash == expected_hash


class PasswordHasher:
    """Password hashing using bcrypt."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password with bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                hashed.encode("utf-8")
            )
        except (ValueError, TypeError):
            return False
