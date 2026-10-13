"""
Generate a professional, fully styled academic DOCX thesis report for CipherVault Lite.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Set cell background color."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding for a table cell (in dxa)."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_callout(doc, text, title="NOTE:"):
    """Add a shaded callout box."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border only (accent border)
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="1B365D"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    run_t = p.add_run(f"{title} ")
    run_t.bold = True
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = RGBColor(27, 54, 93)
    
    run_b = p.add_run(text)
    run_b.font.name = "Calibri"
    run_b.font.size = Pt(10)
    run_b.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph() # Spacing

def add_code_block(doc, code_text):
    """Add a monospace shaded code block."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.1
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph()

def build_document():
    doc = Document()
    
    # Page Setup: Standard Margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True
        
        # Header / Footer for subsequent pages
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("CipherVault Lite | B.Tech CNS Project Thesis")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(100, 116, 139)
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Page Final - Cryptography & Network Security")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(100, 116, 139)

    # Styling Palettes
    COLOR_PRIMARY = RGBColor(27, 54, 93)     # Deep Navy
    COLOR_SECONDARY = RGBColor(44, 77, 117)  # Slate Navy
    COLOR_BODY = RGBColor(30, 41, 59)        # Charcoal Slate
    HEX_HEADER = "1B365D"
    HEX_ALT = "F8FAFC"
    HEX_WHITE = "FFFFFF"

    # ==========================================
    # TITLE PAGE
    # ==========================================
    p_pre = doc.add_paragraph()
    p_pre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pre.paragraph_format.space_before = Pt(40)
    r_pre = p_pre.add_run("A B.TECH MINI-PROJECT THESIS REPORT\nIN\nCRYPTOGRAPHY AND NETWORK SECURITY")
    r_pre.font.name = "Calibri"
    r_pre.font.size = Pt(11)
    r_pre.bold = True
    r_pre.font.color.rgb = RGBColor(100, 116, 139)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("CIPHERVAULT LITE:\nA HYBRID FILE ENCRYPTION AND DECRYPTION SYSTEM USING AES AND RSA")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(22)
    r_title.bold = True
    r_title.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(50)
    r_sub = p_sub.add_run("Authenticated Bulk Encryption (AES-256-GCM) with Public-Key Session Key Encapsulation (RSA-OAEP)")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.italic = True
    r_sub.font.color.rgb = COLOR_SECONDARY

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(40)
    p_meta.paragraph_format.line_spacing = 1.3
    r_m = p_meta.add_run(
        "Submitted by:\n"
        "[Student Name Placeholder] | Roll No / PRN: [Roll Number Placeholder]\n\n"
        "Under the Guidance of:\n"
        "[Guide Name Placeholder], [Designation Placeholder]\n\n"
        "Department of Computer Science & Engineering\n"
        "[College / University Name Placeholder]\n"
        "Academic Year: 2025 - 2026"
    )
    r_m.font.name = "Calibri"
    r_m.font.size = Pt(11)
    r_m.font.color.rgb = COLOR_BODY

    doc.add_page_break()

    # Helper function for adding standard headings
    def add_sec_heading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(15)
        r.bold = True
        r.font.color.rgb = COLOR_PRIMARY

    def add_sub_heading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = "Calibri"
        r.font.size = Pt(12.5)
        r.bold = True
        r.font.color.rgb = COLOR_SECONDARY

    def add_body(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Calibri"
            rb.font.size = Pt(11)
            rb.bold = True
            rb.font.color.rgb = COLOR_PRIMARY
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_BODY
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.font.name = "Calibri"
            rb.font.size = Pt(11)
            rb.bold = True
            rb.font.color.rgb = COLOR_PRIMARY
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_BODY

    # ==========================================
    # 1. ABSTRACT
    # ==========================================
    add_sec_heading("1. Abstract")
    add_body(
        "CipherVault Lite is a desktop-accessible hybrid cryptographic system designed for secure file storage "
        "and transmission. It integrates AES-256 in Galois/Counter Mode (AES-256-GCM) for high-throughput symmetric "
        "bulk encryption and RSA with Optimal Asymmetric Encryption Padding (RSA-OAEP with SHA-256) for asymmetric "
        "session key encapsulation. AES-256-GCM guarantees both data confidentiality and ciphertext authenticity via "
        "a 128-bit authentication tag, while RSA-OAEP eliminates the symmetric key-distribution bottleneck. "
        "The system packages the encrypted payload, a unique 96-bit nonce, the encrypted AES key, and canonical "
        "metadata into a structured, versioned .cvlt envelope. A local web-based graphical interface built using "
        "Streamlit allows users to manage RSA keys, encrypt files of any format (PDF, DOCX, images, text, archives), "
        "decrypt files using matching private keys, and detect unauthorized tampering. The implementation was validated "
        "through an automated suite of 25 test cases achieving a 100% pass rate."
    )

    # ==========================================
    # 2. INTRODUCTION
    # ==========================================
    add_sec_heading("2. Introduction")
    add_body(
        "In modern computer networks, unprotected file sharing introduces severe vulnerabilities, including passive "
        "eavesdropping, data leakage, and malicious payload modification. Securing digital assets requires upholding "
        "the foundational CIA Triad: Confidentiality, Integrity, and Authenticity. While symmetric ciphers like AES "
        "provide high performance for large data volumes, they require both parties to pre-share a secret key across a "
        "secure channel. Conversely, asymmetric ciphers like RSA resolve key distribution using public/private key pairs "
        "but suffer from heavy computational overhead and strict mathematical payload constraints."
    )
    add_body(
        "CipherVault Lite resolves this dilemma by implementing a Hybrid Cryptosystem—the standard architecture powering "
        "protocols such as TLS, PGP, and S/MIME. By combining AES for bulk file encryption with RSA for session key "
        "protection, this project provides an accessible, fully verifiable reference implementation for B.Tech students "
        "studying Cryptography and Network Security (CNS)."
    )

    # ==========================================
    # 3. PROBLEM STATEMENTS
    # ==========================================
    add_sec_heading("3. Problem Statements")
    add_bullet(
        "Encrypting files purely with symmetric ciphers requires both sender and receiver to share the secret key beforehand. "
        "If transmitted across an untrusted channel, the key can be intercepted, exposing all ciphertext to unauthorized decryption.",
        bold_prefix="Symmetric Key Distribution Barrier: "
    )
    add_bullet(
        "RSA relies on modular exponentiation of large integers (C = M^e mod n), making it thousands of times slower than AES. "
        "Furthermore, under RSA-OAEP padding with SHA-256, an RSA-2048 key can encrypt a maximum of only 190 bytes per block, "
        "rendering direct file encryption mathematically impossible without complex chunking.",
        bold_prefix="Asymmetric Computational and Size Bounds: "
    )
    add_bullet(
        "Introductory encryption applications frequently utilize Electronic Codebook (ECB) mode, which leaks structural plaintext "
        "patterns, or Cipher Block Chaining (CBC) mode without an authentication tag (MAC). Unauthenticated ciphertexts are vulnerable "
        "to bit-flipping, byte alteration, and padding oracle attacks.",
        bold_prefix="Vulnerabilities in Unauthenticated Legacy Modes: "
    )

    # ==========================================
    # 4. OBJECTIVES
    # ==========================================
    add_sec_heading("4. Objectives")
    add_bullet("Implement authenticated symmetric encryption using AES-256 in Galois/Counter Mode (GCM).")
    add_bullet("Implement asymmetric key encapsulation using RSA-OAEP (2048-bit minimum) with SHA-256 and MGF1.")
    add_bullet("Prevent metadata tampering by binding package headers into AES-GCM Additional Authenticated Data (AAD).")
    add_bullet("Enforce nonce freshness by generating a cryptographically secure 96-bit random nonce for every operation.")
    add_bullet("Implement standard RSA key management with PKCS#8 password-based key encryption.")
    add_bullet("Deliver a clean, local web-based interface using Streamlit optimized for laboratory and viva demonstrations.")
    add_bullet("Empirically validate implementation correctness and security controls through automated testing.")

    # ==========================================
    # 5. SCOPE AND LIMITATIONS
    # ==========================================
    add_sec_heading("5. Scope and Limitations")
    add_sub_heading("5.1 Project Scope")
    add_bullet("Runs locally on standard Windows, macOS, or Linux personal computers.")
    add_bullet("Encrypts and decrypts all standard binary and text formats (PDF, DOCX, TXT, PNG, JPG, CSV, ZIP) as raw bytes.")
    add_bullet("Enforces a 25 MiB upload threshold suitable for workstation memory boundaries.")
    add_bullet("Exports and loads standard PEM-encoded keys (SubjectPublicKeyInfo for public, PKCS#8 for private).")

    add_sub_heading("5.2 Project Limitations")
    add_bullet("In-memory buffering restricts multi-gigabyte video or archive files to prevent browser memory exhaustion.")
    add_bullet("Zero key escrow: if a user loses the RSA private key or forgets the passphrase, data recovery is mathematically impossible.")
    add_bullet("Single-user local architecture; does not implement multi-tenant databases or distributed network file servers.")

    # ==========================================
    # 6. TECHNOLOGIES AND LIBRARIES
    # ==========================================
    add_sec_heading("6. Technologies and Libraries")
    add_body(
        "The project strictly employs standard Python libraries and established, audited cryptographic primitives. "
        "The complete technical stack is detailed in Table 1."
    )

    # Table 1: Tech Stack
    t1 = doc.add_table(rows=6, cols=3)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Component", "Technology / Library", "Role in CipherVault Lite"]
    for i, h in enumerate(headers):
        cell = t1.cell(0, i)
        set_cell_background(cell, HEX_HEADER)
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(10)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    data_t1 = [
        ("Language & Runtime", "Python 3.11+ (Verified on 3.14)", "Core execution environment and low-level byte manipulation"),
        ("Cryptography Library", "cryptography (v42.0+)", "Audited implementations of AESGCM, RSA, OAEP, SHA256, serialization"),
        ("User Interface", "Streamlit (v1.30+)", "Responsive web UI, file uploaders, metric cards, download handlers"),
        ("Randomness & Security", "secrets & os modules", "CSPRNG for 32-byte AES keys and 12-byte unique nonces"),
        ("Testing Framework", "pytest (v8.0+) & unittest", "Automated test runner verifying functional roundtrips and tamper alerts"),
    ]

    for row_idx, row_data in enumerate(data_t1, start=1):
        bg = HEX_ALT if row_idx % 2 == 1 else HEX_WHITE
        for col_idx, cell_value in enumerate(row_data):
            cell = t1.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            p = cell.paragraphs[0]
            r = p.add_run(cell_value)
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_BODY

    doc.add_paragraph() # Spacing

    # ==========================================
    # 7. PROPOSED SYSTEM DESIGN
    # ==========================================
    add_sec_heading("7. Proposed System Design")
    add_body(
        "CipherVault Lite is structured into a modular, layered architecture that strictly separates "
        "user interaction from low-level cryptographic primitives."
    )

    arch_text = (
        "+------------------------------------------------------------------------+\n"
        "|                        PRESENTATION LAYER (UI)                         |\n"
        "|                              (app.py)                                  |\n"
        "|  [ Home ]  |  [ Encrypt File ]  |  [ Decrypt File ]  |  [ Key Mgmt ]   |\n"
        "+-----------------------------------+------------------------------------+\n"
        "                                    | Invokes\n"
        "+-----------------------------------v------------------------------------+\n"
        "|                       APPLICATION LOGIC LAYER                          |\n"
        "|                                                                        |\n"
        "|   +---------------------+                 +-----------------------+    |\n"
        "|   |   key_manager.py    |                 |    file_format.py     |    |\n"
        "|   | - RSA Key Gen       |                 | - .cvlt Schema Parser |    |\n"
        "|   | - PKCS#8 Passphrase |                 | - Base64 Encoding/Dec |    |\n"
        "|   | - PEM Serializer    |                 | - Filename Sanitizer  |    |\n"
        "|   +----------+----------+                 +-----------+-----------+    |\n"
        "|              |                                        |                |\n"
        "|   +----------v----------+                 +-----------v-----------+    |\n"
        "|   |    encryption.py    |                 |     decryption.py     |    |\n"
        "|   | - AES-256 Key Gen   |                 | - RSA-OAEP Key Unwrap |    |\n"
        "|   | - Nonce Generation  |                 | - 32-Byte Key Verify  |    |\n"
        "|   | - AES-GCM Encrypt   |                 | - AES-GCM AEAD Verify |    |\n"
        "|   | - RSA-OAEP Key Wrap |                 | - Integrity Enforcer  |    |\n"
        "|   +----------+----------+                 +-----------+-----------+    |\n"
        "+--------------+----------------------------------------+----------------+\n"
        "               |                                        |\n"
        "+--------------v----------------------------------------v----------------+\n"
        "|                    CRYPTOGRAPHIC ENGINE & HARDWARE                     |\n"
        "|           Python `cryptography` Hazmat / OpenSSL C Backend             |\n"
        "+------------------------------------------------------------------------+"
    )
    add_code_block(doc, arch_text)

    add_sub_heading("7.1 .cvlt Envelope Format")
    add_body(
        "The encrypted package uses a structured JSON envelope containing all data necessary for decryption "
        "except the recipient's private key. Binary fields are strictly Base64 encoded."
    )
    json_envelope = (
        "{\n"
        '  "format": "CIPHERVAULT_LITE",\n'
        '  "version": "1.0",\n'
        '  "cipher": "AES-256-GCM",\n'
        '  "key_encapsulation": "RSA-OAEP-SHA256",\n'
        '  "metadata": {\n'
        '    "original_filename": "assignment_report.pdf",\n'
        '    "original_size": 154820,\n'
        '    "timestamp": "2026-10-13T06:21:55+00:00"\n'
        '  },\n'
        '  "nonce": "G7w+8X1...==",          // 12-byte fresh nonce (Base64)\n'
        '  "encrypted_key": "x9K2pQ...==",   // 256-byte RSA-OAEP wrapped AES key (Base64)\n'
        '  "ciphertext": "k3La9F...=="       // AES-GCM ciphertext + 16-byte tag (Base64)\n'
        "}"
    )
    add_code_block(doc, json_envelope)

    # ==========================================
    # 8. ALGORITHM AND WORKING
    # ==========================================
    add_sec_heading("8. Algorithm and Working")

    add_sub_heading("8.1 Hybrid Encryption Workflow")
    add_body(
        "Step 1: Input Validation — Verify 0 < len(Plaintext) <= 25 MiB.\n"
        "Step 2: Symmetric Key Generation — Generate random 32-byte key: K_AES = secrets.token_bytes(32).\n"
        "Step 3: Nonce Generation — Generate random 12-byte nonce: Nonce = os.urandom(12).\n"
        "Step 4: Additional Authenticated Data (AAD) — Construct canonical metadata string:\n"
        "        AAD = 'CIPHERVAULT_LITE|1.0|AES-256-GCM|RSA-OAEP-SHA256|' + filename + '|' + str(file_size)\n"
        "Step 5: AES-256-GCM Encryption — Compute ciphertext C and 16-byte authentication tag T:\n"
        "        C || T = AESGCM(K_AES).encrypt(Nonce, Plaintext, associated_data=AAD)\n"
        "Step 6: RSA-OAEP Key Encapsulation — Encrypt K_AES with recipient's public key (e, n):\n"
        "        C_key = RSA_Encrypt(K_pub, K_AES) using OAEP padding with SHA-256 and MGF1.\n"
        "Step 7: Memory Zeroization — Delete reference to K_AES from runtime memory.\n"
        "Step 8: Assembly — Package Nonce, C_key, C||T, and metadata into the .cvlt JSON structure."
    )

    add_sub_heading("8.2 Hybrid Decryption Workflow")
    add_body(
        "Step 1: Package Parsing & Validation — Verify JSON schema, version, Base64 encoding, and field sizes (|Nonce|=12 bytes, |C_key|>=256 bytes).\n"
        "Step 2: Private Key Loading — Decrypt and load recipient's private key using passphrase via PKCS#8.\n"
        "Step 3: Session Key Decapsulation — Recover K_AES = RSA_Decrypt(K_priv, C_key) using OAEP padding. Verify len(K_AES) == 32 bytes.\n"
        "Step 4: AAD Reconstruction — Rebuild canonical AAD from package metadata.\n"
        "Step 5: Authenticated Decryption — Decrypt C||T using AESGCM(K_AES) with Nonce and AAD.\n"
        "        - If computed tag != T: Raise InvalidTag error and halt immediately without decrypting plaintext.\n"
        "        - If valid: Recover verified plaintext.\n"
        "Step 6: Size & Filename Verification — Verify len(Plaintext) == metadata.original_size, sanitize filename, and return verified file."
    )

    # ==========================================
    # 9. SYSTEM REQUIREMENTS
    # ==========================================
    add_sec_heading("9. System Requirements")
    add_bullet("Processor: Intel Core i3 / AMD Ryzen 3 or higher (Dual-Core 2.0 GHz+)")
    add_bullet("RAM: Minimum 2 GB (4 GB recommended)")
    add_bullet("Storage: At least 200 MB free hard drive space")
    add_bullet("Operating System: Microsoft Windows 10 / Windows 11 (64-bit), macOS Monterey+, or Linux")
    add_bullet("Runtime Environment: Python 3.11, 3.12, 3.13, or 3.14")
    add_bullet("Web Browser: Google Chrome, Microsoft Edge, Brave, Mozilla Firefox, or Safari")

    # ==========================================
    # 10. INSTALLATION AND EXECUTION
    # ==========================================
    add_sec_heading("10. Installation and Execution")
    add_body("Execute the following terminal commands to configure and launch CipherVault Lite locally:")
    exec_cmds = (
        "# 1. Open PowerShell / Command Prompt in the project folder\n"
        'cd "c:\\Users\\datta.000\\Desktop\\rojel ki wife"\n\n'
        "# 2. Create and activate a virtual environment\n"
        "python -m venv .venv\n"
        ".venv\\Scripts\\Activate.ps1\n\n"
        "# 3. Install required dependencies\n"
        "python -m pip install -r requirements.txt\n\n"
        "# 4. Execute the automated test suite\n"
        "python -m pytest tests/ -v\n\n"
        "# 5. Launch the Streamlit local web application\n"
        "python -m streamlit run app.py"
    )
    add_code_block(doc, exec_cmds)
    add_callout(doc, "Once launched, Streamlit opens http://localhost:8501 automatically in your default browser.", title="ACCESS:")

    # ==========================================
    # 11. TESTING PLAN
    # ==========================================
    add_sec_heading("11. Testing Plan")
    add_body(
        "A rigorous test matrix of 25 automated unit and integration tests was developed to verify "
        "cryptographic fidelity, boundary limits, and tamper rejection."
    )

    # Table 2: Test Matrix
    t2 = doc.add_table(rows=26, cols=5)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2_headers = ["Test ID", "Target Module", "Test Objective", "Expected Outcome", "Status"]
    for i, h in enumerate(t2_headers):
        cell = t2.cell(0, i)
        set_cell_background(cell, HEX_HEADER)
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Calibri"
        r.font.size = Pt(9.5)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    test_rows = [
        ("TC-01", "key_manager.py", "RSA key generation (2048-bit)", "Valid private & public key pair", "PASS"),
        ("TC-02", "key_manager.py", "Reject insecure key size (< 2048)", "Raise ValueError on key_size=1024", "PASS"),
        ("TC-03", "key_manager.py", "Public key PEM roundtrip", "Valid SubjectPublicKeyInfo PEM", "PASS"),
        ("TC-04", "key_manager.py", "Private key unencrypted roundtrip", "Valid PKCS#8 PEM without password", "PASS"),
        ("TC-05", "key_manager.py", "Private key password encryption", "Encrypted PEM roundtrip with password", "PASS"),
        ("TC-06", "key_manager.py", "Reject wrong private key password", "Raise ValueError on bad password", "PASS"),
        ("TC-07", "key_manager.py", "Reject missing password on encrypted key", "Raise ValueError if password=None", "PASS"),
        ("TC-08", "key_manager.py", "Reject corrupted / empty PEM data", "Raise ValueError on invalid PEM bytes", "PASS"),
        ("TC-09", "encryption.py", "Reject empty file upload (0 bytes)", "Raise ValueError on empty payload", "PASS"),
        ("TC-10", "encryption.py", "Reject oversized payload (> 25 MiB)", "Raise ValueError exceeding 25 MiB limit", "PASS"),
        ("TC-11", "encryption.py", "Ensure zero plaintext leakage in package", "No plaintext bytes found in .cvlt", "PASS"),
        ("TC-12", "encryption.py", "Semantic security (nonce freshness)", "Distinct nonces & ciphertexts per run", "PASS"),
        ("TC-13", "encryption.py", "Verify encryption metrics & metadata", "Accurate stats dictionary & sizes", "PASS"),
        ("TC-14", "decryption.py", "Roundtrip text file recovery", "Exact byte-for-byte match", "PASS"),
        ("TC-15", "decryption.py", "Roundtrip binary PDF recovery", "Exact byte-for-byte match on PDF stream", "PASS"),
        ("TC-16", "decryption.py", "Roundtrip binary PNG image recovery", "Exact byte-for-byte match on image data", "PASS"),
        ("TC-17", "decryption.py", "Reject decryption with wrong private key", "Raise ValueError (RSA decrypt failure)", "PASS"),
        ("TC-18", "file_format.py", "Path traversal prevention in filename", "Sanitized to safe basename (no ../)", "PASS"),
        ("TC-19", "decryption.py", "Reject modified ciphertext (bit flip)", "AES-GCM tag verification fails", "PASS"),
        ("TC-20", "decryption.py", "Reject modified GMAC authentication tag", "AES-GCM tag verification fails", "PASS"),
        ("TC-21", "file_format.py", "Reject corrupted / non-JSON package", "Raise ValueError on malformed package", "PASS"),
        ("TC-22", "file_format.py", "Reject missing required package fields", "Raise ValueError on missing nonce/key", "PASS"),
        ("TC-23", "file_format.py", "Reject invalid Base64 encoded payload", "Raise ValueError on corrupt Base64", "PASS"),
        ("TC-24", "file_format.py", "Reject unsupported package version", "Raise ValueError on version != 1.0", "PASS"),
        ("TC-25", "decryption.py", "Reject metadata tampering via AAD", "AAD mismatch triggers tag failure", "PASS"),
    ]

    for row_idx, row_data in enumerate(test_rows, start=1):
        bg = HEX_ALT if row_idx % 2 == 1 else HEX_WHITE
        for col_idx, cell_value in enumerate(row_data):
            cell = t2.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(cell_value)
            r.font.name = "Calibri"
            r.font.size = Pt(8.5)
            if col_idx == 4:
                r.bold = True
                r.font.color.rgb = RGBColor(16, 128, 64)
            else:
                r.font.color.rgb = COLOR_BODY

    doc.add_paragraph() # Spacing

    # ==========================================
    # 12. EXPECTED OUTPUT
    # ==========================================
    add_sec_heading("12. Expected Output")

    add_sub_heading("12.1 Automated Test Execution Log")
    test_log_txt = (
        "PS C:\\Users\\datta.000\\Desktop\\rojel ki wife> python -m pytest tests/ -v\n"
        "============================= test session starts =============================\n"
        "platform win32 -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0\n"
        "rootdir: C:\\Users\\datta.000\\Desktop\\rojel ki wife\n"
        "collected 25 items\n\n"
        "tests/test_decryption.py::test_incorrect_private_key_causes_decryption_failure PASSED [  4%]\n"
        "tests/test_decryption.py::test_pdf_binary_roundtrip PASSED                             [  8%]\n"
        "tests/test_decryption.py::test_image_binary_roundtrip PASSED                           [ 12%]\n"
        "tests/test_decryption.py::test_text_file_roundtrip PASSED                              [ 16%]\n"
        "tests/test_decryption.py::test_unsafe_filename_sanitized PASSED                         [ 20%]\n"
        "tests/test_encryption.py::test_empty_file_rejected PASSED                              [ 24%]\n"
        "tests/test_encryption.py::test_encryption_statistics_and_metadata PASSED               [ 28%]\n"
        "tests/test_encryption.py::test_oversized_file_rejected PASSED                          [ 32%]\n"
        "tests/test_encryption.py::test_package_does_not_contain_plaintext PASSED               [ 36%]\n"
        "tests/test_encryption.py::test_two_encryptions_produce_different_packages PASSED        [ 40%]\n"
        "tests/test_integrity.py::test_corrupted_package_format_rejected PASSED                [ 44%]\n"
        "tests/test_integrity.py::test_invalid_base64_data_rejected PASSED                       [ 48%]\n"
        "tests/test_integrity.py::test_metadata_tampering_rejected_by_aad PASSED                [ 52%]\n"
        "tests/test_integrity.py::test_missing_package_fields_rejected PASSED                   [ 56%]\n"
        "tests/test_integrity.py::test_modified_authentication_tag_rejected PASSED               [ 60%]\n"
        "tests/test_integrity.py::test_modified_ciphertext_rejected PASSED                       [ 64%]\n"
        "tests/test_integrity.py::test_unsupported_package_version_rejected PASSED               [ 68%]\n"
        "tests/test_key_management.py::test_empty_or_corrupted_pem_rejected PASSED              [ 72%]\n"
        "tests/test_key_management.py::test_insecure_key_size_rejected PASSED                   [ 76%]\n"
        "tests/test_key_management.py::test_missing_password_for_encrypted_key PASSED          [ 80%]\n"
        "tests/test_key_management.py::test_private_key_encrypted_with_password PASSED         [ 84%]\n"
        "tests/test_key_management.py::test_private_key_unencrypted_roundtrip PASSED           [ 88%]\n"
        "tests/test_key_management.py::test_public_key_pem_roundtrip PASSED                    [ 92%]\n"
        "tests/test_key_management.py::test_rsa_key_pair_generation_succeeds PASSED           [ 96%]\n"
        "tests/test_key_management.py::test_wrong_private_key_password_rejected PASSED         [100%]\n\n"
        "============================= 25 passed in 0.98s =============================="
    )
    add_code_block(doc, test_log_txt)

    add_sub_heading("12.2 User Interface Outputs")
    add_bullet("Home Page: Visual workflow diagrams, algorithm specs, and student disclaimer.")
    add_bullet("Key Management Page: PEM download buttons for public_key.pem and PKCS#8 encrypted private_key.pem.")
    add_bullet("Encryption Page: Status alert, metrics (Original Size, Package Size, Elapsed Time in ms), and download button for filename.cvlt.")
    add_bullet("Decryption Page: Authenticated recovery confirmation, original filename, recovered size, and download button.")
    add_bullet("Tamper Rejection Alert: Immediate error on modified ciphertext: '❌ Decryption Failed: Integrity check failed: Authentication tag mismatch.'")

    # ==========================================
    # 13. SS AND DEMONSTRATIONS
    # ==========================================
    add_sec_heading("13. SS and Demonstrations")

    add_sub_heading("13.1 Screenshot Placeholders")
    add_bullet("Figure 1: screenshots/01_home_screen.png — Landing page showing hybrid workflow and algorithm parameters.")
    add_bullet("Figure 2: screenshots/02_encrypt_screen.png — File encryption interface, public key upload, and performance metrics.")
    add_bullet("Figure 3: screenshots/03_decrypt_screen.png — File decryption interface, private key entry, and recovered file download.")
    add_bullet("Figure 4: screenshots/04_tamper_detection.png — AES-GCM authentication failure alert upon unauthorized byte modification.")

    add_sub_heading("13.2 Live Viva Demonstration Protocol")
    add_body(
        "Follow this exact 5-step sequence when demonstrating the application to external examiners:\n\n"
        "1. Step 1 (Key Generation): Navigate to 'Key Management'. Select RSA-2048, check 'Protect Private Key with Password', "
        "enter passphrase 'CollegePass123!', click 'Generate RSA Key Pair', and download both PEM files.\n"
        "2. Step 2 (Encryption): Navigate to 'Encrypt File'. Upload a sample PDF or image, upload 'public_key.pem', click 'Encrypt File Now', "
        "observe execution time (10-40 ms), and download 'document.pdf.cvlt'.\n"
        "3. Step 3 (Nonce Freshness): Click 'Encrypt File Now' again on the same file without changing settings. Open both .cvlt files in Notepad "
        "and show the examiner that the Nonce and Ciphertext strings are completely different.\n"
        "4. Step 4 (Decryption): Navigate to 'Decrypt File'. Upload 'document.pdf.cvlt' and 'private_key.pem', enter passphrase 'CollegePass123!', "
        "click 'Decrypt & Verify File', and open the recovered file to prove exact byte fidelity.\n"
        "5. Step 5 (Tamper Detection): Open 'document.pdf.cvlt' in Notepad, alter a single letter in the ciphertext string, save, and attempt "
        "decryption. Show examiners the immediate 'Authentication tag mismatch' security alert."
    )

    # ==========================================
    # 14. GIT AND LIVE DEMO SUBMISSION
    # ==========================================
    add_sec_heading("14. Git and Live Demo Submission")

    add_sub_heading("14.1 Git Repository Organization")
    git_tree = (
        "CipherVault-Lite/\n"
        "|-- app.py                      # Main Streamlit web application\n"
        "|-- requirements.txt            # Python dependencies (streamlit, cryptography, pytest)\n"
        "|-- README.md                   # Project documentation & viva guide\n"
        "|-- .gitignore                  # Ignores keys, virtualenv, and caches\n"
        "|-- crypto_utils/\n"
        "|   |-- __init__.py             # Public module exports\n"
        "|   |-- key_manager.py          # RSA key generation, PEM serialization & loading\n"
        "|   |-- file_format.py          # .cvlt package schema, Base64 & sanitization\n"
        "|   |-- encryption.py           # AES-256-GCM file encryption & RSA-OAEP wrapping\n"
        "|   `-- decryption.py           # RSA unwrapping & authenticated AES-GCM decryption\n"
        "|-- tests/\n"
        "|   |-- test_key_management.py  # RSA key pair tests & password protection\n"
        "|   |-- test_encryption.py      # Encryption tests, nonces, limits & leak checks\n"
        "|   |-- test_decryption.py      # Roundtrip tests (Text, PDF, Images) & bad keys\n"
        "|   `-- test_integrity.py       # AEAD tag tampering & corrupted packages\n"
        "|-- docs/\n"
        "|   `-- project_report.md       # B.Tech academic mini-project report draft\n"
        "`-- screenshots/\n"
        "    `-- .gitkeep"
    )
    add_code_block(doc, git_tree)

    add_sub_heading("14.2 Git Commands for Submission")
    git_cmds = (
        "# 1. Initialize git repository\n"
        "git init\n\n"
        "# 2. Stage files (sensitive keys and virtualenv are excluded via .gitignore)\n"
        "git add .\n\n"
        "# 3. Commit codebase\n"
        'git commit -m "feat: complete CipherVault Lite hybrid cryptosystem with 25 passing tests"\n\n'
        "# 4. Link remote GitHub repository\n"
        "git remote add origin https://github.com/<your-username>/ciphervault-lite.git\n"
        "git branch -M main\n\n"
        "# 5. Push project to remote\n"
        "git push -u origin main"
    )
    add_code_block(doc, git_cmds)

    add_sub_heading("14.3 Viva Defense Q&A")
    add_bullet(
        "RSA uses modular exponentiation (C = M^e mod n), making it thousands of times slower than symmetric ciphers. "
        "Additionally, under RSA-OAEP with SHA-256, an RSA-2048 key is mathematically limited to a maximum payload of 190 bytes.",
        bold_prefix="Q: Why can't we encrypt an entire file directly using RSA? — "
    )
    add_bullet(
        "ECB reveals structural patterns across identical plaintext blocks. CBC provides confidentiality but lacks integrity. "
        "GCM is an AEAD mode that provides both confidentiality and integrity via an authenticated GMAC tag computed over GF(2^128).",
        bold_prefix="Q: Why use AES-256-GCM over AES-CBC or AES-ECB? — "
    )
    add_bullet(
        "Nonce stands for 'Number used ONCE'. It ensures that encrypting the exact same file twice produces completely different "
        "ciphertexts, preventing replay and pattern analysis attacks.",
        bold_prefix="Q: What is the purpose of the 12-byte Nonce in AES-GCM? — "
    )
    add_bullet(
        "The envelope metadata (filename, file size, version) is fed into AES-GCM as Additional Authenticated Data (AAD). "
        "If an attacker alters the metadata in the JSON envelope, the authentication tag validation fails.",
        bold_prefix="Q: How does the system detect metadata tampering? — "
    )

    # ==========================================
    # 15. CONCLUSION
    # ==========================================
    add_sec_heading("15. Conclusion")
    add_body(
        "CipherVault Lite successfully demonstrates a functional, practical hybrid cryptosystem for file security. "
        "By combining AES-256-GCM for fast, authenticated file encryption with RSA-OAEP for asymmetric key encapsulation, "
        "the system eliminates the symmetric key-distribution dilemma while maintaining high throughput and robust tamper resistance."
    )
    add_body(
        "The application was thoroughly verified across 25 automated tests covering roundtrip fidelity for text and binary payloads, "
        "wrong key rejections, path traversal sanitization, and cryptographic tamper detection. Built with clean, maintainable Python code, "
        "industry-standard cryptography primitives, and an intuitive Streamlit interface, CipherVault Lite serves as an ideal "
        "academic mini-project for Bachelor of Technology students in Computer Science and Information Security."
    )

    # Save document
    output_path = r"c:\Users\datta.000\Desktop\rojel ki wife\CipherVault_Lite_Thesis_Report.docx"
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    build_document()
