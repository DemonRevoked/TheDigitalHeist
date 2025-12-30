#!/usr/bin/env bash
set -euo pipefail

KEY_FILE="/work/keys/mob-02.key"
OUT_DIR="/work/challenge-files/mob-02"

echo "[*] MOB-02 builder using KEY_FILE=$KEY_FILE"
echo "[*] MOB-02 builder publishing to OUT_DIR=$OUT_DIR"

test -f "$KEY_FILE"

chmod +x ./gradlew

ok=0
for i in 1 2 3; do
  echo "[*] Gradle build attempt $i/3"
  if ./gradlew :app:assembleDebug --no-daemon -Pmob02ChallengeKeyFile="$KEY_FILE"; then
    ok=1
    break
  fi
  echo "[!] Gradle build failed; retrying in 5s"
  sleep 5
done

test "$ok" = "1"

APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
test -f "$APK_PATH"

mkdir -p "$OUT_DIR"
cp -f "$APK_PATH" "$OUT_DIR/mob-02.apk"
echo "[+] MOB-02 APK published to $OUT_DIR/mob-02.apk"


