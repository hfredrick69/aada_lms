"""
HIPAA-compliant encryption utilities for PHI data.

Uses PostgreSQL pgcrypto for transparent column-level encryption.
Encryption key should be stored in environment variables, not in code.
"""
from typing import Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
import os


# Encryption key from environment (NEVER hardcode in production)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "change_this_key_in_production")


def encrypt_value(db: Session, value: str) -> Optional[str]:
    """
    Encrypt a value using PostgreSQL pgcrypto.

    Args:
        db: Database session
        value: Plain text value to encrypt

    Returns:
        Base64-encoded encrypted value, or None if value is None
    """
    if value is None:
        return None

    result = db.execute(
        text("SELECT encode(pgp_sym_encrypt(:value, :key), 'base64')"),
        {"value": value, "key": ENCRYPTION_KEY}
    ).scalar()

    return result


def decrypt_value(db: Session, encrypted_value: str) -> Optional[str]:
    """
    Decrypt a value using PostgreSQL pgcrypto.

    Args:
        db: Database session
        encrypted_value: Base64-encoded encrypted value

    Returns:
        Decrypted plain text value, or None if encrypted_value is None
    """
    if encrypted_value is None:
        return None

    result = db.execute(
        text("SELECT pgp_sym_decrypt(decode(:encrypted, 'base64'), :key)"),
        {"encrypted": encrypted_value, "key": ENCRYPTION_KEY}
    ).scalar()

    return result


def encrypt_dict_fields(db: Session, data: dict, fields: list[str]) -> dict:
    """
    Encrypt specific fields in a dictionary.

    Args:
        db: Database session
        data: Dictionary containing data
        fields: List of field names to encrypt

    Returns:
        Dictionary with specified fields encrypted
    """
    result = data.copy()
    for field in fields:
        if field in result and result[field] is not None:
            result[field] = encrypt_value(db, str(result[field]))
    return result


def decrypt_dict_fields(db: Session, data: dict, fields: list[str]) -> dict:
    """
    Decrypt specific fields in a dictionary.

    Args:
        db: Database session
        data: Dictionary containing encrypted data
        fields: List of field names to decrypt

    Returns:
        Dictionary with specified fields decrypted
    """
    result = data.copy()
    for field in fields:
        if field in result and result[field] is not None:
            result[field] = decrypt_value(db, result[field])
    return result


# PHI fields that should be encrypted at rest
PHI_FIELDS = {
    "users": ["first_name", "last_name", "email"],
    "credentials": ["credential_number", "issuing_authority"],
    "transcripts": ["comments"],
    "complaints": ["description", "complainant_name", "complainant_email"],
    "attendance_logs": ["notes"],
    "skill_checkoffs": ["notes", "instructor_comments"],
    "externships": ["site_name", "site_contact", "site_address"],
    "financial_ledger": ["description", "payment_method"],
}


def get_phi_fields(table_name: str) -> list[str]:
    """
    Get list of PHI fields for a given table.

    Args:
        table_name: Name of the database table

    Returns:
        List of field names that contain PHI
    """
    return PHI_FIELDS.get(table_name, [])
