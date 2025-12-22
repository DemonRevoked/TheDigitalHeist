#!/usr/bin/env bash
set -euo pipefail

# Configure student SSH user (storyline-friendly)
STUDENT_USER="${STUDENT_USER:-denver}"
STUDENT_PASS="${STUDENT_PASS:-RedCipher@2}"

if ! id "$STUDENT_USER" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$STUDENT_USER"
fi
echo "$STUDENT_USER:$STUDENT_PASS" | chpasswd

# Start sshd
/usr/sbin/sshd

# Prepare Apache content with key and flag
# These files are served by Apache and used by the PHP validation script
APACHE_CONTENT="/var/www/html"
mkdir -p "$APACHE_CONTENT"

# Read key from file or env; no local generation fallback (keys come from host startup.sh).
if [ -n "${CHALLENGE_KEY_FILE:-}" ] && [ -f "$CHALLENGE_KEY_FILE" ]; then
  export CHALLENGE_KEY="$(cat "$CHALLENGE_KEY_FILE")"
elif [ -n "${CHALLENGE_KEY:-}" ]; then
  export CHALLENGE_KEY
else
  echo "CHALLENGE_KEY not provided; set CHALLENGE_KEY or mount CHALLENGE_KEY_FILE." >&2
  exit 1
fi

# Create key file for Apache to serve (PHP reads key from file)
printf '%s' "$CHALLENGE_KEY" > "$APACHE_CONTENT/key.txt"
chmod 644 "$APACHE_CONTENT/key.txt"
chown www-data:www-data "$APACHE_CONTENT/key.txt"
chown www-data:www-data "$APACHE_CONTENT/validate.php"

# Start Apache server on localhost:31337
# Apache with PHP validates timestamp and serves key/flag
/usr/sbin/apache2ctl start

# Verify Apache is running on port 31337
sleep 2
if (command -v ss >/dev/null 2>&1 && ss -tlnp 2>/dev/null | grep -q ":31337") || \
   (command -v netstat >/dev/null 2>&1 && netstat -tlnp 2>/dev/null | grep -q ":31337"); then
    echo "Apache is running on localhost:31337" >&2
else
    echo "Warning: Apache may not be listening on port 31337" >&2
fi

# Move challenge binary into the student home so the user only interacts there.
APP_DIR="/home/${STUDENT_USER}/evidence"
mkdir -p "$APP_DIR"
cp /app/evidence_tool "$APP_DIR/."
chown -R "${STUDENT_USER}:${STUDENT_USER}" "$APP_DIR"
chmod 700 "/home/${STUDENT_USER}"

# Copy compiled binary to shared challenge-files mount so the landing
# page can expose it for direct download without SSH access.
if [ -d "/challenge-files/re-02-evidence-tampering" ]; then
  cp /app/evidence_tool /challenge-files/re-02-evidence-tampering/evidence_tool
  chmod 755 /challenge-files/re-02-evidence-tampering/evidence_tool || true
fi

# Lock down build artifacts so the student user cannot read them.
chmod 700 /app

# DO NOT expose CHALLENGE_KEY to user environment
# Remove any existing key files from user directory
rm -f "/home/${STUDENT_USER}/.evidence_env"
# Remove any bashrc references to prevent key exposure
sed -i '/source ~\/.evidence_env/d' "/home/${STUDENT_USER}/.bashrc" 2>/dev/null || true

# Keep container running (Apache runs in background, SSH handles connections)
# Apache is already started above and verified
while true; do
    # Verify Apache is still running
    if ! pgrep -x apache2 >/dev/null 2>&1; then
        echo "Apache process died, restarting..." >&2
        /usr/sbin/apache2ctl start
        sleep 2
    fi
    sleep 60  # Check every minute
done
