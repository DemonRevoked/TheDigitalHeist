const express = require("express");
const app = express();

app.get("/", (_req, res) => {
  res.type("text/plain").send("🎭 Professor's Hidden Vault - Access Restricted\n\nThe escape route coordinates are secured. Present your security key to access the rendezvous point data.");
});

app.get("/flag", (req, res) => {
  const token = req.query.token || "";
  if (token !== (process.env.INTERNAL_TOKEN || "")) {
    return res.status(403).type("text/plain").send("❌ Access Denied. Invalid security key. The Professor's vault is impenetrable.");
  }
  res.type("text/plain").send(process.env.FLAG || "FLAG{missing_flag_env}");
});

app.listen(8080, () => console.log("[internal-admin] listening on 8080"));
