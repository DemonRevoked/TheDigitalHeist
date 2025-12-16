#!/usr/bin/env bash
set -euo pipefail

# Configure student SSH user (storyline-friendly)
STUDENT_USER="${STUDENT_USER:-rio}"
STUDENT_PASS="${STUDENT_PASS:-RedCipher@1}"

if ! id "$STUDENT_USER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$STUDENT_USER"
fi
echo "$STUDENT_USER:$STUDENT_PASS" | chpasswd

# Start sshd
/usr/sbin/sshd

# Move challenge binary into the student home so the user only interacts there.
APP_DIR="/home/${STUDENT_USER}/confession"
mkdir -p "$APP_DIR"
cp /app/confession_app "$APP_DIR/."
chown -R "${STUDENT_USER}:${STUDENT_USER}" "$APP_DIR"
chmod 700 "/home/${STUDENT_USER}"

# Lock down build artifacts so the student user cannot read them.
chmod 700 /app

# Read key from file or env; no local generation fallback (keys come from host startup.sh).
if [ -n "${CHALLENGE_KEY_FILE:-}" ] && [ -f "$CHALLENGE_KEY_FILE" ]; then
  export CHALLENGE_KEY="$(cat "$CHALLENGE_KEY_FILE")"
elif [ -n "${CHALLENGE_KEY:-}" ]; then
  export CHALLENGE_KEY
else
  echo "CHALLENGE_KEY not provided; set CHALLENGE_KEY or mount CHALLENGE_KEY_FILE." >&2
  exit 1
fi

# Persist the key for the student session so re-running works without passing env.
KEY_ENV_FILE="/home/${STUDENT_USER}/.confession_env"
echo "export CHALLENGE_KEY='${CHALLENGE_KEY}'" > "$KEY_ENV_FILE"
chown "${STUDENT_USER}:${STUDENT_USER}" "$KEY_ENV_FILE"
chmod 600 "$KEY_ENV_FILE"

# Ensure the key is loaded in interactive shells.
if ! grep -q "source ~/.confession_env" "/home/${STUDENT_USER}/.bashrc"; then
  echo "source ~/.confession_env" >> "/home/${STUDENT_USER}/.bashrc"
fi

# Drop privileges and run from the student's home directory.
su -s /bin/bash -c "cd '$APP_DIR' && env CHALLENGE_KEY='$CHALLENGE_KEY' ./confession_app" "$STUDENT_USER"
