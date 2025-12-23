const { Pool } = require("pg");
const bcrypt = require("bcryptjs");

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

async function initDb() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      role TEXT NOT NULL DEFAULT 'user'
    );
  `);

  await pool.query(`
    CREATE TABLE IF NOT EXISTS invoices (
      id INTEGER PRIMARY KEY,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      amount INTEGER NOT NULL,
      note TEXT NOT NULL
    );
  `);

  // Seed only if empty
  const c = await pool.query("SELECT COUNT(*)::int AS n FROM users");
  if (c.rows[0].n > 0) return;

  const users = [
    { username: "oslo", password: "oslo123", role: "user" },
    { username: "helsinki", password: "helsinki123", role: "user" },
    { username: "Raquel", password: "admin123", role: "admin" }
  ];

  for (const u of users) {
    const hash = await bcrypt.hash(u.password, 10);
    await pool.query(
      "INSERT INTO users (username, password_hash, role) VALUES ($1, $2, $3)",
      [u.username, hash, u.role]
    );
  }

  const oslo = (await pool.query("SELECT id FROM users WHERE username='oslo'")).rows[0].id;
  const helsinki = (await pool.query("SELECT id FROM users WHERE username='helsinki'")).rows[0].id;

  // Oslo invoices (low IDs)
  for (let i = 1001; i <= 1010; i++) {
    await pool.query(
      "INSERT INTO invoices (id, user_id, amount, note) VALUES ($1, $2, $3, $4)",
      [i, oslo, 99 + (i - 1001), "Subscription renewal"]
    );
  }

  // Helsinki invoices (includes the flag invoice at 1057)
  for (let i = 1050; i <= 1060; i++) {
    const note = (i === 1057)
      ? `Quarterly billing note: ${process.env.FLAG || "FLAG{missing_flag_env}"}`
      : "Quarterly billing note: processed";
    await pool.query(
      "INSERT INTO invoices (id, user_id, amount, note) VALUES ($1, $2, $3, $4)",
      [i, helsinki, 199 + (i - 1050), note]
    );
  }
}

module.exports = { pool, initDb };
