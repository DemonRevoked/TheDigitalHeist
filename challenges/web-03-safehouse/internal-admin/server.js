const express = require("express");
const fs = require("fs");
const app = express();

// Read challenge key from file if provided, otherwise use env var
function getChallengeKey() {
  const keyFile = process.env.CHALLENGE_KEY_FILE;
  if (keyFile && fs.existsSync(keyFile)) {
    try {
      const key = fs.readFileSync(keyFile, 'utf8').trim();
      console.log(`✓ Challenge key loaded from file: ${keyFile}`);
      console.log(`✓ Key value: ${key}`);
      return key;
    } catch (err) {
      console.error('Failed to read challenge key file:', err);
    }
  }
  throw new Error(
    "Server misconfigured: missing/invalid CHALLENGE_KEY_FILE mount for internal-admin"
  );
}

app.get("/", (_req, res) => {
  res.type("text/plain").send("🎭 Professor's Hidden Vault - Access Restricted\n\nThe escape route coordinates are secured. Present your security key to access the rendezvous point data.");
});

app.get("/flag", (req, res) => {
  const token = req.query.token || "";
  if (token !== (process.env.INTERNAL_TOKEN || "")) {
    return res.status(403).type("text/plain").send("❌ Access Denied. Invalid security key. The Professor's vault is impenetrable.");
  }
  const challengeKey = getChallengeKey();
  const flag = process.env.FLAG || "TDHCTF{missing_flag_env}";
  res.type("text/plain").send(`${flag} | Key: ${challengeKey}`);
});

app.listen(8080, () => console.log("[internal-admin] listening on 8080"));
