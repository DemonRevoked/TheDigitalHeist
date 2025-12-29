/**
 * Key generation system for per-student unique keys
 * Generates deterministic unique keys based on session ID using HMAC
 */

const crypto = require("crypto");

/**
 * Generate a unique key for a session
 * Uses HMAC-SHA256 with a secret key and session ID to ensure:
 * - Each session gets a unique key
 * - Keys are deterministic (same session ID = same key)
 * - Keys are cryptographically secure
 * 
 * @param {string} sessionId - The session ID
 * @param {string} secretKey - Secret key for HMAC (from environment)
 * @returns {string} Unique key for the session
 */
function generateSessionKey(sessionId, secretKey) {
  if (!sessionId) {
    // Fallback for cases without session (shouldn't happen in normal flow)
    sessionId = "default";
  }
  
  // Use HMAC to generate a deterministic but unique key per session
  const hmac = crypto.createHmac("sha256", secretKey || "mint-key-secret");
  hmac.update(sessionId);
  
  // Return the hex digest (64 characters)
  return hmac.digest("hex");
}

/**
 * Get or generate a key for a session
 * Stores the key in a Map for quick lookup during validation
 */
const KEY_STORE = new Map();

function getSessionKey(sessionId, secretKey) {
  if (!KEY_STORE.has(sessionId)) {
    const key = generateSessionKey(sessionId, secretKey);
    KEY_STORE.set(sessionId, key);
    return key;
  }
  return KEY_STORE.get(sessionId);
}

/**
 * Validate if a provided key matches the session's key
 * @param {string} sessionId - The session ID
 * @param {string} providedKey - The key provided by the user
 * @param {string} secretKey - Secret key for HMAC
 * @returns {boolean} True if key is valid for this session
 */
function validateSessionKey(sessionId, providedKey, secretKey) {
  if (!sessionId || !providedKey) {
    return false;
  }
  
  const expectedKey = generateSessionKey(sessionId, secretKey);
  return providedKey === expectedKey;
}

module.exports = {
  generateSessionKey,
  getSessionKey,
  validateSessionKey,
  KEY_STORE
};

