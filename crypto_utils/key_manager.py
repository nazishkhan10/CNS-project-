"""
CipherVault Lite - Key Manager Module
Handles RSA key-pair generation, PEM serialization, and secure key loading.
Uses cryptography.hazmat.primitives.asymmetric.rsa and serialization APIs.
"""

from typing import Optional, Tuple
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_rsa_key_pair(key_size: int = 2048) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    """
    Generate an RSA private and public key pair.
    
    Args:
        key_size: RSA key size in bits (minimum 2048, e.g. 2048, 3072, 4096).
        
    Returns:
        Tuple of (RSAPrivateKey, RSAPublicKey).
        
    Raises:
        ValueError: If key_size is less than 2048.
    """
    if key_size < 2048:
        raise ValueError("Insecure key size: RSA key size must be at least 2048 bits.")
        
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_public_key(public_key: rsa.RSAPublicKey) -> bytes:
    """
    Serialize an RSA public key to PEM format using SubjectPublicKeyInfo (X.509 standard).
    
    Args:
        public_key: RSAPublicKey instance.
        
    Returns:
        PEM-encoded bytes.
    """
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise TypeError("Expected an RSAPublicKey instance.")
        
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def serialize_private_key(
    private_key: rsa.RSAPrivateKey,
    password: Optional[str] = None
) -> bytes:
    """
    Serialize an RSA private key to PEM format using PKCS#8.
    If a password is provided, encrypts the private key using BestAvailableEncryption.
    
    Args:
        private_key: RSAPrivateKey instance.
        password: Optional passphrase string to encrypt the private key.
        
    Returns:
        PEM-encoded bytes.
    """
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise TypeError("Expected an RSAPrivateKey instance.")
        
    if password:
        encryption_algorithm = serialization.BestAvailableEncryption(password.encode("utf-8"))
    else:
        encryption_algorithm = serialization.NoEncryption()
        
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm,
    )


def load_public_key(pem_data: bytes) -> rsa.RSAPublicKey:
    """
    Safely load and validate an RSA public key from PEM-encoded bytes.
    
    Args:
        pem_data: PEM-encoded public key bytes.
        
    Returns:
        Validated RSAPublicKey.
        
    Raises:
        ValueError: If key data is invalid or key size is less than 2048 bits.
        TypeError: If key is not an RSA public key.
    """
    if not pem_data or not pem_data.strip():
        raise ValueError("Public key data cannot be empty.")
        
    try:
        key = serialization.load_pem_public_key(pem_data)
    except Exception as e:
        raise ValueError(f"Failed to load public key: Malformed PEM data or unsupported format.") from e

    if not isinstance(key, rsa.RSAPublicKey):
        raise TypeError("Loaded key is not an RSA public key.")
        
    if key.key_size < 2048:
        raise ValueError(
            f"Insecure RSA key size: Found {key.key_size} bits. Minimum required is 2048 bits."
        )
        
    return key


def is_private_key_encrypted(pem_data: bytes) -> bool:
    """
    Check if a PEM private key is password-protected without exposing secrets.
    """
    if not pem_data:
        return False
    # PKCS#8 encrypted keys begin with '-----BEGIN ENCRYPTED PRIVATE KEY-----'
    # Traditional SSLeay/OpenSSL encrypted keys contain 'Proc-Type: 4,ENCRYPTED'
    content = pem_data.decode("utf-8", errors="ignore")
    return "-----BEGIN ENCRYPTED PRIVATE KEY-----" in content or "Proc-Type: 4,ENCRYPTED" in content


def load_private_key(
    pem_data: bytes,
    password: Optional[str] = None
) -> rsa.RSAPrivateKey:
    """
    Safely load and validate an RSA private key from PEM-encoded bytes.
    
    Args:
        pem_data: PEM-encoded private key bytes.
        password: Optional passphrase string.
        
    Returns:
        Validated RSAPrivateKey.
        
    Raises:
        ValueError: If key data is invalid, password is incorrect, or key size < 2048 bits.
        TypeError: If key is not an RSA private key.
    """
    if not pem_data or not pem_data.strip():
        raise ValueError("Private key data cannot be empty.")
        
    pw_bytes = password.encode("utf-8") if password else None
    
    try:
        key = serialization.load_pem_private_key(pem_data, password=pw_bytes)
    except TypeError as e:
        # Occurs when the key is encrypted but password=None
        raise ValueError("Private key is password-protected. Please enter the correct passphrase.") from e
    except ValueError as e:
        # Occurs on incorrect password or malformed PEM
        if is_private_key_encrypted(pem_data):
            raise ValueError("Incorrect private key password, or corrupted key file.") from e
        raise ValueError("Failed to load private key: Malformed PEM data.") from e
    except Exception as e:
        raise ValueError("Failed to load private key: Invalid key structure.") from e

    if not isinstance(key, rsa.RSAPrivateKey):
        raise TypeError("Loaded key is not an RSA private key.")
        
    if key.key_size < 2048:
        raise ValueError(
            f"Insecure RSA key size: Found {key.key_size} bits. Minimum required is 2048 bits."
        )
        
    return key
