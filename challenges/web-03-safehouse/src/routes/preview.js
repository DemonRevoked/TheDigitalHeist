const express = require("express");
const router = express.Router();
const fetch = require("node-fetch");

// Naive allowlist domain
const ALLOWLIST_MARKER = "previewme.com";

function naiveValidate(urlStr) {
  // INTENTIONAL FLAW:
  // - only checks string contains allowlist marker
  // - "extracts host" using naive string split (breaks with userinfo @)
  // - blocks localhost/127 only in extracted host, not in actual parsed hostname
  if (typeof urlStr !== "string" || urlStr.length > 2048) return { ok: false, reason: "❌ Invalid network endpoint format. The Professor's security system rejected your request." };
  if (!urlStr.includes(ALLOWLIST_MARKER)) return { ok: false, reason: "⚠️ Security Protocol: Only surveillance targets from previewme.com are allowed by the Professor's system." };

  const afterScheme = urlStr.split("://")[1] || "";
  const hostPort = afterScheme.split("/")[0] || "";
  const hostOnly = hostPort.split(":")[0];

  // Reveal extracted host in error message for debugging (helps students understand the flaw)
  const blocked = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"];
  if (blocked.some(b => hostOnly.includes(b))) {
    return { ok: false, reason: "🚫 Blocked: Local network access is restricted by security protocols." };
  }

  return { ok: true, hostOnly };
}

router.get("/", (req, res) => res.render("preview", { user: req.user, result: null, error: null }));

router.post("/", async (req, res) => {
  const url = (req.body.url || "").trim();

  const v = naiveValidate(url);
  if (!v.ok) return res.render("preview", { user: req.user, result: null, error: v.reason });

  try {
    const r = await fetch(url, { redirect: "follow", timeout: 8000 });
    let body = await r.text();
    const contentType = r.headers.get("content-type") || "unknown";
    
    // Inject subtle hint about internal-admin:8080 in the response
    if (contentType.includes("text/html")) {
      // Add as HTML comment at the beginning
      body = `<!-- Network Configuration: Internal vault server accessible at internal-admin:8080 on safe house network -->\n${body}`;
    } else if (contentType.includes("text/plain") || contentType.includes("text")) {
      // Add as a comment line for text responses
      body = `# Internal Network Reference: internal-admin:8080\n${body}`;
    } else {
      // For other content types, prepend a subtle hint
      body = `[Network Config: internal-admin:8080]\n${body}`;
    }
    
    res.render("preview", {
      user: req.user,
      error: null,
      result: {
        status: r.status,
        contentType: contentType,
        body: body.slice(0, 3000)
      }
    });
  } catch (e) {
    res.render("preview", { user: req.user, result: null, error: `❌ Network scan failed: ${e.message || "Connection error"}` });
  }
});

module.exports = router;
