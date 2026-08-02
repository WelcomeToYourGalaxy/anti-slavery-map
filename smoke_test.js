#!/usr/bin/env node
/**
 * smoke_test.js — run index.html for real and fail on any uncaught error.
 *
 *   npm install            (jsdom only)
 *   node smoke_test.js     (exit 1 on failure)
 *
 * This exists because of a specific bug. An edit to the facility-layer line
 * silently deleted `var facActive={...}` from the end of it. Every data check
 * still passed — the taxonomy validator compares data against the taxonomy, and
 * this was code — so a fatal ReferenceError shipped. Nothing short of executing
 * the page would have caught it.
 *
 * Leaflet and topojson are stubbed with a proxy that absorbs any call, and
 * fetch is stubbed to succeed with empty data. So this does not test that the
 * map looks right. It tests the thing that actually breaks: that every inline
 * script parses, runs top to bottom, and reaches the end without throwing.
 */
const fs = require("fs");
const path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

const VERSION = "smoke_test 2026-08-02c";   // bump when this file changes
const FILE = process.argv[2] || path.join(__dirname, "index.html");
console.log(VERSION + "  |  node " + process.version);
const WAIT = 3000;

let html = fs.readFileSync(FILE, "utf8");
// drop the CDN <script src> tags; the stub below stands in for them
html = html.replace(/<script src="https:\/\/cdnjs[^"]*"><\/script>/g, "");

const STUB = `<script>
(function(){
  window.__errs = [];
  function chain(){ return new Proxy(function(){}, {
    get: (t,p) => {
      if (p==='then'||p==='catch'||p==='finally') return undefined;
      if (p===Symbol.toPrimitive||p==='toString') return () => 'stub';
      return chain();
    },
    apply: () => chain(),
    construct: () => chain()
  }); }
  window.L = chain();
  window.topojson = { feature: () => ({ features: [] }) };
  window.__atlas = { objects: { countries: {} } };
  window.fetch = (u) => Promise.resolve({
    ok: true, status: 200,
    json: () => Promise.resolve(String(u).indexOf('world-atlas') >= 0 ? window.__atlas : {}),
    text: () => Promise.resolve(''),
    arrayBuffer: () => Promise.resolve(new ArrayBuffer(0))
  });
  window.DecompressionStream = undefined;
  function describe(m, f, l, c, err) {
    var parts = [];
    if (m) parts.push(String(m));
    if (err && err.name) parts.push('name=' + err.name);
    if (err && err.message && err.message !== m) parts.push('message=' + err.message);
    if (err && err.stack) parts.push('stack=' + String(err.stack).split(String.fromCharCode(10)).slice(0,3).join(' | '));
    if (f) parts.push('src=' + String(f).slice(-60));
    if (l !== undefined) parts.push('at ' + l + ':' + c);
    if (!parts.length) {
      try { parts.push('opaque:' + JSON.stringify(err)); } catch (e) { parts.push('opaque:unserialisable'); }
    }
    return parts.join('  ');
  }
  window.onerror = function(m,f,l,c,err){ window.__errs.push(describe(m,f,l,c,err)); };
  window.addEventListener('error', function(ev){
    window.__errs.push(describe(ev.message, ev.filename, ev.lineno, ev.colno, ev.error));
  });
  window.addEventListener('unhandledrejection', function(ev){
    window.__errs.push('unhandledrejection  ' + describe('', '', undefined, undefined, ev.reason));
  });
})();
</script>`;
// Check the stub before injecting it. A syntax error in the harness surfaces as
// "uncaught runtime error" against the page under test, which sent me hunting
// through 2.5 MB of index.html for a fault that was in these forty lines.
try {
  const stubBody = /<script>([\s\S]*)<\/script>/.exec(STUB)[1];
  new (require("vm").Script)(stubBody);
} catch (e) {
  console.error("HARNESS BUG: the injected stub does not parse \u2014 " + e.message);
  console.error("This is smoke_test.js's own fault, not index.html's.");
  process.exit(2);
}
html = html.replace("</head>", STUB + "</head>");

const jsdomErrs = [];
// jsdom re-throws some script errors on the Node side; catch them here so the
// run finishes and prints a report instead of dying with a raw stack trace.
process.on("uncaughtException", (e) =>
  jsdomErrs.push((e && (e.message || String(e))) || "unknown"));
process.on("unhandledRejection", (e) =>
  jsdomErrs.push("unhandled rejection: " + ((e && (e.message || String(e))) || "unknown")));
const vc = new VirtualConsole();
vc.on("jsdomError", (e) => {
  const d0 = e && e.detail;
  jsdomErrs.push([
    e && e.type ? "type=" + e.type : "",
    e && e.message ? "message=" + e.message : "",
    d0 && d0.name ? "detailName=" + d0.name : "",
    d0 && d0.message ? "detailMessage=" + d0.message : "",
    d0 && d0.stack ? "detailStack=" + String(d0.stack).split("\n").slice(0, 3).join(" | ") : "",
  ].filter(Boolean).join("  ") || ("opaque jsdomError: " + Object.keys(e || {}).join(",")));
});

const dom = new JSDOM(html, {
  runScripts: "dangerously",
  pretendToBeVisual: true,
  virtualConsole: vc,
});

setTimeout(() => {
  const w = dom.window;
  // An error object with no message at all is not evidence of a fault -- some
  // jsdom versions emit a blank entry when a stripped external <script> tag is
  // encountered, and CI failed on exactly that while local runs passed. Blank
  // entries are counted and reported, but do not fail the build; anything with
  // actual text does.
  // jsdom's CSS parser is not a conformance oracle. Older versions reject
  // stylesheets that every browser accepts, and a "could not parse CSS"
  // jsdomError says something about jsdom, not about the page. It is reported
  // loudly and separately, and the structural check below covers what it was
  // accidentally catching.
  const all = [].concat(w.__errs || [], jsdomErrs.map(String));
  const cssNotes = all.filter((e) => /type=css parsing|Could not parse CSS/i.test(String(e)));
  const raw = all.filter((e) => !/type=css parsing|Could not parse CSS/i.test(String(e)));
  const errs = raw.filter((e) => String(e).replace(/@line.*$/, "").trim().length > 0);
  const blanks = raw.length - errs.length;

  // required elements: if the markup lost one, a handler is wired to nothing
  const NEED = ["map", "header", "sidebar", "rightbar", "helpPanel", "wirePanel",
    "indexPanel", "controls", "legend", "idxList", "intentSel", "angleSel",
    "domainPills", "facFilter", "projSrcBox", "tourPanel", "infoPanel"];
  const missing = NEED.filter((id) => !w.document.getElementById(id));

  // functions the UI calls from inline onclick / onchange attributes
  const FNS = ["applyIntent", "applyAngle", "openTour", "loadWire", "setWireMode",
    "setWireRegion", "hideInfoPanel", "buildIncidents", "mergeIncidents",
    "worldwideHTML", "mapDiag"];
  const undef = FNS.filter((f) => typeof w[f] !== "function");

  // Brace balance per <style> block. This is the check that matters: an extra
  // or missing brace silently kills every rule after it in some engines. One
  // was found this way -- inherited from the source map -- and it had been
  // there all along.
  const styleBlocks = [...html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map((m) => m[1]);
  const unbalanced = [];
  styleBlocks.forEach((s, bi) => {
    let depth = 0;
    for (let i = 0; i < s.length; i++) {
      if (s.startsWith("/*", i)) { const e = s.indexOf("*/", i + 2); i = e < 0 ? s.length : e + 1; continue; }
      const c = s[i];
      if (c === '"' || c === "'") { const q = c; i++; while (i < s.length && s[i] !== q) { if (s[i] === "\\") i++; i++; } continue; }
      if (c === "{") depth++; else if (c === "}") depth--;
    }
    if (depth !== 0) unbalanced.push("style block " + bi + " ends at brace depth " + depth);
  });

  let fail = false;
  const crypto = require("crypto");
  const bytes = fs.statSync(FILE).size;
  const sha = crypto.createHash("sha256").update(fs.readFileSync(FILE)).digest("hex").slice(0, 12);
  console.log("file: " + path.basename(FILE) + "  " + bytes + " bytes  sha256:" + sha);
  console.log("title:", w.document.title);

  if (blanks) {
    // Do not just swallow these: print enough to identify them, so a real
    // fault hiding behind an empty message is still visible in the log.
    console.log("note: " + blanks + " error object(s) with no message text \u2014 "
      + "not treated as failures. Raw form:");
    raw.filter((e) => String(e).replace(/@line.*$/, "").trim().length === 0)
       .slice(0, 3)
       .forEach((e) => console.log("      " + JSON.stringify(String(e)) +
         "  (type " + typeof e + ")"));
  }

  if (errs.length) {
    fail = true;
    console.log("\nFAIL \u2014 uncaught runtime errors:");
    [...new Set(errs)].slice(0, 15).forEach((e) =>
      console.log("  " + JSON.stringify(String(e)).slice(0, 500)));
  } else {
    console.log("runtime errors: none"
      + (blanks ? "  (" + blanks + " empty error object(s) ignored \u2014 jsdom noise, "
                + "not a page fault)" : ""));
  }

  if (cssNotes.length) {
    console.log("note: " + cssNotes.length + " CSS-parser complaint(s) from jsdom \u2014 "
      + "reported, not failed. jsdom's CSS engine rejects things browsers accept; "
      + "the brace check below is what actually guards the stylesheet.");
  }

  if (unbalanced.length) {
    fail = true;
    console.log("\nFAIL \u2014 unbalanced CSS braces:");
    unbalanced.forEach((u) => console.log("  " + u));
  } else {
    console.log("CSS braces: all " + styleBlocks.length + " style blocks balanced");
  }

  if (missing.length) { fail = true; console.log("\nFAIL — missing elements: " + missing.join(", ")); }
  else console.log("required elements: all " + NEED.length + " present");

  if (undef.length) { fail = true; console.log("\nFAIL — handlers not defined: " + undef.join(", ")); }
  else console.log("inline handlers: all " + FNS.length + " defined");

  console.log(fail ? "\nSMOKE TEST FAILED" : "\nSMOKE TEST PASSED");
  process.exit(fail ? 1 : 0);
}, WAIT);
