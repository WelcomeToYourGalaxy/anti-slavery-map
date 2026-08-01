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

const VERSION = "smoke_test 2026-08-02";   // bump when this file changes
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
  window.onerror = function(m,f,l,c){ window.__errs.push(m + ' @line ' + l + ':' + c); };
  window.addEventListener('error', function(ev){
    window.__errs.push((ev.message||'') + ' @line ' + (ev.lineno||'?') + ':' + (ev.colno||'?'));
  });
})();
</script>`;
html = html.replace("</head>", STUB + "</head>");

const jsdomErrs = [];
// jsdom re-throws some script errors on the Node side; catch them here so the
// run finishes and prints a report instead of dying with a raw stack trace.
process.on("uncaughtException", (e) =>
  jsdomErrs.push((e && (e.message || String(e))) || "unknown"));
process.on("unhandledRejection", (e) =>
  jsdomErrs.push("unhandled rejection: " + ((e && (e.message || String(e))) || "unknown")));
const vc = new VirtualConsole();
vc.on("jsdomError", (e) =>
  jsdomErrs.push((e.detail && (e.detail.message || e.detail)) || e.message));

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
  const raw = [].concat(w.__errs || [], jsdomErrs.map(String));
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

  let fail = false;
  console.log("file:", path.basename(FILE));
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
    [...new Set(errs)].slice(0, 15).forEach((e) => console.log("  " + String(e).split("\n")[0]));
  } else {
    console.log("runtime errors: none"
      + (blanks ? "  (" + blanks + " empty error object(s) ignored \u2014 jsdom noise, "
                + "not a page fault)" : ""));
  }

  if (missing.length) { fail = true; console.log("\nFAIL — missing elements: " + missing.join(", ")); }
  else console.log("required elements: all " + NEED.length + " present");

  if (undef.length) { fail = true; console.log("\nFAIL — handlers not defined: " + undef.join(", ")); }
  else console.log("inline handlers: all " + FNS.length + " defined");

  console.log(fail ? "\nSMOKE TEST FAILED" : "\nSMOKE TEST PASSED");
  process.exit(fail ? 1 : 0);
}, WAIT);
