# Ticket to the Vault (Medium)

## 🎭 Story

You are part of a heist crew trying to infiltrate **The Professor's** secure communication network. The Professor uses this system to coordinate with gang members, but he keeps the **master plan** (the flag) locked away in his private dashboard.

Your mission: Exploit a vulnerability in the message system to intercept The Professor's secrets when he reviews gang communications.

## 🎯 What players should learn
- Stored XSS in an admin workflow
- Same-origin actions from injected JS (fetching admin-only endpoints)
- Exfiltration to an in-app collector (safe, CTF-friendly)
- Real-world attack scenario: compromising admin interfaces

## 🔍 Discovery Approach

**This challenge encourages exploration and discovery:**

1. **Test the application** - Try different inputs, see what happens
2. **Explore endpoints** - Check common paths, analyze the structure
3. **Analyze the code** - Source code is available for analysis
4. **Think about the flow** - How does data move through the system?
5. **Build incrementally** - Start simple, build up to the complete solution

**Discovery hints are embedded in the UI** - look carefully at what the application tells you.

## 🏗️ Services
- **web** (Node.js/Express + EJS) — The Professor's communication network
- **db** (PostgreSQL) — Secure message storage
- **professor-bot** (Playwright) — Simulates The Professor reviewing messages

## 🚀 Run
1. Copy `.env.example` to `.env` (optional edits).
2. Start the heist:
   ```bash
   docker compose up --build
   ```
3. Access the network:
   - http://localhost:5002

## 👥 Gang Members
- **Tokyo** - Your character (credentials must be discovered)
- **The Professor** - Bot account that reviews messages (credentials must be discovered)

**💡 How to Discover Credentials:**

The credentials are hidden in a standard web file that web crawlers and bots typically check.

**Hint:** Think about what files web applications expose publicly for automated systems.

## 🎯 Mission Objective

Your mission: Exploit a vulnerability in the message system to intercept The Professor's master plan when he reviews gang communications.

**Challenge:** Discover the vulnerability, find the endpoints, and construct your attack.

**⚠️ Important:** Try to solve this yourself first! The `SOLVE_GUIDE.md` is an optional educational resource for learning the concepts. Use it only if you're stuck or want to understand the technical details.

## 🔄 Challenge Reset

The challenge automatically resets on server startup by default:
- All tickets (messages) are cleared
- All captures (intercepted data) are cleared
- User accounts remain intact

**Configuration:**
- Set `RESET_ON_STARTUP=true` in `.env` to enable auto-reset (default)
- Set `RESET_ON_STARTUP=false` to preserve data across restarts

**Manual Reset:**
- Admin endpoint: `POST /admin/reset` (requires admin login)
- Clears all tickets and captures immediately

## ⚠️ Security Notice
- Keep this instance isolated. Do not deploy on a shared network.
- This is a CTF challenge — vulnerabilities are intentional for educational purposes.
