"""
Test Suite: Hybrid Encryption Module
Tests encryption behavior, random nonce/key generation, size limits, and plaintext leakage checks.
"""

import json
import unittest
from crypto_utils.key_manager import generate_rsa_key_pair
from crypto_utils.encryption import encrypt_file_hybrid
from crypto_utils.file_format import MAX_FILE_SIZE


class TestEncryption(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.priv_key, cls.pub_key = generate_rsa_key_pair(2048)

    def test_empty_file_rejected(self):
        """Test Case 5: Empty files are handled according to documented policy."""
        with self.assertRaises(ValueError) as ctx:
            encrypt_file_hybrid(b"", "empty.txt", self.pub_key)
        self.assertIn("Cannot encrypt an empty file", str(ctx.exception))

    def test_oversized_file_rejected(self):
        """Test Case 15: Oversized uploads (> 25 MiB) are rejected."""
        oversized_data = b"X" * (MAX_FILE_SIZE + 1)
        with self.assertRaises(ValueError) as ctx:
            encrypt_file_hybrid(oversized_data, "large.dat", self.pub_key)
        self.assertIn("exceeds maximum limit", str(ctx.exception))

    def test_package_does_not_contain_plaintext(self):
        """Test Case 16: The encrypted package does not contain the complete original plaintext."""
        secret_content = b"CRITICAL_COLLEGE_CNS_SECRET_PLAIN_TEXT_1234567890"
        pkg_bytes, stats = encrypt_file_hybrid(secret_content, "secret.txt", self.pub_key)
        
        # Verify the raw secret bytes do not appear anywhere in the serialized package
        self.assertNotIn(secret_content, pkg_bytes)
        
        # Verify even substrings of the plaintext do not appear
        self.assertNotIn(b"CRITICAL_COLLEGE", pkg_bytes)

    def test_two_encryptions_produce_different_ciphertext_packages(self):
        """Test Case 17: Encrypting the same file twice produces different packages (fresh AES key + nonce)."""
        data = b"Deterministic payload to be encrypted twice."
        pkg1_bytes, _ = encrypt_file_hybrid(data, "sample.txt", self.pub_key)
        pkg2_bytes, _ = encrypt_file_hybrid(data, "sample.txt", self.pub_key)

        self.assertNotEqual(pkg1_bytes, pkg2_bytes)

        # Parse packages to verify nonce and encrypted keys differ
        p1 = json.loads(pkg1_bytes.decode("utf-8"))
        p2 = json.loads(pkg2_bytes.decode("utf-8"))

        self.assertNotEqual(p1["nonce"], p2["nonce"])
        self.assertNotEqual(p1["encrypted_key"], p2["encrypted_key"])
        self.assertNotEqual(p1["ciphertext"], p2["ciphertext"])

    def test_encryption_statistics_and_metadata(self):
        """Verify returned metrics dict contains correct metadata."""
        data = b"Testing stats output."
        pkg_bytes, stats = encrypt_file_hybrid(data, "test.txt", self.pub_key)
        
        self.assertEqual(stats["original_filename"], "test.txt")
        self.assertEqual(stats["original_size_bytes"], len(data))
        self.assertEqual(stats["package_size_bytes"], len(pkg_bytes))
        self.assertGreater(stats["encryption_time_ms"], 0.0)
        self.assertEqual(stats["rsa_key_size_bits"], 2048)


if __name__ == "__main__":
    unittest.main()
