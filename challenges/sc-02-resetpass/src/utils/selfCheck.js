const crypto = require("crypto");
const { forgotPassword, resetPassword, RESET_STORE } = require("../security/reset");

function isHex64(s) {
  return typeof s === "string" && /^[0-9a-f]{64}$/i.test(s);
}
function sha256Hex(s) {
  return crypto.createHash("sha256").update(s, "utf8").digest("hex");
}

async function runStartupSelfCheck() {
  try {
    // 1) Non-enumerating forgot-password message
    const r1 = await forgotPassword("tokyo@mint.local");
    const r2 = await forgotPassword("ghost@mint.local");
    if (!r1 || !r2 || typeof r1.message !== "string" || typeof r2.message !== "string") return false;
    if (r1.message !== r2.message) return false;

    // 2) Token must be 64-hex and returned for testing
    if (!isHex64(r1.token)) return false;
    const token = r1.token;

    // 3) Store must NOT contain raw token as key
    if (RESET_STORE.has(token)) return false;

    // 4) Must store hashed token with expiry
    const tokenHash = sha256Hex(token);
    const rec = RESET_STORE.get(tokenHash);
    if (!rec) return false;

    const now = Date.now();
    if (!rec.expiresAt || typeof rec.expiresAt !== "number") return false;
    if (rec.expiresAt <= now) return false;
    if (rec.expiresAt > now + (15 * 60 * 1000) + 2000) return false;

    // 5) reset invalid token must fail
    const bad = await resetPassword("00".repeat(32), "newpass123");
    if (bad.ok) return false;

    // 6) reset valid token must succeed
    const good = await resetPassword(token, "newpass123");
    if (!good.ok || good.email !== "tokyo@mint.local") return false;

    // 7) one-time use
    const again = await resetPassword(token, "newpass123");
    if (again.ok) return false;

    return true;
  } catch {
    return false;
  }
}

module.exports = { runStartupSelfCheck };
