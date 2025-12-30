#!/usr/bin/env bash
set -euo pipefail

# Builds the MOB-02 APK inside Docker (no host Java/Android SDK needed)
# and publishes it into ./challenge-files so the landing server can serve it.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

KEY_FILE_HOST="$REPO_ROOT/keys/mob-02.key"
OUT_DIR_HOST="$REPO_ROOT/challenge-files/mob-02-reset-token-forgery"

if ! command -v docker >/dev/null 2>&1; then
  echo "[!] docker not found"
  exit 1
fi

DOCKER_BIN="docker"
if ! docker info >/dev/null 2>&1; then
  if command -v sudo >/dev/null 2>&1 && sudo -n docker info >/dev/null 2>&1; then
    DOCKER_BIN="sudo docker"
  else
    echo "[!] Docker is installed but not accessible (cannot talk to /var/run/docker.sock)."
    echo "    Fix options:"
    echo "    - Run this script with sudo, or"
    echo "    - Add your user to the docker group and re-login:"
    echo "        sudo usermod -aG docker \"$USER\""
    exit 1
  fi
fi

if [ ! -f "$KEY_FILE_HOST" ]; then
  echo "[!] Missing key file: $KEY_FILE_HOST"
  echo "    Run: $REPO_ROOT/startup.sh  (it generates keys/mob-02.key)"
  exit 1
fi

mkdir -p "$OUT_DIR_HOST"

# Use a ready Android SDK image (includes Java + SDK).
ANDROID_IMAGE="${ANDROID_IMAGE:-ghcr.io/cirruslabs/android-sdk:35}"

echo "[*] Docker image: $ANDROID_IMAGE"
echo "[*] Building MOB-02 APK with injected key from: $KEY_FILE_HOST"
echo "[*] Publishing to: $OUT_DIR_HOST/mob-02.apk"

${DOCKER_BIN} run --rm \
  -v "$REPO_ROOT:/work:rw" \
  -w "/work/challenges/mob-02-reset-token-forgery" \
  "$ANDROID_IMAGE" \
  bash -lc '
    set -euo pipefail
    KEY_FILE="/work/keys/mob-02.key"
    OUT_DIR="/work/challenge-files/mob-02-reset-token-forgery"

    if [ ! -f "$KEY_FILE" ]; then
      echo "[!] Missing key file in container: $KEY_FILE" >&2
      exit 1
    fi

    chmod +x ./gradlew

    ./gradlew :app:assembleDebug -Pmob02ChallengeKeyFile="$KEY_FILE"

    APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
    if [ ! -f "$APK_PATH" ]; then
      echo "[!] APK not found at: $APK_PATH" >&2
      exit 1
    fi

    mkdir -p "$OUT_DIR"
    cp -f "$APK_PATH" "$OUT_DIR/mob-02.apk"
    echo "[+] Published APK: $OUT_DIR/mob-02.apk"
  '


