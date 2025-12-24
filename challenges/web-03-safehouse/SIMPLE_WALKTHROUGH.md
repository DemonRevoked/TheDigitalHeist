# 🎭 Simple Walkthrough: La Casa de Papel CTF Challenge

## 📚 What You'll Learn

This challenge teaches you about **SSRF (Server-Side Request Forgery)** - a vulnerability where you can trick a server into making requests to places it shouldn't.

**In simple terms:** The server has a "URL preview" feature that checks if URLs are safe. But the check is flawed, so we can trick it into accessing an internal server that's supposed to be hidden!

---

## 🎯 Your Mission

You're part of the Money Heist crew. The Professor has hidden the final coordinates in a secure internal server. Your job: bypass the security and get those coordinates!

---

## 🚀 Step-by-Step Guide

### Step 1: Start the Challenge

1. Open your terminal
2. Navigate to the challenge folder:
   ```bash
   cd /home/ubuntu/web-ctf/hard
   ```
3. Start the servers:
   ```bash
   sudo docker-compose up --build -d
   ```
4. Wait a few seconds for everything to start
5. Open your browser and go to: **http://localhost:5003**

You should see the Money Heist mission page! 🎭

---

### Step 2: Login

1. Click the **"Enter the Network"** button (or go to `/auth/login`)
2. Enter your credentials:
   - **Codenamе:** `tokyo`
   - **Passphrase:** `tokyo123`
3. Click **"Connect"**

✅ **What happened?** You logged in as Tokyo, a member of the crew.

---

### Step 3: Get the Access Token

1. After logging in, you'll be redirected to the **Command Center**
2. Look for the section that says **"Professor's Access Token"**
3. **Copy the token** - you'll need it later!

It should look something like: `INTERNAL-TOKEN-9f3c2a`

✅ **What happened?** The Professor's access token is displayed on this page. This token is needed to access the internal command server.

---

### Step 4: Understand the Intel Previewer

1. Click **"Access Intel Previewer"** (or go to `/preview`)
2. You'll see a form where you can enter a URL
3. The page says: *"Only URLs from previewme.com are allowed"*

**Try this first (to understand how it works):**
- Enter: `https://previewme.com/`
- Click **"Gather Intel"**
- You should see a response (even if it's an error, that's okay!)

✅ **What happened?** The Intel Previewer fetches URLs and shows you the response. But it only allows URLs from `previewme.com`.

---

### Step 5: Find the Vulnerability

**The Problem:** The validation is flawed! Let's understand why:

The code checks if the URL **string contains** `previewme.com`, but it doesn't properly parse the URL.

**URL Trick:** URLs can have this format:
```
http://username@hostname:port/path
```

The part before `@` is called "userinfo". The validator sees `previewme.com` in the string, but the actual request goes to the hostname after `@`!

---

### Step 6: Craft Your Attack

**Your Goal:** Access the internal command server at `internal-admin:8080/flag`

**The Trick:** Use this URL format:
```
http://previewme.com@internal-admin:8080/flag?token=YOUR_TOKEN
```

**Why this works:**
- ✅ The validator sees `previewme.com` in the string → **PASSES**
- ✅ The validator extracts `previewme.com` as the host → **PASSES**
- ✅ But the actual HTTP request goes to `internal-admin:8080` → **SUCCESS!**

---

### Step 7: Execute the Attack

1. Go to the **Intel Previewer** page (`/preview`)
2. In the URL field, enter:
   ```
   http://previewme.com@internal-admin:8080/flag?token=INTERNAL-TOKEN-9f3c2a
   ```
   ⚠️ **Important:** Replace `INTERNAL-TOKEN-9f3c2a` with the actual token you copied in Step 3!

3. Click **"Gather Intel"**

4. **Success!** You should see:
   - Status: 200
   - Content-Type: text/plain
   - **Body: The final coordinates (your flag!)**

🎉 **Congratulations!** You've successfully bypassed the security and retrieved the final coordinates!

---

## 🔍 Understanding What Happened

### The Vulnerability

The `naiveValidate()` function in `src/routes/preview.js` has three flaws:

1. **String Contains Check:** Only checks if the string contains `previewme.com`, not if it's actually the domain
2. **Naive Parsing:** Uses simple string splitting instead of proper URL parsing
3. **Wrong Host Check:** Checks the extracted host, not the actual parsed hostname

### The Bypass

When you use: `http://previewme.com@internal-admin:8080/flag`

- The validator sees: `previewme.com` ✅
- The validator extracts: `previewme.com@internal-admin` ✅
- But the HTTP client (node-fetch) properly parses it and sends the request to: `internal-admin:8080` ✅

### Why It Matters

- The internal server (`internal-admin:8080`) is only accessible from within the Docker network
- You can't access it directly from your browser
- But you can trick the web server into accessing it for you!
- This is called **SSRF (Server-Side Request Forgery)**

---

## 💡 Key Takeaways

1. **SSRF** allows you to make the server request internal resources
2. **URL parsing is tricky** - always use proper URL parsing libraries
3. **String checks ≠ Security** - never use string operations for security
4. **The `@` trick** exploits the difference between string checks and proper URL parsing

---

## 🎓 Learning Points

- **SSRF vulnerabilities** are common in URL preview/fetch features
- **Naive validation** can always be bypassed
- **Internal services** should be properly isolated
- **Always validate URLs properly** using libraries like `new URL()` in JavaScript

---

## 🆘 Troubleshooting

**Problem:** The attack doesn't work!

**Solutions:**
1. Make sure you copied the token correctly (no extra spaces)
2. Make sure the URL format is exactly: `http://previewme.com@internal-admin:8080/flag?token=YOUR_TOKEN`
3. Check that both Docker containers are running: `sudo docker-compose ps`
4. Try restarting: `sudo docker-compose restart`

**Problem:** Can't access the website!

**Solutions:**
1. Make sure Docker is running: `sudo docker-compose ps`
2. Check the logs: `sudo docker-compose logs web`
3. Make sure port 5003 is not in use by another application

---

## 🎯 Challenge Complete!

If you see the flag/coordinates in the response, you've successfully:
- ✅ Identified the SSRF vulnerability
- ✅ Bypassed naive URL validation
- ✅ Used URL parsing tricks to access internal services
- ✅ Retrieved the final coordinates!

**Well done!** The Professor would be proud! 🎭

---

## 📖 Further Reading

- [OWASP SSRF](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)
- [URL Structure (RFC 3986)](https://tools.ietf.org/html/rfc3986)
- [Node.js URL API](https://nodejs.org/api/url.html)

---

## 🎬 Next Steps

Now that you understand SSRF:
1. Try to find SSRF vulnerabilities in other applications
2. Learn about other SSRF bypass techniques
3. Practice with more CTF challenges
4. Learn how to properly validate URLs in your own code

**Remember:** Always use proper URL parsing libraries and validate the actual parsed hostname, not just the string!

