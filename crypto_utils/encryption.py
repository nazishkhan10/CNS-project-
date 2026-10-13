"""
CipherVault Lite - Hybrid Encryption Module
Implements AES-256-GCM symmetric file encryption and RSA-OAEP asymmetric key protection.
"""

import os
import secrets
import time
from datetime import datetime, timezone
from typing import Tuple, Dict, Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

from .file_format import (
    MAX_FILE_SIZE,
    AES_KEY_LENGTH,
    NONCE_LENGTH,
    FORMAT_ID,
    FORMAT_VERSION,
    CIPHER_ID,
    KEY_ENC_ID,
    compute_associated_data,
    build_encrypted_package,
    sanitize_filename,
)


def encrypt_file_hybrid(
    file_bytes: bytes,
    original_filename: str,
    public_key: rsa.RSAPublicKey,
) -> Tuple[bytes, Dict[str, Any]]:
    """
    Perform authenticated hybrid encryption on file contents.
    
    1. Generates a fresh 32-byte cryptographically secure random AES key.
    2. Generates a fresh 12-byte random nonce for AES-GCM.
    3. Encrypts the file using AES-256-GCM with Additional Authenticated Data (AAD).
    4. Encrypts the 32-byte AES key using RSA-OAEP with SHA-256.
    5. Serializes the result into a .cvlt package.
    
    Args:
        file_bytes: Plaintext binary content of the file.
        original_filename: Name of the original file.
        public_key: Recipient's RSA public key (RSAPublicKey).
        
    Returns:
        Tuple of:
            - package_bytes: Raw bytes of the generated .cvlt file.
            - stats: Dictionary containing metadata, timing, and size metrics.
            
    Raises:
        ValueError: On empty file, file exceeding size limits, or invalid key.
        TypeError: If public_key is not an RSAPublicKey.
    """
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise TypeError("Public key must be an RSAPublicKey instance.")
        
    if not file_bytes:
        raise ValueError("Cannot encrypt an empty file. File payload is 0 bytes.")
        
    file_size = len(file_bytes)
    if file_size > MAX_FILE_SIZE:
        max_mb = MAX_FILE_SIZE // (1024 * 1024)
        raise ValueError(
            f"File size ({file_size / (1024*1024):.2f} MiB) exceeds maximum limit of {max_mb} MiB."
        )

    start_time = time.perf_counter()
    safe_filename = sanitize_filename(original_filename)
    timestamp = datetime.now(timezone.utc).isoformat()

    # Step 1: Generate a fresh 256-bit AES symmetric key
    aes_key = secrets.token_bytes(AES_KEY_LENGTH)

    # Step 2: Generate a fresh 96-bit nonce (never reused)
    nonce = os.urandom(NONCE_LENGTH)

    # Step 3: Compute Additional Authenticated Data (AAD) to protect metadata integrity
    aad = compute_associated_data(
        format_id=FORMAT_ID,
        version=FORMAT_VERSION,
        cipher_id=CIPHER_ID,
        key_enc_id=KEY_ENC_ID,
        filename=safe_filename,
        file_size=file_size,
    )

    # Step 4: Encrypt plaintext using AES-256-GCM (produces ciphertext + 16-byte auth tag)
    aesgcm = AESGCM(aes_key)
    ciphertext_with_tag = aesgcm.encrypt(nonce, file_bytes, associated_data=aad)

    # Step 5: Encrypt the 32-byte AES key using RSA-OAEP with SHA-256
    # RSA encrypts ONLY the symmetric key, keeping asymmetric operations fast & secure
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Zeroize / release the temporary symmetric key reference
    del aes_key

    # Step 6: Assemble into .cvlt package
    package_bytes = build_encrypted_package(
        nonce=nonce,
        encrypted_aes_key=encrypted_aes_key,
        ciphertext_with_tag=ciphertext_with_tag,
        original_filename=safe_filename,
        original_size=file_size,
        timestamp=timestamp,
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    stats = {
        "original_filename": safe_filename,
        "original_size_bytes": file_size,
        "package_size_bytes": len(package_bytes),
        "encryption_time_ms": round(elapsed_ms, 2),
        "cipher": CIPHER_ID,
        "key_encapsulation": KEY_ENC_ID,
        "rsa_key_size_bits": public_key.key_size,
        "timestamp": timestamp,
    }

    return package_bytes, stats
