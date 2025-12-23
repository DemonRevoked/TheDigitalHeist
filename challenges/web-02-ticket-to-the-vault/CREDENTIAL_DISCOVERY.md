# How to Discover Credentials

## Discovery Methods

Students need to find the credentials through code analysis. Here are the methods:

### Method 1: Source Code Analysis (Primary)

**File to check:** `src/storage/db.js`

This file initializes the database and creates default users. The credentials are in comments and code:

```javascript
// Tokyo's credentials: username="tokyo", password="rio123"
// The Professor's credentials: username="admin", password="admin123"
const users = [
  { username: "tokyo", password: "rio123", role: "user" },
  { username: "admin", password: "admin123", role: "admin" }
];
```

**How students find it:**
1. They see the hint on login page: "Check files in src/ directory"
2. They explore the codebase structure
3. They find `src/storage/db.js` (database initialization)
4. They read the file and see the credentials in comments/code

### Method 2: File Exploration

**File:** `CREDENTIALS.md` (in root directory)

This file contains the credentials explicitly, but students need to:
1. List files in the directory
2. Notice `CREDENTIALS.md`
3. Read it to find credentials

### Method 3: Code Comments

**Files with hints:**
- `src/server.js` - Has comment pointing to credentials
- `bot/bot.js` - Has comment mentioning where credentials are

**Discovery path:**
1. Students might check bot code to understand how it works
2. See comment: "Default credentials are in src/storage/db.js"
3. Follow the hint to find credentials

### Method 4: Grep/Search

Students can search for keywords:
```bash
grep -r "tokyo" src/
grep -r "rio123" src/
grep -r "username.*password" src/
```

## Hints Provided

1. **Login Page:** Points to `src/` directory and database files
2. **README:** Explains discovery methods
3. **Source Code Comments:** Direct references in code
4. **File Structure:** CREDENTIALS.md file exists

## Difficulty Assessment

**Current:** Medium
- Requires code analysis
- Hints guide without giving away
- Multiple discovery paths
- Encourages exploration

## Expected Student Behavior

1. See login page → Need credentials
2. Read hint → "Check src/ directory"
3. Explore codebase → Find `src/storage/db.js`
4. Read file → See credentials in comments
5. Use credentials → Login as Tokyo

This teaches:
- Source code analysis
- File exploration
- Reading code comments
- Following hints

