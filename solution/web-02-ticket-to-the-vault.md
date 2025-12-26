# web-02-ticket-to-the-vault — Walkthrough

## Goal
Use **stored XSS** to steal the flag from the admin, then read it in your captures.

## Steps
1. **Open the site**
   - Go to the web page for this challenge.

2. **Find login details**
   - Open:
     - `/robots.txt`
   - Copy Tokyo’s login (it is written there).

3. **Login**
   - Login as Tokyo.

4. **Send a “ticket” with a script**
   - Create a new ticket/message.
   - Put this in the message (stored XSS):
     - It fetches `/admin/flag`
     - Then posts it to `/collector` for your user

5. **Wait**
   - The admin bot visits the admin page every few seconds.
   - Your script runs in the admin’s browser.

6. **Read the captured flag**
   - Open:
     - `/my-captures`
   - The flag will be shown there.

