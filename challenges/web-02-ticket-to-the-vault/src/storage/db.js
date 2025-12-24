const { Pool } = require("pg");
const bcrypt = require("bcryptjs");

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

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
    CREATE TABLE IF NOT EXISTS tickets (
      id SERIAL PRIMARY KEY,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      subject TEXT NOT NULL,
      message TEXT NOT NULL
    );
  `);

  await pool.query(`
    CREATE TABLE IF NOT EXISTS captures (
      id SERIAL PRIMARY KEY,
      user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      data TEXT NOT NULL
    );
  `);

  // Reset challenge data on startup if RESET_ON_STARTUP is set
  const resetOnStartup = process.env.RESET_ON_STARTUP === 'true' || process.env.RESET_ON_STARTUP === '1';
  if (resetOnStartup) {
    console.log('[db] Resetting challenge data (tickets and captures)...');
    await pool.query("TRUNCATE TABLE tickets, captures RESTART IDENTITY CASCADE");
    console.log('[db] Challenge data reset complete');
  }

  // Initialize default users for the challenge
  // Use INSERT ... ON CONFLICT to ensure users always exist with correct passwords
  // This handles cases where users might have been deleted or passwords changed
  const users = [
    { username: "tokyo", password: "rio123", role: "user" },
    { username: "admin", password: "admin123", role: "admin" }
  ];

  for (const u of users) {
    const hash = await bcrypt.hash(u.password, 10);
    // Use ON CONFLICT to update password if user exists, or insert if new
    await pool.query(
      `INSERT INTO users (username, password_hash, role) 
       VALUES ($1, $2, $3)
       ON CONFLICT (username) 
       DO UPDATE SET password_hash = $2, role = $3`,
      [u.username, hash, u.role]
    );
    console.log(`[db] Ensured user exists: ${u.username}`);
  }
}

module.exports = { pool, initDb };
