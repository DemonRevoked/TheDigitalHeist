# web-03-safehouse — Walkthrough

## Goal
Use the URL preview feature to reach an **internal server** (SSRF) and read `/flag`.

## Steps
1. **Open the site**
   - Visit the challenge web page.

2. **Login**
   - Login as:
     - `tokyo`
     - `tokyo123`

3. **Copy the token**
   - Go to the settings / command page.
   - Copy the “Professor’s Access Token”.

4. **Open the URL preview page**
   - Go to `/preview`.

5. **Use the @ trick**
   - Submit this URL (replace TOKEN):
     - `http://previewme.com@internal-admin:8080/flag?token=TOKEN`

6. **Get the flag**
   - The preview response shows the flag text.

