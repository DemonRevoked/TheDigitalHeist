# How Students Will Find Credentials

## Discovery Flow

### Step 1: Initial Encounter
**Where:** Login page (`/auth/login`)

**What students see:**
- Login form asking for "Codename" and "Passphrase"
- No credentials displayed
- Discovery hint section with guidance

**Hint provided:**
```
💡 Discovery Hint
Gang member credentials are embedded in the source code. 
You need to analyze the codebase to find them.

💭 Discovery methods:
• Check files in the src/ directory
• Look for database initialization or user creation code
• Search for files containing "credential" or "user"
• Examine source code comments
```

### Step 2: Following the Hints

**Students will likely:**
1. Read the hint on login page
2. Understand they need to check source code
3. Navigate to `src/` directory
4. Look for database-related files

### Step 3: Finding the Credentials

**Primary Discovery Path: `src/storage/db.js`**

Students will find:
```javascript
// Initialize default users for the challenge
// CTF Discovery: Default user credentials are defined here
// Tokyo's credentials: username="tokyo", password="rio123" 
//   (Rio is Tokyo's love interest in Money Heist)
// The Professor's credentials: username="admin", password="admin123"
const users = [
  { username: "tokyo", password: "rio123", role: "user" },
  { username: "admin", password: "admin123", role: "admin" }
];
```

**Why this works:**
- File name suggests database initialization (`db.js`)
- Location in `src/storage/` suggests it handles data
- Comments explicitly mention "credentials"
- Code shows the actual values

### Alternative Discovery Paths

#### Path 2: CREDENTIALS.md File
- Students exploring root directory
- Notice `CREDENTIALS.md` file
- Read it to find credentials

#### Path 3: Code Comments
- Check `src/server.js` - has comment about credentials
- Check `bot/bot.js` - mentions where credentials are
- Follow hints to `src/storage/db.js`

#### Path 4: Grep/Search
```bash
grep -r "tokyo" src/
grep -r "rio123" src/
grep -r "username.*password" src/
```

### Step 4: Using Credentials

Once found:
- Username: `tokyo`
- Password: `rio123`
- Login and proceed with the challenge

## Hints Provided (From Easiest to Hardest)

### Level 1: Direct Hints (Login Page)
- Points to `src/` directory
- Mentions database files
- Suggests checking comments

### Level 2: Code Comments
- `src/storage/db.js` has explicit comments
- `src/server.js` has credential references
- `bot/bot.js` hints at location

### Level 3: File Names
- `CREDENTIALS.md` is discoverable
- `db.js` suggests database/user data

### Level 4: Code Analysis
- Reading actual code values
- Understanding user initialization

## Expected Student Behavior

**Beginner:**
1. See login page
2. Read hint → Check `src/` directory
3. Find `db.js` → See credentials in comments
4. Use credentials

**Intermediate:**
1. See login page
2. Explore codebase structure
3. Find `CREDENTIALS.md` or `db.js`
4. Extract credentials

**Advanced:**
1. Analyze codebase
2. Search for user creation patterns
3. Find credentials through code analysis
4. May also discover through grep/search

## Teaching Objectives

This credential discovery teaches:
- ✅ Source code analysis skills
- ✅ File exploration techniques
- ✅ Reading code comments
- ✅ Following hints and clues
- ✅ Understanding application structure
- ✅ CTF-style discovery methods

## Difficulty Balance

**Current Setup:**
- Not too easy (not displayed directly)
- Not too hard (clear hints provided)
- Encourages exploration
- Multiple discovery paths
- Appropriate for medium difficulty

**Result:**
Students learn valuable skills while still being able to progress through the challenge.

