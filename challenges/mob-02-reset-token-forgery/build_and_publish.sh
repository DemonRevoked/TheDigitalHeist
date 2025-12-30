#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

KEY_FILE="$REPO_ROOT/keys/mob-02.key"
OUT_DIR="$REPO_ROOT/challenge-files/mob-02-reset-token-forgery"

if [ ! -f "$KEY_FILE" ]; then
  echo "[!] Missing key file: $KEY_FILE"
  echo "    Run: $REPO_ROOT/startup.sh  (it generates keys/mob-02.key)"
  exit 1
fi

MOB02_KEY="$(tr -d '\r\n' < "$KEY_FILE")"
if [ -z "$MOB02_KEY" ]; then
  echo "[!] Key file is empty: $KEY_FILE"
  exit 1
fi

mkdir -p "$OUT_DIR"

echo "[*] Building APK with injected MOB-02 challenge key from: $KEY_FILE"
echo "[*] Output directory: $OUT_DIR"
if ! command -v java >/dev/null 2>&1; then
  echo "[!] Java not found. Install Java 17+ and set JAVA_HOME (or ensure 'java' is on PATH)."
  echo "    Example (Ubuntu): sudo apt-get update && sudo apt-get install -y openjdk-17-jdk"
  exit 1
fi

cd "$SCRIPT_DIR"
chmod +x ./gradlew

./gradlew :app:assembleDebug \
  -Pmob02ChallengeKeyFile="$KEY_FILE"

APK_PATH="$SCRIPT_DIR/app/build/outputs/apk/debug/app-debug.apk"
if [ ! -f "$APK_PATH" ]; then
  echo "[!] Build succeeded but APK not found at: $APK_PATH"
  exit 1
fi

cp -f "$APK_PATH" "$OUT_DIR/mob-02.apk"
echo "[+] Published: $OUT_DIR/mob-02.apk"


