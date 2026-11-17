// Headless test load (STYLE.md §10): Chromium opens viewer.html with the GLB, checks for console
// errors, plays the animation and takes a screenshot.
// Usage: node testload.mjs <file.glb> <screenshot.png> [anim=idle]   -> JSON on stdout
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const here = dirname(fileURLToPath(import.meta.url));
// anim "-" = static model: only check that it loads without errors.
const [glb, shot, anim = "idle", extra = "", held = ""] = process.argv.slice(2);  // extra: more viewer query, e.g. "look=soft"; held: a prop GLB parented to the hand (STYLE.md §9b)
const viewerDir = resolve(here, "..", "viewer");
const threeDir = resolve(here, "node_modules", "three");

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url, "http://x");
    let body, type = "application/octet-stream";
    if (url.pathname === "/" || url.pathname === "/viewer.html") { body = await readFile(join(viewerDir, "viewer.html")); type = "text/html"; }
    else if (url.pathname === "/model.glb") { body = await readFile(resolve(glb)); type = "model/gltf-binary"; }
    else if (url.pathname === "/held.glb" && held) { body = await readFile(resolve(held)); type = "model/gltf-binary"; }
    else { res.writeHead(404); return res.end(); }
    res.writeHead(200, { "content-type": type }); res.end(body);
  } catch (e) { res.writeHead(500); res.end(String(e)); }
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const port = server.address().port;

const result = { ok: false, console_errors: [], page_errors: [], animations: [], playing: null, screenshot: shot };
const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] });
try {
  const page = await browser.newPage({ viewport: { width: 768, height: 768 } });
  // three.js is served from node_modules instead of the CDN in the importmap (offline, pinned).
  await page.route(/https:\/\/unpkg\.com\/three@[^/]+\/(.*)/, async (route) => {
    const rel = route.request().url().replace(/https:\/\/unpkg\.com\/three@[^/]+\//, "");
    try { await route.fulfill({ body: await readFile(join(threeDir, rel)), contentType: "text/javascript" }); }
    catch { await route.fulfill({ status: 404 }); }
  });
  page.on("console", (m) => { if (m.type() === "error") result.console_errors.push(m.text()); });
  page.on("pageerror", (e) => result.page_errors.push(String(e)));
  const q = anim === "-" ? "" : `&anim=${encodeURIComponent(anim)}`;
  await page.goto(`http://127.0.0.1:${port}/viewer.html?model=/model.glb${q}${extra ? "&" + extra : ""}${held ? "&held=/held.glb" : ""}`);
  await page.waitForFunction(() => window.__viewer && (window.__viewer.loaded || window.__viewer.error), null, { timeout: 30000 });
  await page.waitForFunction(() => window.__viewer.time > 0.6 || window.__viewer.frames > 40, null, { timeout: 30000 }).catch(() => {});
  const st = await page.evaluate(() => window.__viewer);
  Object.assign(result, { animations: st.animations, playing: st.playing, height: st.height, time: +st.time.toFixed(2), load_error: st.error });
  await page.screenshot({ path: shot });
  const played = anim === "-" || (st.playing === anim && st.time > 0.5);
  result.ok = st.loaded && !st.error && played
    && result.console_errors.length === 0 && result.page_errors.length === 0;
} catch (e) {
  result.error = String(e);
} finally {
  await browser.close();
  server.close();
}
console.log(JSON.stringify(result));
