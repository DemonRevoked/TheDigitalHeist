require("dotenv").config();
const express = require("express");
const path = require("path");
const fs = require("fs");

const { runStartupSelfCheck } = require("./utils/selfCheck");

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "..", "views"));
app.use(express.static(path.join(__dirname, "..", "public")));
app.use(express.json()); // For JSON body parsing
app.use(express.text({ type: 'text/plain' })); // For text body parsing

const LOGS_DIR = path.join(__dirname, "..", "data", "logs");

// Dynamic function to get current safeJoinLogsPath (allows hot-reloading)
function getSafeJoinLogsPath() {
  // Clear cache and re-require to get latest version
  delete require.cache[require.resolve("./utils/safePath")];
  const { safeJoinLogsPath } = require("./utils/safePath");
  return safeJoinLogsPath;
}

app.get("/", (_req, res) => {
  const files = fs.readdirSync(LOGS_DIR).filter(f => f.endsWith(".log"));
  
  // Read and parse log files for display
  const logs = files.map(file => {
    try {
      const content = fs.readFileSync(path.join(LOGS_DIR, file), "utf8");
      const lines = content.split('\n').filter(line => line.trim());
      return {
        filename: file,
        lines: lines.slice(0, 10), // First 10 lines for preview
        fullContent: content
      };
    } catch (err) {
      return {
        filename: file,
        lines: [],
        fullContent: ""
      };
    }
  });
  
  res.render("index", { files, logs });
});

app.get("/download", (req, res) => {
  const file = (req.query.file || "").toString();
  try {
    const safeJoinLogsPath = getSafeJoinLogsPath();
    const fullPath = safeJoinLogsPath(LOGS_DIR, file);
    const data = fs.readFileSync(fullPath, "utf8");
    res.type("text/plain").send(data);
  } catch {
    res.status(400).type("text/plain").send("blocked");
  }
});

app.get("/vault/key", (_req, res) => {
  if (!app.locals.secure) return res.status(403).type("text/plain").send("Lock engaged");
  res.type("text/plain").send(process.env.FLAG || "TDHCTF{BELLA_CIAO_NO_MORE_DOT_DOT_SLASH}");
});

app.get("/health", (_req, res) => res.json({ ok: true, secure: !!app.locals.secure }));

// robots.txt endpoint
app.get("/robots.txt", (_req, res) => {
  res.type("text/plain").send(`User-agent: *
Disallow: /vault/
Disallow: /source/
# Source code is hidden but accessible if you know where to look`);
});

// Hidden source code endpoints (not linked, but accessible if you know the path)
app.get("/source", (_req, res) => {
  const files = {
    "challenge_info.md": path.join(__dirname, "..", "CHALLENGE_INFO.md"),
    "server.js": path.join(__dirname, "server.js"),
    "safePath.js": path.join(__dirname, "utils", "safePath.js")
  };
  res.json({ message: "Source files available", files: Object.keys(files) });
});

app.get("/source/:file", (req, res) => {
  const fileMap = {
    "challenge_info": path.join(__dirname, "..", "CHALLENGE_INFO.md"),
    "challenge_info.md": path.join(__dirname, "..", "CHALLENGE_INFO.md"),
    "info": path.join(__dirname, "..", "CHALLENGE_INFO.md"),
    "readme": path.join(__dirname, "..", "CHALLENGE_INFO.md"), // Alias for backwards compatibility
    "server": path.join(__dirname, "server.js"),
    "server.js": path.join(__dirname, "server.js"),
    "safepath": path.join(__dirname, "utils", "safePath.js"),
    "safepath.js": path.join(__dirname, "utils", "safePath.js"),
    "safePath.js": path.join(__dirname, "utils", "safePath.js"),
    "safepathjs": path.join(__dirname, "utils", "safePath.js")
  };
  
  const fileName = req.params.file;
  // Try exact match first, then lowercase
  const filePath = fileMap[fileName] || fileMap[fileName.toLowerCase()];
  
  if (!filePath) {
    return res.status(404).type("text/plain").send("File not found. Available: challenge_info.md, server.js, safePath.js");
  }
  
  try {
    const content = fs.readFileSync(filePath, "utf8");
    res.type("text/plain").send(content);
  } catch (err) {
    res.status(500).type("text/plain").send(`Error reading file: ${err.message}`);
  }
});

// Code submission endpoint - allows students to submit their fix
app.post("/submit", (req, res) => {
  try {
    const code = req.body.code || req.body;
    
    if (!code || typeof code !== 'string') {
      return res.status(400).json({ 
        success: false, 
        error: "No code provided. Send your fixed safePath.js code in the request body." 
      });
    }

    // Validate that it looks like JavaScript code
    if (!code.includes('function') && !code.includes('module.exports')) {
      return res.status(400).json({ 
        success: false, 
        error: "Invalid code format. Please submit the complete safePath.js file content." 
      });
    }

    // Write the submitted code to safePath.js
    const safePathFile = path.join(__dirname, "utils", "safePath.js");
    fs.writeFileSync(safePathFile, code, "utf8");

    // Get the new function (getSafeJoinLogsPath handles cache clearing)
    let newSafeJoinLogsPath;
    try {
      newSafeJoinLogsPath = getSafeJoinLogsPath();
      
      // Test 1: Legitimate file should work
      const testResult = newSafeJoinLogsPath(LOGS_DIR, "heist.log");
      if (!testResult || typeof testResult !== 'string') {
        return res.status(400).json({ 
          success: false, 
          error: "Submitted code does not work correctly for legitimate files." 
        });
      }
      
      // Test 2: Traversal must be blocked (must throw)
      try {
        newSafeJoinLogsPath(LOGS_DIR, "../secrets/vault.key");
        // If we get here, traversal is NOT blocked
        return res.json({ 
          success: false, 
          message: "Code submitted, but path traversal is not blocked. Please fix your implementation.",
          secure: false,
          hint: "Your code must throw an error when path traversal is attempted."
        });
      } catch (traversalError) {
        // Perfect! Traversal is blocked and legitimate access works
        // Accept the fix
        app.locals.secure = true;
        return res.json({ 
          success: true, 
          message: "Code submitted successfully! The fix has been applied and validated.",
          secure: true,
          hint: "Try accessing /vault/key now!"
        });
      }
    } catch (err) {
      return res.status(400).json({ 
        success: false, 
        error: `Error loading submitted code: ${err.message}` 
      });
    }

    // Update the secure status
    app.locals.secure = isSecure;

    if (isSecure) {
      return res.json({ 
        success: true, 
        message: "Code submitted successfully! The fix has been applied and validated.",
        secure: true,
        hint: "Try accessing /vault/key now!"
      });
    } else {
      return res.json({ 
        success: false, 
        message: "Code submitted, but the fix doesn't pass security validation. Please check your implementation.",
        secure: false,
        hint: "Make sure your fix blocks all path traversal attempts while allowing legitimate file access."
      });
    }
  } catch (err) {
    return res.status(500).json({ 
      success: false, 
      error: `Error processing submission: ${err.message}` 
    });
  }
});

// Alternative: Submit via PUT to /source/safePath.js
app.put("/source/safePath.js", (req, res) => {
  try {
    const code = req.body.code || req.body;
    
    if (!code || typeof code !== 'string') {
      return res.status(400).json({ 
        success: false, 
        error: "No code provided. Send your fixed safePath.js code in the request body." 
      });
    }

    // Write the submitted code
    const safePathFile = path.join(__dirname, "utils", "safePath.js");
    fs.writeFileSync(safePathFile, code, "utf8");

    // Get the new function (getSafeJoinLogsPath handles cache clearing)
    const newSafeJoinLogsPath = getSafeJoinLogsPath();

    // Run self-check
    const isSecure = runStartupSelfCheck({ 
      safeJoinLogsPath: newSafeJoinLogsPath, 
      logsDir: LOGS_DIR 
    });

    app.locals.secure = isSecure;

    if (isSecure) {
      return res.json({ 
        success: true, 
        message: "Fix applied successfully! Security check passed.",
        secure: true
      });
    } else {
      return res.json({ 
        success: false, 
        message: "Fix applied, but security validation failed.",
        secure: false
      });
    }
  } catch (err) {
    return res.status(500).json({ 
      success: false, 
      error: err.message 
    });
  }
});

const port = Number(process.env.PORT || 3000);
app.locals.secure = runStartupSelfCheck({ safeJoinLogsPath: getSafeJoinLogsPath(), logsDir: LOGS_DIR });

app.listen(port, () => console.log(`[log-viewer] listening on ${port} secure=${app.locals.secure}`));

module.exports = app;
