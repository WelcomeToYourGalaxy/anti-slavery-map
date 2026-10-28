

/* Culprits basemaps for Leaflet 1.9.4 — the six basemaps of the Culprits map
 * (https://welcometoyourgalaxy.github.io/culprits/), ported from its map/app.js.
 * Needs, loaded before this script: Leaflet 1.9.4, maplibre-gl@5.24.0 (JS + CSS)
 * and @maplibre/maplibre-gl-leaflet@0.1.4.
 * Use: var bm = CulpritsBasemaps.attach(leafletMap, { initial: "night" }); bm.set("atlas"); bm.current();
 * Left out from Culprits: its data layers, 3D terrain, globe, sky/atmosphere
 * and UI (the hologram, menus, notes, the click ring). */
(function () {
"use strict";
var ROOT = "https://welcometoyourgalaxy.github.io/culprits/";
var LIST = [["satellite", "Jurassic"], ["atlas", "Atlas"],
  ["night", "Bioluminescent"], ["hell", "Hell"], ["outlines", "Standard"]];

/* ---------- settings, as in Culprits ---------- */
var PLATE = { url: ROOT + "atlas-plate.webp?v=207",
  top: 85.05112877980659, bottom: -80.55, fadeIn: 3, fadeOut: 5 };
var ATLAS_TUNE = { sat: .15, con: .05, lift: .03, hue: -6, sea: .55, green: .30, warm: .22 };
var BASE_GRADE = {
  atlas: { "raster-brightness-min": ATLAS_TUNE.lift, "raster-brightness-max": 1,
           "raster-saturation": ATLAS_TUNE.sat, "raster-contrast": ATLAS_TUNE.con, "raster-hue-rotate": ATLAS_TUNE.hue },
  satellite: { "raster-brightness-min": 0.02, "raster-brightness-max": 0.92,
               "raster-saturation": 0.12, "raster-contrast": 0.06, "raster-hue-rotate": 0 },
};
var SAT_RELIEF = {
  colour: ["interpolate", ["linear"], ["elevation"],
    -8000, "rgba(10,22,42,0.8)", -3500, "rgba(12,28,50,0.72)", -1200, "rgba(16,40,60,0.6)",
    -200, "rgba(26,70,86,0.38)", -40, "rgba(40,96,102,0.22)", 0, "rgba(40,90,90,0.1)",
    1, "rgba(46,52,34,0.32)", 400, "rgba(48,54,36,0.3)", 1000, "rgba(64,70,44,0.28)",
    1700, "rgba(108,100,66,0.26)", 2500, "rgba(118,90,60,0.3)", 3300, "rgba(110,80,62,0.32)",
    4300, "rgba(102,92,84,0.3)", 5500, "rgba(132,128,122,0.2)"],
  seabed: ["interpolate", ["linear"], ["elevation"],
    -8000, "rgba(10,22,42,0.8)", -3500, "rgba(12,28,50,0.72)", -1200, "rgba(16,40,60,0.6)",
    -200, "rgba(26,70,86,0.38)", -40, "rgba(40,96,102,0.22)", -1, "rgba(40,90,90,0.1)", 0, "rgba(0,0,0,0)"],
  sea: ["interpolate", ["linear"], ["elevation"],
    -8000, "rgba(10,22,42,0.6)", -3000, "rgba(12,26,46,0.55)", -1500, "rgba(14,32,52,0.42)",
    -400, "rgba(20,48,64,0.2)", -80, "rgba(20,48,64,0)", 0, "rgba(0,0,0,0)"],
  shade: { "hillshade-method": "multidirectional",
    "hillshade-illumination-direction": [315, 270, 0, 225], "hillshade-illumination-altitude": [40, 35, 35, 50],
    "hillshade-highlight-color": ["rgba(240,236,222,0.1)", "rgba(240,236,222,0.04)", "rgba(240,236,222,0.04)", "rgba(240,236,222,0.02)"],
    "hillshade-shadow-color": ["rgba(18,24,14,0.78)", "rgba(18,24,14,0.42)", "rgba(18,24,14,0.42)", "rgba(18,24,14,0.2)"],
    "hillshade-accent-color": "rgba(18,24,14,0.3)", "hillshade-exaggeration": 1, "hillshade-illumination-anchor": "map" },
  depth: { "hillshade-method": "standard", "hillshade-illumination-direction": 315, "hillshade-illumination-anchor": "map",
    "hillshade-highlight-color": "rgba(240,236,222,0.04)", "hillshade-shadow-color": "rgba(12,18,10,0.55)",
    "hillshade-accent-color": "rgba(12,18,10,0)", "hillshade-exaggeration": 0.6 },
};
var OSM_SOURCE = { type: "vector", url: "https://tiles.openfreemap.org/planet",
  attribution: '<a href="https://openfreemap.org" target="_blank" rel="noopener">OpenFreeMap</a> © OpenStreetMap contributors' };
var TERRAIN_SOURCE = { type: "raster-dem", tiles: ["https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"],
  encoding: "terrarium", tileSize: 256, maxzoom: 12,
  attribution: '<a href="https://registry.opendata.aws/terrain-tiles/" target="_blank" rel="noopener">AWS Terrain Tiles</a>' };
var RELIEF_SOURCE = { type: "raster-dem", tiles: ["https://tiles.mapterhorn.com/{z}/{x}/{y}.webp"],
  encoding: "terrarium", tileSize: 512, maxzoom: 12,
  attribution: '<a href="https://mapterhorn.com/attribution" target="_blank" rel="noopener">© Mapterhorn</a>' };
var BOUNDARIES = { type: "geojson", data: ROOT + "data/boundaries.geojson", promoteId: "iso3" };
var WORLD = { type: "geojson", data: { type: "Feature", properties: {},
  geometry: { type: "Polygon", coordinates: [[[-180, -85.06], [180, -85.06], [180, 85.06], [-180, 85.06], [-180, -85.06]]] } } };

var HELL = {
  sheet: "#1E080B",
  ground: ["interpolate", ["linear"], ["elevation"],
    -8000, "#110407", -5000, "#18060A", -3000, "#20070C", -1500, "#2A0A0F", -500, "#360C11",
    -120, "#481116", -20, "#57151A", -1, "#5F181D",
    0, "#131215", 200, "#151215", 600, "#1A1214", 1200, "#1F1416", 2000, "#241418",
    3000, "#2B151A", 4200, "#33161C", 5600, "#3B171E"],
  shade: { "hillshade-method": "multidirectional",
    "hillshade-illumination-direction": [315, 270, 0, 225], "hillshade-illumination-altitude": [40, 35, 35, 50],
    "hillshade-highlight-color": ["rgba(150,164,186,0.2)", "rgba(150,164,186,0.08)", "rgba(150,164,186,0.08)", "rgba(150,164,186,0.04)"],
    "hillshade-shadow-color": ["rgba(0,0,0,0.8)", "rgba(0,0,0,0.45)", "rgba(0,0,0,0.45)", "rgba(0,0,0,0.25)"],
    "hillshade-accent-color": "rgba(0,0,0,0.3)", "hillshade-exaggeration": 1, "hillshade-illumination-anchor": "map" },
  coast: "#521419", lake: "#3A0C11", lakeEdge: "#5E171C", river: "#9C252B", riverGlow: "#6A1318",
  grave: "#561519", graveEdge: "#74202A", town: "#1C1719", townWork: "#221C1E",
  road: ["#2B1C1E", "#3A2124", "#4C2529"], rail: "#3A3034", building: "#201B1D",
  border: "rgba(170,58,62,0.32)",
};
var WOOD = {
  sheet: "#1E3326",
  source: "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2024_3857/default/g/{z}/{y}/{x}.jpg",
  sourceMaxzoom: 14,
  attribution: '<a href="https://s2maps.eu" target="_blank" rel="noopener">Sentinel-2 cloudless - https://s2maps.eu</a> by EOX IT Services GmbH (Contains modified Copernicus Sentinel data 2024)',
  greens: [[0, "#10221A"], [0.2, "#183320"], [0.4, "#25482A"], [0.6, "#3D6230"], [0.78, "#6B8638"], [0.9, "#A2A253"], [1, "#D6C67E"]],
  earths: [[0, "#2E2116"], [0.25, "#5A4027"], [0.5, "#8A6639"], [0.75, "#B38C53"], [1, "#DCC08A"]],
  waters: [[0, "#24414A"], [0.35, "#2F5054"], [0.65, "#4C7068"], [1, "#93A88A"]],
  snow: "#EDE4CC", paper: "#F1E6C8",
  sea: ["interpolate", ["linear"], ["elevation"],
    -8000, "#1C3A46", -4000, "#24464E", -1500, "#2C5254", -400, "#3A6260", -60, "#4F7568", -1, "#5E806C", 0, "rgba(0,0,0,0)"],
  seaOpacity: 0.35,
  mist: ["interpolate", ["linear"], ["elevation"],
    -1, "rgba(234,220,170,0)", 0, "rgba(234,220,170,0.16)", 300, "rgba(234,220,170,0.1)", 1000, "rgba(234,220,170,0)"],
  shade: { "hillshade-method": "multidirectional",
    "hillshade-illumination-direction": [225, 270, 180, 0], "hillshade-illumination-altitude": [24, 32, 32, 55],
    "hillshade-highlight-color": ["rgba(250,222,150,0.36)", "rgba(250,222,150,0.14)", "rgba(250,222,150,0.1)", "rgba(250,222,150,0.04)"],
    "hillshade-shadow-color": ["rgba(10,30,28,0.46)", "rgba(10,30,28,0.24)", "rgba(10,30,28,0.18)", "rgba(10,30,28,0.1)"],
    "hillshade-accent-color": "rgba(10,30,28,0.22)", "hillshade-exaggeration": 1, "hillshade-illumination-anchor": "map" },
  lake: "#2F5054", lakeOpacity: 0.35, river: "#6E8C7C", town: "#8A7556", townWork: "#7A684D",
  road: ["#6A5840", "#5C4C37", "#4E402E"], rail: "#3A3024", building: "#8A7558",
  border: "rgba(30,22,12,0.45)",
  brushes: [
    { sp: 9, len: [15, 25], w: [6, 9], a: [0.5, 0.78], detail: 0, often: 1 },
    { sp: 6, len: [8, 14], w: [3, 5], a: [0.5, 0.8], detail: 2.5, often: 0.35 },
    { sp: 4, len: [4, 7], w: [1.6, 2.6], a: [0.5, 0.85], detail: 5, often: 0.08 },
  ],
  margin: 32, lightReach: 10, lift: 0.1,
  photo: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  photoAttribution: "Imagery © Esri, Maxar",
  photoFrom: 15.5, photoFull: 16.5, photoGrade: 0.35,
};
var NIGHT = {
  tiles: "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/2016-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png",
  ramp: [[0, "#02040C"], [14, "#050918"], [34, "#0B1430"], [62, "#17295A"], [100, "#2E5390"],
         [145, "#5E8DC2"], [190, "#A5C7E2"], [230, "#DCE8F0"], [255, "#F1F4F6"]],
  sheet: "#02040C",
  shade: { "hillshade-method": "multidirectional",
    "hillshade-illumination-direction": [315, 270, 0, 225], "hillshade-illumination-altitude": [35, 30, 30, 45],
    "hillshade-highlight-color": ["rgba(170,196,230,0.12)", "rgba(170,196,230,0.05)", "rgba(170,196,230,0.05)", "rgba(170,196,230,0.03)"],
    "hillshade-shadow-color": ["rgba(0,1,6,0.45)", "rgba(0,1,6,0.25)", "rgba(0,1,6,0.25)", "rgba(0,1,6,0.15)"],
    "hillshade-accent-color": "rgba(0,1,6,0.15)", "hillshade-exaggeration": 0.8, "hillshade-illumination-anchor": "map" },
  road: ["rgba(150,186,222,0.30)", "rgba(170,202,232,0.45)", "rgba(206,226,240,0.70)"], roadGlow: "#2D5C96",
  seaGlow: ["interpolate", ["linear"], ["elevation"],
    -9000, "rgba(31,79,126,0)", -150, "rgba(31,79,126,0)", -60, "rgba(31,79,126,0.28)", -15, "rgba(31,79,126,0.55)",
    -3, "rgba(74,154,182,0.85)", 0, "rgba(74,154,182,0)", 9000, "rgba(74,154,182,0)"],
  border: "rgba(120,140,196,0.32)",
  attribution: '<a href="https://earthobservatory.nasa.gov/features/NightLights" target="_blank" rel="noopener">NASA Black Marble 2016</a> via GIBS',
};
// Place names in each basemap's own type (Culprits rounds 163h, 165b, 167p).
var NAMES = {
  atlas: { font: { caps: ["IMFellEnglishSC-Regular"], regular: ["IMFellEnglish-Regular"], italic: ["IMFellEnglish-Italic"], bold: ["IMFellEnglish-Regular"] },
    colour: { country: "#E6DAC0", state: "#CFC3A8", city: "#EEE5D0", town: "#DCD2BC", minor: "#C9C0AC", water: "#A8CFCB", peak: "#C9C0AC" },
    halo: "rgba(14,22,22,0.82)", haloWater: "rgba(10,26,30,0.8)", blur: 0.6, hw: function () { return 1.3; },
    sp: { ocean: 0.18, water: 0.06, river: 0.08, state: 0.12, country: 0.24 },
    op: function () { return ["interpolate", ["linear"], ["zoom"], PLATE.fadeIn, 0, PLATE.fadeOut, 1]; } },
  satellite: { font: { caps: ["BarlowSemiCondensed-Medium"], regular: ["BarlowSemiCondensed-Regular"], italic: ["BarlowSemiCondensed-Italic"], bold: ["BarlowSemiCondensed-Medium"] },
    colour: { country: "#E2E5E4", state: "#C4CACB", city: "#E8EAE8", town: "#CDD1D0", minor: "#B5BBBC", water: "#A9C4D2", peak: "#B5BBBC" },
    halo: "rgba(10,12,14,0.8)", haloWater: "rgba(8,16,24,0.78)", blur: 0.6, hw: function () { return 1.2; },
    sp: { ocean: 0.3, water: 0.06, river: 0.08, state: 0.12, country: 0.36 }, op: function () { return 0.95; } },
};
var HW_OWN = { ocean: 1, water: 1, river: 1, road: 1.2, peak: 1.1, village: 1.2, town: 1.2, state: 1, city: 1.3, country: 1.3 };
var SP_OWN = { ocean: 0.22, water: 0.08, river: 0.1, state: 0.15, country: 0.26 };
var OP_OWN = function (p) { return p === "state" ? 0.9 : undefined; };
var GARAMOND = { regular: ["EBGaramond-Regular"], bold: ["EBGaramond-SemiBold"], italic: ["EBGaramond-Italic"], caps: ["EBGaramond-SemiBold"] };
NAMES.hell = { font: GARAMOND, blur: 0.6, hw: function (p) { return HW_OWN[p]; }, sp: SP_OWN, op: OP_OWN,
  colour: { country: "#A9504C", state: "#8C4A47", city: "#CDBDB4", town: "#B4A39B", minor: "#9A8B85", water: "#B0605F", peak: "#958680" },
  halo: "rgba(8,4,5,0.85)", haloWater: "rgba(24,6,9,0.8)" };
NAMES.wood = { font: GARAMOND, blur: 0.8, hw: function (p) { return HW_OWN[p]; }, sp: SP_OWN, op: OP_OWN,
  colour: { country: "#E6D8AE", state: "#D2C49C", city: "#F0E6C8", town: "#E0D4B2", minor: "#CBBF9E", water: "#C3D4C4", peak: "#D4C8A2" },
  halo: "rgba(14,30,18,0.78)", haloWater: "rgba(12,34,36,0.78)" };

/* ---------- PNG writer (stored, uncompressed), as in Culprits ---------- */
var PNG_CRC = (function () {
  var t = new Uint32Array(256);
  for (var n = 0; n < 256; n++) { var c = n; for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
  return t;
})();
function pngCrc(b, a, e) { let c = 0xFFFFFFFF; for (let i = a; i < e; i++) c = PNG_CRC[(c ^ b[i]) & 255] ^ (c >>> 8); return (c ^ 0xFFFFFFFF) >>> 0; }
function rawPng(rgba, w, h) {
  const row = w * 4 + 1, raw = row * h, blocks = Math.ceil(raw / 65535);
  const zlen = 2 + raw + blocks * 5 + 4;
  const out = new Uint8Array(8 + 25 + (12 + zlen) + 12);
  const dv = new DataView(out.buffer);
  out.set([137, 80, 78, 71, 13, 10, 26, 10], 0);
  let o = 8;
  const chunk = (type, len, fill) => {
    dv.setUint32(o, len); o += 4;
    const start = o;
    for (let i = 0; i < 4; i++) out[start + i] = type.charCodeAt(i);
    fill(start + 4); o = start + 4 + len;
    dv.setUint32(o, pngCrc(out, start, o)); o += 4;
  };
  chunk("IHDR", 13, (at) => { dv.setUint32(at, w); dv.setUint32(at + 4, h); out.set([8, 6, 0, 0, 0], at + 8); });
  chunk("IDAT", zlen, (at) => {
    let q = at;
    out[q++] = 0x78; out[q++] = 0x01;
    let a1 = 1, a2 = 0, left = raw, i = 0;
    while (left > 0) {
      const n = Math.min(65535, left);
      left -= n;
      out[q++] = left === 0 ? 1 : 0; out[q++] = n & 255; out[q++] = n >> 8; out[q++] = ~n & 255; out[q++] = (~n >> 8) & 255;
      for (let k = 0; k < n; k++, i++) {
        const y = (i / row) | 0, x = i - y * row;
        const v = x === 0 ? 0 : rgba[y * w * 4 + x - 1];
        out[q++] = v;
        a1 = (a1 + v) % 65521; a2 = (a2 + a1) % 65521;
      }
    }
    dv.setUint32(q, ((a2 << 16) | a1) >>> 0);
  });
  chunk("IEND", 0, () => {});
  return out.buffer;
}
function canvas2d(w, h) {
  const cv = typeof OffscreenCanvas !== "undefined" ? new OffscreenCanvas(w, h) : Object.assign(document.createElement("canvas"), { width: w, height: h });
  return cv.getContext("2d", { willReadFrequently: true });
}

/* ---------- the painted plate (Atlas), cut into map squares ---------- */
let plateBitmap = null;
const plateMerc = (lat) => (1 - Math.log(Math.tan(Math.PI / 4 + lat * Math.PI / 360)) / Math.PI) / 2;
async function platePiece(z, x, y) {
  if (!plateBitmap) {
    plateBitmap = fetch(PLATE.url).then((r) => { if (!r.ok) throw new Error(`${r.status}`); return r.blob(); }).then((b) => createImageBitmap(b));
    plateBitmap.catch(() => { plateBitmap = null; });
  }
  const img = await plateBitmap;
  const n = Math.pow(2, z), top = plateMerc(PLATE.top), bot = plateMerc(PLATE.bottom);
  const ctx = canvas2d(256, 256);
  const y0 = y / n, y1 = (y + 1) / n;
  const a = Math.max(y0, top), b = Math.min(y1, bot);
  if (b > a) {
    const sy = (a - top) / (bot - top) * img.height, sh = (b - a) / (bot - top) * img.height;
    const dy = (a - y0) * n * 256, dh = (b - a) * n * 256;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(img, x / n * img.width, sy, img.width / n, sh, 0, dy, 256, dh);
  }
  return rawPng(ctx.getImageData(0, 0, 256, 256).data, 256, 256);
}

/* ---------- the Atlas's colour washes, a WebGL layer (Culprits atlasWashes) ---------- */
function hexRgb(h) { const n = parseInt(h.slice(1), 16); return [(n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255]; }
function atlasWashPasses(z) {
  const t = z <= 6 ? 1 : z >= 13 ? 0.45 : 1 - (z - 6) * (0.55 / 7), sea = z <= 6 ? 1 : 0.7;
  const passes = [];
  const aSea = ATLAS_TUNE.sea * sea;
  passes.push({ mode: "screen", rgb: hexRgb("#0f3b52").map((c) => c * aSea) });
  const aG = ATLAS_TUNE.green * t;
  passes.push({ mode: "multiply", rgb: hexRgb("#5f8f3a").map((c) => 1 - aG * (1 - (c < .5 ? .5 + c : 1))) });
  const aW = ATLAS_TUNE.warm * t, warm = hexRgb("#f0c073");
  passes.push({ mode: "gain", rgb: warm.map((c) => c > .5 ? aW * (2 * c - 1) : 0) });
  passes.push({ mode: "multiply", rgb: warm.map((c) => c < .5 ? 1 - aW * (1 - 2 * c) : 1) });
  return passes;
}
function washLayer(state) {
  return {
    id: "atlas-washes", type: "custom", renderingMode: "2d",
    onAdd(m, gl) {
      this.map = m; this.programs = new Map();
      const v = [], cols = 96, rows = 64;
      for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
        const x0 = i / cols, x1 = (i + 1) / cols, y0 = j / rows, y1 = (j + 1) / rows;
        v.push(x0, y0, x1, y0, x0, y1, x1, y0, x1, y1, x0, y1);
      }
      this.mesh = new Float32Array(v);
      this.buf = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, this.buf);
      gl.bufferData(gl.ARRAY_BUFFER, this.mesh, gl.STATIC_DRAW);
    },
    program(gl, sd) {
      if (this.programs.has(sd.variantName)) return this.programs.get(sd.variantName);
      const sh = (type, src) => { const o = gl.createShader(type); gl.shaderSource(o, src); gl.compileShader(o);
        if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
      const p = gl.createProgram();
      gl.attachShader(p, sh(gl.VERTEX_SHADER, `#version 300 es\n${sd.vertexShaderPrelude}\n${sd.define}\nin vec2 a_pos;\nvoid main() { gl_Position = projectTile(a_pos); }`));
      gl.attachShader(p, sh(gl.FRAGMENT_SHADER, "#version 300 es\nprecision mediump float;\nuniform vec3 c;\nout vec4 colour;\nvoid main() { colour = vec4(c, 1.0); }"));
      gl.linkProgram(p);
      if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
      const u = (n) => gl.getUniformLocation(p, n);
      const prog = { p, aPos: gl.getAttribLocation(p, "a_pos"), uCol: u("c"), uMatrix: u("u_projection_matrix"),
        uFallback: u("u_projection_fallback_matrix"), uTile: u("u_projection_tile_mercator_coords"),
        uClip: u("u_projection_clipping_plane"), uTransition: u("u_projection_transition") };
      this.programs.set(sd.variantName, prog);
      return prog;
    },
    render(gl, o) {
      // Culprits draws these on every imagery basemap; only on the Atlas do they
      // show (Jurassic has no passes, the others cover them with an opaque sheet).
      if (this.failed || state.kind !== "atlas" || !o || !o.shaderData) return;
      let prog;
      try { prog = this.program(gl, o.shaderData); } catch (e) { this.failed = true; console.warn("[basemaps] atlas washes unavailable:", e.message || e); return; }
      if (gl.bindVertexArray) gl.bindVertexArray(null);
      gl.disable(gl.DEPTH_TEST); gl.disable(gl.STENCIL_TEST); gl.disable(gl.CULL_FACE);
      gl.useProgram(prog.p);
      const d = o.defaultProjectionData;
      if (prog.uMatrix) gl.uniformMatrix4fv(prog.uMatrix, false, d.mainMatrix);
      if (prog.uFallback) gl.uniformMatrix4fv(prog.uFallback, false, d.fallbackMatrix);
      if (prog.uTile) gl.uniform4f(prog.uTile, ...d.tileMercatorCoords);
      if (prog.uClip) gl.uniform4f(prog.uClip, ...d.clippingPlane);
      if (prog.uTransition) gl.uniform1f(prog.uTransition, d.projectionTransition);
      gl.bindBuffer(gl.ARRAY_BUFFER, this.buf);
      gl.enableVertexAttribArray(prog.aPos);
      gl.vertexAttribPointer(prog.aPos, 2, gl.FLOAT, false, 0, 0);
      gl.enable(gl.BLEND);
      const func = { screen: [gl.ONE, gl.ONE_MINUS_SRC_COLOR], multiply: [gl.ZERO, gl.SRC_COLOR], gain: [gl.DST_COLOR, gl.ONE] };
      for (const pass of atlasWashPasses(this.map.getZoom())) {
        const f = func[pass.mode];
        gl.blendFuncSeparate(f[0], f[1], gl.ZERO, gl.ONE);
        gl.uniform3f(prog.uCol, pass.rgb[0], pass.rgb[1], pass.rgb[2]);
        gl.drawArrays(gl.TRIANGLES, 0, this.mesh.length / 2);
      }
    },
  };
}

/* ---------- Woodlands: the Earth re-painted in watercolour and brushstrokes ---------- */
function woodHex(h) { return [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16)); }
function woodRamp(stops) {
  const s = stops.map(([t, c]) => [t, woodHex(c)]);
  return (t) => {
    if (t <= s[0][0]) return s[0][1];
    for (let i = 1; i < s.length; i++) if (t <= s[i][0]) {
      const u = (t - s[i - 1][0]) / (s[i][0] - s[i - 1][0]), a = s[i - 1][1], b = s[i][1];
      return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u];
    }
    return s[s.length - 1][1];
  };
}
function woodGrain(x, y) {
  const h = (i, j) => (Math.imul(Math.imul(i, 374761393) ^ Math.imul(j, 668265263), 1274126177) >>> 0) / 4294967296;
  const i = Math.floor(x), j = Math.floor(y), fx = x - i, fy = y - j;
  const a = h(i, j) + (h(i + 1, j) - h(i, j)) * fx, b = h(i, j + 1) + (h(i + 1, j + 1) - h(i, j + 1)) * fx;
  return a + (b - a) * fy;
}
function woodPaintPixels(data, w, h, gx0, gy0, soft) {
  gx0 = gx0 || 0; gy0 = gy0 || 0; soft = Math.max(1, Math.min(4, soft || 1));
  const greens = woodRamp(WOOD.greens), earths = woodRamp(WOOD.earths), waters = woodRamp(WOOD.waters), snow = woodHex(WOOD.snow), paper = woodHex(WOOD.paper);
  const n = w * h, W = w + 1;
  const sat = (A) => { const S = new Float64Array(W * (h + 1)); for (let y = 0; y < h; y++) { let row = 0; for (let x = 0; x < w; x++) { row += A[y * w + x]; S[(y + 1) * W + x + 1] = S[y * W + x + 1] + row; } } return S; };
  const blur = (A, r) => {
    r = Math.round(r);
    if (r < 1) return A;
    let cur = A;
    for (let pass = 0; pass < 2; pass++) {
      const S = sat(cur), out = new Float32Array(n);
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        const x0 = Math.max(0, x - r), x1 = Math.min(w - 1, x + r), y0 = Math.max(0, y - r), y1 = Math.min(h - 1, y + r);
        out[y * w + x] = (S[(y1 + 1) * W + x1 + 1] - S[y0 * W + x1 + 1] - S[(y1 + 1) * W + x0] + S[y0 * W + x0]) / ((x1 - x0 + 1) * (y1 - y0 + 1));
      }
      cur = out;
    }
    return cur;
  };
  const V = new Float32Array(n), T = new Float32Array(n), K = new Uint8Array(n);
  for (let p = 0; p < n; p++) {
    const r = data[p * 4], g = data[p * 4 + 1], b = data[p * 4 + 2];
    const lum = (0.3 * r + 0.59 * g + 0.11 * b) / 255, mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    if ((b > g + 6 && b > r + 10 && lum < 0.45) || (lum < 0.07 && b >= r)) K[p] = 1;
    else if (lum > 0.72 && mx - mn < 28) K[p] = 2;
    V[p] = Math.max(0, Math.min(1, ((2 * g - r - b) / 255 + 0.01) / 0.1));
    if (K[p] === 1) T[p] = Math.max(0, Math.min(1, (lum - 0.02) / 0.35));
    else {
      const t = Math.min(1, Math.pow(Math.max(0, lum - 0.015) / 0.45, 0.75));
      T[p] = Math.max(0, Math.min(1, 0.5 + (t - 0.5) * 1.15));
    }
  }
  const Vs = blur(V, 3 * soft), Tp = blur(T, soft - 0.5);
  const Tw = blur(T, WOOD.lightReach * soft), Ts = new Float32Array(n);
  for (let p = 0; p < n; p++) Ts[p] = Math.min(Tp[p], Tw[p] + WOOD.lift);
  const R = new Float32Array(n), G = new Float32Array(n), B = new Float32Array(n);
  for (let p = 0; p < n; p++) {
    let c;
    if (K[p] === 1) c = waters(Ts[p]);
    else if (K[p] === 2) c = snow;
    else {
      const v = 0.92 * Vs[p], a = greens(Ts[p]), e = earths(Ts[p]);
      c = [e[0] + (a[0] - e[0]) * v, e[1] + (a[1] - e[1]) * v, e[2] + (a[2] - e[2]) * v];
    }
    R[p] = c[0]; G[p] = c[1]; B[p] = c[2];
  }
  const Rb = blur(R, 3 * soft), Gb = blur(G, 3 * soft), Bb = blur(B, 3 * soft);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const p = y * w + x, q = p * 4;
    let r = R[p] * 0.45 + Rb[p] * 0.55, g = G[p] * 0.45 + Gb[p] * 0.55, b = B[p] * 0.45 + Bb[p] * 0.55;
    const L = 0.3 * r + 0.59 * g + 0.11 * b;
    const grain = 0.6 * woodGrain((gx0 + x) / 1.7, (gy0 + y) / 1.7) + 0.4 * woodGrain((gx0 + x) / 6 + 11, (gy0 + y) / 6 + 7) - 0.5;
    const k = 1 + grain * (0.04 + 0.05 * (1 - L / 255));
    const show = 0.03 + 0.08 * (L / 255);
    data[q] = (r * k) + (paper[0] - r * k) * show; data[q + 1] = (g * k) + (paper[1] - g * k) * show;
    data[q + 2] = (b * k) + (paper[2] - b * k) * show; data[q + 3] = 255;
  }
  return data;
}
function woodStrokes(painted, N, M, z, gx0, gy0) {
  const S = 256, out = new Uint8ClampedArray(S * S * 4), n = N * N;
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const p = ((y + M) * N + x + M) * 4, q = (y * S + x) * 4;
    out[q] = painted[p]; out[q + 1] = painted[p + 1]; out[q + 2] = painted[p + 2]; out[q + 3] = 255;
  }
  const L = new Float32Array(n);
  for (let p = 0; p < n; p++) L[p] = 0.3 * painted[p * 4] + 0.59 * painted[p * 4 + 1] + 0.11 * painted[p * 4 + 2];
  const XX = new Float32Array(n), YY = new Float32Array(n), XY = new Float32Array(n);
  for (let y = 1; y < N - 1; y++) for (let x = 1; x < N - 1; x++) {
    const i = y * N + x;
    const gx = (L[i - N + 1] + 2 * L[i + 1] + L[i + N + 1] - L[i - N - 1] - 2 * L[i - 1] - L[i + N - 1]) / 8;
    const gy = (L[i + N - 1] + 2 * L[i + N] + L[i + N + 1] - L[i - N - 1] - 2 * L[i - N] - L[i - N + 1]) / 8;
    XX[i] = gx * gx; YY[i] = gy * gy; XY[i] = gx * gy;
  }
  const W = N + 1, sum = (A) => { const T = new Float64Array(W * W); for (let y = 0; y < N; y++) { let row = 0; for (let x = 0; x < N; x++) { row += A[y * N + x]; T[(y + 1) * W + x + 1] = T[y * W + x + 1] + row; } } return T; };
  const SXX = sum(XX), SYY = sum(YY), SXY = sum(XY);
  const near = (T, x, y, r) => { const x0 = Math.max(0, x - r), x1 = Math.min(N - 1, x + r), y0 = Math.max(0, y - r), y1 = Math.min(N - 1, y + r); return (T[(y1 + 1) * W + x1 + 1] - T[y0 * W + x1 + 1] - T[(y1 + 1) * W + x0] + T[y0 * W + x0]) / ((x1 - x0 + 1) * (y1 - y0 + 1)); };
  const rand = (seed) => { let a = seed >>> 0; return () => { a = (a + 0x6D2B79F5) >>> 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
  const CELL = 72, world = 256 * Math.pow(2, z);
  const sx0 = gx0 + M, sy0 = gy0 + M;
  const reach = 30;
  const c0 = Math.floor((sx0 - reach) / CELL), c1 = Math.floor((sx0 + S + reach) / CELL);
  const r0 = Math.floor((sy0 - reach) / CELL), r1 = Math.floor((sy0 + S + reach) / CELL);
  WOOD.brushes.forEach((br, li) => {
    for (let cr = r0; cr <= r1; cr++) for (let cc = c0; cc <= c1; cc++) {
      const wc = ((cc % Math.ceil(world / CELL)) + Math.ceil(world / CELL)) % Math.ceil(world / CELL);
      const rnd = rand(Math.imul(z + 1, 73856093) ^ Math.imul(li + 1, 2654435761) ^ Math.imul(wc + 7, 19349663) ^ Math.imul(cr + 7, 83492791));
      for (let oy = 0; oy < CELL; oy += br.sp) for (let ox = 0; ox < CELL; ox += br.sp) {
        const wx = cc * CELL + ox + rnd() * br.sp, wy = cr * CELL + oy + rnd() * br.sp;
        const len = br.len[0] + rnd() * (br.len[1] - br.len[0]), wd = br.w[0] + rnd() * (br.w[1] - br.w[0]);
        const alpha = br.a[0] + rnd() * (br.a[1] - br.a[0]), chance = rnd(), jit = rnd() - 0.5, slant = rnd() - 0.5, bend = (rnd() - 0.5) * 4;
        const id = (rnd() * 1e9) | 0, f1 = 2 + rnd() * 1.5, ph = rnd() * 6.28, warm = rnd() - 0.5;
        const px = Math.floor(wx - gx0), py = Math.floor(wy - gy0);
        if (px < 1 || py < 1 || px >= N - 1 || py >= N - 1) continue;
        const cx = wx - sx0, cy = wy - sy0;
        const ext = len / 2 + wd / 2 + 3;
        if (cx < -ext || cx > S + ext || cy < -ext || cy > S + ext) continue;
        const jxx = near(SXX, px, py, 4), jyy = near(SYY, px, py, 4), jxy = near(SXY, px, py, 4);
        const tr = jxx + jyy, detail = Math.sqrt(tr);
        if (br.detail > 0 && detail < br.detail && chance > br.often) continue;
        const coh = tr > 1e-6 ? Math.sqrt((jxx - jyy) * (jxx - jyy) + 4 * jxy * jxy) / tr : 0;
        const along = 0.5 * Math.atan2(2 * jxy, jxx - jyy) + Math.PI / 2;
        const hand = -0.55 + 0.35 * slant;
        const k = Math.min(1, coh * Math.min(1, detail / 2));
        const ang = Math.atan2(k * Math.sin(2 * along) + (1 - k) * Math.sin(2 * hand), k * Math.cos(2 * along) + (1 - k) * Math.cos(2 * hand)) / 2 + jit * 0.2;
        const pi = (py * N + px) * 4, f = 1 + jit * 0.1;
        const col = [painted[pi] * f * (1 + warm * 0.04), painted[pi + 1] * f, painted[pi + 2] * f * (1 - warm * 0.05)];
        const ux = Math.cos(ang), uy = Math.sin(ang), h = len / 2, hw = wd / 2;
        const i0 = Math.max(0, Math.floor(cx - ext)), i1 = Math.min(S - 1, Math.ceil(cx + ext));
        const j0 = Math.max(0, Math.floor(cy - ext)), j1 = Math.min(S - 1, Math.ceil(cy + ext));
        for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) {
          const qx = i + 0.5 - cx, qy = j + 0.5 - cy, t = qx * ux + qy * uy;
          if (t < -h || t > h) continue;
          const tt = t / h, u = (-qx * uy + qy * ux) - bend * (tt * tt - 0.33);
          const half = hw * (0.55 + 0.45 * Math.sqrt(1 - tt * tt));
          if (Math.abs(u) > half) continue;
          const bi = Math.floor((u + half) / 1.2);
          const hb = (Math.imul(id ^ Math.imul(bi + 7, 0x9E3779B1), 0x85EBCA6B) >>> 0) / 4294967296;
          if (Math.abs(tt) > 0.62 + 0.38 * hb) continue;
          const edge = Math.min(1, (half - Math.abs(u)) / 1.5);
          const bristle = 0.5 + 0.5 * hb + 0.08 * Math.sin(u * f1 + ph);
          const a = Math.min(1, alpha * edge * bristle * (0.65 + 0.35 * (1 - Math.abs(tt))));
          const ridge = 1 + 0.07 * (-u / (half || 1));
          const q = (j * S + i) * 4;
          out[q] = out[q] + (col[0] * ridge - out[q]) * a;
          out[q + 1] = out[q + 1] + (col[1] * ridge - out[q + 1]) * a;
          out[q + 2] = out[q + 2] + (col[2] * ridge - out[q + 2]) * a;
        }
      }
    }
  });
  return out;
}
function woodWork(d) { const px = new Uint8ClampedArray(d.data); woodPaintPixels(px, d.N, d.N, d.gx0, d.gy0, d.soft); return rawPng(woodStrokes(px, d.N, d.M, d.z, d.gx0, d.gy0), 256, 256); }
// Two helpers off the page's thread, made from a Blob; on the page if they cannot start.
var WOOD_HELPERS = null, WOOD_JOBS = new Map(), WOOD_JOB = 0;
function woodHelpers() {
  if (WOOD_HELPERS !== null) return WOOD_HELPERS;
  WOOD_HELPERS = [];
  try {
    const code = "var WOOD = " + JSON.stringify(WOOD) + ";\nvar PNG_CRC = new Uint32Array([" + Array.from(PNG_CRC).join(",") + "]);\n" +
      [woodHex, woodRamp, woodGrain, woodPaintPixels, woodStrokes, pngCrc, rawPng, woodWork].map(String).join("\n") +
      "\nonmessage = (e) => { try { const png = woodWork(e.data); postMessage({ id: e.data.id, png }, [png]); } catch (err) { postMessage({ id: e.data.id, error: String(err) }); } };";
    const url = URL.createObjectURL(new Blob([code], { type: "text/javascript" }));
    for (let i = 0; i < 2; i++) {
      const wk = new Worker(url);
      wk.onmessage = (e) => { const job = WOOD_JOBS.get(e.data.id); if (!job) return; WOOD_JOBS.delete(e.data.id); if (e.data.error) job.no(new Error(e.data.error)); else job.yes(e.data.png); };
      WOOD_HELPERS.push(wk);
    }
  } catch (e) { WOOD_HELPERS = []; }
  return WOOD_HELPERS;
}
function woodPaintJob(d) {
  const hs = woodHelpers();
  if (!hs.length) return Promise.resolve(woodWork(d));
  const id = ++WOOD_JOB;
  return new Promise((yes, no) => { WOOD_JOBS.set(id, { yes, no }); hs[id % hs.length].postMessage(Object.assign({ id }, d), [d.data]); });
}
var WOOD_SRC = new Map();
function woodSourceSquare(z, x, y) {
  const n = Math.pow(2, z);
  if (y < 0 || y >= n) return Promise.resolve(null);
  x = ((x % n) + n) % n;
  const key = z + "/" + x + "/" + y;
  let p = WOOD_SRC.get(key);
  if (!p) {
    const url = WOOD.source.replace("{z}", z).replace("{x}", x).replace("{y}", y);
    p = fetch(url).then((r) => (r.ok ? r.blob() : null)).then((b) => (b ? createImageBitmap(b) : null)).then((bm) => {
      if (!bm) return null;
      const g = canvas2d(256, 256);
      g.drawImage(bm, 0, 0, 256, 256);
      return g.getImageData(0, 0, 256, 256).data;
    }).catch(() => null);
    WOOD_SRC.set(key, p);
    if (WOOD_SRC.size > 96) WOOD_SRC.delete(WOOD_SRC.keys().next().value);
  }
  return p;
}
async function woodComposite(z, x, y, M) {
  const zz = Math.min(z, WOOD.sourceMaxzoom), k = Math.pow(2, z - zz), N = 256 + 2 * M;
  const gx0 = x * 256 - M, gy0 = y * 256 - M;
  const a0 = Math.floor((gx0 / k - 1) / 256), a1 = Math.floor(((gx0 + N) / k + 1) / 256);
  const b0 = Math.floor((gy0 / k - 1) / 256), b1 = Math.floor(((gy0 + N) / k + 1) / 256);
  const got = new Map(), wait = [];
  for (let b = b0; b <= b1; b++) for (let a = a0; a <= a1; a++) wait.push(woodSourceSquare(zz, a, b).then((d) => got.set(a + "/" + b, d)));
  await Promise.all(wait);
  const lim = Math.pow(2, zz) * 256 - 1;
  const px = (sx, sy, c) => {
    sy = Math.max(0, Math.min(lim, sy));
    const a = Math.floor(sx / 256), b = Math.floor(sy / 256), d = got.get(a + "/" + b);
    if (!d) return [42, 70, 46][c];
    return d[((sy - b * 256) * 256 + (sx - a * 256)) * 4 + c];
  };
  const out = new Uint8ClampedArray(N * N * 4);
  for (let v = 0; v < N; v++) for (let u = 0; u < N; u++) {
    const fx = (gx0 + u + 0.5) / k - 0.5, fy = (gy0 + v + 0.5) / k - 0.5;
    const ax = Math.floor(fx), ay = Math.floor(fy), tx = fx - ax, ty = fy - ay, q = (v * N + u) * 4;
    for (let c = 0; c < 3; c++) {
      const top = px(ax, ay, c) * (1 - tx) + px(ax + 1, ay, c) * tx, bot = px(ax, ay + 1, c) * (1 - tx) + px(ax + 1, ay + 1, c) * tx;
      out[q + c] = top * (1 - ty) + bot * ty;
    }
    out[q + 3] = 255;
  }
  return { data: out.buffer, N, M, z, gx0, gy0, soft: k };
}
function woodGradePixels(data, w, h) {
  const greens = woodRamp(WOOD.greens), earths = woodRamp(WOOD.earths), waters = woodRamp(WOOD.waters), snow = woodHex(WOOD.snow), g0 = WOOD.photoGrade;
  for (let p = 0, n = w * h; p < n; p++) {
    const q = p * 4, r = data[q], g = data[q + 1], b = data[q + 2];
    const lum = (0.3 * r + 0.59 * g + 0.11 * b) / 255, mx = Math.max(r, g, b), mn = Math.min(r, g, b);
    let c;
    if ((b > g + 6 && b > r + 10 && lum < 0.45) || (lum < 0.07 && b >= r)) c = waters(Math.max(0, Math.min(1, (lum - 0.02) / 0.35)));
    else if (lum > 0.72 && mx - mn < 28) c = snow;
    else {
      const v = 0.92 * Math.max(0, Math.min(1, ((2 * g - r - b) / 255 + 0.01) / 0.1));
      const t0 = Math.min(1, Math.pow(Math.max(0, lum - 0.015) / 0.45, 0.75)), t = Math.max(0, Math.min(1, 0.5 + (t0 - 0.5) * 1.15));
      const a = greens(t), e = earths(t);
      c = [e[0] + (a[0] - e[0]) * v, e[1] + (a[1] - e[1]) * v, e[2] + (a[2] - e[2]) * v];
    }
    data[q] = r + (c[0] - r) * g0; data[q + 1] = g + (c[1] - g) * g0; data[q + 2] = b + (c[2] - b) * g0; data[q + 3] = 255;
  }
  return data;
}

/* ---------- Bioluminescent: NASA Black Marble re-coloured ---------- */
var NIGHT_TABLE = null;
function nightTable() {
  const t = new Uint8Array(256 * 3), R = NIGHT.ramp;
  for (let v = 0; v < 256; v++) {
    let k = 0; while (k < R.length - 2 && v > R[k + 1][0]) k++;
    const f = Math.max(0, Math.min(1, (v - R[k][0]) / (R[k + 1][0] - R[k][0]))), a = woodHex(R[k][1]), b = woodHex(R[k + 1][1]);
    for (let i = 0; i < 3; i++) t[v * 3 + i] = Math.round(a[i] + (b[i] - a[i]) * f);
  }
  return t;
}
function nightRecolour(px, table) {
  for (let i = 0; i < px.length; i += 4) {
    const r = px[i], g = px[i + 1], b = px[i + 2];
    const v = Math.round(0.5 * Math.max(r, g, b) + 0.5 * (0.3 * r + 0.59 * g + 0.11 * b));
    px[i] = table[v * 3]; px[i + 1] = table[v * 3 + 1]; px[i + 2] = table[v * 3 + 2]; px[i + 3] = 255;
  }
  return px;
}

/* ---------- the custom protocols (global to MapLibre; added once) ---------- */
function zxy(url, re) { const m = url.match(re); if (!m) throw new Error("bad square " + url); return [Number(m[1]), Number(m[2]), Number(m[3])]; }
async function imageData(url, signal) {
  const r = await fetch(url, signal ? { signal } : undefined);
  if (!r.ok) throw new Error(String(r.status));
  const bm = await createImageBitmap(await r.blob());
  const g = canvas2d(bm.width, bm.height);
  g.drawImage(bm, 0, 0);
  return g.getImageData(0, 0, bm.width, bm.height);
}
function addProtocols() {
  if (addProtocols.done) return;
  addProtocols.done = true;
  maplibregl.addProtocol("plate", async (p) => { const [z, x, y] = zxy(p.url, /^plate:\/\/(\d+)\/(\d+)\/(\d+)/); return { data: await platePiece(z, x, y) }; });
  maplibregl.addProtocol("woodpaint", async (p) => {
    const [z, x, y] = zxy(p.url, /^woodpaint:\/\/(\d+)\/(\d+)\/(\d+)/);
    return { data: await woodPaintJob(await woodComposite(z, x, y, WOOD.margin)) };
  });
  maplibregl.addProtocol("woodphoto", async (p, ac) => {
    const [z, x, y] = zxy(p.url, /^woodphoto:\/\/(\d+)\/(\d+)\/(\d+)/);
    const img = await imageData(WOOD.photo.replace("{z}", z).replace("{x}", x).replace("{y}", y), ac && ac.signal);
    return { data: rawPng(woodGradePixels(img.data, img.width, img.height), img.width, img.height) };
  });
  maplibregl.addProtocol("nightlights", async (p, ac) => {
    const [z, y, x] = zxy(p.url, /^nightlights:\/\/(\d+)\/(\d+)\/(\d+)$/);
    const img = await imageData(NIGHT.tiles.replace("{z}", z).replace("{y}", y).replace("{x}", x), ac && ac.signal);
    if (!NIGHT_TABLE) NIGHT_TABLE = nightTable();
    return { data: rawPng(nightRecolour(img.data, NIGHT_TABLE), img.width, img.height) };
  });
}

/* ---------- layer stacks, as in Culprits ---------- */
const kind = (list) => ["match", ["get", "class"], list, true, false];
const zs = (...a) => ["interpolate", ["linear"], ["zoom"], ...a];
const fade = (z0, z1, a) => zs(z0, 0, z1, a);
const roadW = (z0, k0, k2) => (w) => ["interpolate", ["exponential", 1.4], ["zoom"], z0, w * k0, 10, w, 16, w * k2];
const TOWNS = ["residential", "commercial", "industrial", "retail", "suburb", "neighbourhood"];
const building = (c) => ({ type: "fill-extrusion", source: "osm", "source-layer": "building", minzoom: 13,
  paint: { "fill-extrusion-color": c, "fill-extrusion-height": ["coalesce", ["get", "render_height"], 6],
           "fill-extrusion-base": ["coalesce", ["get", "render_min_height"], 0], "fill-extrusion-opacity": zs(13, 0, 14, .9) } });
const T = (id, o) => Object.assign({ id }, o);

function outlineLayers() {      // Standard (Culprits "outlines")
  const road = roadW(5, .3, 6), fd = (a) => zs(3.5, 0, 6, a);
  return [
    T("outline-ocean", { type: "fill", source: "outline-ocean", paint: { "fill-color": "#141C1F", "fill-antialias": false } }),
    T("outline-land", { type: "fill", source: "boundaries", paint: { "fill-color": "#202825" } }),
    T("outline-relief", { type: "hillshade", source: "outline-dem", minzoom: 3.5,
      paint: { "hillshade-exaggeration": .45, "hillshade-shadow-color": "#050504", "hillshade-highlight-color": "#4A4A40", "hillshade-accent-color": "#15150F" } }),
    T("outline-water", { type: "fill", source: "osm", "source-layer": "water", minzoom: 3.5, paint: { "fill-color": "#0B1017", "fill-opacity": 1 } }),
    T("outline-green", { type: "fill", source: "osm", "source-layer": "landcover", minzoom: 5, filter: kind(["wood", "forest", "grass", "wetland", "farmland"]),
      paint: { "fill-color": ["match", ["get", "class"], ["wood", "forest"], "#1C2A20", "wetland", "#1B2624", "#212720"], "fill-opacity": fd(.8) } }),
    T("outline-town", { type: "fill", source: "osm", "source-layer": "landuse", minzoom: 6, filter: kind(TOWNS),
      paint: { "fill-color": ["match", ["get", "class"], "industrial", "#2A2826", "#262625"], "fill-opacity": fd(.9) } }),
    T("outline-waterway", { type: "line", source: "osm", "source-layer": "waterway", minzoom: 6, paint: { "line-color": "#22323C", "line-width": road(.9) } }),
    T("outline-rail", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 9, filter: kind(["rail", "transit"]),
      paint: { "line-color": "#46494A", "line-width": 1, "line-dasharray": [3, 2] } }),
    T("outline-road-minor", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 11, filter: kind(["minor", "service", "track", "street", "street_limited"]),
      paint: { "line-color": "#34373A", "line-width": road(.45) } }),
    T("outline-road", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 7, filter: kind(["secondary", "tertiary"]),
      paint: { "line-color": "#44484A", "line-width": road(.6) } }),
    T("outline-road-major", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 4, filter: kind(["motorway", "trunk", "primary"]),
      paint: { "line-color": "#5E6264", "line-width": road(.8), "line-opacity": fd(1) } }),
    T("outline-buildings", building("#34383A")),
    T("outline-line", { type: "line", source: "boundaries", paint: { "line-color": "rgba(214,211,200,.17)", "line-width": zs(3, .6, 4, .9) } }),
  ];
}
function satLayers() {          // Jurassic (Culprits "satellite") relief over the imagery
  return [
    T("sat-relief-colour", { type: "color-relief", source: "outline-dem", paint: { "color-relief-color": SAT_RELIEF.colour, "color-relief-opacity": 1 } }),
    T("sat-relief-seabed", { type: "color-relief", source: "sea-dem", paint: { "color-relief-color": SAT_RELIEF.seabed, "color-relief-opacity": 1 } }),
    T("sat-relief-shade", { type: "hillshade", source: "outline-dem", paint: SAT_RELIEF.shade }),
    T("sat-relief-depth", { type: "hillshade", source: "outline-dem", paint: SAT_RELIEF.depth }),
    T("sat-relief-sea", { type: "color-relief", source: "sea-dem", paint: { "color-relief-color": SAT_RELIEF.sea, "color-relief-opacity": 1 } }),
  ];
}
function hellLayers() {
  const road = roadW(4, .25, 6);
  return [
    T("outline-hell-sheet", { type: "fill", source: "world", paint: { "fill-color": HELL.sheet, "fill-antialias": false } }),
    T("outline-hell-ground", { type: "color-relief", source: "sea-dem", paint: { "color-relief-color": HELL.ground, "color-relief-opacity": 1 } }),
    T("outline-hell-shade", { type: "hillshade", source: "outline-dem", paint: HELL.shade }),
    T("outline-hell-coast", { type: "fill", source: "osm", "source-layer": "water", minzoom: 7, filter: ["==", ["get", "class"], "ocean"],
      paint: { "fill-color": HELL.coast, "fill-opacity": fade(7, 9, 1) } }),
    T("outline-hell-lake", { type: "fill", source: "osm", "source-layer": "water", filter: ["!=", ["get", "class"], "ocean"],
      paint: { "fill-color": HELL.lake, "fill-outline-color": HELL.lakeEdge } }),
    T("outline-hell-town", { type: "fill", source: "osm", "source-layer": "landuse", minzoom: 6, filter: kind(TOWNS),
      paint: { "fill-color": ["match", ["get", "class"], "industrial", HELL.townWork, HELL.town], "fill-opacity": fade(6, 8, .9) } }),
    T("outline-hell-grave", { type: "fill", source: "osm", "source-layer": "landuse", minzoom: 9, filter: ["==", ["get", "class"], "cemetery"],
      paint: { "fill-color": HELL.grave, "fill-outline-color": HELL.graveEdge, "fill-opacity": fade(9, 11, .8) } }),
    T("outline-hell-river-glow", { type: "line", source: "osm", "source-layer": "waterway", minzoom: 3, filter: ["==", ["get", "class"], "river"],
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": HELL.riverGlow, "line-width": road(4), "line-blur": road(3), "line-opacity": .45 } }),
    T("outline-hell-river", { type: "line", source: "osm", "source-layer": "waterway", minzoom: 3, layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": HELL.river,
        "line-width": ["interpolate", ["exponential", 1.4], ["zoom"], 4, ["match", ["get", "class"], "river", .25, .11],
          10, ["match", ["get", "class"], "river", 1, .45], 16, ["match", ["get", "class"], "river", 6, 2.7]],
        "line-opacity": zs(8, ["match", ["get", "class"], "river", .9, 0], 11, ["match", ["get", "class"], "river", .9, .7]) } }),
    T("outline-hell-rail", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 9, filter: kind(["rail", "transit"]),
      paint: { "line-color": HELL.rail, "line-width": 1, "line-dasharray": [3, 2] } }),
    T("outline-hell-road-minor", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 11, filter: kind(["minor", "service", "track", "street", "street_limited"]),
      paint: { "line-color": HELL.road[0], "line-width": road(.45) } }),
    T("outline-hell-road", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 7, filter: kind(["secondary", "tertiary"]),
      paint: { "line-color": HELL.road[1], "line-width": road(.6) } }),
    T("outline-hell-road-major", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 4, filter: kind(["motorway", "trunk", "primary"]),
      paint: { "line-color": HELL.road[2], "line-width": road(.8), "line-opacity": fade(4, 6, 1) } }),
    T("outline-hell-buildings", building(HELL.building)),
    T("outline-hell-border", { type: "line", source: "boundaries", paint: { "line-color": HELL.border, "line-width": zs(2, .5, 5, .9) } }),
  ];
}
function woodLayers() {
  const road = roadW(4, .25, 6);
  return [
    T("outline-wood-sheet", { type: "fill", source: "world", paint: { "fill-color": WOOD.sheet, "fill-antialias": false } }),
    T("outline-wood-paint", { type: "raster", source: "outline-wood-paint", maxzoom: WOOD.photoFull + 0.5,
      paint: { "raster-opacity": 1, "raster-fade-duration": 200, "raster-resampling": "linear" } }),
    T("outline-wood-photo", { type: "raster", source: "outline-wood-photo", minzoom: WOOD.photoFrom,
      paint: { "raster-opacity": zs(WOOD.photoFrom, 0, WOOD.photoFull, 1), "raster-fade-duration": 200, "raster-resampling": "linear" } }),
    T("outline-wood-sea", { type: "color-relief", source: "sea-dem", paint: { "color-relief-color": WOOD.sea, "color-relief-opacity": WOOD.seaOpacity } }),
    T("outline-wood-shade", { type: "hillshade", source: "outline-dem", paint: WOOD.shade }),
    T("outline-wood-mist", { type: "color-relief", source: "sea-dem", paint: { "color-relief-color": WOOD.mist, "color-relief-opacity": 1 } }),
    T("outline-wood-lake", { type: "fill", source: "osm", "source-layer": "water", filter: ["!=", ["get", "class"], "ocean"],
      paint: { "fill-color": WOOD.lake, "fill-opacity": WOOD.lakeOpacity } }),
    T("outline-wood-town", { type: "fill", source: "osm", "source-layer": "landuse", minzoom: 6, filter: kind(TOWNS),
      paint: { "fill-color": ["match", ["get", "class"], "industrial", WOOD.townWork, WOOD.town], "fill-opacity": fade(6, 8, .55) } }),
    T("outline-wood-river", { type: "line", source: "osm", "source-layer": "waterway", minzoom: 3, layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": WOOD.river, "line-blur": .6,
        "line-width": ["interpolate", ["exponential", 1.4], ["zoom"], 4, ["match", ["get", "class"], "river", .35, .12],
          10, ["match", ["get", "class"], "river", 1.2, .5], 16, ["match", ["get", "class"], "river", 6, 2.7]],
        "line-opacity": zs(8, ["match", ["get", "class"], "river", .85, 0], 11, ["match", ["get", "class"], "river", .85, .65]) } }),
    T("outline-wood-rail", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 9, filter: kind(["rail", "transit"]),
      paint: { "line-color": WOOD.rail, "line-width": 1, "line-dasharray": [3, 2] } }),
    T("outline-wood-road-minor", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 11, filter: kind(["minor", "service", "track", "street", "street_limited"]),
      paint: { "line-color": WOOD.road[0], "line-width": road(.45) } }),
    T("outline-wood-road", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 7, filter: kind(["secondary", "tertiary"]),
      paint: { "line-color": WOOD.road[1], "line-width": road(.6) } }),
    T("outline-wood-road-major", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 4, filter: kind(["motorway", "trunk", "primary"]),
      paint: { "line-color": WOOD.road[2], "line-width": road(.8), "line-opacity": fade(4, 6, .8) } }),
    T("outline-wood-buildings", building(WOOD.building)),
    T("outline-wood-border", { type: "line", source: "boundaries", paint: { "line-color": WOOD.border, "line-width": zs(2, .5, 5, .9) } }),
  ];
}
function nightLayers() {
  const road = roadW(6, .3, 5);
  return [
    T("outline-night-sheet", { type: "fill", source: "world", paint: { "fill-color": NIGHT.sheet, "fill-antialias": false } }),
    T("outline-night-lights", { type: "raster", source: "outline-night-lights", paint: { "raster-fade-duration": 200, "raster-resampling": "linear" } }),
    T("outline-night-shade", { type: "hillshade", source: "outline-dem", paint: NIGHT.shade }),
    T("outline-night-sea-glow", { type: "color-relief", source: "sea-dem", paint: { "color-relief-color": NIGHT.seaGlow, "color-relief-opacity": 1 } }),
    T("outline-night-road-glow", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 7, filter: kind(["motorway", "trunk", "primary"]),
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": NIGHT.roadGlow, "line-width": road(3), "line-blur": road(2.5), "line-opacity": fade(7, 10, .35) } }),
    T("outline-night-road-minor", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 11, filter: kind(["minor", "service", "street", "street_limited"]),
      paint: { "line-color": NIGHT.road[0], "line-width": road(.4), "line-opacity": fade(11, 13, 1) } }),
    T("outline-night-road", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 9, filter: kind(["secondary", "tertiary"]),
      paint: { "line-color": NIGHT.road[1], "line-width": road(.5), "line-opacity": fade(9, 11, 1) } }),
    T("outline-night-road-major", { type: "line", source: "osm", "source-layer": "transportation", minzoom: 7, filter: kind(["motorway", "trunk", "primary"]),
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": NIGHT.road[2], "line-width": road(.6), "line-opacity": fade(7, 9, 1) } }),
    T("outline-night-border", { type: "line", source: "boundaries", paint: { "line-color": NIGHT.border, "line-width": zs(2, .4, 6, .8) } }),
  ];
}
// OpenFreeMap's place, water, river, road and peak names in a basemap's own type.
function nameLayers(k) {
  const t = NAMES[k], nm = ["coalesce", ["get", "name_en"], ["get", "name:latin"], ["get", "name"]];
  const L = (p, o, c, water, layout) => {
    const paint = { "text-color": t.colour[c], "text-halo-color": water ? t.haloWater : t.halo, "text-halo-width": t.hw(p), "text-halo-blur": t.blur };
    if (t.op(p) !== undefined) paint["text-opacity"] = t.op(p);
    return Object.assign({ id: `outline-${k}-name-${p}`, type: "symbol", source: "osm", paint,
      layout: Object.assign({ "text-field": nm }, layout) }, o);
  };
  const f = t.font, sp = t.sp;
  return [
    L("ocean", { "source-layer": "water_name", filter: kind(["ocean", "sea"]) }, "water", true,
      { "text-font": f.italic, "text-size": zs(1, 11, 6, 16), "text-letter-spacing": sp.ocean, "text-max-width": 6 }),
    L("water", { "source-layer": "water_name", minzoom: 5, filter: ["!", kind(["ocean", "sea"])] }, "water", true,
      { "text-font": f.italic, "text-size": zs(5, 11, 14, 14), "text-letter-spacing": sp.water, "text-max-width": 7 }),
    L("river", { "source-layer": "waterway", minzoom: 9 }, "water", true,
      { "text-font": f.italic, "text-size": zs(9, 11, 15, 14), "symbol-placement": "line", "text-letter-spacing": sp.river }),
    L("road", { "source-layer": "transportation_name", minzoom: 13 }, "minor", false,
      { "text-font": f.regular, "text-size": zs(13, 11, 17, 14), "symbol-placement": "line" }),
    L("peak", { "source-layer": "mountain_peak", minzoom: 9 }, "peak", false, { "text-font": f.italic, "text-size": 12, "text-max-width": 7 }),
    L("village", { "source-layer": "place", minzoom: 11, filter: kind(["village", "hamlet", "suburb", "neighbourhood", "quarter"]) }, "minor", false,
      { "text-font": f.regular, "text-size": zs(11, 11, 16, 14), "text-max-width": 7 }),
    L("town", { "source-layer": "place", minzoom: 7, filter: kind(["town"]) }, "town", false,
      { "text-font": f.regular, "text-size": zs(7, 11, 14, 16), "text-max-width": 7 }),
    L("state", { "source-layer": "place", minzoom: 4, maxzoom: 9, filter: kind(["state", "province"]) }, "state", false,
      { "text-font": f.italic, "text-size": zs(4, 10, 8, 13), "text-transform": "uppercase", "text-letter-spacing": sp.state, "text-max-width": 8 }),
    L("city", { "source-layer": "place", minzoom: 3, filter: kind(["city"]) }, "city", false,
      { "text-font": f.bold, "text-size": zs(3, 11, 8, 15, 14, 20), "text-max-width": 7 }),
    L("country", { "source-layer": "place", maxzoom: 8, filter: kind(["country"]) }, "country", false,
      { "text-font": f.caps, "text-size": zs(1, 10, 3, 13, 6, 17), "text-transform": "uppercase", "text-letter-spacing": sp.country, "text-max-width": 7 }),
  ];
}
// OpenStreetMap's points of interest, on every basemap, from zoom 14 (Culprits round 166p).
function placeLayers() {
  const colour = ["match", ["get", "class"],
    ["restaurant", "fast_food", "cafe", "bar", "beer", "ice_cream", "bakery", "alcohol_shop"], "#5FA8B4",
    ["shop", "grocery", "clothing_store", "convenience", "supermarket", "jewelry", "hairdresser", "laundry", "furniture", "hardware", "mobile_phone",
     "books", "music", "gift", "shoe", "florist", "butcher", "car", "bicycle", "electronics", "toys", "pet", "optician", "art_gallery"], "#6F93C8",
    ["hospital", "doctors", "dentist", "pharmacy", "veterinary"], "#8FC3D6",
    ["school", "college", "kindergarten", "library", "music_school"], "#4E8FAE",
    ["place_of_worship", "cemetery", "grave_yard"], "#7A86B8",
    ["bus", "railway", "fuel", "parking", "ferry_terminal", "harbor", "airport", "aerialway", "entrance", "bicycle_rental", "car_rental"], "#5B7DA6",
    ["town_hall", "police", "fire_station", "post", "prison", "office", "embassy", "townhall", "court"], "#3F6E9A",
    ["park", "garden", "playground", "pitch", "stadium", "swimming", "sports", "golf", "zoo", "museum", "attraction", "theatre", "cinema",
     "monument", "castle", "viewpoint", "campsite", "information"], "#78B0A8", "#8A9AAE"];
  return [
    T("outline-places-dot", { type: "circle", source: "osm", "source-layer": "poi", minzoom: 14,
      paint: { "circle-color": colour, "circle-radius": zs(14, 2.2, 18, 4.5), "circle-stroke-color": "#0B1620",
               "circle-stroke-width": 0.8, "circle-opacity": 0.92, "circle-pitch-alignment": "map" } }),
    T("outline-places-name", { type: "symbol", source: "osm", "source-layer": "poi", minzoom: 15.5,
      layout: { "text-field": ["coalesce", ["get", "name_en"], ["get", "name:latin"], ["get", "name"]], "text-font": ["Jost-Regular"],
                "text-size": zs(15.5, 10, 19, 12.5), "text-variable-anchor": ["left", "right", "top", "bottom"], "text-radial-offset": 0.7,
                "text-justify": "auto", "text-max-width": 8, "text-optional": true },
      paint: { "text-color": "#C9D3D8", "text-halo-color": "#0B1620", "text-halo-width": 1.1, "text-halo-blur": 0.6 } }),
  ];
}

/* ---------- attach to a Leaflet map ---------- */
function create(container, opts) {
  opts = opts || {};
  if (opts.plate) PLATE.url = opts.plate;
  addProtocols();
  const state = { kind: null, want: opts.initial || "night", ready: false, stacks: {}, attribution: "" };
  const map = new maplibregl.Map({
    container: container, center: opts.center || [10, 18], zoom: opts.zoom == null ? 1.6 : opts.zoom, minZoom: 0, maxZoom: 16,
    attributionControl: false, renderWorldCopies: false, fadeDuration: 0, dragRotate: false, pitchWithRotate: false, touchPitch: false,
    pixelRatio: Math.min(window.devicePixelRatio || 1, 1.5),
    style: {
      version: 8, glyphs: ROOT + "glyphs/{fontstack}/{range}.pbf", projection: { type: opts.projection || "globe" },
      sources: {
        world: WORLD,
        base: { type: "raster", tiles: ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"],
                tileSize: 256, maxzoom: 18, attribution: "Imagery © Esri, Maxar" },
        hillshade: { type: "raster", tiles: ["https://services.arcgisonline.com/arcgis/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}"],
                     tileSize: 256, maxzoom: 16, attribution: "Hillshade © Esri" },
        labels: { type: "raster", tiles: ["https://a.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}@2x.png?key=cb1_494p_1_eebbbfcb65bc573e54783d42"],
                  tileSize: 256, attribution: "Labels © CARTO, © OpenStreetMap" },
        "plate-base": { type: "raster", tiles: ["plate://{z}/{x}/{y}"], tileSize: 256, maxzoom: 3,
                        bounds: [-180, PLATE.bottom, 180, PLATE.top] },
      },
      layers: [
        // The flat Culprits map's world-sized sheet (its "world-fill").
        { id: "world-fill", type: "fill", source: "world", paint: { "fill-color": "#0B1017" } },
        { id: "base", type: "raster", source: "base", layout: { visibility: "none" }, paint: Object.assign({ "raster-opacity": 1 }, BASE_GRADE.atlas) },
        { id: "hillshade", type: "raster", source: "hillshade", layout: { visibility: "none" },
          paint: { "raster-opacity": zs(4, .18, 9, .34, 13, .46) } },
      ],
    },
  });
  map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right");

  // Jurassic's faint vignette (Culprits #defence-hud), over the basemap's own picture.
  const vig = document.createElement("div");
  vig.style.cssText = "position:absolute;inset:0;pointer-events:none;display:none;z-index:1;background:radial-gradient(ellipse at center, rgba(0,0,0,0) 62%, rgba(8,7,10,.18) 100%)";
  map.getCanvasContainer().appendChild(vig);
  const share = (id, spec) => { if (!map.getSource(id)) map.addSource(id, Object.assign({}, spec)); };
  const add = (layers, before) => layers.forEach((l) => map.addLayer(Object.assign({}, l, { layout: Object.assign({}, l.layout || {}, { visibility: "none" }) }), before));
  const afterPlate = () => { const all = map.getStyle().layers, at = all.findIndex((l) => l.id === "plate-base"); return all[at + 1] && all[at + 1].id; };
  // Each stack is added the first time it is chosen, where Culprits puts it.
  const build = {
    outlines() { share("boundaries", BOUNDARIES); share("osm", OSM_SOURCE); share("outline-dem", RELIEF_SOURCE); share("outline-ocean", WORLD);
      return add(outlineLayers(), "atlas-washes"), outlineLayers(); },
    satellite() { share("outline-dem", RELIEF_SOURCE); share("sea-dem", TERRAIN_SOURCE); return add(satLayers(), "atlas-washes"), satLayers(); },
    hell() { share("boundaries", BOUNDARIES); share("osm", OSM_SOURCE); share("outline-dem", RELIEF_SOURCE); share("sea-dem", TERRAIN_SOURCE);
      add(hellLayers(), afterPlate()); add(nameLayers("hell")); return hellLayers().concat(nameLayers("hell")); },
    wood() { share("boundaries", BOUNDARIES); share("osm", OSM_SOURCE); share("outline-dem", RELIEF_SOURCE); share("sea-dem", TERRAIN_SOURCE);
      share("outline-wood-paint", { type: "raster", tiles: ["woodpaint://{z}/{x}/{y}"], tileSize: 256, maxzoom: 18, attribution: WOOD.attribution });
      share("outline-wood-photo", { type: "raster", tiles: ["woodphoto://{z}/{x}/{y}"], tileSize: 256, minzoom: 15, maxzoom: 18, attribution: WOOD.photoAttribution });
      add(woodLayers(), afterPlate()); add(nameLayers("wood")); return woodLayers().concat(nameLayers("wood")); },
    night() { share("boundaries", BOUNDARIES); share("osm", OSM_SOURCE); share("outline-dem", RELIEF_SOURCE); share("sea-dem", TERRAIN_SOURCE);
      share("outline-night-lights", { type: "raster", tiles: ["nightlights://{z}/{y}/{x}"], tileSize: 256, maxzoom: 8, attribution: NIGHT.attribution });
      add(nightLayers(), afterPlate()); return nightLayers(); },
    atlas() { return []; },
  };
  const ids = (k) => (state.stacks[k] || (state.stacks[k] = build[k]())).map((l) => l.id);
  const show = (id, on) => { if (map.getLayer(id)) map.setLayoutProperty(id, "visibility", on ? "visible" : "none"); };

  function apply(k) {
    if (!build[k]) throw new Error("unknown basemap " + k);
    ids(k);
    state.kind = k;
    for (const o of Object.keys(state.stacks)) for (const id of state.stacks[o].map((l) => l.id)) show(id, o === k);
    show("base", k === "atlas" || k === "satellite");
    if (k === "atlas" || k === "satellite") for (const p in BASE_GRADE[k]) map.setPaintProperty("base", p, BASE_GRADE[k][p]);
    show("hillshade", k === "atlas");
    show("plate-base", k === "atlas");
    // CARTO's picture of names only where the basemap has no names of its own.
    show("labels", k === "night" || k === "outlines");
    for (const n of ["atlas", "satellite"]) for (const l of nameLayers(n)) show(l.id, n === k);
    vig.style.display = k === "satellite" ? "block" : "none";
    map.triggerRepaint();
    attribution();
    if (opts.onApply) opts.onApply(k);
  }
  function attribution() {}
  map.on("load", () => {
    map.addLayer(washLayer(state));
    map.addLayer({ id: "plate-base", type: "raster", source: "plate-base", layout: { visibility: "none" },
      paint: { "raster-opacity": zs(PLATE.fadeIn, 1, PLATE.fadeOut, 0), "raster-fade-duration": 0 } });
    share("osm", OSM_SOURCE);
    add(placeLayers());
    for (const id of ["outline-places-dot", "outline-places-name"]) show(id, true);
    map.addLayer({ id: "labels", type: "raster", source: "labels", layout: { visibility: "none" }, paint: { "raster-opacity": .92 } });
    add(nameLayers("atlas")); add(nameLayers("satellite"));
    state.ready = true;
    apply(state.want);
    if (opts.onReady) opts.onReady();
  });
  return {
    set(k) { if (!build[k]) throw new Error("unknown basemap " + k); state.want = k; if (state.ready) apply(k); },
    current() { return state.ready ? state.kind : state.want; },
    maplibre: map,
  };
}


window.CulpritsBasemaps = { list: LIST.map((x) => x.slice()), create };
})();


