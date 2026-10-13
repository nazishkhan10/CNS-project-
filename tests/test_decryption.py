"""
Test Suite: Hybrid Decryption Module
Tests roundtrip decryption for text, PDF, and image payloads, wrong keys, and filename sanitization.
"""

import unittest
from crypto_utils.key_manager import generate_rsa_key_pair
from crypto_utils.encryption import encrypt_file_hybrid
from crypto_utils.decryption import decrypt_file_hybrid


class TestDecryption(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.priv_key, cls.pub_key = generate_rsa_key_pair(2048)
        cls.wrong_priv_key, _ = generate_rsa_key_pair(2048)

    def test_text_file_roundtrip(self):
        """Test Case 2 & 18: A text file can be encrypted and decrypted; returns exact original bytes."""
        original_text = b"Hello, CNS College Lab! This is an important assignment text.\nLine 2\nLine 3."
        pkg_bytes, _ = encrypt_file_hybrid(original_text, "notes.txt", self.pub_key)
        
        decrypted_bytes, filename, stats = decrypt_file_hybrid(pkg_bytes, self.priv_key)
        self.assertEqual(decrypted_bytes, original_text)
        self.assertEqual(filename, "notes.txt")
        self.assertEqual(stats["recovered_size_bytes"], len(original_text))

    def test_pdf_binary_roundtrip(self):
        """Test Case 3: A PDF-like binary payload can be encrypted and decrypted without corruption."""
        # Simulated PDF header + binary stream + trailer
        pdf_payload = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n%%EOF"
        pkg_bytes, _ = encrypt_file_hybrid(pdf_payload, "project_report.pdf", self.pub_key)
        
        decrypted_bytes, filename, _ = decrypt_file_hybrid(pkg_bytes, self.priv_key)
        self.assertEqual(decrypted_bytes, pdf_payload)
        self.assertEqual(filename, "project_report.pdf")

    def test_image_binary_roundtrip(self):
        """Test Case 4: An image-like binary payload can be encrypted and decrypted without corruption."""
        # Simulated PNG magic bytes + chunks + arbitrary high-entropy bytes
        png_magic = b"\x89PNG\r\n\x1a\n"
        arbitrary_image_data = png_magic + bytes(range(256)) * 10
        pkg_bytes, _ = encrypt_file_hybrid(arbitrary_image_data, "photo.png", self.pub_key)
        
        decrypted_bytes, filename, _ = decrypt_file_hybrid(pkg_bytes, self.priv_key)
        self.assertEqual(decrypted_bytes, arbitrary_image_data)
        self.assertEqual(filename, "photo.png")

    def test_incorrect_private_key_causes_decryption_failure(self):
        """Test Case 6: An incorrect private key causes decryption failure."""
        data = b"Confidential information protected by User A's public key."
        pkg_bytes, _ = encrypt_file_hybrid(data, "confidential.txt", self.pub_key)
        
        # Attempt decryption using wrong private key
        with self.assertRaises(ValueError) as ctx:
            decrypt_file_hybrid(pkg_bytes, self.wrong_priv_key)
        self.assertIn("RSA decryption failed", str(ctx.exception))

    def test_unsafe_filename_sanitized(self):
        """Test Case 14: Unsafe filenames with path traversal tokens are sanitized."""
        data = b"Testing filename sanitization."
        malicious_filename = "../../../etc/passwd"
        pkg_bytes, _ = encrypt_file_hybrid(data, malicious_filename, self.pub_key)
        
        decrypted_bytes, safe_filename, _ = decrypt_file_hybrid(pkg_bytes, self.priv_key)
        self.assertEqual(decrypted_bytes, data)
        self.assertNotIn("/", safe_filename)
        self.assertNotIn("\\", safe_filename)
        self.assertNotIn("..", safe_filename)
        self.assertEqual(safe_filename, "passwd")


if __name__ == "__main__":
    unittest.main()
