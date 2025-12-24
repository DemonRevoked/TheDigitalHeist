# 🎭 Quick Reference Guide

## 🚀 Quick Start

```bash
cd /home/ubuntu/web-ctf/hard
sudo docker-compose up --build -d
# Open: http://localhost:5003
```

## 🔑 Credentials

- **Username:** `tokyo`
- **Password:** `tokyo123`

## 🎯 Attack Steps (TL;DR)

1. **Login** → `tokyo/tokyo123`
2. **Get Token** → Copy from Command Center (`/settings`)
3. **Craft URL** → `http://previewme.com@internal-admin:8080/flag?token=YOUR_TOKEN`
4. **Submit** → In Intel Previewer (`/preview`)
5. **Get Flag** → Read the response!

## 🔍 The Vulnerability

**Location:** `src/routes/preview.js` - `naiveValidate()` function

**Flaws:**
- Only checks if string contains `previewme.com`
- Uses naive string splitting (breaks with `@`)
- Doesn't properly parse the URL

## 💣 The Payload

```
http://previewme.com@internal-admin:8080/flag?token=INTERNAL-TOKEN-xxxxx
```

**Why it works:**
- Validator sees `previewme.com` ✅
- Validator extracts `previewme.com@internal-admin` ✅  
- But HTTP request goes to `internal-admin:8080` ✅

## 📍 Key Endpoints

- **Home:** `/`
- **Login:** `/auth/login`
- **Command Center:** `/settings` (requires login)
- **Intel Previewer:** `/preview` (requires login)
- **Internal Server:** `http://internal-admin:8080/flag` (internal only)

## 🛠️ Useful Commands

```bash
# Check if containers are running
sudo docker-compose ps

# View logs
sudo docker-compose logs web
sudo docker-compose logs internal-admin

# Restart services
sudo docker-compose restart

# Stop services
sudo docker-compose down
```

## 🎓 What is SSRF?

**Server-Side Request Forgery** - Tricking a server into making requests to internal/private resources that shouldn't be accessible.

## ⚠️ Common Mistakes

- Forgetting to include the token in the URL
- Using wrong URL format (missing `@` or `http://`)
- Not replacing `YOUR_TOKEN` with actual token
- Using `https://` instead of `http://` (internal server uses HTTP)

## ✅ Success Indicators

- Status: 200
- Response contains the flag/coordinates
- No error messages

## 🆘 Still Stuck?

1. Check the full walkthrough: `SIMPLE_WALKTHROUGH.md`
2. Verify containers are running
3. Double-check the token from `/settings`
4. Make sure URL format is exactly correct

---

**Remember:** The `@` trick works because the validator checks the string, but the HTTP client parses the URL properly!

