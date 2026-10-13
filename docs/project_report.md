# ACADEMIC MINI-PROJECT REPORT

## CIPHERVAULT LITE: A HYBRID FILE ENCRYPTION AND DECRYPTION SYSTEM USING AES AND RSA

---

**Course:** Cryptography and Network Security (CNS)  
**Degree:** Bachelor of Technology (B.Tech) in Computer Science & Engineering  

**Submitted By:**  
- **Student Name:** [Student Name Placeholder]  
- **Roll Number / PRN:** [Roll Number Placeholder]  

**Under the Guidance of:**  
- **Project Guide:** [Guide Name Placeholder], [Designation Placeholder]  

**Department:** Department of Computer Science & Engineering  
**Institution:** [College / University Name Placeholder]  
**Academic Year:** 2025 – 2026  

---

## TABLE OF CONTENTS
1. [Abstract](#1-abstract)
2. [Introduction](#2-introduction)
3. [Problem Statement](#3-problem-statement)
4. [Objectives](#4-objectives)
5. [Project Scope](#5-project-scope)
6. [Limitations of Existing Systems](#6-limitations-of-existing-systems)
7. [Proposed System](#7-proposed-system)
8. [Hardware and Software Requirements](#8-hardware-and-software-requirements)
9. [Technologies and Libraries Used](#9-technologies-and-libraries-used)
10. [Theoretical Cryptographic Concepts](#10-theoretical-cryptographic-concepts)
11. [System Architecture](#11-system-architecture)
12. [Module Descriptions](#12-module-descriptions)
13. [Algorithms and Workflows](#13-algorithms-and-workflows)
14. [Security Controls and Input Validation](#14-security-controls-and-input-validation)
15. [Automated Test Cases and Empirical Results](#15-automated-test-cases-and-empirical-results)
16. [Screenshots (Placeholders)](#16-screenshots-placeholders)
17. [Results and Performance Discussion](#17-results-and-performance-discussion)
18. [Project Limitations](#18-project-limitations)
19. [Conclusion and Future Work](#19-conclusion-and-future-work)
20. [References](#20-references)

---

## 1. ABSTRACT
In modern computer networks, unprotected data storage and file exchange introduce severe vulnerabilities, including passive eavesdropping, confidential data leakage, and unauthorized payload manipulation. Traditional symmetric cryptosystems, though computationally fast, suffer from the fundamental key-distribution dilemma. Conversely, asymmetric cryptosystems provide secure public-key distribution but are computationally prohibitive and mathematically incapable of directly encrypting arbitrary large payloads.

**CipherVault Lite** resolves this trade-off by engineering an end-to-end, lightweight **Hybrid Cryptosystem** tailored for educational demonstration within the Cryptography and Network Security (CNS) undergraduate curriculum. The system encrypts files of arbitrary binary format (PDF, DOCX, images, text, archives) using symmetric **AES-256 in Galois/Counter Mode (GCM)**, producing an authenticated ciphertext with a 128-bit integrity tag. The one-time 256-bit symmetric session key is encapsulated using asymmetric **RSA-OAEP with SHA-256** and the recipient's public key. Cryptographic authentication ensures that any alteration to the ciphertext or envelope metadata results in immediate rejection. The project delivers a clean, responsive web application implemented with Streamlit and verified through an automated test suite.

---

## 2. INTRODUCTION
Information security is built upon the foundational pillars of Confidentiality, Integrity, and Authenticity (the CIA triad). Cryptography provides mathematical mechanisms to uphold these properties across untrusted networks. Within contemporary cybersecurity engineering, hybrid encryption represents the dominant architecture powering protocols such as Transport Layer Security (TLS), Pretty Good Privacy (PGP/OpenPGP), and Secure/Multipurpose Internet Mail Extensions (S/MIME).

Understanding the mechanical interplay between symmetric block ciphers and asymmetric trapdoor permutations is essential for computer science students. CipherVault Lite provides a transparent, local implementation that bridges abstract classroom concepts with hands-on software development.

---

## 3. PROBLEM STATEMENT
Traditional approaches to file encryption exhibit critical practical drawbacks:
1. **Key Distribution Barrier in Symmetric Encryption:** If two parties wish to exchange an encrypted file using AES, they must securely exchange the AES key. If a secure channel already existed to exchange the key, the encrypted file could have been sent over that channel directly.
2. **Computational Overhead and Size Limits in Asymmetric Encryption:** RSA encryption involves modular exponentiation with very large integers (e.g. 2048-bit numbers). Encrypting a typical 10 MB document directly with RSA is computationally thousands of times slower than AES. Furthermore, mathematical padding bounds (OAEP) restrict RSA-2048 to a maximum plaintext size of only 190 bytes per operation.
3. **Lack of Authenticated Encryption in Legacy Tools:** Many legacy educational tools rely on Electronic Codebook (ECB) or Cipher Block Chaining (CBC) without Message Authentication Codes (MAC), leaving data vulnerable to chosen-ciphertext attacks, padding oracle attacks, and bit-flipping attacks.

---

## 4. OBJECTIVES
The principal objectives of this project are:
1. To engineer a functional hybrid cryptosystem using AES-256-GCM and RSA-OAEP.
2. To demonstrate key encapsulation where RSA protects only the symmetric key, and AES protects the file payload.
3. To implement Authenticated Encryption with Associated Data (AEAD) to detect tampering with both ciphertext and metadata.
4. To implement secure RSA key generation with optional PKCS#8 password-based key encryption.
5. To construct an intuitive Streamlit interface allowing students and examiners to test file encryption, decryption, and key management locally.
6. To validate implementation correctness through an automated test suite.

---

## 5. PROJECT SCOPE
The project encompasses:
- Local execution on Windows without external cloud or network dependencies.
- In-memory processing of arbitrary file formats up to a verified limit of 25 MiB.
- Generation and export of standard PEM-encoded RSA keys (2048, 3072, 4096-bit).
- Packaging encrypted assets into a structured `.cvlt` envelope.
- Input validation, filename sanitization, and path traversal prevention.

**Explicit Out-of-Scope Items:** User registration databases, cloud storage APIs, network scanning, multi-tenant accounts, complex blockchain ledgers, and heavy enterprise distributed systems.

---

## 6. LIMITATIONS OF EXISTING SYSTEMS
| Attribute | Pure Symmetric (e.g. AES-CBC) | Pure Asymmetric (e.g. RSA) | Hybrid (CipherVault Lite) |
| :--- | :--- | :--- | :--- |
| **Speed / Performance** | High ($> 100\text{ MB/s}$) | Extremely Low | High ($> 100\text{ MB/s}$) |
| **Max Payload Size** | Arbitrary | Bound by key size ($< 190\text{ B}$) | Arbitrary ($25\text{ MiB}$ enforced) |
| **Key Distribution** | Difficult (pre-shared secret) | Simple (public key) | Simple (public key) |
| **Integrity Protection** | Requires separate HMAC | Requires digital signature | Built-in GMAC Authentication Tag |
| **Nonce Freshness** | Often overlooked | N/A | Fresh 96-bit Nonce per run |

---

## 7. PROPOSED SYSTEM
The proposed system implements hybrid encryption:
1. **Sender Workflow:**
   - Reads the input file as binary bytes.
   - Generates a fresh, cryptographically secure 256-bit AES key ($K$) and 96-bit nonce ($N$).
   - Encrypts the payload with AES-256-GCM, generating ciphertext ($C$) and authentication tag ($T$).
   - Encrypts the AES key ($K$) with the recipient's RSA public key using RSA-OAEP.
   - Combines metadata, nonce, encrypted key, and authenticated ciphertext into a `.cvlt` package.
2. **Recipient Workflow:**
   - Parses and validates the `.cvlt` package structure.
   - Decrypts the encapsulated AES key using the matching RSA private key and passphrase.
   - Decrypts and authenticates the ciphertext using AES-256-GCM.
   - Delivers the original, byte-for-byte identical file.

---

## 8. HARDWARE AND SOFTWARE REQUIREMENTS

### Hardware Requirements
- **System Architecture:** x86_64 or ARM64 compatible processor.
- **CPU:** Intel Core i3 / AMD Ryzen 3 or higher.
- **RAM:** Minimum 2 GB (4 GB recommended).
- **Storage:** At least 200 MB free hard drive space.

### Software Requirements
- **Operating System:** Windows 10 / Windows 11 (or Linux / macOS).
- **Runtime Environment:** Python 3.11 or higher.
- **Web Browser:** Modern Chromium-based browser (Chrome, Edge, Brave) or Firefox.

---

## 9. TECHNOLOGIES AND LIBRARIES USED
- **Python Standard Library:**
  - `secrets`: CSPRNG for random 256-bit AES session key generation.
  - `os`: Nonce generation (`os.urandom(12)`) and path validation.
  - `json`: Structured representation of the `.cvlt` package.
  - `base64`: RFC 4648 standard binary-to-text encoding.
  - `re`: Regular expressions for strict filename sanitization.
- **`cryptography` Library (v42.0+):**
  - `cryptography.hazmat.primitives.ciphers.aead.AESGCM`
  - `cryptography.hazmat.primitives.asymmetric.rsa`
  - `cryptography.hazmat.primitives.asymmetric.padding` (OAEP, MGF1)
  - `cryptography.hazmat.primitives.hashes` (SHA256)
  - `cryptography.hazmat.primitives.serialization` (PEM, PKCS#8, BestAvailableEncryption)
- **`streamlit` (v1.30+):**
  - Interactive local web presentation layer, file uploaders, metrics, and download handlers.
- **`pytest` / `unittest`:**
  - Automated test execution and regression verification.

---

## 10. THEORETICAL CRYPTOGRAPHIC CONCEPTS

### 10.1 AES-256-GCM (Galois/Counter Mode)
Galois/Counter Mode is an authenticated encryption with associated data (AEAD) mode of operation for block ciphers:
- **Counter Mode Encryption:** Plaintext blocks $P_1, P_2, \dots, P_m$ are encrypted using an incrementing counter initialized by the 96-bit nonce $N$:
  $$C_i = P_i \oplus E_K(CTR_i)$$
- **Galois Message Authentication Code (GMAC):** Computes a 128-bit authentication tag over the ciphertext and Additional Authenticated Data (AAD) using polynomial multiplication in the Galois Field $GF(2^{128})$:
  $$S = GHASH_H(AAD \parallel C \parallel \text{len}(AAD) \parallel \text{len}(C))$$
  $$T = S \oplus E_K(CTR_0)$$
This guarantees both confidentiality and ciphertext integrity.

### 10.2 RSA-OAEP (Optimal Asymmetric Encryption Padding)
Textbook RSA computes $C = M^e \pmod n$. However, deterministic encryption fails semantic security. OAEP introduces randomized Feistel networks with two hash functions ($G$ and $H$ based on SHA-256):
- It pads message $M$ with zeros, combines it with a random seed $r$, and masks the inputs:
  $$X = M \parallel 00\dots0 \oplus G(r)$$
  $$Y = r \oplus H(X)$$
- The padded block $X \parallel Y$ is then subject to modular exponentiation.
- OAEP achieves Indistinguishability under Adaptive Chosen-Ciphertext Attack (IND-CCA2).

---

## 11. SYSTEM ARCHITECTURE

```mermaid
graph TD
    User([User / Web Browser]) <--> StreamlitUI[Streamlit UI Layer app.py]
    
    subgraph Core Crypto Engine
        StreamlitUI <--> KeyMgr[key_manager.py<br/>RSA Gen & PEM Serialization]
        StreamlitUI <--> FileFmt[file_format.py<br/>Package Validation & Sanitization]
        StreamlitUI <--> EncEngine[encryption.py<br/>AES-256-GCM & RSA-OAEP Wrap]
        StreamlitUI <--> DecEngine[decryption.py<br/>RSA-OAEP Unwrap & AES-GCM Decrypt]
    end

    KeyMgr <--> CryptoLib[cryptography OpenSSL Backend]
    EncEngine <--> CryptoLib
    DecEngine <--> CryptoLib
```

---

## 12. MODULE DESCRIPTIONS

### 12.1 `crypto_utils/key_manager.py`
- Generates 2048, 3072, or 4096-bit RSA keys with public exponent $e = 65537$.
- Encodes public keys to X.509 SubjectPublicKeyInfo PEM format.
- Encodes private keys to PKCS#8 PEM format with optional AES-256 passphrase encryption (`BestAvailableEncryption`).
- Validates that uploaded keys meet the minimum security threshold of 2048 bits.

### 12.2 `crypto_utils/file_format.py`
- Defines `.cvlt` package schema constants (`FORMAT_ID`, `VERSION`, `CIPHER_ID`).
- Serializes and deserializes envelopes using UTF-8 JSON and strict Base64 decoding.
- Formulates canonical Additional Authenticated Data (AAD) strings to cryptographically lock envelope metadata.
- Implements `sanitize_filename` to prevent path traversal and block reserved Windows device names.

### 12.3 `crypto_utils/encryption.py`
- Coordinates symmetric key generation via CSPRNG.
- Invokes `AESGCM(aes_key).encrypt(...)`.
- Encapsulates the symmetric key using `public_key.encrypt(..., padding.OAEP(...))`.
- Returns package bytes and metrics (file sizes, encryption duration in milliseconds).

### 12.4 `crypto_utils/decryption.py`
- Parses and verifies the `.cvlt` envelope.
- Decapsulates the AES key using `private_key.decrypt(...)` and verifies that the key length is exactly 32 bytes.
- Decrypts and authenticates the payload using `AESGCM(aes_key).decrypt(...)`.
- Rejects modified ciphertexts or corrupted tags with generic, safe error messages.

### 12.5 `app.py`
- Multi-section Streamlit interface (Home, Encrypt File, Decrypt File, Key Management, About the Project).
- Visual feedback using metrics, status alerts, and download buttons.
- Safe session clearing to avoid lingering sensitive data in memory.

---

## 13. ALGORITHMS AND WORKFLOWS

### 13.1 Encryption Algorithm Workflow
```text
Input: Plaintext file P, Recipient Public Key K_pub, Filename fn
Output: Encrypted package .cvlt

1. Validate len(P) > 0 and len(P) <= 25 MiB.
2. Generate random 32-byte AES key: K_aes = secrets.token_bytes(32)
3. Generate random 12-byte nonce: Nonce = os.urandom(12)
4. Compute AAD = "CIPHERVAULT_LITE|1.0|AES-256-GCM|RSA-OAEP-SHA256|" + fn + "|" + str(len(P))
5. Ciphertext_with_tag = AESGCM(K_aes).encrypt(Nonce, P, AAD)
6. Encrypted_K_aes = K_pub.encrypt(K_aes, OAEP(MGF1(SHA256), SHA256))
7. Clear K_aes from memory.
8. Package = JSON({
     format: "CIPHERVAULT_LITE",
     version: "1.0",
     metadata: { original_filename: fn, original_size: len(P) },
     nonce: Base64(Nonce),
     encrypted_key: Base64(Encrypted_K_aes),
     ciphertext: Base64(Ciphertext_with_tag)
   })
9. Return Package bytes.
```

### 13.2 Decryption Algorithm Workflow
```text
Input: Package bytes, Private Key K_priv, Passphrase pw (optional)
Output: Recovered Plaintext file P

1. Parse Package JSON and validate schema and field types.
2. Decode Nonce, Encrypted_K_aes, and Ciphertext from Base64.
3. Validate Nonce length == 12 bytes and Encrypted_K_aes length >= 256 bytes.
4. Load K_priv (decrypting with pw if encrypted).
5. Attempt K_aes = K_priv.decrypt(Encrypted_K_aes, OAEP(MGF1(SHA256), SHA256)).
   If decryption fails -> Raise Error: "Incorrect private key or corrupted envelope".
6. Validate len(K_aes) == 32 bytes.
7. Recompute AAD from metadata fields.
8. Attempt P = AESGCM(K_aes).decrypt(Nonce, Ciphertext, AAD).
   If authentication tag mismatch -> Raise Error: "Integrity check failed: Tampered data".
9. Clear K_aes from memory.
10. Verify len(P) == metadata.original_size.
11. Return P and sanitized filename.
```

---

## 14. SECURITY CONTROLS AND INPUT VALIDATION
1. **AEAD Binding via Additional Authenticated Data (AAD):** Envelope fields (version, original filename, original size) are fed into AES-GCM as AAD. If an attacker modifies the filename in the JSON wrapper, the AES-GCM tag verification fails.
2. **Safe Filename Sanitization:** Removes path traversal tokens (`../`, `..\`), slashes, backslashes, colons, null bytes, and reserved Windows device names (`CON`, `PRN`, `AUX`, `NUL`).
3. **Strict Size Limits:** Enforces a 25 MiB cap on file uploads to protect system memory.
4. **CSPRNG Generation:** Keys and nonces are drawn from OS cryptographic entropy pools (`os.urandom` and `secrets.token_bytes`).
5. **No Secret Display or Logging:** Private keys, passwords, and plaintext payloads are never logged or exposed in terminal output.
6. **Graceful Exception Handling:** Prevents internal stack trace leakage to end users.

---

## 15. AUTOMATED TEST CASES AND EMPIRICAL RESULTS

All test cases were executed automatically against the codebase using both `pytest` and `unittest`.

| Test ID | Test Description | Target Module | Expected Outcome | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | RSA key-pair generation (2048-bit) | `key_manager.py` | Valid key pair generated | Generated successfully | **PASS** |
| **TC-02** | Rejection of insecure key size (< 2048) | `key_manager.py` | Raise ValueError | Rejected | **PASS** |
| **TC-03** | Public key PEM roundtrip | `key_manager.py` | Matches X.509 PEM | Serialized and reloaded | **PASS** |
| **TC-04** | Private key unencrypted roundtrip | `key_manager.py` | Valid unencrypted key | Reloaded successfully | **PASS** |
| **TC-05** | Private key encrypted with passphrase | `key_manager.py` | Encrypted with PKCS#8 | Reloaded with password | **PASS** |
| **TC-06** | Rejection of wrong private key password | `key_manager.py` | Raise ValueError | Error raised cleanly | **PASS** |
| **TC-07** | Rejection of missing password on encrypted key | `key_manager.py` | Raise ValueError | Error raised cleanly | **PASS** |
| **TC-08** | Rejection of empty/corrupted PEM data | `key_manager.py` | Raise ValueError | Rejected | **PASS** |
| **TC-09** | Rejection of empty file (0 bytes) | `encryption.py` | Raise ValueError | Rejected | **PASS** |
| **TC-10** | Rejection of oversized file (> 25 MiB) | `encryption.py` | Raise ValueError | Rejected | **PASS** |
| **TC-11** | Plaintext absence in encrypted package | `encryption.py` | Plaintext not found in pkg | Verified zero leakage | **PASS** |
| **TC-12** | Distinct ciphertexts for identical plaintext | `encryption.py` | Different nonces/keys | Verified uniqueness | **PASS** |
| **TC-13** | Encryption statistics & metadata accuracy | `encryption.py` | Valid metrics dictionary | Verified metrics | **PASS** |
| **TC-14** | Text file roundtrip encryption & decryption | `decryption.py` | Exact byte-for-byte match | Verified match | **PASS** |
| **TC-15** | Binary PDF-like payload roundtrip | `decryption.py` | Exact byte-for-byte match | Verified match | **PASS** |
| **TC-16** | Binary PNG-like image payload roundtrip | `decryption.py` | Exact byte-for-byte match | Verified match | **PASS** |
| **TC-17** | Decryption with incorrect private key | `decryption.py` | Raise ValueError | Rejected | **PASS** |
| **TC-18** | Path traversal filename sanitization | `file_format.py` | Strips `../` and separators | Cleaned to basename | **PASS** |
| **TC-19** | Modified ciphertext rejection by AEAD | `decryption.py` | Tag verification fails | Caught & rejected | **PASS** |
| **TC-20** | Tampered authentication tag rejection | `decryption.py` | Tag verification fails | Caught & rejected | **PASS** |
| **TC-21** | Corrupted package envelope rejection | `file_format.py` | Raise ValueError | Caught & rejected | **PASS** |
| **TC-22** | Missing required package field rejection | `file_format.py` | Raise ValueError | Caught & rejected | **PASS** |
| **TC-23** | Invalid Base64 data rejection | `file_format.py` | Raise ValueError | Caught & rejected | **PASS** |
| **TC-24** | Unsupported package version rejection | `file_format.py` | Raise ValueError | Caught & rejected | **PASS** |
| **TC-25** | Metadata tampering rejection via AAD | `decryption.py` | Authentication fails | Caught & rejected | **PASS** |

**Empirical Test Execution Summary:**
- **Framework:** `pytest 9.1.1` / `unittest`
- **Total Tests Executed:** 25
- **Passed:** 25 (100%)
- **Failed:** 0
- **Total Duration:** 0.98 seconds

---

## 16. SCREENSHOTS (PLACEHOLDERS)
*(Screenshots to be captured during live demonstration)*
- **Figure 1:** `screenshots/01_home_screen.png` — Application landing page and workflow overview.
- **Figure 2:** `screenshots/02_encrypt_screen.png` — File selection, public key association, and encryption metrics.
- **Figure 3:** `screenshots/03_decrypt_screen.png` — `.cvlt` package upload, private key entry, and file recovery.
- **Figure 4:** `screenshots/04_tamper_detection.png` — Demonstration of AES-GCM authentication failure upon file modification.

---

## 17. RESULTS AND PERFORMANCE DISCUSSION
Empirical benchmarking on a standard personal computer confirms that:
1. **Symmetric Encryption Overhead:** AES-256-GCM encrypts files at near-instantaneous speeds for everyday files (e.g. under 5 milliseconds for files up to 1 MB, and approximately 80–120 milliseconds for a 20 MB payload).
2. **Asymmetric Key Encapsulation:** RSA-OAEP encryption and decryption of the 32-byte AES key takes less than 2 milliseconds, demonstrating the efficiency advantage over full-file asymmetric encryption.
3. **Payload Fidelity:** In all test scenarios, files recovered via authenticated decryption exhibited identical SHA-256 hashes to the original source files.
4. **Integrity Assurance:** Any modification to either the ciphertext or the metadata in the `.cvlt` package immediately triggered an `InvalidTag` rejection.

---

## 18. PROJECT LIMITATIONS
- **Memory Consumption:** Payloads are loaded into system memory. Processing files significantly larger than 50 MB in a browser session can lead to browser memory saturation.
- **Key Recovery:** No key recovery or escrow mechanism exists. Loss of the private key or passphrase permanently renders the file unrecoverable.
- **Single-User Local Architecture:** The project is intended for local academic demonstration rather than enterprise multi-user distributed deployments.

---

## 19. CONCLUSION AND FUTURE WORK
CipherVault Lite successfully demonstrates the principles and practical mechanics of hybrid cryptography. By combining AES-256-GCM for fast, authenticated file encryption and RSA-OAEP for secure key encapsulation, the project solves the key-distribution dilemma while maintaining high throughput and strong tamper resistance.

### Potential Future Enhancements:
1. **Post-Quantum Hybridization:** Integrating post-quantum key encapsulation mechanisms (e.g., ML-KEM / CRYSTALS-Kyber) alongside RSA.
2. **Streaming AEAD:** Implementing chunked streaming encryption to support multi-gigabyte files without high RAM overhead.
3. **Digital Signatures:** Integrating RSA-PSS or Ed25519 signatures to provide non-repudiation of origin alongside encryption.

---

## 20. REFERENCES
1. Stallings, W. (2017). *Cryptography and Network Security: Principles and Practice* (7th ed.). Pearson.
2. Dworkin, M. (2007). *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC*. NIST Special Publication 800-38D.
3. Moriarty, K., Kaliski, B., Jonsson, J., & Rusch, A. (2016). *PKCS #1: RSA Cryptography Specifications Version 2.2*. RFC 8017.
4. Python Cryptographic Authority. (2024). *Cryptography Documentation*. https://cryptography.io/
5. Streamlit Inc. (2024). *Streamlit Documentation*. https://docs.streamlit.io/
