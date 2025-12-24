# CTF Challenge Walkthrough: La Casa de Papel — SSRF Filter Bypass + Internal Service Pivot

## 🎭 Challenge Overview

**Difficulty:** Hard  
**Category:** Web Security / SSRF  
**Storyline:** Money Heist (La Casa de Papel)  
**Objective:** You are part of the Money Heist crew. The Professor has hidden the final coordinates in a secure internal command server. Your mission: bypass the security measures and retrieve the coordinates using the Intel Previewer system.

## Learning Objectives

- Understanding SSRF vulnerabilities in URL preview features
- Bypassing naive allowlist validation using URL parsing tricks
- Using the userinfo `@` trick to bypass domain checks
- Pivoting to internal services on Docker networks

---

## Setup

1. **Start the services:**
   ```bash
   docker compose up --build
   ```

2. **Access the application:**
   - Open http://localhost:5003 in your browser

3. **Verify services are running:**
   - Main web app should be accessible
   - Internal admin service runs at `http://internal-admin:8080` (only accessible from Docker network)

---

## Step-by-Step Solution

### Step 1: Access the Application

Navigate to http://localhost:5003. You'll see the Money Heist mission brief with a login option.

### Step 2: Login

1. Click "Enter the Network" or navigate to `/auth/login`
2. Use the provided credentials:
   - **Codenamе:** `tokyo` (or `alice` for backward compatibility)
   - **Passphrase:** `tokyo123` (or `alice123`)
3. After successful login, you'll be redirected to the Command Center (`/settings`)

### Step 3: Retrieve the Professor's Access Token

1. On the Command Center page (`/settings`), you'll see a section titled "Professor's Access Token"
2. **Copy the token** - this is intentionally leaked and will be needed to access the internal admin service
3. The token is displayed in a `<pre>` tag, something like: `INTERNAL-TOKEN-xxxxx`

**Why this step matters:** The internal admin service requires this token to return the flag. Without it, you'll get a 403 Forbidden response.

### Step 4: Understand the Intel Previewer

1. Navigate to `/preview` (or click "Intel Previewer" from the home page)
2. Notice the form that allows you to enter a target URL
3. The hint says: "Only URLs from previewme.com are allowed by the Professor's system"
4. Try entering a normal URL first: `https://previewme.com/`
   - This should work and show you the intelligence report

### Step 5: Analyze the Vulnerability

The vulnerability is in the `naiveValidate()` function in `src/routes/preview.js`. Let's understand the flaws:

#### Flaw #1: String Contains Check
```javascript
if (!urlStr.includes(ALLOWLIST_MARKER)) return { ok: false, reason: "url must reference previewme.com" };
```
This only checks if the string contains `"previewme.com"` anywhere, not if it's actually the domain.

#### Flaw #2: Naive Host Extraction
```javascript
const afterScheme = urlStr.split("://")[1] || "";
const hostPort = afterScheme.split("/")[0] || "";
const hostOnly = hostPort.split(":")[0];
```
This uses simple string splitting, which breaks when URLs contain userinfo (the `@` character).

#### Flaw #3: Blocklist Only Checks Extracted Host
```javascript
const blocked = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"];
if (blocked.some(b => hostOnly.includes(b))) return { ok: false, reason: "blocked host" };
```
The blocklist only checks the naively extracted host, not the actual parsed hostname.

### Step 6: Craft the SSRF Payload

The key insight is that URLs can contain **userinfo** before the hostname, separated by `@`:

```
http://username@hostname:port/path
```

When the validator processes:
```
http://previewme.com@internal-admin:8080/flag?token=PROFESSOR_TOKEN
```

1. ✅ String contains check: `"previewme.com"` is found in the string
2. ✅ Host extraction: `afterScheme.split("/")[0]` gives `"previewme.com@internal-admin:8080"`
3. ✅ Host only: `hostPort.split(":")[0]` gives `"previewme.com@internal-admin"`
4. ✅ Blocklist check: `"previewme.com@internal-admin"` doesn't contain blocked hosts
5. ✅ Validation passes!

But when `node-fetch` actually makes the HTTP request, it properly parses the URL and sends the request to `internal-admin:8080`, not `previewme.com`.

### Step 7: Execute the SSRF Attack

1. In the Intel Previewer form, enter the malicious URL:
   ```
   http://previewme.com@internal-admin:8080/flag?token=<PROFESSOR_TOKEN>
   ```
   Replace `<PROFESSOR_TOKEN>` with the access token you copied from Step 3.

2. Click "Gather Intel"

3. The server will:
   - Validate the URL (passes due to the vulnerability)
   - Make an HTTP request to `http://internal-admin:8080/flag?token=...`
   - Return the response, which contains the **FINAL COORDINATES** (flag)

### Step 8: Retrieve the Final Coordinates

The response should show:
- **Status:** 200
- **Content-Type:** text/plain
- **Body:** The final coordinates (flag) (e.g., `FLAG{HARD_SSRF_INTERNAL_PIVOT}`)

🎭 **Mission Complete!** You've successfully bypassed the Professor's security and retrieved the final coordinates!

---

## Technical Deep Dive

### Why the Bypass Works

The vulnerability exists because of a mismatch between:
- **What the validator checks:** A naively extracted hostname from string manipulation
- **What the HTTP client uses:** A properly parsed URL according to RFC 3986

#### URL Structure
According to RFC 3986, a URL has this structure:
```
scheme://[userinfo@]host[:port][/path][?query][#fragment]
```

The `userinfo` part (before `@`) is typically `username:password`, but can be any string.

#### The Parsing Difference

**Validator's naive parsing:**
```javascript
"http://previewme.com@internal-admin:8080/flag"
  .split("://")[1]           // "previewme.com@internal-admin:8080/flag"
  .split("/")[0]             // "previewme.com@internal-admin:8080"
  .split(":")[0]             // "previewme.com@internal-admin" ❌ Wrong!
```

**Proper URL parsing (what node-fetch uses):**
```javascript
new URL("http://previewme.com@internal-admin:8080/flag")
  .hostname                  // "internal-admin" ✅ Correct!
```

### Internal Service Architecture

The Docker Compose setup creates two services:

1. **web service:**
   - Exposed on host port 5003
   - Can make requests to other Docker services by hostname
   - Runs the vulnerable preview feature

2. **internal-admin service:**
   - Only exposed internally (not on host ports)
   - Accessible at `http://internal-admin:8080` from within Docker network
   - Requires `INTERNAL_TOKEN` to return the flag

The SSRF allows the web service to act as a proxy, making requests to the internal service on behalf of the attacker.

---

## Alternative Approaches

### Method 1: Direct SSRF (Used Above)
```
http://previewme.com@internal-admin:8080/flag?token=TOKEN
```

### Method 2: Using URL Encoding
Some systems might require URL encoding:
```
http://previewme.com%40internal-admin:8080/flag?token=TOKEN
```

### Method 3: Using Different Schemes
If the validator is even more naive, you might try:
```
http://previewme.com@127.0.0.1:8080/flag?token=TOKEN
```
But this would be blocked by the localhost check.

---

## Defense Recommendations

### 1. Use Proper URL Parsing
```javascript
const url = new URL(urlStr);
const hostname = url.hostname;
```

### 2. Whitelist Instead of Blacklist
Maintain a strict allowlist of permitted domains:
```javascript
const ALLOWED_DOMAINS = ['previewme.com'];
if (!ALLOWED_DOMAINS.includes(hostname)) {
  return { ok: false, reason: "domain not allowed" };
}
```

### 3. Validate the Entire URL
Check that the parsed hostname matches what you expect:
```javascript
const url = new URL(urlStr);
if (url.hostname !== 'previewme.com' && !url.hostname.endsWith('.previewme.com')) {
  return { ok: false, reason: "domain not allowed" };
}
```

### 4. Use a URL Validation Library
Libraries like `validator.js` or `is-url` can help, but still require proper domain checking.

### 5. Network-Level Restrictions
- Use firewall rules to restrict outbound connections
- Use a proxy with allowlist rules
- Run internal services on separate networks

### 6. Sanitize User Input
Always parse and validate URLs properly, never trust string manipulation for security checks.

---

## Common Mistakes to Avoid

1. **String contains checks:** `url.includes("domain.com")` can be bypassed
2. **Naive regex:** Simple regex patterns can be bypassed with encoding
3. **Blacklisting:** Always prefer whitelisting
4. **Trusting client-side validation:** Always validate on the server
5. **Ignoring URL parsing edge cases:** Userinfo, encoding, redirects, etc.

---

## Key Takeaways

1. **SSRF vulnerabilities** allow attackers to make the server request internal resources
2. **URL parsing is complex** - always use proper URL parsing libraries
3. **String manipulation is not security** - never use string operations for security checks
4. **Whitelisting > Blacklisting** - maintain strict allowlists
5. **Internal services** should be properly isolated and protected
6. **The `@` trick** exploits the difference between string checks and proper URL parsing

---

## Challenge Completion

Once you've retrieved the final coordinates, you've successfully:
- ✅ Identified the SSRF vulnerability in the Intel Previewer
- ✅ Bypassed the Professor's naive allowlist validation
- ✅ Used URL parsing tricks to access the internal command server
- ✅ Pivoted through the Intel Network to reach the Professor's command server
- ✅ Retrieved the final coordinates using the leaked access token

🎭 **Congratulations!** You've completed the Money Heist challenge and retrieved the final coordinates! The Professor would be proud! 🎉

