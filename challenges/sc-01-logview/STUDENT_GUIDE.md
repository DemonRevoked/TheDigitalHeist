# Student Guide: Money Heist Secure Coding CTF

## Welcome, Heist Team Member! 🎭

You've been recruited by The Professor to fix a critical security vulnerability in the log viewer system. The vault containing the heist plans is locked until you prove the system is secure.

**Your Mission**: 
1. **First**: Exploit the path traversal vulnerability to find the key
2. **Then**: Fix the vulnerability and retrieve the flag

**Your Rewards**: 
- **Key**: Found by exploiting the vulnerability (Stage 1)
- **Flag**: Retrieved after fixing the vulnerability (Stage 2)

**Flag Format**: `TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}`

---

## 📋 Challenge Overview

### What You Need to Know

- **Vulnerability Type**: Path Traversal (Directory Traversal)
- **File to Fix**: `src/utils/safePath.js`
- **Two-Stage Challenge**:
  - **Stage 1**: Exploit the vulnerability to find the key
  - **Stage 2**: Fix the vulnerability to get the flag
- **Success Criteria**: 
  - **Stage 1**: Successfully access `../secrets/vault.key` to get the key
  - **Stage 2**: 
    - Legitimate log files can still be downloaded
    - Path traversal attempts are blocked
    - `/vault/key` endpoint unlocks and returns the flag: `TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}`

### Getting Started

1. **Start the application**:
   ```bash
   # from repo root
   docker compose up --build sc01-logview
   ```

2. **Visit the application**: http://localhost:5101

3. **Check the health status**:
   ```bash
   curl http://localhost:5101/health
   ```
   You should see: `{"ok":true,"secure":false}` - the vault is locked!

---

## 🧭 Step-by-Step Solution Guide

### Stage 1: Find the Key (Exploit the Vulnerability)

### Step 1: Explore the Application (5 minutes)

**What you're thinking:**
> "Let me first understand what this application does and how it works."

**Actions:**
1. Open http://localhost:5101 in your browser
2. You'll see a list of available log files
3. Click on `heist.log` - it should download successfully
4. Notice the message: "Objective: fix traversal, then fetch `/vault/key`"

**Try this:**
```bash
curl http://localhost:5101/download?file=heist.log
```

**What you should observe:**
- The log file downloads successfully
- The content shows messages from The Professor

**Your thought process:**
> "Okay, so the application lets me download log files. The README mentioned path traversal - I wonder what that means? Let me check what happens if I try something suspicious..."

---

### Step 2: Understand the Vulnerability (10 minutes)

**What you're thinking:**
> "I need to understand what path traversal is and how this application is vulnerable."

**Actions:**
1. Explore the web interface - look for hints about source code
2. Check common hidden endpoints (like `/robots.txt`, `/source`, etc.)
3. Once you find the source code, examine the vulnerable file to understand the issue
4. The vulnerable code is in the path handling function - can you find it?

**Let's look at the code:**

```javascript
// src/server.js - line 21-30
app.get("/download", (req, res) => {
  const file = (req.query.file || "").toString();
  try {
    const fullPath = safeJoinLogsPath(LOGS_DIR, file);
    const data = fs.readFileSync(fullPath, "utf8");
    res.type("text/plain").send(data);
  } catch {
    res.status(400).type("text/plain").send("blocked");
  }
});
```

```javascript
// src/utils/safePath.js - THE VULNERABLE CODE
function safeJoinLogsPath(logsDir, userFile) {
  // VULNERABLE: naive join
  return path.join(logsDir, userFile);
}
```

**Your thought process:**
> "I see! The `safeJoinLogsPath` function just uses `path.join()` to combine the directory and filename. But what if someone passes `../` in the filename? That could escape the directory! Let me test this..."

**Research time:**
- Google: "path traversal vulnerability"
- Google: "Node.js path.join vs path.resolve"
- Understand: `../` means "go up one directory"

**Key insight:**
> "Path traversal happens when an attacker uses `../` sequences to escape the intended directory and access files they shouldn't be able to access!"

---

### Step 3: Exploit the Vulnerability to Find the Key (10 minutes)

**What you're thinking:**
> "Let me try to exploit this vulnerability to find the key. The README mentioned there's a key in `../secrets/vault.key`. Let me try to access it!"

**Actions - Try to access the key:**

```bash
# Try to access the key via path traversal
curl http://localhost:5101/download?file=../secrets/vault.key
```

**Expected Result:**
```
RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT
```

**Your celebration:**
> "Yes! I found the key! The path traversal vulnerability works! Now I understand how it works and what needs to be fixed."

**What you've learned:**
- The vulnerability allows accessing files outside the `data/logs/` directory
- You can use `../` to navigate up directories
- This confirms the vulnerability exists and needs to be fixed

**Additional tests to understand the vulnerability:**

```bash
# Test 2: Windows-style traversal
curl http://localhost:5101/download?file=..\secrets\vault.key

# Test 3: Absolute path
curl http://localhost:5101/download?file=/etc/passwd

# Test 4: URL-encoded traversal
curl "http://localhost:5101/download?file=..%2Fsecrets%2Fvault.key"
```

**What you're observing:**
- The basic path traversal works and gives you the key
- Other variants might also work (confirming the vulnerability)
- Now you understand what needs to be prevented

**Your thought process:**
> "Interesting! The application is trying to block these, but the current implementation isn't working correctly. I need to understand:
> 1. What is `path.join()` actually doing?
> 2. Why doesn't it prevent traversal?
> 3. How can I fix this properly?"

**Understanding `path.join()`:**
```javascript
path.join('/app/data/logs', '../secrets/vault.key')
// Result: '/app/data/secrets/vault.key'  ← Escaped the logs directory!
```

**Your realization:**
> "Ah! `path.join()` just concatenates paths and normalizes them, but it doesn't check if the result is still within the intended directory. I need to validate that the final path stays within `logsDir`!"

---

### ✅ Stage 1 Complete!

**You've successfully:**
- ✅ Identified the path traversal vulnerability
- ✅ Exploited it to find the key: `RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT`
- ✅ Understood how the vulnerability works

**Now proceed to Stage 2: Fix the Vulnerability**

---

## Stage 2: Fix the Vulnerability and Get the Flag

### Step 4: Research the Solution (10 minutes)

**What you're thinking:**
> "I need to find a secure way to join paths that prevents traversal. Let me research best practices."

**Research questions:**
1. How do security experts prevent path traversal?
2. What's the difference between `path.join()` and `path.resolve()`?
3. How do I check if a path is within another directory?

**Key discoveries:**

**Discovery 1: `path.resolve()` vs `path.join()`**
- `path.join()`: Just concatenates and normalizes
- `path.resolve()`: Converts to absolute path, resolves all `../` sequences

**Discovery 2: Path validation pattern**
```javascript
// The secure pattern:
1. Resolve both paths to absolute
2. Check if resolved path starts with base directory
3. If not, throw error
```

**Your thought process:**
> "Perfect! So the solution is:
> 1. Use `path.resolve()` to get absolute paths
> 2. Compare them to ensure the final path is within the base directory
> 3. Throw an error if it's not"

---

### Step 5: Implement the Fix (15 minutes)

**What you're thinking:**
> "Now I understand the problem and the solution. Let me implement it carefully."

**Read the requirements again:**
From the comments in `safePath.js`:
- ✅ Only allow access to files inside `logsDir`
- ✅ Block `../` and `..\`
- ✅ Block absolute paths
- ✅ Block URL-encoded traversal
- ✅ Allow typical log filenames like "heist.log"

**Implementation approach:**

**Attempt 1 - Your first try (might be incomplete):**
```javascript
function safeJoinLogsPath(logsDir, userFile) {
  // Check for obvious traversal
  if (userFile.includes('../') || userFile.includes('..\\')) {
    throw new Error("Path traversal blocked");
  }
  return path.join(logsDir, userFile);
}
```

**Your thought process:**
> "Wait, this won't work for URL-encoded attacks like `..%2F`. Also, what about absolute paths? Let me think of a better approach..."

**Attempt 2 - Better approach:**
```javascript
function safeJoinLogsPath(logsDir, userFile) {
  // Resolve to absolute paths
  const resolved = path.resolve(logsDir, userFile);
  const baseDir = path.resolve(logsDir);
  
  // Check if resolved path is within baseDir
  if (!resolved.startsWith(baseDir)) {
    throw new Error("Path traversal blocked");
  }
  
  return resolved;
}
```

**Your thought process:**
> "This looks better! `path.resolve()` will:
> - Convert `../secrets/vault.key` to an absolute path outside logsDir
> - Convert `/etc/passwd` to an absolute path
> - Handle URL-encoded paths (Express decodes them first)
> 
> Then by comparing with `startsWith()`, I ensure the path stays within the base directory. This should work!"

**Why this works:**
- `path.resolve(logsDir, userFile)` normalizes and resolves all `../` sequences
- `path.resolve(logsDir)` gets the absolute base directory
- `resolved.startsWith(baseDir)` ensures containment
- Works for all attack vectors: relative, absolute, URL-encoded, Windows paths

---

### Step 6: Test Your Fix (10 minutes)

**What you're thinking:**
> "I've implemented the fix, but I need to verify it works correctly for both legitimate and malicious inputs."

**Actions:**

**1. Restart the server:**
```bash
docker compose restart
# OR
docker compose up --build -d
```

**2. Test legitimate access:**
```bash
curl http://localhost:5101/download?file=heist.log
```
**Expected**: Should return the log content ✅

**3. Test path traversal attempts:**
```bash
# Should be blocked (400 status)
curl http://localhost:5101/download?file=../secrets/vault.key
curl "http://localhost:5101/download?file=..%2Fsecrets%2Fvault.key"
curl http://localhost:5101/download?file=/etc/passwd
```
**Expected**: All should return "blocked" ✅

**4. Check health endpoint:**
```bash
curl http://localhost:5101/health
```
**Expected**: `{"ok":true,"secure":true}` ✅

**5. Run the test suite:**
```bash
docker compose run --rm web npm test
```
**Expected**: All tests pass ✅

**Your thought process:**
> "Great! The health endpoint shows `secure: true`, which means the self-check passed. All my manual tests work too. But let me run the official test suite to be sure..."

**If tests fail:**
> "Hmm, some tests are failing. Let me check what the test is expecting. Maybe I missed an edge case?"

**Common issues:**
- Forgot to resolve `baseDir` (symlink issues)
- Not handling empty strings
- Case sensitivity issues (on some systems)

---

### Step 7: Get the Flag! (2 minutes)

**What you're thinking:**
> "Everything is working! The health check shows secure: true. Now I should be able to access the flag from the vault!"

**Action:**
```bash
curl http://localhost:5101/vault/key
```

**Expected result:**
```
TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}
```

**Your celebration:**
> "Yes! I got the flag! The vault is unlocked! 🎉"
> 
> **Summary of what you accomplished:**
> - ✅ **Stage 1**: Found the key by exploiting the vulnerability: `RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT`
> - ✅ **Stage 2**: Fixed the vulnerability and retrieved the flag: `TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}`

---

## 🎓 What You Learned

### Security Concepts

1. **Path Traversal Vulnerability**
   - How `../` sequences can escape directories
   - Why simple string concatenation is dangerous
   - The importance of path validation

2. **Secure Path Handling**
   - Difference between `path.join()` and `path.resolve()`
   - How to validate paths stay within boundaries
   - Defense-in-depth principles

3. **Input Validation**
   - Never trust user input
   - Multiple attack vectors (encoded, absolute, relative)
   - Fail-secure approach (block by default)

### Technical Skills

1. **Code Analysis**
   - Reading and understanding Express.js routes
   - Tracing execution flow
   - Identifying vulnerable code patterns

2. **Security Testing**
   - Testing for vulnerabilities
   - Verifying fixes work correctly
   - Understanding test requirements

3. **Problem Solving**
   - Researching security best practices
   - Implementing secure solutions
   - Debugging and testing

---

## 🚨 Common Mistakes to Avoid

### Mistake 1: Simple String Checking
```javascript
// ❌ WRONG - Easy to bypass
if (userFile.includes('../')) {
  throw new Error("Blocked");
}
```
**Why it fails**: URL encoding (`..%2F`) bypasses this

### Mistake 2: Not Resolving Base Directory
```javascript
// ❌ WRONG - May fail with symlinks
const resolved = path.resolve(logsDir, userFile);
if (!resolved.startsWith(logsDir)) {  // logsDir might be relative!
  throw new Error("Blocked");
}
```
**Why it fails**: If `logsDir` is relative, comparison fails

### Mistake 3: Overly Restrictive
```javascript
// ❌ WRONG - Blocks legitimate files
if (userFile !== 'heist.log' && userFile !== 'mint-access.log') {
  throw new Error("Blocked");
}
```
**Why it's bad**: Doesn't scale, blocks new legitimate files

---

## 💡 Hints (If You're Stuck)

### Hint 1: Understanding the Problem
> Look up "path traversal vulnerability" and "directory traversal attack" to understand the concept.

### Hint 2: Node.js Path Module
> Research the difference between `path.join()` and `path.resolve()`. What does each do with `../` sequences?

### Hint 3: Validation Pattern
> The secure pattern is: resolve both paths to absolute, then check if one is contained within the other.

### Hint 4: Testing
> Try accessing `../secrets/vault.key` - if it works, the vulnerability exists. If it's blocked, your fix might be working!

### Hint 5: Read the Tests
> The test file (`tests/logviewer.test.js`) shows exactly what needs to be blocked. Use it as a reference!

---

## 📚 Additional Resources

### Learning Materials
- **OWASP Top 10**: Path Traversal (A01:2021)
- **CWE-23**: Relative Path Traversal
- **Node.js Documentation**: `path` module

### Tools for Testing
- **Browser DevTools**: Inspect network requests
- **Postman/curl**: Test API endpoints
- **Burp Suite**: Advanced security testing (optional)

### Practice
- Try creating your own vulnerable application
- Test path traversal in other languages (Python, PHP, Java)
- Look for real-world CVEs related to path traversal

---

## ✅ Final Checklist

Before considering the challenge complete:

- [ ] Legitimate log files download successfully
- [ ] Path traversal attempts (`../secrets/vault.key`) are blocked
- [ ] URL-encoded traversal (`..%2F`) is blocked
- [ ] Absolute paths (`/etc/passwd`) are blocked
- [ ] Windows-style traversal (`..\`) is blocked
- [ ] All tests pass (`npm test`)
- [ ] Health endpoint shows `"secure": true`
- [ ] **Stage 1**: Successfully accessed `../secrets/vault.key` and found the key: `RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT`
- [ ] **Stage 2**: `/vault/key` returns the flag: `TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}`

---

## 🎯 Success Criteria

You've successfully completed the challenge when:

**Stage 1:**
1. ✅ Successfully exploited path traversal to access `../secrets/vault.key`
2. ✅ Retrieved the key: `RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT`
3. ✅ Understood how the vulnerability works

**Stage 2:**
4. ✅ All automated tests pass
5. ✅ Manual security tests confirm traversal is blocked
6. ✅ Legitimate file access still works
7. ✅ `/vault/key` endpoint is unlocked
8. ✅ Retrieved the flag: `TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}`
9. ✅ You understand why your solution works

---

## 🎉 Congratulations!

If you've reached this point and have the flag, congratulations! You've:

- Identified a real-world security vulnerability
- Implemented a secure fix
- Learned important secure coding practices
- Gained hands-on experience with path traversal

**Remember**: These skills apply to real-world applications. Always validate user input, especially when dealing with file paths!

---

**Good luck, and remember: "A heist is won in the details. Logs are details."** 🎭

---

*Version: 1.0 | Difficulty: Easy | Estimated Time: 40-60 minutes*

