require("dotenv").config();
const express = require("express");
const session = require("express-session");
const path = require("path");
const fs = require("fs");
const PgSession = require("connect-pg-simple")(session);

const { pool, initDb } = require("./storage/db");
const authRoutes = require("./routes/auth");
const { requireLogin, requireAdmin } = require("./routes/middleware");

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "..", "views"));

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, "..", "public")));

app.use(session({
  store: new PgSession({ pool, createTableIfMissing: true }),
  secret: process.env.SESSION_SECRET || "dev-secret",
  resave: false,
  saveUninitialized: false,
  cookie: { httpOnly: true }
}));

app.use((req, _res, next) => {
  req.user = req.session.user || null;
  next();
});

app.get("/", (req, res) => res.render("index", { user: req.user }));

app.use("/auth", authRoutes);

// Message submission (gang members send messages to The Professor)
app.get("/tickets/new", requireLogin, (req, res) => res.render("new_ticket", { user: req.user, msg: null }));
app.post("/tickets/new", requireLogin, async (req, res) => {
  const { subject, message } = req.body;
  await pool.query(
    "INSERT INTO tickets (user_id, subject, message) VALUES ($1, $2, $3)",
    [req.user.id, subject || "(no subject)", message || ""]
  );
  res.render("new_ticket", { user: req.user, msg: "Message sent. The Professor will review it shortly." });
});

// Intercepted intelligence page (where players see captured data)
app.get("/my-captures", requireLogin, async (req, res) => {
  const { rows } = await pool.query(
    "SELECT id, captured_at, data FROM captures WHERE user_id = $1 ORDER BY id DESC LIMIT 50",
    [req.user.id]
  );
  res.render("captures", { user: req.user, captures: rows });
});

// Collector endpoint (where XSS payloads exfiltrate The Professor's secrets)
app.post("/collector", async (req, res) => {
  // Collector is intentionally simple; in real apps you'd authenticate/authorize properly.
  // We tie captures to a user_id passed in the request for CTF convenience.
  const { user_id, data } = req.body || {};
  
  console.log(`[collector] Received request: user_id=${user_id}, data length=${data ? data.length : 0}, data preview=${data ? data.substring(0, 100) : 'null'}`);
  
  if (!user_id || typeof data !== "string") {
    console.log(`[collector] Invalid request: user_id=${user_id}, data type=${typeof data}`);
    return res.status(400).json({ ok: false });
  }
  
  const userId = Number(user_id);
  
  // Check if this is a flag (contains FLAG{ or flag{ - case insensitive)
  const isFlag = /flag\{/i.test(data);
  
  if (isFlag) {
    console.log(`[collector] ✓ Flag detected for user_id=${userId}: ${data.substring(0, 50)}...`);
    // Check if user already has this exact flag captured
    const existing = await pool.query(
      "SELECT id FROM captures WHERE user_id = $1 AND data = $2 LIMIT 1",
      [userId, data]
    );
    
    if (existing.rows.length > 0) {
      // Flag already captured, don't insert duplicate
      console.log(`[collector] Flag already captured for user_id=${userId}`);
      return res.json({ ok: true, message: "Flag already captured" });
    }
  }
  
  // Insert new capture (either first flag capture or non-flag data)
  await pool.query("INSERT INTO captures (user_id, data) VALUES ($1, $2)", [userId, data]);
  console.log(`[collector] Captured data for user_id=${userId}, isFlag=${isFlag}`);
  res.json({ ok: true });
});

// The Professor's dashboard (where he reviews all gang messages)
app.get("/admin/tickets", requireLogin, requireAdmin, async (req, res) => {
  const { rows } = await pool.query(`
    SELECT t.id, t.subject, t.message, u.username
    FROM tickets t JOIN users u ON u.id = t.user_id
    ORDER BY t.id DESC LIMIT 30
  `);
  res.render("admin_tickets", { user: req.user, tickets: rows });
});

// The Professor's master plan (admin-only secret endpoint)
app.get("/admin/flag", requireLogin, requireAdmin, (_req, res) => {
  const flag = process.env.FLAG || "FLAG{missing_flag_env}";

  // Challenge key is dynamic per restart; always read it from the mounted file.
  const keyFile = process.env.CHALLENGE_KEY_FILE;
  if (!keyFile || !fs.existsSync(keyFile)) {
    return res
      .status(500)
      .type("text/plain")
      .send("Server misconfigured: missing CHALLENGE_KEY_FILE mount");
  }
  const challengeKey = fs.readFileSync(keyFile, "utf8").trim();
  if (!challengeKey) {
    return res
      .status(500)
      .type("text/plain")
      .send("Server misconfigured: empty challenge key file");
  }

  // Return key right next to the flag so bot/XSS exfil captures both.
  res.type("text/plain").send(`${flag} ${challengeKey}`);
});

// Reset endpoint (for CTF management - clears tickets and captures)
app.post("/admin/reset", requireLogin, requireAdmin, async (_req, res) => {
  try {
    await pool.query("TRUNCATE TABLE tickets, captures RESTART IDENTITY CASCADE");
    res.json({ ok: true, message: "Challenge data reset successfully" });
  } catch (e) {
    res.status(500).json({ ok: false, error: e.message });
  }
});

const port = Number(process.env.PORT || 3000);

initDb()
  .then(() => {
    app.listen(port, () => console.log(`[xss] listening on ${port}`));
  })
  .catch((e) => {
    console.error("DB init failed:", e);
    process.exit(1);
  });
