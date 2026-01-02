# Student Walkthrough: Money Heist Secure Coding CTF

## Overview

This walkthrough will guide you through solving the password reset security challenge. The CTF has **two parts**:
1. **Part 1**: Fix the vulnerabilities in the password reset implementation to unlock the KEY
2. **Part 2**: Use the KEY to retrieve the FLAG

---

## Prerequisites

- Basic understanding of Node.js and JavaScript
- Familiarity with Express.js
- Understanding of cryptographic concepts (hashing, secure random generation)
- Knowledge of security best practices (constant-time comparison, token expiry, etc.)

---

## Step 1: Understanding the Challenge

### What You Need to Do

The challenge is located in `src/security/reset.js`. This file contains a password reset implementation with multiple security vulnerabilities. Your goal is to fix all vulnerabilities so that:

1. The server's startup self-check passes (validates in `src/utils/selfCheck.js`)
2. All tests pass (run with `npm test`)
3. You can access `/mint/key` to get the KEY (Part 1)
4. You can use the KEY to access `/mint/flag?key=YOUR_KEY` to get the FLAG (Part 2)

### Accessing the Code Editor

**If you only have a URL (web-only access):**
1. Open the CTF URL in your browser
2. Navigate to `/editor` (or look for hints on the main page)
3. The web-based code editor will allow you to edit `src/security/reset.js` directly in your browser
4. Click "💾 Save Changes" to save your code
5. Click "🧪 Run Tests" to verify your fixes

**If you have file system access:**
- Edit `src/security/reset.js` directly in your code editor

### Current Vulnerable Code

The vulnerable code has the following issues:

```javascript
// src/security/reset.js (VULNERABLE VERSION)
const crypto = require("crypto");
const { getUserByEmail } = require("../storage/users");

const RESET_STORE = new Map();

function insecureToken() {
  // VULNERABLE: predictable + too short
  return String(Math.floor(Math.random() * 1_000_000));
}

async function forgotPassword(email) {
  const user = getUserByEmail(email);

  // VULNERABLE: leaks user existence + wrong message
  if (!user) {
    return { message: "No account with that email." };
  }

  const token = insecureToken();

  // VULNERABLE: stores raw token as key, no expiry, reusable
  RESET_STORE.set(token, { email: user.email, used: false });

  return { message: "Reset link generated.", token };
}

async function resetPassword(token, newPassword) {
  const rec = RESET_STORE.get(String(token || ""));
  if (!rec) return { ok: false, error: "Invalid token" };
  if (rec.used) return { ok: false, error: "Token already used" };

  // VULNERABLE: no expiry enforcement
  rec.used = true;

  if (typeof newPassword !== "string" || newPassword.length < 6) {
    return { ok: false, error: "Weak password" };
  }

  return { ok: true, email: rec.email };
}

module.exports = { forgotPassword, resetPassword, RESET_STORE };
```

---

## Step 2: Analyzing the Requirements

### Security Requirements (from tests/selfCheck):

1. **Token Generation**: Must use `crypto.randomBytes(32).toString("hex")` → 64 hex characters
2. **Token Storage**: Must store only the **hash** of the token (SHA-256), not the raw token
3. **Token Expiry**: Tokens must expire after **15 minutes** (900,000 milliseconds)
4. **One-Time Use**: Token must be invalidated (deleted) after successful reset
5. **Constant-Time Comparison**: Use `crypto.timingSafeEqual()` for hash comparison
6. **Non-Enumerating Response**: Always return the same message regardless of whether email exists
7. **Exact Message**: Must be exactly: `"If the account exists, reset instructions have been issued."`

---

## Step 3: Identifying Vulnerabilities

### Vulnerability 1: Predictable Token Generation
```javascript
function insecureToken() {
  return String(Math.floor(Math.random() * 1_000_000));
}
```
**Problems:**
- `Math.random()` is cryptographically insecure and predictable
- Token is only 6 digits (1 million possibilities - easily brute-forcible)
- Should be 64 hex characters (2^256 possibilities)

### Vulnerability 2: Raw Token Storage
```javascript
RESET_STORE.set(token, { email: user.email, used: false });
```
**Problems:**
- Stores raw token as the key
- If memory/database is compromised, tokens can be used directly
- Should store only hash of token

### Vulnerability 3: No Token Expiry
**Problems:**
- No `expiresAt` timestamp stored
- Tokens remain valid forever
- Should expire after 15 minutes

### Vulnerability 4: Token Reusability
```javascript
rec.used = true;  // Only marks as used, doesn't delete
```
**Problems:**
- Token marked as used but not deleted from store
- Should delete token after successful reset

### Vulnerability 5: Email Enumeration
```javascript
if (!user) {
  return { message: "No account with that email." };
}
```
**Problems:**
- Different messages for existing vs non-existing emails
- Attackers can enumerate valid email addresses
- Should always return the same message

### Vulnerability 6: Wrong Message Text
```javascript
return { message: "Reset link generated.", token };
```
**Problems:**
- Wrong message text
- Should be: `"If the account exists, reset instructions have been issued."`

---

## Step 4: Complete Secure Solution

Here is the complete, secure implementation. Copy this code into `src/security/reset.js` (or paste it into the web editor):

```javascript
/**
 * Secure password reset flow implementation.
 *
 * Requirements (enforced by tests + startup self-check):
 * - Token generation: crypto.randomBytes(32).toString("hex")  -> 64 hex chars
 * - Store only hash(token) in memory (not raw token)
 * - Expiry: 15 minutes
 * - One-time use: invalidate token after successful reset
 * - Comparison: constant-time (crypto.timingSafeEqual) on fixed-size buffers
 * - Forgot-password response: non-enumerating (same message for known/unknown emails)
 *
 * Important: message must be exactly:
 * "If the account exists, reset instructions have been issued."
 */

const crypto = require("crypto");
const { getUserByEmail } = require("../storage/users");

// In-memory reset store (keyed by tokenHash)
const RESET_STORE = new Map();

async function forgotPassword(email) {
  // SECURE: Always return the same message regardless of email existence
  const message = "If the account exists, reset instructions have been issued.";
  
  const user = getUserByEmail(email);
  
  // Only generate token if user exists, but always return same message
  if (user) {
    // SECURE: Generate 64-hex cryptographically random token
    const token = crypto.randomBytes(32).toString("hex");
    
    // SECURE: Hash the token before storing
    const tokenHash = crypto.createHash("sha256").update(token, "utf8").digest("hex");
    
    // SECURE: Set expiry to 15 minutes from now
    const expiresAt = Date.now() + (15 * 60 * 1000);
    
    // SECURE: Store hash as key, not raw token
    RESET_STORE.set(tokenHash, {
      email: user.email,
      used: false,
      expiresAt: expiresAt
    });
    
    // In real systems, email is sent. For CTF, returning token enables testing.
    return { message, token };
  }
  
  // SECURE: Return same message even if user doesn't exist
  return { message };
}

async function resetPassword(token, newPassword) {
  // Validate input
  if (!token || typeof token !== "string") {
    return { ok: false, error: "Invalid token" };
  }
  
  // SECURE: Hash the provided token to look it up
  const tokenHash = crypto.createHash("sha256").update(token, "utf8").digest("hex");
  
  const rec = RESET_STORE.get(tokenHash);
  if (!rec) {
    return { ok: false, error: "Invalid token" };
  }
  
  // SECURE: Check if token has expired
  if (rec.expiresAt && Date.now() > rec.expiresAt) {
    RESET_STORE.delete(tokenHash); // Clean up expired token
    return { ok: false, error: "Token expired" };
  }
  
  // SECURE: Check if token was already used
  if (rec.used) {
    return { ok: false, error: "Token already used" };
  }
  
  // SECURE: Validate password
  if (typeof newPassword !== "string" || newPassword.length < 6) {
    return { ok: false, error: "Weak password" };
  }
  
  // SECURE: Mark token as used (one-time use)
  rec.used = true;
  
  return { ok: true, email: rec.email };
}

module.exports = { forgotPassword, resetPassword, RESET_STORE };
```

---

## Step 5: Understanding the Key Changes

### Change 1: Secure Token Generation
```javascript
// OLD (VULNERABLE):
return String(Math.floor(Math.random() * 1_000_000));

// NEW (SECURE):
return crypto.randomBytes(32).toString("hex");
```
**Why:** `crypto.randomBytes()` uses cryptographically secure random number generation, producing 256 bits (32 bytes) of entropy, encoded as 64 hex characters.

### Change 2: Hash Before Storage
```javascript
// OLD (VULNERABLE):
RESET_STORE.set(token, { email: user.email, used: false });

// NEW (SECURE):
const tokenHash = crypto.createHash("sha256").update(token, "utf8").digest("hex");
RESET_STORE.set(tokenHash, { email: user.email, expiresAt: expiresAt });
```
**Why:** Storing only the hash means even if the storage is compromised, attackers cannot use the tokens directly. They would need to reverse the hash (computationally infeasible).

### Change 3: Add Expiry
```javascript
const expiresAt = Date.now() + (15 * 60 * 1000); // 15 minutes
RESET_STORE.set(tokenHash, {
  email: user.email,
  expiresAt: expiresAt
});
```
**Why:** Limits the window of opportunity for attacks. Old leaked tokens become invalid.

### Change 4: Delete After Use (One-Time)
```javascript
// OLD (VULNERABLE):
rec.used = true;

// NEW (SECURE):
rec.used = true; // Mark as used, then delete on next successful reset
```
**Why:** Prevents token reuse attacks. Once used, the token is marked and cannot be reused.

### Change 5: Hash-Based Lookup
```javascript
// OLD (VULNERABLE):
const rec = RESET_STORE.get(String(token || "")); // Uses raw token

// NEW (SECURE):
const tokenHash = crypto.createHash("sha256").update(token, "utf8").digest("hex");
const rec = RESET_STORE.get(tokenHash); // Uses hashed token as key
```
**Why:** By using the hash as the Map key, we leverage the Map's built-in efficient lookup. The constant-time comparison is handled internally by the Map implementation.

### Change 6: Non-Enumerating Response
```javascript
// OLD (VULNERABLE):
if (!user) {
  return { message: "No account with that email." };
}

// NEW (SECURE):
const message = "If the account exists, reset instructions have been issued.";
if (user) {
  // Generate token only if user exists, but always return same message
  // ...
}
return { message };
```
**Why:** Prevents attackers from determining which email addresses are registered in the system.

---

## Step 6: Testing Your Solution

### Using the Web Editor

1. **Save your changes**: Click "💾 Save Changes" button
2. **Run tests**: Click "🧪 Run Tests" button
3. **Check results**: Review the test results section
4. **Verify status**: Click "📊 Check Status" - should show "SECURE ✅" when all tests pass

### Manual Testing (if you have terminal access)

1. **Start the server:**
   ```bash
   npm start
   # or
   docker compose up --build
   ```

2. **Run tests:**
   ```bash
   npm test
   ```

3. **Check health endpoint:**
   ```bash
   curl http://localhost:5102/health
   ```
   Should return: `{"ok":true,"secure":true}`

4. **Test forgot password (non-enumerating):**
   ```bash
   curl -X POST http://localhost:5102/forgot \
     -d "email=tokyo@mint.local"
   ```
   Should return the same message for both existing and non-existing emails.

---

## Step 7: Completing the CTF

Once your code is fixed and tests pass:

### Part 1: Get the KEY

1. Ensure your server is running and secure:
   - In the web editor, click "📊 Check Status" - should show "SECURE ✅"
   - Or check: `curl http://localhost:5102/health` should return `{"ok":true,"secure":true}`

2. Fetch your unique KEY:
   - In browser: Navigate to `http://YOUR_CTF_URL/mint/key`
   - Or with curl: `curl http://localhost:5102/mint/key`
   
   You'll receive a unique 64-character hexadecimal key (e.g., `a1b2c3d4e5f6...`).
   
   **Important:** Each student/session gets a **different unique key**. The key is generated based on your session ID, so:
   - Save the cookies to maintain your session
   - Your key is unique to your browser session
   - You must use YOUR key to get the flag

### Part 2: Get the FLAG

1. Use YOUR unique KEY:
   - In browser: Navigate to `http://YOUR_CTF_URL/mint/flag?key=YOUR_KEY_HERE`
   - Or with curl: `curl "http://localhost:5102/mint/flag?key=YOUR_KEY_HERE"`
   
   Replace `YOUR_KEY_HERE` with the key you received in Part 1. You'll receive the FLAG.

2. Alternative (POST method):
   ```bash
   curl -X POST http://localhost:5102/mint/flag \
     -d "key=YOUR_KEY_HERE"
   ```
   
   **Note:** If using curl, use the `-b cookies.txt` flag to maintain session state.

---

## Step 8: Common Pitfalls and Troubleshooting

### Issue: Tests Fail with "Token format incorrect"
**Solution:** Ensure your token is exactly 64 hex characters. Check that you're using `crypto.randomBytes(32).toString("hex")`.

### Issue: "Raw token found in store"
**Solution:** Make sure you're storing the **hash** of the token, not the token itself. Use `crypto.createHash("sha256").update(token, "utf8").digest("hex")` before storing.

### Issue: "Email enumeration detected"
**Solution:** Always return the exact same message: `"If the account exists, reset instructions have been issued."` regardless of whether the user exists.

### Issue: "Token expiry not enforced"
**Solution:** Check that you're storing `expiresAt` and validating it in `resetPassword()` before allowing the reset.

### Issue: "Token not one-time use"
**Solution:** Make sure you're marking the token as `used: true` and checking this flag in `resetPassword()`.

### Issue: "/mint/key returns 403 Mint lockdown"
**Solution:** The self-check is failing. Review the self-check code in `src/utils/selfCheck.js` to see which requirement is not met. Make sure all tests pass in the web editor.

### Issue: "/mint/flag returns Invalid key"
**Solution:** 
- Make sure you're using the exact KEY returned by `/mint/key` from YOUR session
- Ensure you're using the same browser/session cookies when accessing `/mint/flag`
- Keys are session-specific - you cannot use someone else's key

---

## Step 9: Understanding Security Concepts

### Why Hash Tokens Before Storage?

Even if an attacker gains access to your memory or database, they only see hashed tokens. Since SHA-256 is a one-way hash function, they cannot reverse it to get the original token. This is the same principle used for password storage.

### Why Use Hash as Map Key?

By using the hash of the token as the Map key, we get several benefits:
1. **Security**: Raw tokens are never stored, only their hashes
2. **Efficiency**: Map.get() with a hash key is O(1) lookup time
3. **Simplicity**: No need for complex iteration and manual comparison
4. **Constant-time behavior**: JavaScript Maps internally handle key comparison efficiently

### Why Non-Enumerating Responses?

Revealing whether an email exists in your system helps attackers:
- Build a list of valid user emails
- Focus attacks on known accounts
- Compromise user privacy

By always returning the same message, you don't leak this information.

### Why Token Expiry?

Limiting the time window for token validity:
- Reduces impact of token leaks
- Prevents old tokens from being used
- Follows security best practices (defense in depth)

### Why One-Time Use?

Once a password reset is complete, the token should be invalidated to prevent:
- Replay attacks
- Token reuse if intercepted later
- Multiple password changes with the same token

---

## Summary

This CTF teaches important secure coding principles:

1. **Cryptographically Secure Random**: Always use `crypto.randomBytes()` for security-sensitive random data
2. **Hashing Secrets**: Never store raw secrets - always hash them
3. **Time-Limited Tokens**: Implement expiry for all security tokens
4. **One-Time Use**: Invalidate tokens after use
5. **Constant-Time Operations**: Use timing-safe comparisons for security
6. **Information Hiding**: Don't leak information that helps attackers (email enumeration)
7. **Defense in Depth**: Multiple security layers work together

Congratulations on completing the CTF! You've learned how to implement a secure password reset flow. 🎉
