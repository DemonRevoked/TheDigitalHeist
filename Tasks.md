🧠 THE DIGITAL HEIST — BUILD PLAYBOOK

CTF Style: Jeopardy (custom-built platform)  
Total Challenges: 20  
Flag Format: `TDHCTF{meaningful_string_per_challenge}`
Runtime keying: On `startup.sh`, generate a per-instance key and place it alongside the flag (e.g., `KEY=<nonce>`). Each run produces a new key to authenticate solves per deployment.
Delivery: Each challenge ships as an isolated kit (assets + README + verifier).  
QA: Smoke-test solve flow, verify flag checker, confirm difficulty notes.

---

## Chapter 1 — Entry Phase (Reverse Engineering & Mobile)

### CHALLENGE 1 — RE-01: The Confession App
- Narrative hook: “Well-being” app hides operational logs.
- Build kit: Linux ELF `confession_app`, fake console UI, hardcoded phrase, 5-line README.
- Mechanics: Straight string comparison; no obfuscation.
- Player path: Run → inspect with `strings/ghidra` → recover phrase → submit.
- Validation: Server checks exact phrase; return hint “Network Gateway Identified.”
- Flag: `TDHCTF{confession_gateway_phrase}`
- Difficulty: Easy (Intro RE)

### CHALLENGE 2 — RE-02: Evidence Tampering Tool
- Narrative hook: Cleanup unit rewrites timestamps.
- Build kit: Stripped ELF with timestamp math, obfuscated arithmetic loop, README explaining input/output format.
- Mechanics: Time offset logic; no easy strings; mild anti-debug timing.
- Player path: Decompile → trace time math → derive manipulated timestamp → submit value.
- Validation: Verifier recalculates offset; accepts only correct timestamp.
- Flag: `TDHCTF{tampered_time_offset}`
- Difficulty: Hard (Advanced RE)

### CHALLENGE 3 — MOB-01: Best Friend’s Backup
- Narrative hook: Android cloud backup from an operative.
- Build kit: Android backup directory, SMS SQLite with a deleted thread, metadata files, short README.
- Mechanics: Deleted-record recovery from SQLite.
- Player path: Extract backup → open DB → recover deleted SMS → read network hint → submit.
- Validation: Exact recovered SMS content.
- Flag: `TDHCTF{deleted_sms_gateway_hint}`
- Difficulty: Easy

### CHALLENGE 4 — MOB-02: Fake Safety App
- Narrative hook: “Safety” APK beacons to covert server.
- Build kit: Android APK, hardcoded API endpoint, beacon logic, README with app context.
- Mechanics: APK RE, endpoint discovery; optional light obfuscation of strings.
- Player path: Decompile → locate covert API → submit endpoint URL.
- Validation: URL string match.
- Flag: `TDHCTF{covert_beacon_endpoint}`
- Difficulty: Hard (Mobile RE)

---

## Chapter 2 — Intelligence Gathering (Forensics & Web)

### CHALLENGE 5 — DF-01: The Night Walk Photo
- Narrative hook: Photo reveals more than intended.
- Build kit: JPEG with manipulated EXIF and light-source anomaly.
- Mechanics: EXIF analysis and metadata reconstruction.
- Player path: Extract EXIF → spot hidden unit code/location → submit code.
- Validation: Matches EXIF-derived unit identifier.
- Flag: `TDHCTF{exif_shadow_unit}`
- Difficulty: Medium

### CHALLENGE 6 — DF-02: Burned USB
- Narrative hook: Damaged USB holds a network blueprint.
- Build kit: Corrupted disk image with fragmented files and partial diagram.
- Mechanics: File carving and reassembly.
- Player path: Carve files → rebuild diagram → extract node label.
- Validation: Diagram node identifier.
- Flag: `TDHCTF{carved_network_node}`
- Difficulty: Hard

### CHALLENGE 7 — WEB-01: Memorial Website
- Narrative hook: Public memorial hides policy docs.
- Build kit: Simple web app with hidden directories and deleted HTML.
- Mechanics: Directory brute force; static file discovery.
- Player path: Enumerate paths → read hidden docs → extract key sentence.
- Validation: Exact text fragment.
- Flag: `TDHCTF{hidden_policy_sentence}`
- Difficulty: Easy

### CHALLENGE 8 — WEB-02: Anonymous Tip Portal
- Narrative hook: Whistleblower report buried in DB.
- Build kit: Login form with SQLi/IDOR, seeded database row, README with request format.
- Mechanics: SQL Injection to dump internal report.
- Player path: Craft payload → read report → extract architecture ID.
- Validation: DB architecture ID value.
- Flag: `TDHCTF{whistleblower_architecture_id}`
- Difficulty: Medium

### CHALLENGE 9 — WEB-03: Case Management System
- Narrative hook: Evidence hashes silently replaced.
- Build kit: Auth logic flaw + hash replacement workflow; minimal front-end; README.
- Mechanics: Logic flaw chaining to bypass auth and view hashes.
- Player path: Exploit auth bug → access hash logs → identify tampered entry.
- Validation: Tampered hash value.
- Flag: `TDHCTF{replaced_evidence_hash}`
- Difficulty: Hard

---

## Chapter 3 — Crypto Break-In

### CHALLENGE 10 — CRYPTO-01: Diary Lock
- Narrative hook: Operative diary uses weak cipher.
- Build kit: Encrypted text file, substitution cipher hint, README with flavor text.
- Mechanics: Monoalphabetic substitution; frequency analysis.
- Player path: Analyze frequency → map cipher → decrypt phrase.
- Validation: Decrypted phrase.
- Flag: `TDHCTF{diary_cipher_plaintext}`
- Difficulty: Easy

### CHALLENGE 11 — CRYPTO-02: Encrypted Voice Memo
- Narrative hook: Memo names the chief architect.
- Build kit: AES-encrypted binary blob, known-plaintext structure, sample IV/nonce, README with format.
- Mechanics: Known-plaintext attack / crib dragging.
- Player path: Use known structure → derive key/segment → recover name → submit.
- Validation: Architect name string.
- Flag: `TDHCTF{chief_architect_name}`
- Difficulty: Medium

### CHALLENGE 12 — CRYPTO-03: Police Secure Vault
- Narrative hook: RSA vault with weak padding.
- Build kit: RSA parameters with bad padding, ciphertext, README.
- Mechanics: Padding oracle / low-exponent exploit.
- Player path: Factor/attack → recover master key index → submit.
- Validation: Master key index value.
- Flag: `TDHCTF{master_key_index}`
- Difficulty: Hard

---

## Chapter 4 — System Breach (Network, Secure Coding, Exploitation)

### CHALLENGE 13 — NET-01: Suspicious Network Logs
- Narrative hook: Rogue engineer signals the AI node.
- Build kit: PCAP with repeatable pattern, README describing capture context.
- Mechanics: Traffic pattern analysis; timing or payload signature.
- Player path: Inspect PCAP → isolate pattern → map to engineer ID → submit.
- Validation: Engineer ID string.
- Flag: `TDHCTF{rogue_engineer_signal}`
- Difficulty: Medium

### CHALLENGE 14 — NET-02: Internal Police Network
- Narrative hook: DNS tunnels move AI logs.
- Build kit: DNS tunnel logs/pcap, encoded payload, README.
- Mechanics: Protocol analysis; decode tunneled data.
- Player path: Reassemble tunnel → decode payload → find tunnel key → submit.
- Validation: Tunnel key value.
- Flag: `TDHCTF{dns_tunnel_key}`
- Difficulty: Hard

### CHALLENGE 15 — SC-01: Student Portal Bug
- Narrative hook: Intern portal leaks dev API tokens.
- Build kit: Web form with input validation flaw, seeded messages, README.
- Mechanics: Input sanitization bypass leading to data leak.
- Player path: Trigger leak → read communications → extract API token → submit.
- Validation: API token string.
- Flag: `TDHCTF{leaked_dev_api_token}`
- Difficulty: Easy

### CHALLENGE 16 — SC-02: Evidence Upload Script
- Narrative hook: File upload silently overwrites evidence.
- Build kit: Backend upload service with overwrite bug, sample files, README.
- Mechanics: Overwrite logic to replace stored evidence.
- Player path: Abuse upload → replace file → retrieve decoy hash → submit.
- Validation: Decoy hash value.
- Flag: `TDHCTF{decoy_evidence_hash}`
- Difficulty: Medium

### CHALLENGE 17 — EXP-01: Locked Laptop
- Narrative hook: Compromised laptop guards AI training creds.
- Build kit: Linux VM snapshot, privesc vector (e.g., SUID misconfig), README with access instructions.
- Mechanics: Local privilege escalation.
- Player path: Enumerate → exploit privesc → read local creds file → submit.
- Validation: Credential string.
- Flag: `TDHCTF{training_env_creds}`
- Difficulty: Medium

### CHALLENGE 18 — EXP-02: Police Server Root
- Narrative hook: Central server = final vault.
- Build kit: Hardened VM, chained exploit path (e.g., web→ssh→kernel), README with entrypoint.
- Mechanics: Multi-step exploitation, privilege escalation.
- Player path: Gain foothold → chain exploit → root → capture proof.
- Validation: Root proof token in `/root/proof.txt`.
- Flag: `TDHCTF{root_server_proof}`
- Difficulty: Hard

---

## Chapter 5 — The AI Twist (ML/Detection)

### CHALLENGE 19 — AI-01: Fake Chat Analysis
- Narrative hook: AI impersonates field officers.
- Build kit: Chat log corpus with stylometric patterns, README describing chat context.
- Mechanics: Pattern/ML-lite anomaly detection (simple stats acceptable).
- Player path: Analyze style shifts → identify AI marker phrase → submit marker.
- Validation: Marker phrase.
- Flag: `TDHCTF{ai_marker_phrase}`
- Difficulty: Easy

### CHALLENGE 20 — AI-02: Deepfake Audio
- Narrative hook: Deepfake audio misleads command structure.
- Build kit: Multiple WAV/OGG clips, subtle artifacts, README with scenario.
- Mechanics: Audio forensics (FFT/noise floor/phasing) to spot generated clip.
- Player path: Inspect spectra → find manipulated signature → submit signature token.
- Validation: Manipulation signature string.
- Flag: `TDHCTF{deepfake_audio_signature}`
- Difficulty: Hard