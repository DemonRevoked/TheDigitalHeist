/**
 * TODO (player): Replace this insecure reset flow with a secure one.
 *
 * Requirements (enforced by tests + startup self-check):
 * - Token generation: crypto.randomBytes(32).toString("hex")  -> 64 hex chars
 * - Store only hash(token) in memory (not raw token)
 * - Expiry: 15 minutes
 * - One-time use: invalidate token after successful reset
 * - Comparison: constant-time (crypto.timingSafeEqual) on fixed-size buffers
 * - Forgot-password response: non-enumerating (same message for known/unknown emails)
 *
 * Important: message must be exactly:
 * "If the account exists, reset instructions have been issued."
 *
 * Note: To edit this file, visit /editor in your browser.
 */

const crypto = require("crypto");
const { getUserByEmail } = require("../storage/users");

// In-memory reset store (should be keyed by tokenHash when fixed)
const RESET_STORE = new Map();

function insecureToken() {
  // VULNERABLE: predictable + too short
  return String(Math.floor(Math.random() * 1_000_000));
}

async function forgotPassword(email) {
  const user = getUserByEmail(email);

  // VULNERABLE: leaks user existence + wrong message
  if (!user) {
    return { message: "No account with that email." };
  }

  const token = insecureToken();

  // VULNERABLE: stores raw token as key, no expiry, reusable
  RESET_STORE.set(token, { email: user.email, used: false });

  // In real systems, email is sent. For CTF, returning token enables testing.
  return { message: "Reset link generated.", token };
}

async function resetPassword(token, newPassword) {
  const rec = RESET_STORE.get(String(token || ""));
  if (!rec) return { ok: false, error: "Invalid token" };
  if (rec.used) return { ok: false, error: "Token already used" };

  // VULNERABLE: no expiry enforcement
  rec.used = true;

  if (typeof newPassword !== "string" || newPassword.length < 6) {
    return { ok: false, error: "Weak password" };
  }

  return { ok: true, email: rec.email };
}

module.exports = { forgotPassword, resetPassword, RESET_STORE };
