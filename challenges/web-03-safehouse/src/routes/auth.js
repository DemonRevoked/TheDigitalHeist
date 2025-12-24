const express = require("express");
const router = express.Router();

// Simple auth for CTF (no DB to keep this challenge focused on SSRF)
// Money Heist themed credentials
const USERS = {
  tokyo: { password: "tokyo123", role: "user" },
  alice: { password: "alice123", role: "user" } // Keep for backward compatibility
};

router.get("/login", (req, res) => res.render("login", { error: null }));

router.post("/login", (req, res) => {
  const { username, password } = req.body;
  const u = USERS[username];
  if (!u || u.password !== password) return res.status(401).render("login", { error: "Invalid credentials" });
  req.session.user = { id: 1, username, role: u.role };
  res.redirect("/settings");
});

router.post("/logout", (req, res) => {
  req.session.destroy(() => res.redirect("/"));
});

module.exports = router;
