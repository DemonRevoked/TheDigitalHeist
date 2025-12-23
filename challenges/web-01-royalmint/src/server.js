require("dotenv").config();
const express = require("express");
const session = require("express-session");
const path = require("path");
const PgSession = require("connect-pg-simple")(session);

const { pool, initDb } = require("./storage/db");
const authRoutes = require("./routes/auth");
const invoiceRoutes = require("./routes/invoices");
const { requireLogin } = require("./routes/middleware");

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

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "..", "public", "index.html"));
});

app.use("/auth", authRoutes);
app.use("/invoices", requireLogin, invoiceRoutes);

app.get("/me", requireLogin, async (req, res) => {
  // Show user's invoice IDs to make the app feel realistic.
  const { rows } = await pool.query(
    "SELECT id, amount, note FROM invoices WHERE user_id = $1 ORDER BY id ASC LIMIT 20",
    [req.user.id]
  );
  
  if (req.headers['accept']?.includes('application/json') || req.query.format === 'json') {
    return res.json({ user: req.user, invoices: rows });
  }
  
  res.render("me", { user: req.user, invoices: rows });
});

const port = Number(process.env.PORT || 3000);

initDb()
  .then(() => {
    app.listen(port, () => console.log(`[idor] listening on ${port}`));
  })
  .catch((e) => {
    console.error("DB init failed:", e);
    process.exit(1);
  });
