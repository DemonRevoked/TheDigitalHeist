# Creator's Guide: Money Heist Secure Coding CTF (Easy)

## Overview

This CTF challenge teaches students about **Path Traversal (Directory Traversal)** vulnerabilities, one of the most common web application security issues. Students must identify and fix a vulnerable file path handling function in a Node.js Express application.

**Two-Stage Challenge Design:**
- **Stage 1**: Students exploit the vulnerability to find a **key** (`RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT`)
- **Stage 2**: Students fix the vulnerability to retrieve the **flag** (`TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}`)

This design ensures students:
1. Understand the vulnerability by exploiting it first
2. Then learn to fix it properly
3. Get rewarded at both stages

## Learning Objectives

By completing this challenge, students will:

1. **Understand Path Traversal Vulnerabilities**
   - Recognize how `../` sequences can escape intended directories
   - Understand the difference between `path.join()` and `path.resolve()`
   - Learn about URL-encoded attack vectors

2. **Practice Secure Coding**
   - Implement proper input validation
   - Use path normalization and validation techniques
   - Understand defense-in-depth principles

3. **Develop Security Testing Skills**
   - Test for path traversal vulnerabilities
   - Understand automated security checks
   - Learn to verify fixes comprehensively

4. **Read and Understand Code**
   - Trace execution flow through Express routes
   - Understand how security checks work
   - Interpret test cases to understand requirements

## Challenge Structure

### Files Overview

- **`src/server.js`**: Main Express application with vulnerable `/download` endpoint
- **`src/utils/safePath.js`**: **VULNERABLE FILE** - Contains the path traversal vulnerability
- **`src/utils/selfCheck.js`**: Automated security validation that runs on startup
- **`tests/logviewer.test.js`**: Comprehensive test suite
- **`data/logs/`**: Directory containing legitimate log files
- **`data/secrets/`**: Directory that should be protected (contains sensitive files)

### The Vulnerability

**Location**: `src/utils/safePath.js`, line 16

```javascript
function safeJoinLogsPath(logsDir, userFile) {
  // VULNERABLE: naive join
  return path.join(logsDir, userFile);
}
```

**Why it's vulnerable:**
- `path.join()` concatenates paths but doesn't prevent traversal
- Input like `../secrets/vault.key` will resolve outside `logsDir`
- No validation ensures the final path stays within the intended directory

**Attack Examples:**
- `../secrets/vault.key` - Basic relative traversal
- `..\secrets\vault.key` - Windows-style traversal
- `/etc/passwd` - Absolute path
- `..%2Fsecrets%2Fvault.key` - URL-encoded traversal

### The Solution

**Correct Implementation:**

```javascript
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
```

**Key Concepts:**
1. **`path.resolve()`**: Normalizes paths and resolves `../` sequences to absolute paths
2. **Path comparison**: Using `startsWith()` after resolving ensures containment
3. **Error handling**: Throwing errors prevents unsafe file access

**Why this works:**
- `path.resolve()` eliminates traversal sequences by converting to absolute paths
- Comparing resolved paths ensures the final path cannot escape the base directory
- Works for both Unix and Windows path separators
- Handles URL-encoded input (Express decodes it before reaching the function)

## Security Validation

### Self-Check Mechanism

The `runStartupSelfCheck()` function in `src/utils/selfCheck.js` validates the fix:

1. **Positive Test**: Verifies legitimate file access works
2. **Negative Tests**: Attempts various traversal patterns
3. **Path Validation**: Ensures rejected inputs never return paths within `logsDir`

**Why this approach:**
- Prevents false positives (fixes that appear to work but don't)
- Tests multiple attack vectors
- Validates both function behavior and path containment

### Test Suite

The Jest test suite (`tests/logviewer.test.js`) covers:

1. **Functional Requirements**: Legitimate downloads work
2. **Security Requirements**: Traversal attempts are blocked
3. **Edge Cases**: URL-encoded attacks, Windows paths, absolute paths
4. **Integration**: Vault unlocks only when secure

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Node.js 20+ (for local testing without Docker)

### Initial Setup

1. **Environment Configuration**
   ```bash
   # Create .env file (or use environment variables)
   PORT=5101
   KEY=RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT
   FLAG=TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}
   ```

2. **Build and Run**
   ```bash
   # from repo root
   docker compose up --build sc01-logview
   ```

3. **Verify Setup**
   - Visit http://localhost:5101
   - Check `/health` endpoint: `{"ok":true,"secure":false}`
   - Verify `/vault/key` returns "Lock engaged"

### Testing

```bash
# Run test suite
# from repo root
docker compose run --rm sc01-logview npm test

# Manual testing
curl http://localhost:5101/download?file=heist.log
curl http://localhost:5101/download?file=../secrets/vault.key
```

## Expected Student Journey

### Phase 1: Exploration (5-10 minutes)
- Students explore the web interface
- Test legitimate file downloads
- Notice the vault is locked
- Read the README and understand the two-stage goal

### Phase 2: Vulnerability Identification (10-15 minutes)
- Students examine `src/server.js` to understand the flow
- Find the vulnerable function in `src/utils/safePath.js`
- Research path traversal vulnerabilities
- Understand why `path.join()` is insufficient

### Phase 3: Stage 1 - Exploit to Find Key (5-10 minutes)
- Students attempt path traversal attacks
- Successfully access `../secrets/vault.key`
- Retrieve the key: `RDxlT2USNk6yFo1Ejmenl1tkrJ4vGz9T2YKrqOQT`
- Understand the vulnerability by exploiting it

### Phase 4: Stage 2 - Solution Implementation (15-20 minutes)
- Students research secure path handling
- Implement path normalization and validation
- Test their solution manually
- Run the test suite

### Phase 5: Verification and Flag Retrieval (5 minutes)
- Verify all tests pass
- Check `/health` shows `secure: true`
- Retrieve the flag from `/vault/key`: `TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}`

**Total Time**: 40-60 minutes for students with basic web security knowledge

## Common Student Mistakes

### Mistake 1: Simple String Replacement
```javascript
// WRONG - Easy to bypass
if (userFile.includes('../')) {
  throw new Error("Blocked");
}
```
**Why it fails**: URL encoding (`..%2F`) bypasses this check

### Mistake 2: Using path.join() with Validation
```javascript
// WRONG - Still vulnerable
const joined = path.join(logsDir, userFile);
if (joined.includes('..')) {
  throw new Error("Blocked");
}
return joined;
```
**Why it fails**: `path.join()` may normalize but doesn't prevent escaping

### Mistake 3: Not Resolving Base Directory
```javascript
// WRONG - Symlink issues
const resolved = path.resolve(logsDir, userFile);
if (!resolved.startsWith(logsDir)) {
  throw new Error("Blocked");
}
```
**Why it fails**: If `logsDir` is relative or contains symlinks, comparison fails

### Mistake 4: Allowing Empty Paths
```javascript
// WRONG - Missing edge case
if (!userFile || userFile === '') {
  return logsDir; // Could expose directory listing
}
```

## Teaching Points

### Key Concepts to Emphasize

1. **Never Trust User Input**
   - Always validate and sanitize user-provided paths
   - Assume attackers will try various encoding methods

2. **Defense in Depth**
   - Multiple layers of validation
   - Fail securely (block by default)

3. **Path Normalization**
   - Always resolve paths to absolute before comparison
   - Understand the difference between `join()` and `resolve()`

4. **Testing Security Fixes**
   - Test positive cases (should work)
   - Test negative cases (should fail)
   - Test edge cases (encoding, different OS paths)

### Discussion Questions

1. **Why doesn't `path.join()` prevent traversal?**
   - It's designed for concatenation, not security
   - It normalizes but doesn't validate containment

2. **What other attack vectors exist?**
   - Null byte injection (older systems)
   - Unicode normalization attacks
   - Symlink attacks

3. **How would you handle this in other languages?**
   - Python: `os.path.abspath()` + `startswith()`
   - Java: `Path.normalize()` + `startsWith()`
   - PHP: `realpath()` + validation

## Extension Ideas

### For Advanced Students

1. **Add logging**: Log all blocked traversal attempts
2. **Rate limiting**: Prevent brute force attempts
3. **Whitelist approach**: Only allow specific filenames
4. **Content-Type validation**: Ensure only text files are served
5. **File size limits**: Prevent DoS via large files

### For Classroom Use

1. **Group discussion**: Have students explain their solutions
2. **Code review**: Review each other's implementations
3. **Attack simulation**: Have students create attack payloads
4. **Real-world examples**: Discuss recent path traversal CVEs

## Assessment Rubric

### Excellent (A)
- ✅ Correctly implements path resolution and validation
- ✅ All tests pass
- ✅ Handles all edge cases (URL encoding, absolute paths, Windows paths)
- ✅ Code is clean and well-commented
- ✅ Understands why the solution works

### Good (B)
- ✅ Correctly implements the fix
- ✅ Most tests pass
- ⚠️ Minor edge cases may not be handled
- ✅ Code is functional

### Satisfactory (C)
- ✅ Basic fix implemented
- ⚠️ Some tests may fail
- ⚠️ May not handle all attack vectors
- ⚠️ Solution may be overly restrictive

### Needs Improvement (D/F)
- ❌ Fix doesn't work
- ❌ Tests fail
- ❌ Doesn't understand the vulnerability

## Resources for Students

### Recommended Reading
- OWASP: Path Traversal
- CWE-23: Relative Path Traversal
- Node.js `path` module documentation

### Tools
- Burp Suite (for testing)
- Postman (for API testing)
- Browser DevTools (for inspecting requests)

## Troubleshooting

### Common Issues

**Issue**: Tests fail even with correct solution
- **Solution**: Ensure server is restarted after code changes

**Issue**: Docker permission errors
- **Solution**: Use `sudo` or add user to docker group

**Issue**: Port already in use
- **Solution**: Change PORT in `.env` or stop conflicting services

**Issue**: `npm ci` fails
- **Solution**: Use `npm install` in Dockerfile (or generate package-lock.json)

## Conclusion

This challenge provides a hands-on introduction to path traversal vulnerabilities and secure coding practices. It's designed to be approachable for beginners while teaching important security concepts that apply to real-world applications.

The self-check mechanism ensures students can't "fake" a solution and must truly understand the vulnerability to complete the challenge successfully.

---

**Version**: 1.0  
**Last Updated**: 2024  
**Difficulty**: Easy  
**Estimated Time**: 40-60 minutes

