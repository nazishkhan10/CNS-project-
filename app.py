"""
CipherVault Lite - Hybrid File Encryption and Decryption System Using AES and RSA
A Cryptography and Network Security (CNS) Mini-Project for B.Tech Students.
Built with Streamlit and the Python `cryptography` library.
"""

import os
import io
import time
import streamlit as st

from crypto_utils.key_manager import (
    generate_rsa_key_pair,
    serialize_public_key,
    serialize_private_key,
    load_public_key,
    load_private_key,
    is_private_key_encrypted,
)
from crypto_utils.file_format import (
    FORMAT_ID,
    FORMAT_VERSION,
    CIPHER_ID,
    KEY_ENC_ID,
    MAX_FILE_SIZE,
    MAX_PACKAGE_SIZE,
    sanitize_filename,
)
from crypto_utils.encryption import encrypt_file_hybrid
from crypto_utils.decryption import decrypt_file_hybrid

# Page configuration
st.set_page_config(
    page_title="CipherVault Lite | CNS Hybrid Encryption",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Helper for formatted file sizes
def format_size(size_bytes: int) -> str:
    """Format bytes into a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KiB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MiB"


# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🔐 CipherVault Lite")
st.sidebar.caption("Hybrid Cryptosystem (AES-256-GCM + RSA-OAEP)")
st.sidebar.markdown("---")

menu_choice = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "🔒 Encrypt File", "🔓 Decrypt File", "🔑 Key Management", "📖 About the Project"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Course:** Cryptography & Network Security\n\n"
    "**Primitives:**\n"
    "- AES-256-GCM (AEAD)\n"
    "- RSA-OAEP (SHA-256)\n"
    "- PKCS#8 Key Protection\n\n"
    "**Upload Limit:** 25 MiB"
)

if st.sidebar.button("🧹 Clear Session & Cache"):
    st.session_state.clear()
    st.rerun()


# ==============================================================================
# 1. HOME SECTION
# ==============================================================================
if menu_choice == "🏠 Home":
    st.title("CipherVault Lite")
    st.subheader("Hybrid File Encryption and Decryption Using AES and RSA")
    st.markdown(
        """
        Welcome to **CipherVault Lite**, a local Cryptography and Network Security (CNS) 
        mini-project demonstrating practical **Hybrid Encryption**.
        """
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(
            """
            ### 📌 Problem Statement
            Storing or transmitting files in plaintext exposes confidential data to unauthorized interception, 
            eavesdropping, and tampering. While symmetric ciphers like **AES** are fast and handle large data 
            efficiently, they face the **key-distribution problem**. Asymmetric ciphers like **RSA** solve 
            key exchange using public/private key pairs, but are computationally slow and cannot directly encrypt 
            arbitrary-sized files.
            
            ### 💡 The Hybrid Solution
            **CipherVault Lite** combines the best of both cryptographic worlds:
            1. **AES-256-GCM (Symmetric):** Rapidly encrypts any arbitrary file format (PDF, DOCX, images, text) 
               using a fresh, random 256-bit symmetric key and guarantees **both confidentiality and integrity**.
            2. **RSA-OAEP (Asymmetric):** Protects only the small 32-byte AES key using the recipient's 
               2048-bit (or higher) RSA public key.
            3. **Secure Decryption:** Only the legitimate recipient possessing the matching RSA private key 
               can recover the AES key and decrypt the file.
            """
        )

    with col2:
        st.markdown(
            """
            ### ⚡ System Specifications
            | Component | Specification |
            | :--- | :--- |
            | **Symmetric Cipher** | AES-256 in GCM Mode (AEAD) |
            | **Nonce Size** | 96 bits (12 bytes, unique per run) |
            | **Auth Tag** | 128 bits (16 bytes, GMAC) |
            | **Asymmetric Cipher** | RSA (2048, 3072, 4096-bit) |
            | **Padding Scheme** | OAEP with MGF1 (SHA-256) |
            | **Key Serialization** | PEM (SubjectPublicKeyInfo & PKCS#8) |
            | **Package Format** | Versioned `.cvlt` Envelope |
            | **Max Upload Size** | 25 MiB (Enforced) |
            """
        )

    st.markdown("---")
    st.subheader("🔄 Hybrid Workflow Overview")
    
    st.markdown(
        """
        ```text
        [ SENDER: Encryption ]
        Plaintext File ────────► [ AES-256-GCM ] ────────► Ciphertext + Tag
                                       ▲
        Fresh 32-byte AES Key ─────────┘
                │
                └────────► [ RSA-OAEP (Public Key) ] ────► Encrypted AES Key
                                                                 │
                                                                 ▼
                                                  Assemble into .cvlt Package
        ────────────────────────────────────────────────────────────────────────
        [ RECIPIENT: Decryption ]
        .cvlt Package ────────► Encrypted AES Key ────► [ RSA-OAEP (Private Key) ]
                                                                 │
                                                           Recovered AES Key
                                                                 ▼
        Ciphertext + Tag ─────────────────────────────► [ AES-256-GCM (Auth) ]
                                                                 │
                                                                 ▼
                                                         Verified Original File
        ```
        """
    )

    st.markdown("---")
    st.warning(
        "⚠️ **Educational Disclaimer:** CipherVault Lite is designed as an educational mini-project for "
        "the B.Tech Cryptography & Network Security (CNS) curriculum. It runs entirely on your local machine "
        "and is intended for classroom demonstration and laboratory examination."
    )


# ==============================================================================
# 2. ENCRYPT FILE SECTION
# ==============================================================================
elif menu_choice == "🔒 Encrypt File":
    st.title("🔒 Encrypt File")
    st.markdown(
        "Encrypt any document, image, or archive using **AES-256-GCM** and seal the key using **RSA-OAEP**."
    )

    col_file, col_key = st.columns([1, 1], gap="medium")

    with col_file:
        st.subheader("1. Select File to Encrypt")
        uploaded_file = st.file_uploader(
            "Choose a file (All formats supported: PDF, DOCX, TXT, PNG, JPG, CSV, ZIP)",
            type=None,
            help="Files are processed directly in-memory as raw binary bytes.",
        )
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            st.caption(f"**Filename:** `{uploaded_file.name}` | **Size:** {format_size(len(file_bytes))}")
            if len(file_bytes) == 0:
                st.error("❌ The selected file is empty (0 bytes). Please choose a valid file.")
            elif len(file_bytes) > MAX_FILE_SIZE:
                st.error(f"❌ File exceeds the maximum allowed limit of {format_size(MAX_FILE_SIZE)}.")

    with col_key:
        st.subheader("2. Recipient Public Key")
        key_source = st.radio(
            "Public Key Source:",
            ["Upload Existing Public Key (.pem)", "Generate New Key Pair Here"],
            index=0,
        )

        recipient_public_key = None

        if key_source == "Upload Existing Public Key (.pem)":
            pub_file = st.file_uploader("Upload recipient's public_key.pem", type=["pem", "pub", "txt"])
            if pub_file is not None:
                try:
                    pub_bytes = pub_file.getvalue()
                    recipient_public_key = load_public_key(pub_bytes)
                    st.success(f"✅ Valid RSA Public Key loaded ({recipient_public_key.key_size}-bit).")
                except Exception as e:
                    st.error(f"❌ Invalid Public Key: {str(e)}")

        else:
            st.info("Generate a temporary or fresh key pair right now:")
            quick_key_size = st.selectbox("Key Size:", [2048, 3072, 4096], index=0)
            quick_pw = st.text_input(
                "Passphrase for Private Key (Recommended):",
                type="password",
                help="Encrypts the private key with AES-256 using PKCS#8.",
            )
            
            if st.button("Generate RSA Key Pair"):
                with st.spinner("Generating cryptographically secure RSA key pair..."):
                    priv_k, pub_k = generate_rsa_key_pair(quick_key_size)
                    st.session_state["quick_pub_pem"] = serialize_public_key(pub_k)
                    st.session_state["quick_priv_pem"] = serialize_private_key(priv_k, password=quick_pw if quick_pw else None)
                    st.session_state["quick_key_size"] = quick_key_size
                    st.success("✅ RSA Key Pair successfully generated!")

            if "quick_pub_pem" in st.session_state:
                try:
                    recipient_public_key = load_public_key(st.session_state["quick_pub_pem"])
                    st.markdown("**Download Your Keys:**")
                    col_k1, col_k2 = st.columns(2)
                    with col_k1:
                        st.download_button(
                            label="📥 Download public_key.pem",
                            data=st.session_state["quick_pub_pem"],
                            file_name="public_key.pem",
                            mime="application/x-pem-file",
                        )
                    with col_k2:
                        st.download_button(
                            label="📥 Download private_key.pem",
                            data=st.session_state["quick_priv_pem"],
                            file_name="private_key.pem",
                            mime="application/x-pem-file",
                            help="Keep this file secure! It is required for decryption.",
                        )
                    st.caption("🚨 **Important:** Keep `private_key.pem` secret! Do not share it with anyone.")
                except Exception as e:
                    st.error(f"Error reading generated key: {str(e)}")

    st.markdown("---")
    st.subheader("3. Execute Hybrid Encryption")

    ready_to_encrypt = (
        uploaded_file is not None 
        and len(uploaded_file.getvalue()) > 0 
        and len(uploaded_file.getvalue()) <= MAX_FILE_SIZE 
        and recipient_public_key is not None
    )

    if st.button("🔐 Encrypt File Now", disabled=not ready_to_encrypt, type="primary"):
        try:
            with st.spinner("Encrypting payload and encapsulating symmetric key..."):
                file_bytes = uploaded_file.getvalue()
                pkg_bytes, stats = encrypt_file_hybrid(
                    file_bytes=file_bytes,
                    original_filename=uploaded_file.name,
                    public_key=recipient_public_key,
                )

                st.session_state["last_encrypted_pkg"] = pkg_bytes
                st.session_state["last_encrypted_filename"] = f"{sanitize_filename(uploaded_file.name)}.cvlt"
                st.session_state["last_encrypt_stats"] = stats

            st.success("🎉 Encryption Successful! The `.cvlt` package is ready for secure storage or transfer.")

        except Exception as e:
            st.error(f"❌ Encryption Failed: {str(e)}")

    if "last_encrypted_pkg" in st.session_state and "last_encrypt_stats" in st.session_state:
        stats = st.session_state["last_encrypt_stats"]
        pkg_data = st.session_state["last_encrypted_pkg"]
        pkg_filename = st.session_state["last_encrypted_filename"]

        st.markdown("### 📊 Encryption Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Original Size", format_size(stats["original_size_bytes"]))
        m2.metric("Encrypted Package Size", format_size(stats["package_size_bytes"]))
        m3.metric("Processing Time", f"{stats['encryption_time_ms']} ms")
        m4.metric("RSA Key Size", f"{stats['rsa_key_size_bits']} bits")

        st.download_button(
            label=f"💾 Download Encrypted Package ({pkg_filename})",
            data=pkg_data,
            file_name=pkg_filename,
            mime="application/json",
            type="primary",
        )
        st.info(
            "💡 **Next Step:** You can safely store or send this `.cvlt` file. "
            "To recover the file, use the **Decrypt File** section along with the recipient's **RSA Private Key**."
        )


# ==============================================================================
# 3. DECRYPT FILE SECTION
# ==============================================================================
elif menu_choice == "🔓 Decrypt File":
    st.title("🔓 Decrypt File")
    st.markdown(
        "Recover your original file from a `.cvlt` encrypted package using your **RSA Private Key**."
    )

    col_pkg, col_priv = st.columns([1, 1], gap="medium")

    with col_pkg:
        st.subheader("1. Upload Encrypted Package (.cvlt)")
        pkg_file = st.file_uploader(
            "Select .cvlt package file",
            type=["cvlt", "json", "txt"],
            help="Upload the package generated by CipherVault Lite.",
        )
        if pkg_file is not None:
            pkg_raw = pkg_file.getvalue()
            st.caption(f"**Package File:** `{pkg_file.name}` | **Size:** {format_size(len(pkg_raw))}")
            if len(pkg_raw) == 0:
                st.error("❌ The uploaded package is empty.")
            elif len(pkg_raw) > MAX_PACKAGE_SIZE:
                st.error(f"❌ Package exceeds the maximum limit of {format_size(MAX_PACKAGE_SIZE)}.")

    with col_priv:
        st.subheader("2. Upload Matching RSA Private Key")
        priv_file = st.file_uploader(
            "Upload private_key.pem",
            type=["pem", "key", "txt"],
            help="The RSA private key corresponding to the public key used during encryption.",
        )
        
        passphrase_input = ""
        is_encrypted_key = False

        if priv_file is not None:
            priv_bytes = priv_file.getvalue()
            is_encrypted_key = is_private_key_encrypted(priv_bytes)
            
            if is_encrypted_key:
                st.warning("🔒 This private key is password-protected.")
                passphrase_input = st.text_input(
                    "Enter Private Key Passphrase:",
                    type="password",
                    help="Passphrase used during key generation.",
                )
            else:
                st.info("ℹ️ Unencrypted private key detected.")

    st.markdown("---")
    st.subheader("3. Authenticated Decryption")

    ready_to_decrypt = (
        pkg_file is not None 
        and len(pkg_file.getvalue()) > 0 
        and priv_file is not None 
        and len(priv_file.getvalue()) > 0
    )

    if st.button("🔓 Decrypt & Verify File", disabled=not ready_to_decrypt, type="primary"):
        try:
            with st.spinner("Validating package and verifying cryptographic authenticity..."):
                priv_bytes = priv_file.getvalue()
                
                # Step 1: Safely load private key
                try:
                    loaded_priv_key = load_private_key(
                        pem_data=priv_bytes,
                        password=passphrase_input if passphrase_input else None,
                    )
                except ValueError as ve:
                    st.error(f"❌ Private Key Error: {str(ve)}")
                    st.stop()

                # Step 2: Decrypt package using hybrid scheme
                pkg_raw = pkg_file.getvalue()
                decrypted_bytes, recovered_filename, dec_stats = decrypt_file_hybrid(
                    package_bytes=pkg_raw,
                    private_key=loaded_priv_key,
                )

                st.session_state["decrypted_payload"] = decrypted_bytes
                st.session_state["recovered_filename"] = recovered_filename
                st.session_state["dec_stats"] = dec_stats

            st.success("✅ Authenticated Decryption Successful! File integrity and authenticity verified.")

        except ValueError as ve:
            # Clean generic user-facing message for tampered or mismatched data
            st.error(f"❌ Decryption Failed: {str(ve)}")
            st.caption("Verification failed: Either an incorrect private key was used, or the ciphertext/tag was modified.")
        except Exception as e:
            st.error("❌ Decryption Failed: Unable to verify or recover file.")

    if "decrypted_payload" in st.session_state and "dec_stats" in st.session_state:
        dec_stats = st.session_state["dec_stats"]
        dec_payload = st.session_state["decrypted_payload"]
        rec_name = st.session_state["recovered_filename"]

        st.markdown("### 📊 Decryption Metrics")
        d1, d2, d3 = st.columns(3)
        d1.metric("Recovered Filename", rec_name)
        d2.metric("Recovered File Size", format_size(dec_stats["recovered_size_bytes"]))
        d3.metric("Decryption Time", f"{dec_stats['decryption_time_ms']} ms")

        st.download_button(
            label=f"💾 Download Recovered File ({rec_name})",
            data=dec_payload,
            file_name=rec_name,
            mime="application/octet-stream",
            type="primary",
        )


# ==============================================================================
# 4. KEY MANAGEMENT SECTION
# ==============================================================================
elif menu_choice == "🔑 Key Management":
    st.title("🔑 Key Management")
    st.markdown(
        "Generate and manage standard **RSA Key Pairs** using PEM encoding and PKCS#8 encryption."
    )

    tab_gen, tab_inspect = st.tabs(["Generate RSA Key Pair", "Inspect PEM Key"])

    with tab_gen:
        st.subheader("Generate a New Key Pair")
        col_g1, col_g2 = st.columns([1, 1], gap="medium")

        with col_g1:
            key_size = st.selectbox(
                "RSA Key Size (bits):",
                [2048, 3072, 4096],
                index=0,
                help="2048-bit is the current standard recommended minimum for RSA.",
            )
            protect_with_pw = st.checkbox(
                "Protect Private Key with Password (Recommended)",
                value=True,
                help="Encrypts private_key.pem using AES-256 and PKCS#8.",
            )
            password = ""
            confirm_pw = ""
            if protect_with_pw:
                password = st.text_input("Enter Passphrase:", type="password", key="km_pw")
                confirm_pw = st.text_input("Confirm Passphrase:", type="password", key="km_cpw")
            else:
                st.warning("⚠️ Warning: Exporting private key without a password is not recommended for production.")

            if st.button("Generate RSA Key Pair", key="km_gen_btn", type="primary"):
                if protect_with_pw and (not password or password != confirm_pw):
                    st.error("❌ Passwords do not match or are empty.")
                else:
                    with st.spinner("Generating cryptographically secure RSA key pair..."):
                        priv_key, pub_key = generate_rsa_key_pair(key_size)
                        st.session_state["km_pub"] = serialize_public_key(pub_key)
                        st.session_state["km_priv"] = serialize_private_key(
                            priv_key, password=password if protect_with_pw else None
                        )
                        st.session_state["km_size"] = key_size
                        st.success("✅ RSA Key Pair successfully generated!")

        with col_g2:
            st.markdown(
                """
                ### 🔑 Key Roles Explained
                - **Public Key (`public_key.pem`):** 
                  Can be freely distributed. Senders use it to encrypt the symmetric AES key.
                - **Private Key (`private_key.pem`):** 
                  Must be kept strictly confidential. The recipient uses it to decrypt the AES key.
                - **Crucial Rule:** 
                  If you lose your private key or forget its password, **encrypted files cannot be recovered**.
                """
            )

        if "km_pub" in st.session_state and "km_priv" in st.session_state:
            st.markdown("---")
            st.subheader("📥 Download Generated Keys")
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.download_button(
                    label="📥 Download public_key.pem",
                    data=st.session_state["km_pub"],
                    file_name="public_key.pem",
                    mime="application/x-pem-file",
                    type="primary",
                )
            with d_col2:
                st.download_button(
                    label="📥 Download private_key.pem",
                    data=st.session_state["km_priv"],
                    file_name="private_key.pem",
                    mime="application/x-pem-file",
                    help="Store this file in a safe location!",
                )

    with tab_inspect:
        st.subheader("Inspect Existing PEM Key")
        st.markdown("Upload any PEM key to check its format, key size, and encryption status without exposing secrets.")
        
        inspect_file = st.file_uploader("Upload PEM Key (.pem)", type=["pem", "key", "pub", "txt"], key="inspect_upload")
        if inspect_file is not None:
            raw_data = inspect_file.getvalue()
            
            # Check public key
            is_pub = False
            try:
                pub = load_public_key(raw_data)
                is_pub = True
                st.success(f"✅ Valid **RSA Public Key** ({pub.key_size} bits).")
            except Exception:
                pass

            # Check private key
            if not is_pub:
                try:
                    is_enc = is_private_key_encrypted(raw_data)
                    st.info(f"ℹ️ **RSA Private Key** detected. Password Protection: **{'Yes (Encrypted)' if is_enc else 'No (Plaintext)'}**")
                except Exception as e:
                    st.error("❌ Unrecognized key format or malformed PEM file.")


# ==============================================================================
# 5. ABOUT THE PROJECT SECTION
# ==============================================================================
elif menu_choice == "📖 About the Project":
    st.title("📖 About CipherVault Lite")
    st.subheader("A Practical Cryptography & Network Security (CNS) Mini-Project")

    st.markdown(
        """
        ### 🎓 Academic Context
        This mini-project was developed for the **Cryptography and Network Security (CNS)** course 
        in Bachelor of Technology (B.Tech) Computer Science / Information Technology programs.
        
        It addresses the core curriculum topics:
        - Symmetric Ciphers (AES in Galois/Counter Mode)
        - Asymmetric Cryptosystems (RSA-OAEP)
        - Cryptographic Hash Functions & Integrity Tags (SHA-256, GMAC)
        - Key Management and Distribution
        """
    )

    t1, t2, t3 = st.tabs(["Hybrid Encryption Theory", "Why AES-GCM & RSA-OAEP?", "College Viva Q&A"])

    with t1:
        st.markdown(
            """
            #### What is Hybrid Cryptography?
            Pure asymmetric encryption (like RSA) is mathematically too slow and constrained by key size to 
            encrypt large files directly. For example, a 2048-bit RSA key with OAEP padding can only encrypt 
            at most 190 bytes of data!
            
            Pure symmetric encryption (like AES) is blazingly fast and handles gigabytes of data with ease, 
            but requires both communicating parties to securely share the secret key beforehand.
            
            **The Hybrid Approach bridges this gap:**
            1. Generate a one-time random 256-bit AES key for the session.
            2. Encrypt the bulky file with AES-256-GCM.
            3. Encrypt the 32-byte AES key using RSA-OAEP with the recipient's public key.
            4. Package both together. The recipient unlocks the AES key using their private key, then decrypts the file.
            """
        )

    with t2:
        st.markdown(
            r"""
            #### Why AES-256-GCM over AES-CBC or AES-ECB?
            - **No ECB (Electronic Codebook):** ECB encrypts identical blocks into identical ciphertext, leaking patterns (e.g. the ECB Penguin problem).
            - **No Plain CBC without MAC:** CBC mode alone provides confidentiality but NOT integrity, leaving it vulnerable to padding oracle attacks (e.g., POODLE).
            - **AES-GCM (Galois/Counter Mode):** Provides **Authenticated Encryption with Associated Data (AEAD)**. It encrypts using counter mode and generates an authentication tag (GMAC) in parallel. Any alteration of even a single bit in the ciphertext or metadata causes decryption to immediately fail.

            #### Why RSA-OAEP over Textbook RSA or PKCS#1 v1.5?
            - **Textbook RSA** ($C = M^e \pmod n$) is deterministic and completely insecure.
            - **PKCS#1 v1.5** padding is vulnerable to Bleichenbacher's million-message chosen-ciphertext attack.
            - **RSA-OAEP (Optimal Asymmetric Encryption Padding):** Uses randomized Feistel networks with hash functions (SHA-256) to ensure plaintext-awareness and semantic security under Chosen-Ciphertext Attacks (IND-CCA2).
            """
        )

    with t3:
        st.markdown(
            r"""
            #### 💡 Typical College Viva Questions & Answers
            
            **Q1: Why can't we encrypt an entire 10 MB PDF directly using RSA?**  
            *Answer:* RSA is based on modular exponentiation of large numbers ($c = m^e \pmod n$), which is 
            computationally thousands of times slower than symmetric ciphers. Furthermore, RSA-OAEP padding 
            limits the plaintext size to $k - 2hLen - 2$ bytes (190 bytes for RSA-2048 with SHA-256).

            **Q2: What is the purpose of the 12-byte Nonce in AES-GCM?**  
            *Answer:* Nonce stands for 'Number used ONCE'. It ensures that encrypting the same file twice produces 
            completely different ciphertexts, preventing replay and pattern analysis attacks. Reusing a nonce with 
            the same key in GCM mode is catastrophic as it reveals the hash subkey ($H$).

            **Q3: How does the system detect if an attacker alters the encrypted file?**  
            *Answer:* AES-GCM produces a 16-byte authentication tag calculated over the ciphertext and Additional 
            Authenticated Data (AAD) using Galois Field multiplication ($GF(2^{128})$). If even 1 bit is flipped, 
            the computed tag will not match, and decryption will raise an `InvalidTag` exception.

            **Q4: What happens if the private key password is forgotten?**  
            *Answer:* The private key is encrypted with AES-256 using PKCS#8. Without the correct password, the 
            private key cannot be decrypted, making recovery of the encapsulated AES key mathematically impossible.
            """
        )

    st.markdown("---")
    st.caption("CipherVault Lite — Department of Computer Science & Engineering")
