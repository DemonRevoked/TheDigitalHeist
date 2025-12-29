const bcrypt = require("bcryptjs");

// Simple in-memory storage for the CTF
const _users = new Map();

// Seed user
(function seed() {
  const id = 1;
  _users.set(id, {
    id,
    email: "tokyo@mint.local",
    passwordHash: bcrypt.hashSync("tokyo123", 10)
  });
})();

function getUserByEmail(email) {
  const e = (email || "").toLowerCase().trim();
  for (const u of _users.values()) {
    if (u.email.toLowerCase() === e) return u;
  }
  return null;
}

async function setPasswordForUser(userId, newPassword) {
  const u = _users.get(userId);
  if (!u) throw new Error("no user");
  u.passwordHash = await bcrypt.hash(newPassword, 10);
}

const USERS = {
  async verifyPassword(userId, password) {
    const u = _users.get(userId);
    if (!u) return false;
    return bcrypt.compare(password, u.passwordHash);
  }
};

module.exports = { USERS, getUserByEmail, setPasswordForUser, _users };
