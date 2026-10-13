"""
CipherVault Lite - File Format & Envelope Specification
Defines the .cvlt package structure, canonical serialization, Base64 encoding,
strict schema validation, and safe filename sanitization.
"""

import base64
import json
import os
import re
from typing import Dict, Any, Tuple

FORMAT_ID = "CIPHERVAULT_LITE"
FORMAT_VERSION = "1.0"
CIPHER_ID = "AES-256-GCM"
KEY_ENC_ID = "RSA-OAEP-SHA256"

# 25 MiB upload limit as required by project specifications
MAX_FILE_SIZE = 25 * 1024 * 1024  # 26,214,400 bytes
# Allow headroom for Base64 encoding (33% expansion) + envelope metadata
MAX_PACKAGE_SIZE = 36 * 1024 * 1024  # 37,748,736 bytes

NONCE_LENGTH = 12       # 96 bits standard for AES-GCM
AES_KEY_LENGTH = 32     # 256 bits for AES-256
TAG_LENGTH = 16         # 128 bits authentication tag

# Reserved Windows device names
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize an uploaded or recovered filename to prevent path traversal
    and OS injection attacks.
    
    Args:
        filename: Original user-provided filename.
        
    Returns:
        Safe base filename string.
    """
    if not filename or not isinstance(filename, str):
        return "decrypted_file.bin"
        
    # Extract only basename (strips any path prefixes like ../ or C:\)
    clean_name = os.path.basename(filename.strip())
    
    # Replace dangerous characters: slashes, backslashes, colons, null bytes, wildcards
    clean_name = re.sub(r'[\x00-\x1f\x7f/\\:*\?"<>|]', '_', clean_name)
    
    # Strip leading/trailing dots and spaces
    clean_name = clean_name.strip(". ")
    
    # Check for reserved Windows device names (e.g. CON.txt or NUL)
    name_root = clean_name.split('.')[0].upper()
    if name_root in WINDOWS_RESERVED_NAMES or not clean_name:
        clean_name = f"safe_{clean_name}" if clean_name else "decrypted_file.bin"
        
    return clean_name[:128]  # Limit length to 128 characters


def compute_associated_data(format_id: str, version: str, cipher_id: str, key_enc_id: str, filename: str, file_size: int) -> bytes:
    """
    Construct canonical Additional Authenticated Data (AAD) for AES-256-GCM.
    Binding this metadata into the cipher's authentication tag guarantees that
    any tampering with package metadata will cause decryption authentication to fail.
    """
    canonical_aad = f"{format_id}|{version}|{cipher_id}|{key_enc_id}|{filename}|{file_size}"
    return canonical_aad.encode("utf-8")


def build_encrypted_package(
    nonce: bytes,
    encrypted_aes_key: bytes,
    ciphertext_with_tag: bytes,
    original_filename: str,
    original_size: int,
    timestamp: str,
) -> bytes:
    """
    Assemble the complete .cvlt encrypted package JSON structure and return UTF-8 bytes.
    
    Args:
        nonce: 12-byte AES-GCM nonce.
        encrypted_aes_key: RSA-OAEP encrypted AES-256 key.
        ciphertext_with_tag: AES-GCM ciphertext with appended authentication tag.
        original_filename: Name of the original file.
        original_size: Size in bytes of original plaintext.
        timestamp: ISO format timestamp string.
        
    Returns:
        UTF-8 encoded JSON bytes of the .cvlt package.
    """
    safe_name = sanitize_filename(original_filename)
    package = {
        "format": FORMAT_ID,
        "version": FORMAT_VERSION,
        "cipher": CIPHER_ID,
        "key_encapsulation": KEY_ENC_ID,
        "metadata": {
            "original_filename": safe_name,
            "original_size": int(original_size),
            "timestamp": timestamp,
        },
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "encrypted_key": base64.b64encode(encrypted_aes_key).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext_with_tag).decode("ascii"),
    }
    
    json_str = json.dumps(package, indent=2)
    return json_str.encode("utf-8")


def parse_and_validate_package(package_bytes: bytes) -> Dict[str, Any]:
    """
    Strictly parse and validate an uploaded .cvlt package.
    
    Args:
        package_bytes: Raw bytes of the uploaded .cvlt file.
        
    Returns:
        Dict containing decoded binary components:
            - nonce_bytes: bytes (12 bytes)
            - encrypted_key_bytes: bytes (RSA block)
            - ciphertext_bytes: bytes (ciphertext + tag)
            - metadata: dict
            - associated_data: bytes (canonical AAD)
            - original_filename: safe string
            
    Raises:
        ValueError: On schema violation, corrupted payload, unsupported version,
                    missing fields, or invalid Base64.
    """
    if not package_bytes or not package_bytes.strip():
        raise ValueError("Encrypted package is empty.")
        
    if len(package_bytes) > MAX_PACKAGE_SIZE:
        raise ValueError(
            f"Package exceeds maximum size limit ({MAX_PACKAGE_SIZE // (1024*1024)} MiB)."
        )

    # 1. JSON decoding
    try:
        package_dict = json.loads(package_bytes.decode("utf-8"))
    except UnicodeDecodeError as e:
        raise ValueError("Malformed package: File is not valid UTF-8 text.") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Corrupted package structure: Invalid JSON format ({e.msg}).") from e

    if not isinstance(package_dict, dict):
        raise ValueError("Corrupted package structure: Root JSON element must be an object.")

    # 2. Check required top-level fields
    required_keys = {"format", "version", "cipher", "key_encapsulation", "metadata", "nonce", "encrypted_key", "ciphertext"}
    missing = required_keys - set(package_dict.keys())
    if missing:
        raise ValueError(f"Invalid package: Missing required field(s): {', '.join(sorted(missing))}.")

    # 3. Validate header identifiers
    if package_dict["format"] != FORMAT_ID:
        raise ValueError(f"Unsupported format identifier: '{package_dict['format']}'. Expected '{FORMAT_ID}'.")
        
    if package_dict["version"] != FORMAT_VERSION:
        raise ValueError(f"Unsupported package version: '{package_dict['version']}'. Only version '{FORMAT_VERSION}' is supported.")

    if package_dict["cipher"] != CIPHER_ID:
        raise ValueError(f"Unsupported cipher: '{package_dict['cipher']}'. Expected '{CIPHER_ID}'.")

    if package_dict["key_encapsulation"] != KEY_ENC_ID:
        raise ValueError(f"Unsupported key encapsulation: '{package_dict['key_encapsulation']}'. Expected '{KEY_ENC_ID}'.")

    # 4. Validate metadata
    metadata = package_dict["metadata"]
    if not isinstance(metadata, dict):
        raise ValueError("Package metadata must be a dictionary.")
        
    if "original_filename" not in metadata or "original_size" not in metadata:
        raise ValueError("Metadata is missing 'original_filename' or 'original_size'.")
        
    if not isinstance(metadata["original_size"], int) or metadata["original_size"] < 0:
        raise ValueError("Metadata 'original_size' must be a non-negative integer.")

    safe_filename = sanitize_filename(str(metadata["original_filename"]))

    # 5. Base64 decoding with strict validation
    def decode_b64(field_name: str) -> bytes:
        val = package_dict[field_name]
        if not isinstance(val, str):
            raise ValueError(f"Field '{field_name}' must be a Base64-encoded string.")
        try:
            return base64.b64decode(val.encode("ascii"), validate=True)
        except Exception as e:
            raise ValueError(f"Corrupted data in field '{field_name}': Invalid Base64 encoding.") from e

    nonce_bytes = decode_b64("nonce")
    encrypted_key_bytes = decode_b64("encrypted_key")
    ciphertext_bytes = decode_b64("ciphertext")

    # 6. Validate binary field lengths
    if len(nonce_bytes) != NONCE_LENGTH:
        raise ValueError(f"Invalid nonce length: Got {len(nonce_bytes)} bytes, expected {NONCE_LENGTH} bytes.")

    # Valid RSA encrypted block sizes for 2048, 3072, 4096 bits (256, 384, 512 bytes)
    if len(encrypted_key_bytes) not in (256, 384, 512):
        raise ValueError(
            f"Invalid encrypted key block length: {len(encrypted_key_bytes)} bytes. "
            "Expected 256, 384, or 512 bytes (RSA 2048/3072/4096-bit)."
        )

    # Must contain at least the 16-byte authentication tag
    if len(ciphertext_bytes) < TAG_LENGTH:
        raise ValueError(
            f"Ciphertext is too short: {len(ciphertext_bytes)} bytes. "
            f"Minimum size is {TAG_LENGTH} bytes for authentication tag."
        )

    # Construct Associated Data
    aad = compute_associated_data(
        format_id=package_dict["format"],
        version=package_dict["version"],
        cipher_id=package_dict["cipher"],
        key_enc_id=package_dict["key_encapsulation"],
        filename=safe_filename,
        file_size=metadata["original_size"],
    )

    return {
        "nonce_bytes": nonce_bytes,
        "encrypted_key_bytes": encrypted_key_bytes,
        "ciphertext_bytes": ciphertext_bytes,
        "metadata": metadata,
        "associated_data": aad,
        "original_filename": safe_filename,
    }
