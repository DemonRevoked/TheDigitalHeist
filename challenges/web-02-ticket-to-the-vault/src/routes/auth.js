const express = require("express");
const bcrypt = require("bcryptjs");
const { pool } = require("../storage/db");

const router = express.Router();

router.get("/login", (req, res) => res.render("login", { error: null }));

router.post("/login", async (req, res) => {
  const { username, password } = req.body;
  const { rows } = await pool.query("SELECT * FROM users WHERE username=$1", [username]);
  const user = rows[0];
  if (!user) return res.status(401).render("login", { error: "Invalid credentials" });

  const ok = await bcrypt.compare(password, user.password_hash);
  if (!ok) return res.status(401).render("login", { error: "Invalid credentials" });

  req.session.user = { id: user.id, username: user.username, role: user.role };
  res.redirect("/");
});

router.post("/logout", (req, res) => {
  req.session.destroy(() => res.redirect("/"));
});

module.exports = router;
