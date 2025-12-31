#!/bin/bash
set -e

# ============================================
# Configuration - SSH User Credentials
# ============================================
SSH_USERNAME="ctfadmin"
SSH_PASSWORD="CreatorOfUpsideDown2025!"
SSH_PORT="22"

# ============================================
# Configuration - Key Encryption (AES-128-CBC)
# ============================================
# NOTE: AES-128 requires a 16-byte key and 16-byte IV.
# These values are 16 ASCII chars each (16 bytes).
SECRET_KEY="initvector123456"
IV="passwordpassword"

# ============================================
# Task 1: Install Dependencies
# ============================================
install_dependencies() {
  echo "[*] Updating system packages..."
  sudo apt update -y
  # openssl + xxd (vim-common) are required for key encryption
  sudo apt install -y git curl ca-certificates gnupg lsb-release openssh-server openssl vim-common

  echo "[*] Installing Docker..."
  # Add Docker GPG key if not already present
  if [ ! -f /usr/share/keyrings/docker.gpg ]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker.gpg
  fi

  # Add Docker repository if not already present
  if [ ! -f /etc/apt/sources.list.d/docker.list ]; then
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
  fi

  sudo apt update -y
  sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

  echo "[+] Dependencies installed successfully!"
}

# ============================================
# Task 2.5: Ensure Docker Daemon Running
# ============================================
ensure_docker_running() {
  echo "[*] Ensuring Docker daemon is running..."
  if systemctl is-active --quiet docker; then
    echo "[*] Docker is already active."
    return
  fi

  sudo systemctl start docker || {
    echo "[!] Failed to start docker service. Please check system logs." >&2
    exit 1
  }

  sudo systemctl enable docker >/dev/null 2>&1 || true

  if systemctl is-active --quiet docker; then
    echo "[+] Docker started successfully."
  else
    echo "[!] Docker is not active after start attempt." >&2
    exit 1
  fi
}

# ============================================
# Task 2: Setup SSH and Create User
# ============================================
setup_ssh_user() {
  echo "[*] Setting up SSH and creating user..."

  # Create user if it doesn't exist
  if ! id "$SSH_USERNAME" &>/dev/null; then
    sudo useradd -m -s /bin/bash "$SSH_USERNAME"
    echo "[+] User '$SSH_USERNAME' created."
  else
    echo "[*] User '$SSH_USERNAME' already exists."
  fi

  # Set the password for the user
  echo "$SSH_USERNAME:$SSH_PASSWORD" | sudo chpasswd
  echo "[+] Password set for user '$SSH_USERNAME'."

  # Ensure SSH service is enabled and running
  sudo systemctl enable ssh
  sudo systemctl start ssh

  # Configure SSH to allow password authentication
  sudo sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
  sudo sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

  # Ensure SSH listens on desired port
  sudo sed -i "s/^#Port .*/Port $SSH_PORT/" /etc/ssh/sshd_config
  sudo sed -i "s/^Port .*/Port $SSH_PORT/" /etc/ssh/sshd_config
  if ! grep -q "^Port $SSH_PORT" /etc/ssh/sshd_config; then
    echo "Port $SSH_PORT" | sudo tee -a /etc/ssh/sshd_config >/dev/null
  fi

  # Restart SSH to apply changes
  sudo systemctl restart ssh

  echo "[+] SSH configured on port $SSH_PORT with password authentication enabled."
  echo "[+] Access credentials:"
  echo "    Username: $SSH_USERNAME"
  echo "    Password: $SSH_PASSWORD"
}

# ============================================
# Task 3: Generate Keys (per-challenge)
# ============================================
generate_key() {
  local static1=$1
  local static2=$2
  local rand1=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)
  local rand2=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)
  # 32-character key: Static(8) + Random(8) + Random(8) + Static(8)
  # This is intentionally 32 bytes so AES-128-CBC -nopad can encrypt without padding.
  echo "${static1}${rand1}${rand2}${static2}"
}

# Encrypt key using AES-128-CBC with no padding and return hex string (no newlines)
encrypt_key() {
  local plaintext="$1"

  # AES-128 expects 16-byte key and 16-byte IV (32 hex chars each).
  # If SECRET_KEY/IV are longer, OpenSSL ignores the excess; we truncate to avoid warnings.
  local key_hex
  local iv_hex
  key_hex="$(printf "%s" "$SECRET_KEY" | xxd -p | tr -d '\n' | cut -c1-32)"
  iv_hex="$(printf "%s" "$IV" | xxd -p | tr -d '\n' | cut -c1-32)"

  printf "%s" "$plaintext" | openssl enc -aes-128-cbc \
    -K "$key_hex" \
    -iv "$iv_hex" \
    -nopad | xxd -p | tr -d '\n'
}

generate_all_keys() {
  echo "[*] Generating per-challenge keys..."

  mkdir -p "$KEY_DIR"
  
  # Ensure challenge-files directories exist for file-based challenges
  CHALLENGE_FILES_DIR="$SCRIPT_DIR/challenge-files"
  mkdir -p "$CHALLENGE_FILES_DIR/crypto-01-intercepted-comms"
  mkdir -p "$CHALLENGE_FILES_DIR/crypto-02-vault-breach"
  mkdir -p "$CHALLENGE_FILES_DIR/crypto-03-quantum-safe"
  mkdir -p "$CHALLENGE_FILES_DIR/df-01-night-walk-photo"
  mkdir -p "$CHALLENGE_FILES_DIR/df-02-burned-usb"
  mkdir -p "$CHALLENGE_FILES_DIR/net-01-onion-pcap"
  mkdir -p "$CHALLENGE_FILES_DIR/net-02-doh-rhythm"
  # MOB-01 (APK download) uses slug folder "mob-01" so the landing page can attach files to the existing mob-01 card.
  mkdir -p "$CHALLENGE_FILES_DIR/mob-01"
  # MOB-02 (APK download) uses slug folder "mob-02" so the landing page can attach files to the existing mob-02 card.
  rm -rf "$CHALLENGE_FILES_DIR/mob-02-reset-token-forgery" >/dev/null 2>&1 || true
  mkdir -p "$CHALLENGE_FILES_DIR/mob-02"
  echo "[+] Challenge file directories created"

  # Generate plaintext keys (32 chars) first so we can keep a backup before encrypting.
  pkey1=$(generate_key "Pz1aQw9L" "nE7rVb5C")    # RE-01
  pkey2=$(generate_key "Dx4kHt2M" "yL6uFp8S")    # RE-02
  pkey3=$(generate_key "Jc7mRz3T" "qN5vGd1X")    # MOB-01
  pkey4=$(generate_key "Sb2pLk6W" "tH9eCx4U")    # MOB-02
  pkey5=$(generate_key "Ve8nYs1Q" "mR3jAa7D")    # DF-01
  pkey6=$(generate_key "Lf5tPg9B" "zK2cWx8N")    # DF-02
  pkey7=$(generate_key "Qr4vJm2Z" "pS6bHd5F")    # WEB-01
  pkey8=$(generate_key "Mx9eUc4A" "gT1nVy7P")    # WEB-02
  pkey9=$(generate_key "Ha3sDl5R" "wQ8kBn2C")    # WEB-03
  pkey10=$(generate_key "Nk6yFo1E" "rJ4vGz9T")   # CRYPTO-01
  pkey11=$(generate_key "Cp8tMe2H" "uL5qRx7V")   # CRYPTO-02
  pkey12=$(generate_key "Zs7dWc3B" "yF9nPa6M")   # CRYPTO-03
  pkey13=$(generate_key "Tb1vKx8Q" "oD4mJg5L")   # NET-01 (Onion PCAP)
  pkey14=$(generate_key "Ry2hLp9S" "cN6tVf3A")   # NET-02 (DoH Rhythm)
  pkey15=$(generate_key "Uw5qGd7X" "iB2lZc8R")   # SC-01
  pkey16=$(generate_key "Gj3nSa6Y" "tE9pQk4M")   # SC-02
  pkey17=$(generate_key "Pa4mHv1Z" "sC8xLn5J")   # EXP-01
  pkey18=$(generate_key "Xe6bJr2U" "hV7dMf9P")   # EXP-02
  pkey19=$(generate_key "Ko9tQw4D" "lS1pRg3N")   # AI-01
  pkey20=$(generate_key "Lr2yNc5F" "dA7mVh8K")   # AI-02

  # Encrypt keys (hex) for use by the containers.
  key1=$(encrypt_key "$pkey1")
  key2=$(encrypt_key "$pkey2")
  key3=$(encrypt_key "$pkey3")
  key4=$(encrypt_key "$pkey4")
  key5=$(encrypt_key "$pkey5")
  key6=$(encrypt_key "$pkey6")
  key7=$(encrypt_key "$pkey7")
  key8=$(encrypt_key "$pkey8")
  key9=$(encrypt_key "$pkey9")
  key10=$(encrypt_key "$pkey10")
  key11=$(encrypt_key "$pkey11")
  key12=$(encrypt_key "$pkey12")
  key13=$(encrypt_key "$pkey13")
  key14=$(encrypt_key "$pkey14")
  key15=$(encrypt_key "$pkey15")
  key16=$(encrypt_key "$pkey16")
  key17=$(encrypt_key "$pkey17")
  key18=$(encrypt_key "$pkey18")
  key19=$(encrypt_key "$pkey19")
  key20=$(encrypt_key "$pkey20")

  # Backup / comparison file for development: plaintext + encrypted side-by-side.
  # Format: TSV with header columns: CHALLENGE, PLAINTEXT, ENCRYPTED_HEX
  # Lock it down to the current user by default.
  (
    umask 077
    cat > "$KEY_DIR/keys.txt" << EOF
CHALLENGE       PLAINTEXT       ENCRYPTED_HEX
RE-01   $pkey1  $key1
RE-02   $pkey2  $key2
MOB-01  $pkey3  $key3
MOB-02  $pkey4  $key4
DF-01   $pkey5  $key5
DF-02   $pkey6  $key6
WEB-01  $pkey7  $key7
WEB-02  $pkey8  $key8
WEB-03  $pkey9  $key9
CRYPTO-01       $pkey10 $key10
CRYPTO-02       $pkey11 $key11
CRYPTO-03       $pkey12 $key12
NET-01  $pkey13 $key13
NET-02  $pkey14 $key14
SC-01   $pkey15 $key15
SC-02   $pkey16 $key16
EXP-01  $pkey17 $key17
EXP-02  $pkey18 $key18
AI-01   $pkey19 $key19
AI-02   $pkey20 $key20
EOF
  )
  chmod 600 "$KEY_DIR/keys.txt" 2>/dev/null || true

  # Write keys to well-known paths for container mounts
  echo "$key1"  > "$KEY_DIR/re-01.key"
  echo "$key2"  > "$KEY_DIR/re-02.key"
  echo "$key3"  > "$KEY_DIR/mob-01.key"
  echo "$key4"  > "$KEY_DIR/mob-02.key"
  # Keep backward-compatible names AND slug-based names for file generators.
  echo "$key5"  > "$KEY_DIR/df-01.key"
  echo "$key5"  > "$KEY_DIR/df-01-night-walk-photo.key"
  echo "$key6"  > "$KEY_DIR/df-02.key"
  echo "$key6"  > "$KEY_DIR/df-02-burned-usb.key"
  echo "$key7"  > "$KEY_DIR/web-01.key"
  echo "$key8"  > "$KEY_DIR/web-02.key"
  echo "$key9"  > "$KEY_DIR/web-03.key"
  echo "$key10" > "$KEY_DIR/crypto-01.key"
  echo "$key11" > "$KEY_DIR/crypto-02.key"
  echo "$key12" > "$KEY_DIR/crypto-03.key"
  # Keep backward-compatible names AND new slug-based names (used by the generators).
  echo "$key13" > "$KEY_DIR/net-01.key"
  echo "$key13" > "$KEY_DIR/net-01-onion-pcap.key"
  echo "$key14" > "$KEY_DIR/net-02.key"
  echo "$key14" > "$KEY_DIR/net-02-doh-rhythm.key"
  echo "$key15" > "$KEY_DIR/sc-01.key"
  echo "$key16" > "$KEY_DIR/sc-02.key"
  echo "$key17" > "$KEY_DIR/exp-01.key"
  echo "$key18" > "$KEY_DIR/exp-02.key"
  echo "$key19" > "$KEY_DIR/ai-01.key"
  echo "$key20" > "$KEY_DIR/ai-02.key"

  echo "[+] Key comparison table (plaintext + encrypted) saved to: $KEY_DIR/keys.txt"
  echo "[+] 20 keys generated, encrypted (AES-128-CBC), and saved under $KEY_DIR/*.key"

  # Write a repo-root .env so docker-compose.yml variable interpolation works even when
  # running `sudo docker compose ...` later (sudo typically does not preserve exported vars).
  # This prevents failures like:
  #   required variable EXP01_KEY is missing a value
  ENV_FILE="$SCRIPT_DIR/.env"
  (
    umask 077
    cat > "$ENV_FILE" << EOF
# Auto-generated by startup.sh on $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# Used by docker-compose.yml for interpolation (including docker compose down).
RE01_KEY=$(tr -d '\n\r' < "$KEY_DIR/re-01.key")
RE02_KEY=$(tr -d '\n\r' < "$KEY_DIR/re-02.key")
EXP01_KEY=$(tr -d '\n\r' < "$KEY_DIR/exp-01.key")
EXP02_KEY=$(tr -d '\n\r' < "$KEY_DIR/exp-02.key")
# Optional flags (can be overridden by editing this file)
EXP01_FLAG=${EXP01_FLAG:-TDHCTF{berlins_locker_compromised}}
EXP02_FLAG=${EXP02_FLAG:-TDHCTF{PIVOTED_THEN_ROOTED_BY_CRON}}
EOF
  )
  echo "[+] Wrote docker compose env file: $ENV_FILE"

  # Generate offline network challenge artifacts (PCAPs) so they are downloadable from the landing page.
  # IMPORTANT: this must run AFTER keys are written so KEY:<...> is embedded into the PCAP each startup.
  # Pure python; no external deps.
  if command -v python3 >/dev/null 2>&1; then
    echo "[*] Generating NET challenge artifacts (embedding per-startup keys)..."
    python3 "$SCRIPT_DIR/challenges/net-01-onion-pcap/src/generate_pcap.py" >/dev/null 2>&1 || echo "[!] NET-01 PCAP generation failed (continuing)"
    python3 "$SCRIPT_DIR/challenges/net-02-doh-rhythm/src/generate_pcap.py" >/dev/null 2>&1 || echo "[!] NET-02 PCAP generation failed (continuing)"
    echo "[+] NET challenge artifact generation step complete"

    echo "[*] Generating DF challenge artifacts (embedding per-startup keys)..."
    python3 "$SCRIPT_DIR/challenges/df-01-night-walk-photo/src/generate_photo.py" >/dev/null 2>&1 || echo "[!] DF-01 photo generation failed (continuing)"
    python3 "$SCRIPT_DIR/challenges/df-02-burned-usb/src/generate_usb_image.py" >/dev/null 2>&1 || echo "[!] DF-02 USB image generation failed (continuing)"
    echo "[+] DF challenge artifact generation step complete"
  else
    echo "[!] python3 not found; skipping NET artifact generation"
  fi

  # MOB-02 APK build is executed via docker-compose service `mob02-apkbuilder`
  # when containers are started (Task 4). This ensures each startup embeds
  # the freshly generated key from ./keys/mob-02.key into the APK.
}

# ============================================
# Task 4: Start Docker Containers
# ============================================
start_containers() {
  echo "[*] Starting Docker containers..."
  if command -v docker-compose >/dev/null 2>&1; then
    dc="docker-compose"
  else
    dc="docker compose"
  fi
  $dc -f "$SCRIPT_DIR/docker-compose.yml" down 2>/dev/null || true
  
  # Read keys and export as environment variables for docker-compose build args
  # These will be embedded into the binaries at compile time
  if [ -f "$KEY_DIR/re-01.key" ]; then
    export RE01_KEY="$(cat "$KEY_DIR/re-01.key" | tr -d '\n\r')"
  fi
  if [ -f "$KEY_DIR/re-02.key" ]; then
    export RE02_KEY="$(cat "$KEY_DIR/re-02.key" | tr -d '\n\r')"
  fi
  # NOTE: Web challenges read keys from mounted key files at runtime (CHALLENGE_KEY_FILE).
  # We intentionally do NOT export key values into the environment here.
  # Expose exp challenge keys to docker-compose dynamically (read from files each run)
  if [ -f "$KEY_DIR/exp-01.key" ]; then
    export EXP01_KEY="$(cat "$KEY_DIR/exp-01.key" | tr -d '\n\r')"
  fi
  if [ -f "$KEY_DIR/exp-02.key" ]; then
    export EXP02_KEY="$(cat "$KEY_DIR/exp-02.key" | tr -d '\n\r')"
  fi
  # Expose exp challenge flags (allow override via environment).
  export EXP01_FLAG="${EXP01_FLAG:-TDHCTF{berlins_locker_compromised}}"
  export EXP02_FLAG="${EXP02_FLAG:-TDHCTF{PIVOTED_THEN_ROOTED_BY_CRON}}"
  
  # Build offline APK artifacts (MOB-02) so they are downloadable from the landing page.
  # IMPORTANT: must run AFTER keys are written so the per-startup key is embedded into the APK.
  echo "[*] Building MOB-02 APK artifact (docker compose one-shot)..."
  if ! $dc -f "$SCRIPT_DIR/docker-compose.yml" --profile artifacts run --rm mob02-apkbuilder; then
    echo "[!] MOB-02 APK build failed; aborting startup to avoid incomplete deployment."
    exit 1
  fi

  echo "[*] Building MOB-01 APK artifact (docker compose one-shot)..."
  if ! $dc -f "$SCRIPT_DIR/docker-compose.yml" --profile artifacts run --rm mob01-apkbuilder; then
    echo "[!] MOB-01 APK build failed; aborting startup to avoid incomplete deployment."
    exit 1
  fi

  $dc -f "$SCRIPT_DIR/docker-compose.yml" up --build -d
  echo "[+] Docker containers started!"
}

# ============================================
# Main Execution
# ============================================
main() {
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  KEY_DIR="$SCRIPT_DIR/keys"

  echo "=========================================="
  echo "  The Digital Heist Setup Script"
  echo "=========================================="

  #install_dependencies          # disabled for dev env
  #setup_ssh_user                # disabled for dev env
  #ensure_docker_running         # assume docker is already running in dev
  generate_all_keys
  start_containers

  echo ""
  echo "=========================================="
  echo "  Setup Complete!"
  echo "=========================================="
  echo ""
}

main
