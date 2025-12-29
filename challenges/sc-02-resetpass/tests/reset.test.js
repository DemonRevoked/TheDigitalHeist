const request = require("supertest");
const crypto = require("crypto");

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
    expect(k.text.trim().length).toBeGreaterThan(10);
    // Key should be 64 hex characters (HMAC-SHA256 output)
    expect(k.text.trim()).toMatch(/^[0-9a-f]{64}$/i);
  });

  test("mint flag must be fetchable with correct key from same session", async () => {
    // Create an agent to maintain cookies/session across requests
    const agent = request.agent(app);
    
    // First get the key (this creates/uses a session)
    const keyResponse = await agent.get("/mint/key");
    expect(keyResponse.status).toBe(200);
    const key = keyResponse.text.trim();
    expect(key.length).toBe(64);

    // Use the key to get the flag (via query parameter) - same session
    const flagResponse1 = await agent.get(`/mint/flag?key=${key}`);
    expect(flagResponse1.status).toBe(200);
    expect(flagResponse1.text.trim().length).toBeGreaterThan(10);

    // Use the key to get the flag (via POST body) - same session
    const flagResponse2 = await agent.post("/mint/flag").send({ key });
    expect(flagResponse2.status).toBe(200);
    expect(flagResponse2.text.trim()).toBe(flagResponse1.text.trim());

    // Invalid key should fail (even with same session)
    const invalidResponse = await agent.get("/mint/flag?key=invalid_key");
    expect(invalidResponse.status).toBe(403);
    expect(invalidResponse.text).toBe("Invalid key");
  });

  test("mint flag rejects key from different session", async () => {
    // Create two different agents (different sessions)
    const agent1 = request.agent(app);
    const agent2 = request.agent(app);
    
    // Get key from session 1
    const keyResponse1 = await agent1.get("/mint/key");
    expect(keyResponse1.status).toBe(200);
    const key1 = keyResponse1.text.trim();
    
    // Get key from session 2 (should be different)
    const keyResponse2 = await agent2.get("/mint/key");
    expect(keyResponse2.status).toBe(200);
    const key2 = keyResponse2.text.trim();
    
    // Keys should be different (different sessions)
    expect(key1).not.toBe(key2);
    
    // Key from session 1 should not work in session 2
    const crossSessionResponse = await agent2.get(`/mint/flag?key=${key1}`);
    expect(crossSessionResponse.status).toBe(403);
    expect(crossSessionResponse.text).toBe("Invalid key");
    
    // Each key should work in its own session
    const validResponse1 = await agent1.get(`/mint/flag?key=${key1}`);
    expect(validResponse1.status).toBe(200);
    
    const validResponse2 = await agent2.get(`/mint/flag?key=${key2}`);
    expect(validResponse2.status).toBe(200);
  });
});
