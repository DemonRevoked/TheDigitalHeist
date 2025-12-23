const express = require("express");
const bcrypt = require("bcryptjs");
const { pool } = require("../storage/db");

const router = express.Router();

router.get("/login", (req, res) => res.render("login", { error: null }));

// VULNERABLE: Username check endpoint for SQL injection enumeration
// Payloads for username enumeration:
// GET /auth/check?username=' UNION SELECT username FROM users--
// GET /auth/check?username=' OR '1'='1' UNION SELECT username FROM users--
router.get("/check", async (req, res) => {
  const { username } = req.query;
  
  if (!username) {
    return res.status(400).json({ error: "Username parameter required" });
  }
  
  // Check if UNION is being used
  if (username.toLowerCase().includes('union')) {
    try {
      const unionQuery = `SELECT username FROM users WHERE '1'='2' UNION SELECT username FROM users`;
      const { rows: unionRows } = await pool.query(unionQuery);
      if (unionRows.length > 0) {
        const usernames = unionRows.map(row => row.username).filter((v, i, a) => a.indexOf(v) === i);
        return res.json({ exists: true, users: usernames });
      }
    } catch (e) {
      // Fall through
    }
  }
  
  try {
    // VULNERABLE: SQL Injection - string concatenation allows UNION-based enumeration
    const query = `SELECT username FROM users WHERE username='${username}'`;
    const { rows } = await pool.query(query);
    
    if (rows.length > 0) {
      // If UNION injection returned multiple users, return all
      if (rows.length > 1) {
        const usernames = rows.map(row => row.username).filter((v, i, a) => a.indexOf(v) === i);
        return res.json({ exists: true, users: usernames });
      }
      return res.json({ exists: true, username: rows[0].username });
    }
    
    return res.json({ exists: false });
  } catch (error) {
    // SQL error - return generic error
    return res.status(400).json({ 
      error: "SQL Error" 
    });
  }
});

router.post("/login", async (req, res) => {
  const { username, password } = req.body;
  
  // VULNERABLE: SQL Injection - using string concatenation instead of parameterized queries
  // This allows:
  // 1. Bypassing authentication with payloads like:
  //    - Username: Raquel'-- 
  //    - Username: oslo'-- 
  //    - Username: ' OR '1'='1'--
  //    - Password: (anything, will be commented out)
  // 2. Username enumeration with UNION-based SQL injection:
  //    - Username: ' OR '1'='2' UNION SELECT NULL::integer, username, NULL::text, NULL::text FROM users--
  //    - Username: ' UNION SELECT NULL, username, NULL, NULL FROM users--
  //    - Password: (anything)
  //    This will return all usernames in the error message
  // NOTE: Helsinki's account is restricted and cannot be logged into directly
  try {
    // Vulnerable query - allows SQL injection to bypass password check and enumerate usernames
    // The query structure: SELECT * FROM users WHERE username='...' AND password_hash='...'
    // SELECT * returns 4 columns: id (integer), username (text), password_hash (text), role (text)
    const query = `SELECT * FROM users WHERE username='${username}' AND password_hash='${password}'`;
    const { rows } = await pool.query(query);
    
    if (rows.length > 0) {
      // Check if this is a UNION-based enumeration attempt (multiple rows returned)
      if (rows.length > 1) {
        // Extract unique usernames from UNION result
        const usernames = rows.map(row => row.username).filter((v, i, a) => a.indexOf(v) === i);
        const userList = usernames.join(', ');
        
        // Return usernames in response for enumeration
        if (req.headers['content-type']?.includes('application/json')) {
          return res.status(401).json({ 
            error: "Invalid credentials", 
            hint: `Users found: ${userList}` 
          });
        }
        return res.status(401).render("login", { 
          error: `Invalid credentials. Users found: ${userList}` 
        });
      }
      
      // Single user found (either legitimate or via SQL injection)
      const user = rows[0];
      
      // Prevent Helsinki from logging in - their account is restricted
      // Students must use SQL injection to log in as Oslo, then exploit IDOR to access Helsinki's invoices
      if (user.username.toLowerCase() === 'helsinki') {
        if (req.headers['content-type']?.includes('application/json')) {
          return res.status(403).json({ error: "Account access restricted" });
        }
        return res.status(403).render("login", { error: "Account access restricted" });
      }
      
      req.session.user = { id: user.id, username: user.username, role: user.role };
      
      if (req.headers['content-type']?.includes('application/json')) {
        return res.json({ success: true, user: req.session.user });
      }
      return res.redirect("/me");
    }
    
    // If no user found but UNION was in the payload, try to extract usernames
    if (username.toLowerCase().includes('union')) {
      try {
        // Execute the actual UNION query from the payload to get usernames
        // The payload format: ' OR '1'='2' UNION SELECT ... FROM users--
        // We'll construct a working UNION query
        const unionQuery = `SELECT * FROM users WHERE '1'='2' UNION SELECT id, username, password_hash, role FROM users`;
        const { rows: unionRows } = await pool.query(unionQuery);
        if (unionRows.length > 0) {
          const usernames = unionRows.map(row => row.username).filter((v, i, a) => a.indexOf(v) === i);
          const userList = usernames.join(', ');
          if (req.headers['content-type']?.includes('application/json')) {
            return res.status(401).json({ 
              error: "Invalid credentials", 
              hint: `Users found: ${userList}` 
            });
          }
          return res.status(401).render("login", { 
            error: `Invalid credentials. Users found: ${userList}` 
          });
        }
      } catch (unionError) {
        // If UNION fails, continue to normal error
      }
    }
    
    // If no user found, return error
    if (req.headers['content-type']?.includes('application/json')) {
      return res.status(401).json({ error: "Invalid credentials" });
    }
    return res.status(401).render("login", { error: "Invalid credentials" });
  } catch (error) {
    // SQL error - check if UNION was attempted and try to extract usernames
    if (username.toLowerCase().includes('union')) {
      try {
        const unionQuery = `SELECT * FROM users WHERE '1'='2' UNION SELECT id, username, password_hash, role FROM users`;
        const { rows: unionRows } = await pool.query(unionQuery);
        if (unionRows.length > 0) {
          const usernames = unionRows.map(row => row.username).filter((v, i, a) => a.indexOf(v) === i);
          const userList = usernames.join(', ');
          if (req.headers['content-type']?.includes('application/json')) {
            return res.status(401).json({ 
              error: "Invalid credentials", 
              hint: `Users found: ${userList}` 
            });
          }
          return res.status(401).render("login", { 
            error: `Invalid credentials. Users found: ${userList}` 
          });
        }
      } catch (e) {
        // Provide hint if UNION fails
      }
    }
    
    // SQL error - return generic error message
    if (req.headers['content-type']?.includes('application/json')) {
      return res.status(400).json({ 
        error: "SQL Error" 
      });
    }
    return res.status(400).render("login", { 
      error: "SQL Error" 
    });
  }
});

router.post("/logout", (req, res) => {
  req.session.destroy(() => {
    if (req.headers['content-type']?.includes('application/json')) {
      return res.json({ success: true });
    }
    res.redirect("/");
  });
});

router.get("/current", (req, res) => {
  if (req.user) {
    return res.json({ user: req.user });
  }
  res.status(401).json({ error: "Not authenticated" });
});

module.exports = router;
