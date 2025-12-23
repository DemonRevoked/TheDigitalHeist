const { chromium } = require("playwright");

// The Professor's automated review system
const BASE_URL = process.env.BASE_URL || "http://web:3000";
const ADMIN_USER = process.env.ADMIN_USER || "admin";
const ADMIN_PASS = process.env.ADMIN_PASS || "admin123";
const BOT_INTERVAL_MS = Number(process.env.BOT_INTERVAL_MS || 8000);

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function run() {
  console.log(`[professor-bot] The Professor is monitoring the network. base=${BASE_URL} interval=${BOT_INTERVAL_MS}ms`);

  const browser = await chromium.launch({ args: ["--no-sandbox"] });
  const context = await browser.newContext();
  const page = await context.newPage();

  while (true) {
    try {
      // The Professor logs into his command center
      await page.goto(`${BASE_URL}/auth/login`, { waitUntil: "domcontentloaded", timeout: 30000 });
      await page.fill('input[name="username"]', ADMIN_USER);
      await page.fill('input[name="password"]', ADMIN_PASS);
      await page.click('button[type="submit"]');
      await page.waitForLoadState("domcontentloaded");

      // The Professor reviews all gang messages (this is where XSS executes)
      await page.goto(`${BASE_URL}/admin/tickets`, { waitUntil: "domcontentloaded", timeout: 30000 });

      // Give time for any injected JavaScript to execute and intercept secrets
      await sleep(2500);

      // Logout (best effort)
      await page.evaluate(() => {
        const form = document.querySelector('form[action="/auth/logout"]');
        if (form) form.submit();
      }).catch(() => {});

      console.log("[professor-bot] The Professor reviewed all messages");
    } catch (e) {
      console.log("[professor-bot] error:", (e && e.message) ? e.message : e);
    }

    await sleep(BOT_INTERVAL_MS);
  }
}

run().catch((e) => {
  console.error("[bot] fatal:", e);
  process.exit(1);
});
