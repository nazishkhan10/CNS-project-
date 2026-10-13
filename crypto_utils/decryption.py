"""
CipherVault Lite - Hybrid Decryption Module
Recovers symmetric AES key using RSA-OAEP and decrypts payload using authenticated AES-256-GCM.
"""

import time
from typing import Tuple, Dict, Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag

from .file_format import (
    AES_KEY_LENGTH,
    parse_and_validate_package,
)


def decrypt_file_hybrid(
    package_bytes: bytes,
    private_key: rsa.RSAPrivateKey,
) -> Tuple[bytes, str, Dict[str, Any]]:
    """
    Perform authenticated hybrid decryption on a .cvlt package.
    
    1. Strictly validates the package envelope, schema, Base64 encodings, and lengths.
    2. Decrypts the encapsulated 32-byte AES key using RSA-OAEP with SHA-256.
    3. Verifies that the recovered AES key is exactly 32 bytes (256 bits).
    4. Decrypts the ciphertext using AES-256-GCM with Additional Authenticated Data (AAD).
    5. Rejects modified ciphertext, corrupted tags, or altered metadata.
    
    Args:
        package_bytes: Raw bytes of the uploaded .cvlt file.
        private_key: Recipient's RSA private key (RSAPrivateKey).
        
    Returns:
        Tuple of:
            - decrypted_bytes: Original binary content of the file.
            - safe_filename: Sanitized original filename.
            - stats: Dictionary containing decryption metrics and metadata.
            
    Raises:
        ValueError: On corrupted package, invalid key, wrong key, or authentication tag failure.
        TypeError: If private_key is not an RSAPrivateKey instance.
    """
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise TypeError("Private key must be an RSAPrivateKey instance.")
        
    start_time = time.perf_counter()

    # Step 1: Parse and validate the envelope
    parsed = parse_and_validate_package(package_bytes)
    
    nonce_bytes = parsed["nonce_bytes"]
    encrypted_key_bytes = parsed["encrypted_key_bytes"]
    ciphertext_bytes = parsed["ciphertext_bytes"]
    metadata = parsed["metadata"]
    aad = parsed["associated_data"]
    safe_filename = parsed["original_filename"]

    # Step 2: Decrypt the AES symmetric key using RSA-OAEP
    try:
        aes_key = private_key.decrypt(
            encrypted_key_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except Exception as e:
        raise ValueError(
            "RSA decryption failed: Incorrect private key or corrupted key envelope."
        ) from e

    # Step 3: Validate the recovered AES key length (must be 32 bytes for AES-256)
    if len(aes_key) != AES_KEY_LENGTH:
        raise ValueError(
            f"Invalid recovered AES key size ({len(aes_key)} bytes). Expected {AES_KEY_LENGTH} bytes."
        )

    # Step 4: Authenticated AES-GCM decryption
    try:
        aesgcm = AESGCM(aes_key)
        decrypted_bytes = aesgcm.decrypt(
            nonce_bytes,
            ciphertext_bytes,
            associated_data=aad,
        )
    except InvalidTag as e:
        # AEAD integrity check failed: either ciphertext, nonce, or metadata was modified
        raise ValueError(
            "Integrity check failed: Authentication tag mismatch. "
            "The file content or its metadata has been modified or corrupted."
        ) from e
    except Exception as e:
        raise ValueError("Decryption failed: Unable to verify payload authenticity.") from e
    finally:
        # Step 5: Clean up symmetric key reference in memory
        del aes_key

    # Step 6: Verify recovered plaintext size matches package metadata
    if len(decrypted_bytes) != metadata["original_size"]:
        raise ValueError(
            f"Integrity check failed: Recovered file size ({len(decrypted_bytes)} bytes) "
            f"does not match expected size ({metadata['original_size']} bytes)."
        )

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    stats = {
        "original_filename": safe_filename,
        "recovered_size_bytes": len(decrypted_bytes),
        "decryption_time_ms": round(elapsed_ms, 2),
        "rsa_key_size_bits": private_key.key_size,
    }

    return decrypted_bytes, safe_filename, stats
