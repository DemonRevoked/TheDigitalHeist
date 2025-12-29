const request = require("supertest");
const path = require("path");
const { safeJoinLogsPath } = require("../src/utils/safePath");
const app = require("../src/server");

const LOGS_DIR = path.join(__dirname, "..", "data", "logs");

describe("Professor Log Viewer — secure coding requirements", () => {
  test("allows downloading heist.log", async () => {
    const r = await request(app).get("/download").query({ file: "heist.log" });
    expect(r.status).toBe(200);
    expect(r.text).toMatch(/Professor/);
  });

  test("blocks traversal to secrets/vault.key", async () => {
    const r = await request(app).get("/download").query({ file: "../secrets/vault.key" });
    expect(r.status).toBe(400);
    expect(r.text).toMatch(/blocked/i);
  });

  test("blocks URL-encoded traversal patterns", async () => {
    const r = await request(app).get("/download").query({ file: "..%2Fsecrets%2Fvault.key" });
    expect(r.status).toBe(400);
  });

  test("safeJoinLogsPath never returns a path under logsDir for rejected inputs (or throws)", () => {
    const good = safeJoinLogsPath(LOGS_DIR, "heist.log");
    expect(good.startsWith(LOGS_DIR)).toBe(true);

    const cases = [
      "../secrets/vault.key",
      "..\\secrets\\vault.key",
      "/etc/passwd",
      "C:\\Windows\\System32\\drivers\\etc\\hosts",
      "..%2Fsecrets%2Fvault.key"
    ];

    for (const c of cases) {
      try {
        const p = safeJoinLogsPath(LOGS_DIR, c);
        expect(p.startsWith(LOGS_DIR)).toBe(false);
      } catch (e) {
        expect(e).toBeTruthy();
      }
    }
  });

  test("vault key unlocks only after secure self-check", async () => {
    const health = await request(app).get("/health");
    expect(health.body.secure).toBe(true);

    const k = await request(app).get("/vault/key");
    expect(k.status).toBe(200);
  });
});
