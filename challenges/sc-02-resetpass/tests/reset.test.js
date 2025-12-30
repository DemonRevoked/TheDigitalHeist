const request = require("supertest");
const crypto = require("crypto");

// Ensure deterministic key/flag in tests (dotenv in server won't override existing env vars).
const fs = require("fs");
const os = require("os");
const path = require("path");

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "tdh-sc02-"));
const keyFile = path.join(tmpDir, "sc-02.key");
fs.writeFileSync(keyFile, "TEST_CHALLENGE_KEY_sc02_resetpass\n", "utf8");
process.env.KEY_SECRET_FILE = keyFile;
process.env.FLAG = "FLAG{TEST_FLAG_sc02_resetpass}";

const app = require("../src/server");
const { RESET_STORE } = require("../src/security/reset");

function sha256Hex(s) {
  return crypto.createHash("sha256").update(s, "utf8").digest("hex");
}

const EXPECTED_MESSAGE = "If the account exists, reset instructions have been issued.";

describe("Mint reset flow — secure coding requirements", () => {
  test("forgot-password must not enumerate", async () => {
    const r1 = await request(app).post("/forgot").type("form").send({ email: "tokyo@mint.local" });
    const r2 = await request(app).post("/forgot").type("form").send({ email: "ghost@mint.local" });

    expect(r1.status).toBe(200);
    expect(r2.status).toBe(200);

    expect(r1.text).toContain(EXPECTED_MESSAGE);
    expect(r2.text).toContain(EXPECTED_MESSAGE);
  });

  test("startup self-check must pass after fixes", async () => {
    const h = await request(app).get("/health");
    expect(h.body.ok).toBe(true);
    expect(h.body.secure).toBe(true);
  });

  test("forgotPassword must produce 64-hex token and store only token hash", async () => {
    const mod = require("../src/security/reset");
    const out = await mod.forgotPassword("tokyo@mint.local");

    expect(out.message).toBe(EXPECTED_MESSAGE);
    expect(out.token).toMatch(/^[0-9a-f]{64}$/i);

    expect(RESET_STORE.has(out.token)).toBe(false);

    const th = sha256Hex(out.token);
    expect(RESET_STORE.has(th)).toBe(true);

    const rec = RESET_STORE.get(th);
    expect(typeof rec.email).toBe("string");
    expect(typeof rec.expiresAt).toBe("number");
    expect(rec.expiresAt).toBeGreaterThan(Date.now());
  });

  test("token must be one-time use and expiry must be enforced", async () => {
    const mod = require("../src/security/reset");
    const out = await mod.forgotPassword("tokyo@mint.local");

    const ok = await mod.resetPassword(out.token, "newpass123");
    expect(ok.ok).toBe(true);

    const again = await mod.resetPassword(out.token, "newpass123");
    expect(again.ok).toBe(false);

    const th = sha256Hex(out.token);
    const rec = RESET_STORE.get(th);
    rec.expiresAt = Date.now() - 1000;

    const expired = await mod.resetPassword(out.token, "newpass123");
    expect(expired.ok).toBe(false);
  });

  test("mint key must be fetchable after secure self-check", async () => {
    const k = await request(app).get("/mint/key");
    expect(k.status).toBe(200);
    expect(k.text.trim()).toBe("TEST_CHALLENGE_KEY_sc02_resetpass");
  });

  test("mint flag must be fetchable with correct key", async () => {
    const keyResponse = await request(app).get("/mint/key");
    expect(keyResponse.status).toBe(200);
    const key = keyResponse.text.trim();

    const flagResponse1 = await request(app).get(`/mint/flag?key=${encodeURIComponent(key)}`);
    expect(flagResponse1.status).toBe(200);
    expect(flagResponse1.text.trim()).toBe(process.env.FLAG);

    const flagResponse2 = await request(app).post("/mint/flag").send({ key });
    expect(flagResponse2.status).toBe(200);
    expect(flagResponse2.text.trim()).toBe(process.env.FLAG);

    const invalidResponse = await request(app).get("/mint/flag?key=invalid_key");
    expect(invalidResponse.status).toBe(403);
    expect(invalidResponse.text).toBe("Invalid key");
  });
});
