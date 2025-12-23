# Challenge 1 (Easy) — Royal Mint Heist
## SQL Injection + IDOR / Broken Object Level Authorization (BOLA)

A multi-layered web security challenge themed around Money Heist (La Casa de Papel), where players must exploit SQL Injection to bypass authentication and then use IDOR to access unauthorized resources.

## What players should learn
- SQL Injection for authentication bypass
- Authentication != Authorization
- ID enumeration and broken object-level access control
- Multi-step exploitation techniques

## Challenge Theme
**Royal Mint - Invoice Portal**: A secure financial records management system where players must exploit vulnerabilities to access sensitive invoice data.

## Services
- web (Node.js/Express)
- db (PostgreSQL)

## Run
1. Copy `.env.example` to `.env` and (optionally) change values.
2. Start:
   ```bash
   docker compose up --build
   ```
3. Open:
   - http://localhost:5001

## Challenge Flow

### Step 1: SQL Injection Authentication Bypass
The login page is vulnerable to SQL Injection. Players must:
- Enumerate usernames using UNION-based SQL injection
- Bypass authentication to log in as a user

**Working payloads:**
- Username enumeration: `' OR '1'='2' UNION SELECT id, username, password_hash, role FROM users--`
- Authentication bypass: `oslo'--` or `' OR '1'='1'--`

### Step 2: IDOR Exploitation
Once logged in, players must:
- Access Helsinki's invoice #1057 from Oslo's account
- The invoice endpoint doesn't verify ownership before displaying invoices

**Target:** Invoice ID 1057 (Helsinki's invoice containing the flag)

## User Accounts

### Regular Users
- **oslo** / oslo123 (has invoices 1001-1010)
- **helsinki** / helsinki123 (has invoices 1050-1060, including flag at #1057)
  - ⚠️ **Account is restricted** - cannot log in directly
  - Must be accessed via IDOR from another account

### Admin Account
- **Raquel** / admin123 (admin role, not needed for solve)

## Flag Location
The flag is stored in **Helsinki's invoice #1057** in the `note` field.

**Flag Format:** `FLAG{DENVER_LAUGHS_AT_BROKEN_ACL}`

## Vulnerabilities

### 1. SQL Injection (Login)
- **Location:** `src/routes/auth.js` - POST `/auth/login`
- **Issue:** String concatenation instead of parameterized queries
- **Impact:** Authentication bypass and username enumeration

### 2. IDOR / Broken Object Level Authorization
- **Location:** `src/routes/invoices.js` - GET `/invoices/:id`
- **Issue:** Fetches invoice by ID without checking ownership
- **Impact:** Unauthorized access to other users' invoices

## Solution Walkthrough

1. **Enumerate usernames:**
   - Use UNION SQL injection: `' OR '1'='2' UNION SELECT id, username, password_hash, role FROM users--`
   - Discover: oslo, helsinki, Raquel

2. **Bypass authentication:**
   - Log in as oslo using: `oslo'--` (password: anything)

3. **Exploit IDOR:**
   - Access `/invoices/1057` directly
   - View Helsinki's invoice containing the flag

4. **Capture the flag:**
   - Flag is in the invoice note: `FLAG{DENVER_LAUGHS_AT_BROKEN_ACL}`

## Notes for creators
- SQL Injection vulnerability is in `src/routes/auth.js`: uses string concatenation for SQL queries
- IDOR vulnerability is in `src/routes/invoices.js`: fetches invoice by id without checking ownership
- Helsinki's account is restricted in the login route to prevent direct access
- The flag is stored in Helsinki's invoice `id=1057` by the seed script
- Database is seeded automatically on first run with test data
