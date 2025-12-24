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

  // Set up network request monitoring (before any navigation)
  let flagRequestMade = false;
  let collectorRequestMade = false;
  
  page.on('request', (request) => {
    const url = request.url();
    const method = request.method();
    // Log all requests to help debug
    if (url.includes('/collector') || url.includes('/admin/flag') || url.includes('flag')) {
      console.log(`[professor-bot] Detected request: ${method} ${url}`);
      if (url.includes('/admin/flag') || (url.includes('flag') && method === 'GET')) {
        flagRequestMade = true;
        console.log(`[professor-bot] ✓ Flag request detected!`);
      }
      if (url.includes('/collector') && method === 'POST') {
        collectorRequestMade = true;
        console.log(`[professor-bot] ✓ Collector request detected!`);
      }
    }
  });
  
  // Also monitor all fetch/XHR requests via page evaluation
  page.on('response', async (response) => {
    const url = response.url();
    const status = response.status();
    if (url.includes('/admin/flag')) {
      flagRequestMade = true;
      console.log(`[professor-bot] ✓ Flag endpoint accessed: ${status} ${url}`);
      try {
        const text = await response.text();
        console.log(`[professor-bot] Flag content received: ${text.substring(0, 50)}...`);
      } catch (e) {
        // Response already consumed
      }
    }
  });

  page.on('response', async (response) => {
    const url = response.url();
    const status = response.status();
    if (url.includes('/admin/flag')) {
      flagRequestMade = true;
      console.log(`[professor-bot] ✓ Flag endpoint accessed: ${status} ${url}`);
      if (status === 200) {
        try {
          const text = await response.text();
          console.log(`[professor-bot] Flag content received: ${text.substring(0, 50)}...`);
        } catch (e) {
          // Response already consumed or error
        }
      }
    }
    if (url.includes('/collector')) {
      console.log(`[professor-bot] Response: ${status} ${url}`);
    }
  });

  // Log all console messages (helps debug XSS execution)
  page.on('console', (msg) => {
    const text = msg.text();
    const type = msg.type();
    if (type === 'error' || text.includes('fetch') || text.includes('collector') || text.includes('flag')) {
      console.log(`[professor-bot] Console [${type}]: ${text}`);
    }
  });

  // Log page errors
  page.on('pageerror', (error) => {
    console.log(`[professor-bot] Page error: ${error.message}`);
  });

  while (true) {
    try {
      // The Professor logs into his command center
      await page.goto(`${BASE_URL}/auth/login`, { waitUntil: "domcontentloaded", timeout: 30000 });
      await page.fill('input[name="username"]', ADMIN_USER);
      await page.fill('input[name="password"]', ADMIN_PASS);
      await page.click('button[type="submit"]');
      await page.waitForLoadState("domcontentloaded");

      // Reset flags for this cycle
      flagRequestMade = false;
      collectorRequestMade = false;

      // The Professor reviews all gang messages (this is where XSS executes)
      await page.goto(`${BASE_URL}/admin/tickets`, { waitUntil: "load", timeout: 30000 });
      
      // Wait for page to fully load including scripts
      await page.waitForLoadState("load");
      
      // Wait for scripts to execute and network requests to complete
      // XSS payloads need time to: fetch('/admin/flag') -> then POST to /collector
      let waitCount = 0;
      const maxWaits = 15; // Wait up to 15 seconds for requests
      while (waitCount < maxWaits && (!flagRequestMade || !collectorRequestMade)) {
        await sleep(1000);
        waitCount++;
        if (waitCount % 3 === 0) {
          console.log(`[professor-bot] Waiting for requests... (${waitCount}s) flag=${flagRequestMade} collector=${collectorRequestMade}`);
        }
      }
      
      // Give additional time for the collector request to complete
      await sleep(3000);
      
      // Wait for network to be completely idle (all requests completed)
      try {
        await page.waitForLoadState("networkidle", { timeout: 5000 });
      } catch (e) {
        // Ignore timeout - proceed anyway
        console.log("[professor-bot] Network idle timeout, proceeding anyway");
      }
      
      if (flagRequestMade && collectorRequestMade) {
        console.log("[professor-bot] ✓ Flag exfiltration detected!");
      } else {
        console.log(`[professor-bot] ⚠ Flag request: ${flagRequestMade}, Collector request: ${collectorRequestMade}`);
      }

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
