require("dotenv").config();
const express = require("express");
const session = require("express-session");
const path = require("path");

const fs = require("fs");
const { runStartupSelfCheck } = require("./utils/selfCheck");
const { forgotPassword, resetPassword } = require("./security/reset");
const { USERS, getUserByEmail, setPasswordForUser } = require("./storage/users");
const { getSessionKey, validateSessionKey } = require("./utils/keyGenerator");

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "..", "views"));
app.use(express.static(path.join(__dirname, "..", "public")));

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(session({
  secret: "mint-session-secret",
  resave: false,
  saveUninitialized: true, // Enable to ensure each request gets a session ID for unique keys
  cookie: { httpOnly: true, sameSite: "lax" }
}));

app.use((req, _res, next) => {
  req.user = req.session.user || null;
  next();
});

app.get("/", (req, res) => res.render("index", { user: req.user }));

app.get("/login", (req, res) => res.render("login", { error: null }));
app.post("/login", async (req, res) => {
  const { email, password } = req.body;
  const u = getUserByEmail(email);
  if (!u) return res.status(401).render("login", { error: "Invalid credentials" });

  const ok = await USERS.verifyPassword(u.id, password);
  if (!ok) return res.status(401).render("login", { error: "Invalid credentials" });

  req.session.user = { id: u.id, email: u.email };
  res.redirect("/badge");
});

app.post("/logout", (req, res) => req.session.destroy(() => res.redirect("/")));

app.get("/badge", (req, res) => {
  if (!req.user) return res.redirect("/login");
  res.render("badge", { user: req.user, secure: !!app.locals.secure });
});

app.get("/forgot", (_req, res) => res.render("forgot", { msg: null }));
app.post("/forgot", async (req, res) => {
  const email = (req.body.email || "").toString();
  const out = await forgotPassword(email);
  res.render("forgot", { msg: out.message });
});

app.get("/reset", (_req, res) => res.render("reset", { error: null, msg: null }));
app.post("/reset", async (req, res) => {
  const { token, newPassword } = req.body;
  const result = await resetPassword(token, newPassword);
  if (!result.ok) return res.status(400).render("reset", { error: result.error, msg: null });

  const u = getUserByEmail(result.email);
  await setPasswordForUser(u.id, newPassword);

  res.render("reset", { error: null, msg: "Badge access updated. Proceed to the vault." });
});

app.get("/mint/key", (req, res) => {
  if (!app.locals.secure) return res.status(403).type("text/plain").send("Mint lockdown");
  
  // Get session ID (express-session creates this automatically)
  // req.sessionID is available even before req.session is created
  const sessionId = req.sessionID || "default";
  const secretKey = process.env.KEY_SECRET || "mint-key-secret";
  const uniqueKey = getSessionKey(sessionId, secretKey);
  
  res.type("text/plain").send(uniqueKey);
});

app.get("/mint/flag", (req, res) => {
  const providedKey = req.query.key || req.body.key || "";
  
  // Get session ID for validation
  const sessionId = req.sessionID || "default";
  const secretKey = process.env.KEY_SECRET || "mint-key-secret";
  
  if (!validateSessionKey(sessionId, providedKey, secretKey)) {
    return res.status(403).type("text/plain").send("Invalid key");
  }
  
  res.type("text/plain").send(process.env.FLAG || "FLAG{missing_env}");
});

app.post("/mint/flag", (req, res) => {
  const providedKey = req.query.key || req.body.key || "";
  
  // Get session ID for validation
  const sessionId = req.sessionID || "default";
  const secretKey = process.env.KEY_SECRET || "mint-key-secret";
  
  if (!validateSessionKey(sessionId, providedKey, secretKey)) {
    return res.status(403).type("text/plain").send("Invalid key");
  }
  
  res.type("text/plain").send(process.env.FLAG || "FLAG{missing_env}");
});

app.get("/health", (_req, res) => res.json({ ok: true, secure: !!app.locals.secure }));

// Code Editor Routes - Web-based file access
app.get("/editor", (_req, res) => {
  const resetFilePath = path.join(__dirname, "security", "reset.js");
  let fileContent = "";
  try {
    fileContent = fs.readFileSync(resetFilePath, "utf8");
  } catch (err) {
    fileContent = "// Error reading file";
  }
  res.render("editor", { 
    fileContent, 
    secure: !!app.locals.secure,
    filePath: "src/security/reset.js"
  });
});

app.get("/api/file", (_req, res) => {
  const resetFilePath = path.join(__dirname, "security", "reset.js");
  try {
    const fileContent = fs.readFileSync(resetFilePath, "utf8");
    res.json({ success: true, content: fileContent, path: "src/security/reset.js" });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post("/api/file", (req, res) => {
  const resetFilePath = path.join(__dirname, "security", "reset.js");
  const { content } = req.body;
  
  if (!content || typeof content !== "string") {
    return res.status(400).json({ success: false, error: "Invalid content" });
  }
  
  try {
    // Backup original file
    const backupPath = resetFilePath + ".backup." + Date.now();
    if (fs.existsSync(resetFilePath)) {
      fs.copyFileSync(resetFilePath, backupPath);
    }
    
    // Write new content
    fs.writeFileSync(resetFilePath, content, "utf8");
    
    // Clear ALL require caches related to reset and selfCheck
    const resetModulePath = require.resolve("./security/reset");
    const selfCheckModulePath = require.resolve("./utils/selfCheck");
    
    // Clear the modules from cache
    delete require.cache[resetModulePath];
    delete require.cache[selfCheckModulePath];
    
    // Clear the RESET_STORE by requiring fresh module
    const { RESET_STORE: FreshStore } = require("./security/reset");
    FreshStore.clear(); // Clear any old data
    
    // Re-require selfCheck to get fresh functions
    const { runStartupSelfCheck: freshSelfCheck } = require("./utils/selfCheck");
    
    // Re-run self-check with fresh modules
    freshSelfCheck().then(secure => {
      app.locals.secure = secure;
      if (secure) {
        res.json({ 
          success: true, 
          message: "File saved successfully!",
          secure: secure,
          backup: path.basename(backupPath)
        });
      } else {
        res.json({ 
          success: true, 
          message: "File saved, but security checks failed. Please review the requirements.",
          secure: false,
          backup: path.basename(backupPath),
          hint: "Check: message format, token generation, token hashing, expiry, one-time use"
        });
      }
    }).catch(err => {
      res.json({ 
        success: true, 
        message: "File saved but self-check error occurred",
        secure: false,
        error: err.message,
        stack: process.env.NODE_ENV === 'development' ? err.stack : undefined
      });
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get("/api/status", (_req, res) => {
  res.json({ 
    secure: !!app.locals.secure,
    timestamp: new Date().toISOString()
  });
});

app.post("/api/test", async (req, res) => {
  // Run a quick test by calling the functions directly
  try {
    // Force fresh require to get latest code
    const resetModulePath = require.resolve("./security/reset");
    const selfCheckPath = require.resolve("./utils/selfCheck");
    delete require.cache[resetModulePath];
    delete require.cache[selfCheckPath];
    
    const { forgotPassword: fp, resetPassword: rp, RESET_STORE } = require("./security/reset");
    
    // Clear store to start fresh
    RESET_STORE.clear();
    
    // Test forgotPassword
    const result1 = await fp("tokyo@mint.local");
    const result2 = await fp("nonexistent@test.com");
    
    // Run self-check to verify security
    const { runStartupSelfCheck: freshSelfCheck } = require("./utils/selfCheck");
    const isSecure = await freshSelfCheck();
    
    const tests = {
      messageConsistency: result1.message === result2.message,
      correctMessage: result1.message === "If the account exists, reset instructions have been issued.",
      tokenFormat: result1.token ? /^[0-9a-f]{64}$/i.test(result1.token) : false,
      secure: isSecure
    };
    
    const allPassed = Object.values(tests).every(v => v === true);
    
    // Only update app.locals.secure if ALL tests pass
    if (allPassed) {
      app.locals.secure = true;
    }
    
    res.json({ 
      success: true, 
      tests,
      allPassed: allPassed,
      secure: isSecure
    });
  } catch (err) {
    res.status(500).json({ 
      success: false, 
      error: err.message,
      stack: err.stack
    });
  }
});

const port = Number(process.env.PORT || 3000);

(async () => {
  app.locals.secure = await runStartupSelfCheck();
  app.listen(port, () => console.log(`[mint-reset] listening on ${port} secure=${app.locals.secure}`));
})();

module.exports = app;
