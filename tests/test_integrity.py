"""
Test Suite: Integrity Verification & Tamper Resistance
Tests AEAD authentication failure, corrupted packages, modified ciphertext,
tampered tags, missing fields, invalid Base64, and version mismatch.
"""

import base64
import json
import unittest
from crypto_utils.key_manager import generate_rsa_key_pair
from crypto_utils.encryption import encrypt_file_hybrid
from crypto_utils.decryption import decrypt_file_hybrid


class TestIntegrity(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.priv_key, cls.pub_key = generate_rsa_key_pair(2048)
        cls.test_data = b"Critical medical record: Blood group O+, Allergic to Penicillin."
        cls.pkg_bytes, _ = encrypt_file_hybrid(cls.test_data, "medical_report.txt", cls.pub_key)

    def _get_pkg_dict(self):
        return json.loads(self.pkg_bytes.decode("utf-8"))

    def test_modified_ciphertext_rejected(self):
        """Test Case 8: Modified ciphertext is rejected by AES-GCM."""
        pkg_dict = self._get_pkg_dict()
        ct_bytes = bytearray(base64.b64decode(pkg_dict["ciphertext"]))
        
        # Flip a bit in the ciphertext portion (before the 16-byte tag)
        ct_bytes[0] ^= 0x01
        pkg_dict["ciphertext"] = base64.b64encode(bytes(ct_bytes)).decode("ascii")
        tampered_pkg = json.dumps(pkg_dict).encode("utf-8")
        
        with self.assertRaises(ValueError) as ctx:
            decrypt_file_hybrid(tampered_pkg, self.priv_key)
        self.assertIn("Integrity check failed", str(ctx.exception))

    def test_modified_authentication_tag_rejected(self):
        """Test Case 9: A modified AES-GCM authentication tag is rejected."""
        pkg_dict = self._get_pkg_dict()
        ct_bytes = bytearray(base64.b64decode(pkg_dict["ciphertext"]))
        
        # In cryptography AESGCM, the last 16 bytes are the authentication tag
        ct_bytes[-1] ^= 0xFF
        pkg_dict["ciphertext"] = base64.b64encode(bytes(ct_bytes)).decode("ascii")
        tampered_pkg = json.dumps(pkg_dict).encode("utf-8")
        
        with self.assertRaises(ValueError) as ctx:
            decrypt_file_hybrid(tampered_pkg, self.priv_key)
        self.assertIn("Integrity check failed", str(ctx.exception))

    def test_corrupted_package_format_rejected(self):
        """Test Case 10: Corrupted encrypted package (non-JSON / truncated) is rejected."""
        corrupted_bytes = b"NOT_A_VALID_JSON_PACKAGE{random_bytes: 12345"
        with self.assertRaises(ValueError) as ctx:
            decrypt_file_hybrid(corrupted_bytes, self.priv_key)
        self.assertIn("Corrupted package structure", str(ctx.exception))

    def test_missing_package_fields_rejected(self):
        """Test Case 11: Missing package fields are rejected."""
        required_keys = ["format", "version", "cipher", "key_encapsulation", "metadata", "nonce", "encrypted_key", "ciphertext"]
        for key in required_keys:
            pkg_dict = self._get_pkg_dict()
            del pkg_dict[key]
            tampered_pkg = json.dumps(pkg_dict).encode("utf-8")
            with self.assertRaises(ValueError) as ctx:
                decrypt_file_hybrid(tampered_pkg, self.priv_key)
            self.assertIn("Missing required field", str(ctx.exception))

    def test_invalid_base64_data_rejected(self):
        """Test Case 12: Invalid Base64 data is rejected."""
        pkg_dict = self._get_pkg_dict()
        pkg_dict["nonce"] = "!!!INVALID_BASE64_CHARACTERS!!!"
        tampered_pkg = json.dumps(pkg_dict).encode("utf-8")
        with self.assertRaises(ValueError) as ctx:
            decrypt_file_hybrid(tampered_pkg, self.priv_key)
        self.assertIn("Invalid Base64 encoding", str(ctx.exception))

    def test_unsupported_package_version_rejected(self):
        """Test Case 13: Unsupported package versions are rejected."""
        pkg_dict = self._get_pkg_dict()
        pkg_dict["version"] = "99.0"
        tampered_pkg = json.dumps(pkg_dict).encode("utf-8")
        with self.assertRaises(ValueError) as ctx:
            decrypt_file_hybrid(tampered_pkg, self.priv_key)
        self.assertIn("Unsupported package version", str(ctx.exception))

    def test_metadata_tampering_rejected_by_aad(self):
        """Tampering with metadata (e.g. changing original filename or size) fails AAD verification."""
        pkg_dict = self._get_pkg_dict()
        pkg_dict["metadata"]["original_filename"] = "forged_malicious_name.exe"
        tampered_pkg = json.dumps(pkg_dict).encode("utf-8")
        with self.assertRaises(ValueError) as ctx:
            decrypt_file_hybrid(tampered_pkg, self.priv_key)
        self.assertIn("Integrity check failed", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
