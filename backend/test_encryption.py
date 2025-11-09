#!/usr/bin/env python3
"""
Test script to verify database encryption is working correctly.

This script verifies that user PII is encrypted at rest and can be
decrypted correctly using the encryption utilities.
"""

import os
import sys

# Set up path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.utils.encryption import encrypt_value, decrypt_value  # noqa: E402


def test_encryption():
    """Test that user data is encrypted and can be decrypted"""

    # Create database connection
    db = SessionLocal()

    try:
        print("=" * 60)
        print("TESTING DATABASE ENCRYPTION")
        print("=" * 60)

        # Get first user from database
        result = db.execute(text("""
            SELECT id, first_name, last_name, email
            FROM users
            LIMIT 1
        """))

        user = result.fetchone()

        if not user:
            print("❌ No users found in database to test")
            return False

        print(f"\nUser ID: {user.id}")
        print(f"Encrypted first_name (base64): {user.first_name[:50]}...")
        print(f"Encrypted last_name (base64):  {user.last_name[:50]}...")
        print(f"Encrypted email (base64):      {user.email[:50]}...")

        # Decrypt the values
        print("\n" + "=" * 60)
        print("DECRYPTING VALUES")
        print("=" * 60)

        decrypted_first = decrypt_value(db, user.first_name)
        decrypted_last = decrypt_value(db, user.last_name)
        decrypted_email = decrypt_value(db, user.email)

        print(f"\nDecrypted first_name: {decrypted_first}")
        print(f"Decrypted last_name:  {decrypted_last}")
        print(f"Decrypted email:      {decrypted_email}")

        # Verify decryption worked
        if decrypted_first and decrypted_last and decrypted_email:
            print("\n" + "=" * 60)
            print("✅ ENCRYPTION TEST PASSED")
            print("=" * 60)
            print("\nUser PII is successfully encrypted at rest!")
            print("Decryption is working correctly.")

            # Test re-encryption
            print("\n" + "=" * 60)
            print("TESTING RE-ENCRYPTION")
            print("=" * 60)

            re_encrypted = encrypt_value(db, decrypted_first)
            print(f"\nRe-encrypted first_name: {re_encrypted[:50]}...")

            # They should match if using same key
            if re_encrypted == user.first_name:
                print("✅ Re-encryption produces same ciphertext (deterministic)")
            else:
                print("⚠️  Re-encryption produces different ciphertext (non-deterministic)")
                print("   This is expected if using random IV/salt")

            return True
        else:
            print("\n" + "=" * 60)
            print("❌ ENCRYPTION TEST FAILED")
            print("=" * 60)
            print("\nDecryption returned null values!")
            return False

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ENCRYPTION TEST FAILED")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_encryption()
    sys.exit(0 if success else 1)
