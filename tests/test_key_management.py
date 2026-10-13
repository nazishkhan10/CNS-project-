"""
Test Suite: RSA Key Management
Tests key pair generation, PEM serialization, encryption with password, and safe loading.
"""

import unittest
from cryptography.hazmat.primitives.asymmetric import rsa

from crypto_utils.key_manager import (
    generate_rsa_key_pair,
    serialize_public_key,
    serialize_private_key,
    load_public_key,
    load_private_key,
    is_private_key_encrypted,
)


class TestKeyManagement(unittest.TestCase):
    
    def test_rsa_key_pair_generation_succeeds(self):
        """Test Case 1: RSA key-pair generation succeeds."""
        priv_key, pub_key = generate_rsa_key_pair(2048)
        self.assertIsInstance(priv_key, rsa.RSAPrivateKey)
        self.assertIsInstance(pub_key, rsa.RSAPublicKey)
        self.assertEqual(priv_key.key_size, 2048)
        self.assertEqual(pub_key.key_size, 2048)

    def test_insecure_key_size_rejected(self):
        """Ensure key sizes below 2048 bits are rejected."""
        with self.assertRaises(ValueError):
            generate_rsa_key_pair(1024)

    def test_public_key_pem_roundtrip(self):
        """Serialize public key to PEM and load it back."""
        _, pub_key = generate_rsa_key_pair(2048)
        pem_bytes = serialize_public_key(pub_key)
        self.assertTrue(pem_bytes.startswith(b"-----BEGIN PUBLIC KEY-----"))
        
        loaded_pub = load_public_key(pem_bytes)
        self.assertEqual(loaded_pub.key_size, 2048)

    def test_private_key_unencrypted_roundtrip(self):
        """Serialize unencrypted private key and load it back."""
        priv_key, _ = generate_rsa_key_pair(2048)
        pem_bytes = serialize_private_key(priv_key, password=None)
        self.assertFalse(is_private_key_encrypted(pem_bytes))
        
        loaded_priv = load_private_key(pem_bytes, password=None)
        self.assertEqual(loaded_priv.key_size, 2048)

    def test_private_key_encrypted_with_password(self):
        """Serialize private key with passphrase and verify encryption."""
        priv_key, _ = generate_rsa_key_pair(2048)
        passphrase = "CorrectCollegePassword123!"
        pem_bytes = serialize_private_key(priv_key, password=passphrase)
        
        self.assertTrue(is_private_key_encrypted(pem_bytes))
        loaded_priv = load_private_key(pem_bytes, password=passphrase)
        self.assertEqual(loaded_priv.key_size, 2048)

    def test_wrong_private_key_password_rejected(self):
        """Test Case 7: A wrong private-key password is rejected."""
        priv_key, _ = generate_rsa_key_pair(2048)
        pem_bytes = serialize_private_key(priv_key, password="SecretPassword1")
        
        with self.assertRaises(ValueError) as ctx:
            load_private_key(pem_bytes, password="WrongPassword2")
        self.assertIn("Incorrect private key password", str(ctx.exception))

    def test_missing_password_for_encrypted_key_rejected(self):
        """Attempting to load encrypted private key with no password must fail clearly."""
        priv_key, _ = generate_rsa_key_pair(2048)
        pem_bytes = serialize_private_key(priv_key, password="SecretPassword1")
        
        with self.assertRaises(ValueError) as ctx:
            load_private_key(pem_bytes, password=None)
        self.assertIn("password-protected", str(ctx.exception))

    def test_empty_or_corrupted_pem_rejected(self):
        """Empty or invalid PEM byte payloads must raise ValueError."""
        with self.assertRaises(ValueError):
            load_public_key(b"")
        with self.assertRaises(ValueError):
            load_public_key(b"not-a-valid-pem")
        with self.assertRaises(ValueError):
            load_private_key(b"")
        with self.assertRaises(ValueError):
            load_private_key(b"garbage-private-key-data")


if __name__ == "__main__":
    unittest.main()
