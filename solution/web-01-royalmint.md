# web-01-royalmint — Walkthrough

## Goal
Log in, then read **someone else’s invoice** to get the flag (IDOR bug).

## Steps
1. **Open the site**
   - Visit the challenge in your browser.

2. **Find a username (easy way)**
   - Open:
     - `/auth/check?username=' UNION SELECT username FROM users--`
   - You should see usernames like `oslo`, `helsinki`, `Raquel`.

3. **Bypass login (SQL injection)**
   - Go to the login page.
   - Use username:
     - `oslo'--`
   - Use any password.
   - You should get logged in.

4. **Exploit IDOR**
   - Open this URL while logged in:
     - `/invoices/1057`
   - This invoice is not yours, but the app still shows it.

5. **Copy the flag**
   - The invoice note contains the flag (and also a “Key:” value).

