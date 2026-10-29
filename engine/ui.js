/* ui.js -- panel layout and click behaviour for the anti-slavery map.
   Runs after the page's own script and before engine/child.js. It builds the boxes the child layer mounts into,
   moves the help and about text into popups, and replaces hover highlighting with click selection. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var mk = function (html) { var d = document.createElement("div"); d.innerHTML = html.trim(); return d.firstChild; };

  /* ---------- palettes: one per basemap, the same sets as the secret society infiltration map ---------- */
  var PAL = window.SS_PAL = {
    night: { b: ["#a4c3df", "#62bcda", "#3859c7", "#cedfe9", "#85d7e0", "#2d39a9", "#5782c7", "#b8d3e0"],
      t: { covert: "#c6e4e7", statenet: "#2f38b1" },
      r: ["#8bb6e4", "#689dcf", "#4b88b9", "#457292", "#405c6d"], p: ["#6cb2e5", "#b9e1e9", "#546dd4", "#a7a9dd", "#1ca7e3", "#dbe3f0", "#78dee3", "#293aae", "#b4c7da"], ln: "#cfe2f0",
      card: "rgba(8,16,26,.94)", edge: "#1d3147", ui: ["#326c9f", "#95c6e4", "#06101c"] },
    outlines: { b: ["#d0605e", "#a07cc4", "#6a9fd4", "#4fb0a8", "#7fae6a", "#a8806a", "#d487a8", "#9aa3ad"],
      t: { covert: "#4fb0a8", statenet: "#d0605e" },
      r: ["#c8464f", "#d98482", "#b9a6c2", "#7ea3c9", "#5b7fa6"], p: ["#d0605e", "#6a9fd4", "#a07cc4", "#4fb0a8", "#a8806a", "#b5577f", "#e09ab8", "#7fae6a", "#9aa3ad"], ln: "#e2e5e8",
      card: "rgba(14,18,20,.94)", edge: "#2c3640", ui: ["#4f6f8f", "#a9c4dc", "#0c1012"] },
    satellite: { b: ["#a9c48f", "#7fae7a", "#5e8a5a", "#c9d9b4", "#8fbfa2", "#4f7a52", "#9aaa72", "#b7cfa9"],
      t: { covert: "#cfe0c0", statenet: "#4d7448" },
      r: ["#c2d8a8", "#9fbf86", "#7ea36a", "#617f52", "#4a5f42"], p: ["#8fbf7a", "#cfe0b8", "#5f8f5a", "#a9b88a", "#6fae92", "#e0ead6", "#b3d39a", "#3f6a40", "#bccaa8"], ln: "#e3ecd8",
      card: "rgba(10,18,12,.94)", edge: "#2a3d2c", ui: ["#4f7a52", "#b3d39a", "#0a120c"] },
    atlas: { b: ["#4f7a4a", "#2f5d3a", "#1f3a2a", "#7c9a5e", "#3f7262", "#26402f", "#5a6b3c", "#8aa57a"],
      t: { covert: "#8fae86", statenet: "#1f3526" },
      r: ["#2c4a2a", "#3f6338", "#5c7d4c", "#7e9a6a", "#a2b694"], p: ["#3a6b3a", "#7fa06a", "#2c4d3e", "#5c7a52", "#1f5a4a", "#9db58a", "#4f8a6a", "#24361f", "#6f8a72"], ln: "#24361f", light: true,
      card: "rgba(12,20,14,.94)", edge: "#2f4632", ui: ["#3f6b45", "#a9c79a", "#0c140e"] },
    hell: { b: ["#e0a8a0", "#c46a62", "#8e2f34", "#efcfc8", "#d4868a", "#6e2228", "#a8484a", "#e8bdb4"],
      t: { covert: "#f0d4cd", statenet: "#7a2a30" },
      r: ["#e8a49a", "#cc7a72", "#a85a56", "#7f4644", "#5e3a3a"], p: ["#d9827a", "#f0c7bf", "#a63a3c", "#c99a94", "#d0565e", "#f7e1dc", "#e8a89e", "#7a2228", "#d4b0aa"], ln: "#f2dcd6",
      card: "rgba(22,9,11,.94)", edge: "#4a2226", ui: ["#8e3a3e", "#e8aaa4", "#14080a"] }
  };
  var P = PAL.atlas;
  function bmKey() { try { return (window.__BM && window.__BM.current()) || "atlas"; } catch (e) { return "atlas"; } }
  function ramp5() { return [P.r[4], P.r[3], P.r[2], P.r[1], P.r[0]]; }   // lowest to highest; the strongest colour means most
  function hexA(h, a) { var x = h.replace("#", ""); return "rgba(" + parseInt(x.slice(0, 2), 16) + "," + parseInt(x.slice(2, 4), 16) + "," + parseInt(x.slice(4, 6), 16) + "," + a + ")"; }
  function HAS() { return P.ui[1]; } function SELC() { return P.ln; } function LINKC() { return P.light ? P.t.covert : P.b[2]; }

  /* ---------- draggable boxes ---------- */
  function drag(box, handle) {
    var sx, sy, sl, st, on = false;
    handle.addEventListener("mousedown", function (e) {
      if (e.target.closest("button,a,input,select")) return;
      var r = box.getBoundingClientRect(); on = true; sx = e.clientX; sy = e.clientY; sl = r.left; st = r.top; e.preventDefault();
    });
    document.addEventListener("mousemove", function (e) {
      if (!on) return;
      var w = box.offsetWidth, h = box.offsetHeight;
      box.style.left = Math.max(4, Math.min(sl + e.clientX - sx, innerWidth - w - 4)) + "px";
      box.style.top = Math.max(4, Math.min(st + e.clientY - sy, innerHeight - 40)) + "px";
      box.style.right = "auto"; box.style.bottom = "auto"; box._moved = true;
    });
    document.addEventListener("mouseup", function () { on = false; });
  }
  function box(id, title, cls) {
    var b = mk('<div id="' + id + '" class="uibox ' + (cls || "") + '" role="dialog"><div class="uib-h"><span>' + esc(title) + '</span><button type="button" title="Close" aria-label="Close">×</button></div><div class="uib-b"></div></div>');
    document.body.appendChild(b);
    drag(b, b.querySelector(".uib-h"));
    b.querySelector(".uib-h button").addEventListener("click", function () { b.classList.remove("open"); if (b._onClose) b._onClose(); place(); });
    ["mousedown", "wheel", "dblclick", "click", "touchstart"].forEach(function (t) { b.addEventListener(t, function (e) { e.stopPropagation(); }, { passive: true }); });
    return b;
  }
  function centre(b, w, maxH) {
    if (b._moved) return;
    var m = mid();
    w = Math.min(w, m.r - m.l, innerWidth - 24);
    b.style.width = w + "px"; b.style.maxHeight = (maxH || innerHeight - 100) + "px";
    b.style.left = Math.round(m.l + (m.r - m.l - w) / 2) + "px";
    b.style.top = Math.max(70, Math.round((innerHeight - Math.min(b.offsetHeight || 300, maxH || 600)) / 2)) + "px";
  }

  /* The free middle of the screen: right of the second column, left of the right-hand bar. */
  function mid() {
    var l = 14, r = innerWidth - 14;
    var c = $("#cnCol"); if (c && c.offsetWidth) l = c.getBoundingClientRect().right + 10;
    else { var w = $("#wirePanel"); if (w && w.offsetWidth) l = w.getBoundingClientRect().right + 10; }
    var rb = $("#rightbar"); if (rb && rb.offsetWidth) r = rb.getBoundingClientRect().left - 10;
    if (r - l < 340) { l = 14; r = innerWidth - 14; }
    return { l: l, r: r };
  }

  /* ---------- layout ---------- */
  var col, keyPanel, patPanel, summary, country, how, about, hint;
  function layout() {
    var sb = $("#sidebar");
    ["#wirePanel", "#indexPanel"].forEach(function (q) { var e = $(q); if (e && sb && sb.contains(e)) document.body.appendChild(e); });

    col = mk('<div id="cnCol"></div>');
    keyPanel = mk('<div id="cnKeyPanel" class="uip"><div class="uip-h"><span>Child abuse networks and child trafficking</span><span class="uip-t">−</span></div><div class="uip-b cnui" id="cnKeyHost"></div></div>');
    patPanel = mk('<div id="cnPatPanel" class="uip"><div class="uip-h"><span>Patterns behind the scenes</span><span class="uip-t">−</span></div><div class="uip-b cnui" id="cnPatHost"></div></div>');
    var rb = $("#rightbar");
    if (rb) rb.insertBefore(keyPanel, rb.firstChild); else col.appendChild(keyPanel);
    col.appendChild(patPanel); document.body.appendChild(col);
    [keyPanel, patPanel].forEach(function (p) {
      var h = p.querySelector(".uip-h");
      h.addEventListener("click", function (e) { if (e.target.closest(".ib")) return; p.classList.toggle("collapsed"); h.querySelector(".uip-t").textContent = p.classList.contains("collapsed") ? "+" : "−"; reflowInfo(); });
      ["wheel", "mousedown", "dblclick", "click"].forEach(function (t) { p.addEventListener(t, function (e) { e.stopPropagation(); }, { passive: true }); });
    });

    document.body.appendChild(mk('<div id="bmBar"></div>'));
    ["wheel", "mousedown", "dblclick", "click"].forEach(function (t) { $("#bmBar").addEventListener(t, function (e) { e.stopPropagation(); }, { passive: true }); });

    summary = box("cnSummary", "On record here");
    country = box("cnCountry", "Child abuse networks and child trafficking");
    country.querySelector(".uib-b").className = "cnc-body cnui";
    how = box("uiHow", "How to use this map");
    about = box("uiAbout", "About");
    hint = box("uiHint", "");

    var hb = $("#helpPanel .help-body"); if (hb) { while (hb.firstChild) how.querySelector(".uib-b").appendChild(hb.firstChild); }
    var lead = $("#wirePanel .wire-lead"); if (lead) about.querySelector(".uib-b").appendChild(lead);

    var hdr = $("#header");
    if (hdr) {
      var btns = mk('<div id="hdrBtns"><button type="button" id="howBtn">How to use this map</button><button type="button" id="aboutBtn">About</button></div>');
      hdr.appendChild(btns);
      $("#howBtn").addEventListener("click", function () { toggle(how, 640); });
      $("#aboutBtn").addEventListener("click", function () { toggle(about, 620); });
    }
    window.__uiPlace = place;
    addEventListener("resize", function () { place(); placeBar(); });
  }
  function toggle(b, w) { if (b.classList.contains("open")) { b.classList.remove("open"); return; } b.classList.add("open"); b.scrollTop = 0; centre(b, w); }

  /* Basemap bar sits left of the zoom buttons. */
  function placeBar() {
    var bar = $("#bmBar"), z = $(".leaflet-top.leaflet-left"); if (!bar) return;
    var right = 16; if (z) { var r = z.getBoundingClientRect(); if (r.width) right = innerWidth - r.left + 8; }
    bar.style.right = right + "px";
  }

  /* The two centre boxes: summary on top, the child-networks section under it. */
  function place() {
    var m = mid(), w = Math.min(560, m.r - m.l), left = Math.round(m.l + (m.r - m.l - w) / 2);
    var top = 70;
    if (summary.classList.contains("open") && !summary._moved) {
      summary.style.left = left + "px"; summary.style.width = w + "px"; summary.style.top = top + "px";
      summary.style.maxHeight = Math.round(innerHeight * 0.32) + "px";
      top += summary.offsetHeight + 8;
    } else if (summary.classList.contains("open")) top = 70;
    if (country.classList.contains("open") && !country._moved) {
      country.style.left = left + "px"; country.style.width = w + "px"; country.style.top = top + "px";
      country.style.maxHeight = (innerHeight - top - 18) + "px";
    }
    reflowInfo();
  }

  /* A country's resources stay in their box in the second column, under the two panels' headings. */
  function reflowInfo() {
    var p = $("#infoPanel"); if (!p || !p.classList.contains("open")) return;
    if (innerWidth <= 640) { p.style.left = p.style.width = p.style.top = p.style.bottom = p.style.maxHeight = ""; return; }
    var c = col && col.getBoundingClientRect(), last = patPanel && patPanel.getBoundingClientRect();
    var top = last && last.height ? Math.round(last.bottom) + 9 : 70;
    if (top > innerHeight - 220) top = Math.max(70, innerHeight - 320);
    p.style.right = "auto"; p.style.left = (c ? Math.round(c.left) : 322) + "px"; p.style.width = (c && c.width ? Math.round(c.width) : 270) + "px";
    p.style.top = top + "px"; p.style.bottom = "18px"; p.style.maxHeight = (innerHeight - top - 18) + "px"; p.style.overflowY = "auto";
  }

  /* ---------- country selection (click, not hover) ---------- */
  var SEL = null, LINKED = null, origStyle = null;
  var CUTS = [2, 4, 6, 9];
  function prevClass(rate) { for (var i = 0; i < CUTS.length; i++) if (rate < CUTS[i]) return i; return 4; }
  window.prevColour = function (rate) { if (!rate) return null; return { fill: ramp5()[prevClass(rate)], op: 0.55 }; };
  function style(f) {
    var a3 = NUM2A3[f.id] || "", s = origStyle(f) || {};
    var has = s.color === "#ffd24a" || s.color === "#9fd0e6";
    var o = has ? { color: HAS(), weight: 1.2, opacity: 0.75 } : { color: P.edge, weight: 0.5, opacity: 0.35 };
    var rate = window.prevOn && window.PREV_RATE && window.PREV_RATE[a3];
    o.fillColor = rate ? ramp5()[prevClass(rate)] : HAS(); o.fillOpacity = rate ? 0.55 : 0;
    if (OVON) { rate = 0; var oc = ovColour(OVON, a3); o.fillColor = oc || HAS(); o.fillOpacity = oc ? 0.62 : 0; if (oc) rate = 1; }
    if (LINKED && LINKED[a3]) { o.color = LINKC(); o.weight = 2.8; o.opacity = 1; if (!rate) { o.fillColor = LINKC(); o.fillOpacity = 0.22; } }
    if (SEL === a3) { o.color = SELC(); o.weight = 3.6; o.opacity = 1; if (!rate) { o.fillColor = SELC(); o.fillOpacity = 0.14; } }
    return o;
  }
  function restyle() { try { geojsonLayer.setStyle(style); } catch (e) {} }

  function hookCountries() {
    origStyle = window.baseStyle;
    window.baseStyle = window.__baseStyle = style; geojsonLayer.options.style = style;
    window.setLinkedCountries = function (set) { LINKED = set || null; restyle(); };
    geojsonLayer.eachLayer(function (l) {
      l.off("mouseover"); l.off("mouseout"); l.off("mousemove");
      var f = l.feature;
      l.on("click", function () {
        var a3 = NUM2A3[f.id] || ""; if (!a3) return;
        setTimeout(function () {
          var open = $("#infoPanel") && $("#infoPanel").classList.contains("open");
          if (!open && !(typeof gbNav !== "undefined" && gbNav && gbNav.iso === a3)) return;
          select(a3, (trackerData[a3] && trackerData[a3].name) || (f.properties && f.properties.name) || a3);
        }, 0);
      });
    });
    restyle();
  }
  function select(a3, name) {
    SEL = a3; restyle();
    var b = summary.querySelector(".uib-b"), h = "";
    try { window._chvIso = null; if (window.CLEVEL && window.CLEVEL[a3] && window.CLEVEL[a3].length) { clevelShow(a3, name, { x: 0, y: 0 }); h = $("#cHover").innerHTML; } } catch (e) {}
    var ov = ovText(a3); if (ov) h = ov + h;
    if (h) { summary.querySelector(".uib-h span").textContent = name + ": on record"; b.innerHTML = h; summary.classList.add("open"); summary.scrollTop = 0; }
    else summary.classList.remove("open");
    place();
  }
  function unselect() { SEL = null; summary.classList.remove("open"); country.classList.remove("open"); restyle(); }

  /* ---------- corridors: click one and its two countries light up ---------- */
  function hookRoutes() {
    var orig = window.drawRoutes; if (!orig || orig.__ui) return;
    var w = function () {
      var r = orig.apply(this, arguments);
      (window._routeRefs || []).forEach(function (ref) {
        ref.layers.forEach(function (l) { l.on("click", function () { focusRoute(ref); }); });
      });
      return r;
    };
    w.__ui = true; window.drawRoutes = w;
    try { if (window._routeRefs && window._routeRefs.length) drawRoutes(); } catch (e) {}
  }
  function focusRoute(ref) {
    window.ROUTE_PINNED = "route"; window.ROUTE_FOCUS = null;
    (window._routeRefs || []).forEach(function (x) {
      var on = x === ref;
      x.layers.forEach(function (l) { try { if (l.setStyle) l.setStyle(l._isDot ? { opacity: on ? 0.95 : 0.06, fillOpacity: on ? 0.95 : 0.06 } : { opacity: on ? 0.95 : 0.06, weight: x.w * (on ? 1.5 : 0.8) }); } catch (e) {} });
    });
    var s = {}; s[ref.from] = 1; s[ref.to] = 1; window.setLinkedCountries(s);
  }

  /* ---------- "Lower level" from the national box lists the regions ---------- */
  function hookDrill() {
    var orig = window.gbUnitDown;
    window.gbUnitDown = function () {
      if (!(gbNav && gbPopupCtx && gbPopupCtx.lvl === "ADM0")) return orig.apply(this, arguments);
      var body = $("#infoBody"), old = body && body.querySelector(".gb-sublist");
      if (old) { old.remove(); return; }
      try { gbShow(); } catch (e) {}
      var bar = body && body.querySelector(".gb-zoombar"); if (!bar) return;
      var list = mk('<div class="gb-sublist"><div class="gbs-h">Loading the regions…</div></div>'); bar.parentNode.insertBefore(list, bar.nextSibling);
      var iso = gbNav.iso;
      gbChildren(gbStack[0], function (res) {
        if (!res || !res.feats || !res.feats.length) { list.innerHTML = '<div class="gbs-h">No regions are mapped for this country.</div>'; return; }
        var items = res.feats.map(function (f) { var n = gbChildName(f); var has = false; try { has = !!gbMatchRegion(iso, n); } catch (e) {} return { f: f, n: n, has: has }; });
        items.sort(function (a, b) { return (b.has - a.has) || a.n.localeCompare(b.n); });
        var nh = items.filter(function (x) { return x.has; }).length;
        list.innerHTML = '<div class="gbs-h">' + items.length + ' regions' + (nh ? ' · ' + nh + ' with their own entries (filled dot)' : '') + '. Choose one.</div>' +
          items.map(function (x, i) { return '<div class="gbs-i' + (x.has ? " has" : "") + '" data-i="' + i + '"><i></i>' + esc(x.n) + '</div>'; }).join("");
        list.querySelectorAll(".gbs-i").forEach(function (el) {
          el.addEventListener("click", function () { var x = items[+el.dataset.i]; try { gbDescend(res.lvl, res.isAdm4, x.f, gbFeatBounds(x.f), null); } catch (e) { console.warn(e); } });
        });
      });
    };
  }

  /* ---------- goals, angles and lenses: clear the map and say what to do next ---------- */
  var saved = null;
  function setChk(id, v) { var e = document.getElementById(id); if (!e || e.checked === v) return; e.checked = v; e.dispatchEvent(new Event("change", { bubbles: true })); }
  function clearMap() {
    if (saved) return;
    var g = function (id) { var e = document.getElementById(id); return e ? e.checked : null; };
    saved = { proj: g("projChk"), fac: g("facToggle"), route: g("routeChk"), prev: !!window.prevOn, ov: null };
    saved.ov = OVON; if (OVON) ovSet(null);
    setChk("projChk", false); setChk("facToggle", false); setChk("routeChk", false);
    if (window.prevOn) window.togglePrevalence(false);
    if (window.cnHide) window.cnHide();
  }
  function restoreMap() {
    if (!saved) return; var s = saved; saved = null;
    if (s.proj) setChk("projChk", true); if (s.fac) setChk("facToggle", true); if (s.route) setChk("routeChk", true);
    if (s.prev) window.togglePrevalence(true);
    if (s.ov) ovSet(s.ov);
    if (window.cnRestore) window.cnRestore();
  }
  function showHint(title, text) {
    if (!text) { hint.classList.remove("open"); restoreMap(); return; }
    clearMap();
    hint.querySelector(".uib-h span").textContent = title;
    hint.querySelector(".uib-b").innerHTML = '<div>' + esc(text) + '</div><div class="uih-go">Click a country to see these resources for it. Outlined countries have at least one.</div>' +
      '<div class="uih-row"><button type="button" class="uibtn" id="uihBack">Show the other map layers again</button></div>';
    $("#uihBack").addEventListener("click", function () { restoreMap(); hint.classList.remove("open"); });
    hint.classList.add("open"); hint._moved = false; centre(hint, 460, 360);
  }
  function hookSelectors() {
    var oi = window.applyIntent, oa = window.applyAngle;
    window.applyIntent = function (v) { var r = oi.apply(this, arguments); var it = v && v !== "all" && INTENTS[v]; var o = $("#intentSel option[value='" + v + "']"); showHint(o ? o.textContent.replace(/^\d+\s*·\s*/, "") : "Your goal", it ? it.hint : ""); return r; };
    window.applyAngle = function (v) { var r = oa.apply(this, arguments); var t = v && v !== "all" ? ANGLEHINT[v] : ""; var o = $("#angleSel option[value='" + v + "']"); showHint(o ? o.textContent : "How you will act", t); return r; };
    var dp = $("#domainPills");
    if (dp) dp.addEventListener("click", function (e) {
      var p = e.target.closest(".dpill"); if (!p) return;
      setTimeout(function () { var d = $("#domainDesc"); var t = domain !== "all" && d ? d.textContent.trim() : ""; showHint("Lens: " + p.textContent.trim(), t); }, 0);
    });
    hint._onClose = function () {};
  }

  /* ---------- map key: one list, the same row for every layer ---------- */
  var HOW = {
    "projects.json": "markers", "points.json": "markers", "infra.json": "markers", "vessels.json": "markers", "suspected.json": "markers",
    "sites.json": "markers", "wire.json": "markers", "bulk.json": "markers", "companies.json": "box", "cases.json": "box", "law.json": "box",
    "directory.json": "list", "prevalence.json": "shade", "routes.json": "lines"
  };
  function sevC(k) { return { 1: P.r[4], 2: P.r[3], 3: P.r[2], 4: P.r[1], 5: P.r[0] }[k]; }
  function dot(c) { return '<span class="sw-d" style="background:' + c + '"></span>'; }
  function swatch(kind) {
    if (kind === "markers") return dot(sevC(2)) + dot(sevC(3)) + dot(sevC(4)) + dot(sevC(5));
    if (kind === "shade") return ramp5().map(function (c) { return '<span class="sw-o" style="background:' + c + ';width:6px;border-radius:0"></span>'; }).join("");
    if (kind === "lines") return [0, 2, 4].map(function (i) { return '<span class="sw-l" style="border-color:' + P.b[i] + ';width:8px"></span>'; }).join("");
    if (kind === "facilities") return dot(P.p[0]) + dot(P.p[1]) + dot(P.p[2]) + dot(P.p[3]);
    if (kind === "list") return '<span class="sw-o" style="border:1px solid ' + HAS() + ';background:repeating-linear-gradient(180deg,' + HAS() + ' 0 1px,transparent 1px 3px)"></span>';
    return '<span class="sw-o" style="border:2px solid ' + SELC() + '"></span>';
  }
  var HOWTXT = { markers: "markers on the map", box: "figures in a clicked country's summary", list: "a clicked country's list of resources", shade: "country shading", lines: "lines between countries" };
  window.renderDataStatus = function () {
    var el = document.getElementById("ukData"); if (!el || typeof DATA_LAYERS === "undefined") return;
    var rows = "";
    DATA_LAYERS.forEach(function (L) {
      var s = window.DATA_STATUS[L.f], how = HOW[L.f] || "box"; if (!s) return;
      rows += '<div class="uk-row' + (s.ok ? "" : " off") + '"><span class="uk-sw" data-k="' + how + '">' + swatch(how) + '</span><span class="uk-l">' + esc(L.label) +
        '<span class="uk-d">' + (s.ok ? "Shown as " + HOWTXT[how] : "Not collected yet") + '</span></span><span class="uk-n">' + (s.ok ? s.n.toLocaleString() : "–") + '</span></div>';
    });
    el.innerHTML = rows;
  };
  function row(id, kind, label, count, info, checked) {
    return '<div class="uk-row"><label class="uk-c"><input type="checkbox" data-uk="' + id + '"' + (checked ? " checked" : "") + '></label><span class="uk-sw" data-k="' + kind + '">' + swatch(kind) + '</span>' +
      '<span class="uk-l">' + label + '</span><span class="uk-n">' + (count == null ? "" : count) + '</span>' + (info ? '<button type="button" class="uk-i" data-uki="' + id + '" title="What is this?">i</button>' : '') + '</div>' +
      (info ? '<div class="uk-info" data-ukinfo="' + id + '">' + info + '</div>' : '');
  }
  var SHADES = [["none", "No shading"], ["prev", "Estimated modern slavery per 1,000 people"]];
  function sec(id, title, body, open) {
    return '<div class="uk-sec' + (open ? "" : " shut") + '" data-uks="' + id + '"><div class="uk-h"><span>' + title + '</span><span class="uk-t">' + (open ? "−" : "+") + '</span></div><div class="uk-b">' + body + '</div></div>';
  }
  var keyBuilt = false;
  function buildKey() {
    var lb = $("#legBody"); if (!lb || keyBuilt) return;
    var chk = function (id) { var e = document.getElementById(id); return !!(e && e.checked); };
    var keep = { sev: $("#legBody .proj-size:not(.proj-phase)"), phase: $("#legBody .proj-phase"), search: $("#legBody .proj-search"), time: $("#legBody .proj-time"),
      src: $("#projSrcBox"), type: $("#projTypeBox"), fac: $("#facFilter"), detail: $("#legBody .lp-detail"), inc: $("#incCount"), bg: $("#bgStatus") };
    var hold = mk('<div id="ukHold" style="display:none"></div>');
    while (lb.firstChild) hold.appendChild(lb.firstChild);
    lbInfo = function () {}; var sevInfo = 'Each marker is a place or sector where forced labour or child labour is on record. Colour shows how serious the record is:' +
      [[2, "a news report, before any raid, rescue or charge"], [3, "documented in a named public source, or a raid, rescue or charge"], [4, "systemic: across a sector or region, or involving children"], [5, "gravest: state-imposed, a whole national industry, or deaths"]]
        .map(function (x) { return '<div class="ur">' + dot(sevC(x[0])) + x[1] + '</div>'; }).join("") + 'A pin is a known site. A dashed ring stands for a country or region, with no exact site in the source.';
    var rtInfo = 'Origin to destination, from identified-victim records (CTDC). ' + '<span style="color:' + P.b[0] + '">●</span> labour, <span style="color:' + P.b[2] + '">●</span> sexual, <span style="color:' + P.b[4] + '">●</span> mixed or unknown. Thicker means more people. A dashed ring is trafficking within one country. Click a line to light up both of its countries.';
    var facInfo = 'Police stations, courthouses, town halls, government offices, agency headquarters and embassies, from OpenStreetMap: where reports are made and records are kept. Choose the types under "Government building types".';
    var shadeRows = SHADES.concat(OVS.map(function (m) { return [m.k, m.label]; })).map(function (x) {
      return '<label class="uk-row uk-radio"><input type="radio" name="ukShade" value="' + x[0] + '"' + ((x[0] === "prev" && window.prevOn) || (x[0] === "none" && !window.prevOn && !OVON) || x[0] === OVON ? " checked" : "") + '><span class="uk-l">' + esc(x[1]) + '</span><span class="uk-st" data-ukst="' + x[0] + '"></span></label>';
    }).join("");
    var outl = '<div class="uk-out" id="ukOut"><div class="ur"><span class="sw-o" style="border:1.5px solid ' + HAS() + '"></span>Outlined: has resources for your filters</div>' +
      '<div class="ur"><span class="sw-o" style="border:3px solid ' + SELC() + '"></span>The country you clicked</div>' +
      '<div class="ur"><span class="sw-o" style="border:3px solid ' + LINKC() + '"></span>Linked by a corridor to the clicked country, or both ends of a clicked corridor</div></div>';
    lb.innerHTML =
      sec("on", "On the map", row("proj", "markers", "Cases and sites", null, sevInfo, chk("projChk")) + row("route", "lines", "Trafficking corridors", null, rtInfo, chk("routeChk")) +
        row("fac", "facilities", "Government buildings", null, facInfo, chk("facToggle")), true) +
      sec("shade", "Shade the countries by", shadeRows + '<div id="ukLeg" class="ukey"></div>' + outl, true) +
      sec("filt", "Filter the cases and sites", '<div id="ukFilt"></div>', false) +
      sec("facs", "Government building types", '<div id="ukFac"></div>', false) +
      sec("data", "Where the data comes from", '<div id="ukData"></div><div id="ukMore"></div>', false);
    lb.appendChild(hold);
    var f = $("#ukFilt"); ["sev", "phase", "search", "time", "src", "type"].forEach(function (k) { if (keep[k]) f.appendChild(keep[k]); });
    if (keep.fac) $("#ukFac").appendChild(keep.fac);
    ["inc", "bg", "detail"].forEach(function (k) { if (keep[k]) $("#ukMore").appendChild(keep[k]); });
    /* severity pills get their colour */
    f.querySelectorAll(".ps-pill[data-ms]").forEach(function (pl) { var k = +pl.dataset.ms; if (k && !pl.querySelector(".sw-d")) pl.insertAdjacentHTML("afterbegin", dot(sevC(k))); });
    lb.querySelectorAll(".uk-h").forEach(function (h) { h.addEventListener("click", function () { var s0 = h.parentNode; s0.classList.toggle("shut"); h.querySelector(".uk-t").textContent = s0.classList.contains("shut") ? "+" : "−"; }); });
    lb.querySelectorAll(".uk-i").forEach(function (b0) { b0.addEventListener("click", function (e) { e.preventDefault(); var i = lb.querySelector('[data-ukinfo="' + b0.dataset.uki + '"]'); if (i) i.classList.toggle("open"); }); });
    var map0 = { proj: "projChk", route: "routeChk", fac: "facToggle" };
    lb.querySelectorAll("input[data-uk]").forEach(function (cb) {
      var orig = document.getElementById(map0[cb.dataset.uk]);
      cb.addEventListener("change", function () { setChk(map0[cb.dataset.uk], cb.checked); });
      if (orig) orig.addEventListener("change", function () { cb.checked = orig.checked; });
    });
    lb.querySelectorAll("input[name=ukShade]").forEach(function (r) { r.addEventListener("change", function () { if (r.checked) setShade(r.value); }); });
    keyBuilt = true; renderDataStatus(); shadeLegend();
    // the host sets these switches in code without a change event, so keep the copies in step
    setInterval(function () { lb.querySelectorAll("input[data-uk]").forEach(function (cb) { var o = document.getElementById(map0[cb.dataset.uk]); if (o && cb.checked !== o.checked) cb.checked = o.checked; }); }, 800);
  }
  var lbInfo = null;
  function theme(k) {
    P = PAL[k] || PAL.atlas;
    var rs = document.documentElement.style;
    rs.setProperty("--accent", P.ui[0]); rs.setProperty("--accent-hi", P.ui[1]); rs.setProperty("--accent-soft", hexA(P.ui[0], 0.4));
    rs.setProperty("--card", P.card); rs.setProperty("--line", P.edge); rs.setProperty("--uiln", P.ln);
    try { if (window.PJ_PC) { [1, 2, 3, 4, 5].forEach(function (i) { window.PJ_PC[i] = sevC(i); }); if (window.pjRender) window.pjRender(); } } catch (e) {}
    window.routeColour = function (kind) { return kind === "sexual exploitation" ? P.b[2] : kind === "labour exploitation" ? P.b[0] : P.b[4]; };
    try { drawRoutes(); } catch (e) {}
    try { if (window.FACCOL) { ["po", "ch", "th", "go", "mi", "dp", "fs", "bd", "pr"].forEach(function (x, i) { window.FACCOL[x] = P.p[i]; });
      var ft = document.getElementById("facToggle"); if (ft && ft.checked) { setChk("facToggle", false); setChk("facToggle", true); } } } catch (e) {}
    restyle(); if (ovLines) ovDrawLines(OVD.corridors);
    if (keyBuilt) {
      document.querySelectorAll(".uk-sw[data-k]").forEach(function (el) { el.innerHTML = swatch(el.dataset.k); });
      var o = $("#ukOut"); if (o) o.innerHTML = '<div class="ur"><span class="sw-o" style="border:1.5px solid ' + HAS() + '"></span>Outlined: has resources for your filters</div>' +
        '<div class="ur"><span class="sw-o" style="border:3px solid ' + SELC() + '"></span>The country you clicked</div>' +
        '<div class="ur"><span class="sw-o" style="border:3px solid ' + LINKC() + '"></span>Linked by a corridor to the clicked country, or both ends of a clicked corridor</div>';
      document.querySelectorAll("#ukFilt .ps-pill[data-ms] .sw-d").forEach(function (d0) { d0.style.background = sevC(+d0.parentNode.dataset.ms); });
      var i1 = $('[data-ukinfo="proj"]'); if (i1) i1.innerHTML = sevInfoHTML(); var i2 = $('[data-ukinfo="route"]'); if (i2) i2.innerHTML = rtInfoHTML();
    }
    shadeLegend();
  }
  function sevInfoHTML() { return 'Each marker is a place or sector where forced labour or child labour is on record. Colour shows how serious the record is:' +
      [[2, "a news report, before any raid, rescue or charge"], [3, "documented in a named public source, or a raid, rescue or charge"], [4, "systemic: across a sector or region, or involving children"], [5, "gravest: state-imposed, a whole national industry, or deaths"]]
        .map(function (x) { return '<div class="ur">' + dot(sevC(x[0])) + x[1] + '</div>'; }).join("") + 'A pin is a known site. A dashed ring stands for a country or region, with no exact site in the source.'; }
  function rtInfoHTML() { return 'Origin to destination, from identified-victim records (CTDC). <span style="color:' + P.b[0] + '">\u25cf</span> labour, <span style="color:' + P.b[2] + '">\u25cf</span> sexual, <span style="color:' + P.b[4] + '">\u25cf</span> mixed or unknown. Thicker means more people. A dashed ring is trafficking within one country. Click a line to light up both of its countries.'; }
  function setShade(k) {
    if (k === "none") { ovSet(null); if (window.prevOn) window.togglePrevalence(false); shadeLegend(); return; }
    if (k === "prev") { ovSet(null); if (!window.prevOn) window.togglePrevalence(true); shadeLegend(); return; }
    var st = $('[data-ukst="' + k + '"]'); if (st) st.textContent = "loading…";
    ovLoad(k).then(function (d) { if (st) st.textContent = d ? "" : "not available"; if (d) { ovSet(k); shadeLegend(); } });
  }
  function shadeLegend() {
    var el = $("#ukLeg"); if (!el) return;
    document.querySelectorAll("input[name=ukShade]").forEach(function (r) { r.checked = OVON ? r.value === OVON : (window.prevOn ? r.value === "prev" : r.value === "none"); });
    if (OVON && OVD[OVON]) { var d = OVD[OVON], m = ovMeta(OVON); el.innerHTML = '<div class="uk-d" style="margin-bottom:4px">' + esc(m.note) + '</div>' + ovLegend(m) + '<div class="uk-d" style="margin-top:4px">' + esc(d.source) + ', ' + esc(d.as_of) + '. Click a country for its entry.</div>'; return; }
    if (window.prevOn) { el.innerHTML = '<div class="ramp">' + ramp5().map(function (c) { return '<span style="background:' + c + '"></span>'; }).join("") + '</div><div class="rl"><span>under 2</span><span>2–4</span><span>4–6</span><span>6–9</span><span>9+</span></div><div class="uk-d" style="margin-top:4px">Walk Free, Global Slavery Index 2023: people in forced labour, forced marriage and forced sexual exploitation per 1,000, modelled from surveys.</div>'; return; }
    el.innerHTML = "";
  }

  /* ---------- context overlays ---------- */
  function OVR(i) { return ramp5()[i]; }
  var OVS = [
    { k: "sez", label: "Special economic zones", note: "Zones where ordinary labour, tax and customs rules are relaxed for investors. Count of zones per country.",
      bins: [[0, 0, "none counted"], [1, 5, "1–5"], [6, 20, "6–20"], [21, 100, "21–100"], [101, 1e12, "over 100"]] },
    { k: "listed_goods", label: "Listed goods by country (US DOL)", note: "How many goods the US Labor Department lists as made with child or forced labour in the country.",
      bins: [[1, 1, "1"], [2, 3, "2–3"], [4, 6, "4–6"], [7, 12, "7–12"], [13, 1e12, "13 or more"]] },
    { k: "c29_c182", label: "ILO Convention ratifications", note: "How many of five ILO instruments the state has ratified: C29, its 2014 Protocol, C105, C138 and C182. Darker means fewer.",
      bins: [[5, 5, "all 5"], [4, 4, "4"], [3, 3, "3"], [2, 2, "2"], [0, 1, "0–1"]] },
    { k: "corridors", label: "Labour migration corridors", note: "Main routes for contract workers, from the sending country’s own count of workers sent. Countries shaded by workers sent in a year; click a line for the corridor and its recruitment costs.",
      bins: [[0, 199999, "<200k"], [200000, 499999, "200–500k"], [500000, 999999, "0.5–1m"], [1000000, 1999999, "1–2m"], [2000000, 1e12, ">2m"]] },
    { k: "due_diligence", label: "Supply-chain due-diligence laws", note: "National laws in force that make companies report on, or act on, forced labour in their supply chains.",
      cats: [["transparency", "must publish a statement", 1], ["due diligence", "must find and act on risks", 4], ["eu", "EU law, not yet applying", 0]] }
  ];
  var OVD = {}, OVON = null, ovLines = null;
  function ovMeta(k) { for (var i = 0; i < OVS.length; i++) if (OVS[i].k === k) return OVS[i]; }
  function ovColour(k, a3) {
    var d = OVD[k], m = ovMeta(k); if (!d) return null;
    var c = d.countries && d.countries[a3];
    if (m.cats) {
      if (c) { for (var i = 0; i < m.cats.length; i++) if (m.cats[i][0] === c.v) return OVR(m.cats[i][2]); }
      if (d.eu_note && d.eu_note.members && d.eu_note.members.indexOf(a3) >= 0) return OVR(0);
      return null;
    }
    if (!c || c.v == null) return null;
    for (var j = 0; j < m.bins.length; j++) if (c.v >= m.bins[j][0] && c.v <= m.bins[j][1]) return OVR(j);
    return null;
  }
  function ovText(a3) {
    if (!OVON || !OVD[OVON]) return "";
    var d = OVD[OVON], m = ovMeta(OVON), c = d.countries && d.countries[a3], t = "";
    if (c) t += '<div>' + esc(c.text) + (c.url ? ' <a href="' + esc(c.url) + '" target="_blank" rel="noopener">Source</a>' : '') + '</div>';
    if (OVON === "due_diligence" && d.eu_note && d.eu_note.members.indexOf(a3) >= 0) t += '<div style="margin-top:4px">' + esc(d.eu_note.text) + '</div>';
    if (OVON === "corridors") (d.lines || []).filter(function (l) { return l.from === a3 || l.to === a3; }).forEach(function (l) {
      t += '<div style="margin-top:4px"><b>' + esc(nm(l.from)) + ' → ' + esc(nm(l.to)) + '.</b> ' + esc(l.text) + (l.url ? ' <a href="' + esc(l.url) + '" target="_blank" rel="noopener">Source</a>' : '') + '</div>'; });
    if (!t) t = '<div class="mute">Nothing recorded for this country in this layer.</div>';
    return '<div class="ukey" style="border-bottom:1px solid rgba(149,171,150,.2);padding-bottom:7px;margin-bottom:7px"><b>' + esc(m.label) + '</b>' + t + '<div class="mute" style="margin-top:3px">' + esc(d.source) + ', ' + esc(d.as_of) + '.</div></div>';
  }
  function nm(a3) { return (trackerData[a3] && trackerData[a3].name) || (window.ISO_NAME && window.ISO_NAME[a3]) || a3; }
  function ovLegend(m) {
    var rows = m.cats ? m.cats.map(function (c) { return '<div class="ur"><span class="sw-o" style="background:' + OVR(c[2]) + '"></span>' + esc(c[1]) + '</div>'; }).join("")
      : '<div class="ramp">' + m.bins.map(function (b, i) { return '<span style="background:' + OVR(i) + '"></span>'; }).join("") + '</div><div class="rl">' + m.bins.map(function (b) { return '<span>' + esc(b[2]) + '</span>'; }).join("") + '</div>';
    if (m.k === "corridors") rows += '<div class="ur" style="margin-top:4px"><span class="sw-l" style="border-color:' + P.ln + '"></span>corridor; thicker means more workers</div>';
    return rows;
  }
  function ovDrawLines(d) {
    if (ovLines) { map.removeLayer(ovLines); ovLines = null; }
    if (!d || !d.lines) return;
    var C = window.ISO_CENTROID || {}, g = L.layerGroup(), max = 1;
    d.lines.forEach(function (l) { if (l.v) max = Math.max(max, l.v); });
    d.lines.forEach(function (l) {
      var a = C[l.from], b = C[l.to]; if (!a || !b) return;
      var lat1 = a[0], lon1 = a[1], lat2 = b[0], lon2 = b[1];
      if (Math.abs(lon2 - lon1) > 180) lon2 += lon1 > lon2 ? 360 : -360;
      var cx = (lat1 + lat2) / 2 - (lon2 - lon1) * 0.14, cy = (lon1 + lon2) / 2 + (lat2 - lat1) * 0.14, pts = [];
      for (var t = 0; t <= 1.0001; t += 0.05) { var u = 1 - t; pts.push([u * u * lat1 + 2 * u * t * cx + t * t * lat2, u * u * lon1 + 2 * u * t * cy + t * t * lon2]); }
      var w = l.v ? 1.5 + 4.5 * Math.sqrt(l.v / max) : 1.5;
      var pl = L.polyline(pts, { color: P.ln, weight: w, opacity: 0.85, dashArray: l.v ? null : "4 4" });
      pl.bindPopup('<div class="popup-country">' + esc(nm(l.from)) + ' → ' + esc(nm(l.to)) + '</div><div class="tracker-desc">' + esc(l.text) + (l.url ? '<br><a href="' + esc(l.url) + '" target="_blank" rel="noopener">Source</a>' : '') + '</div>');
      g.addLayer(pl);
    });
    ovLines = g.addTo(map);
  }
  function ovSet(k) {
    OVON = k || null;
    if (OVON && window.prevOn) window.togglePrevalence(false);
    ovDrawLines(OVON === "corridors" ? OVD.corridors : null);
    restyle();
    if (SEL) select(SEL, nm(SEL));
    shadeLegend();
  }
  function ovLoad(k) {
    if (OVD[k]) return Promise.resolve(OVD[k]);
    return fetch("data/overlays/" + k + ".json").then(function (r) { if (!r.ok) throw 0; return r.json(); })
      .catch(function () { return (window.__BUNDLED && window.__BUNDLED["data/overlays/" + k + ".json"]) || null; })
      .then(function (d) { if (d) OVD[k] = d; return d; });
  }
  /* ---------- boot ---------- */
  layout();
  var tries = 0;
  (function wait() {
    if (typeof geojsonLayer === "undefined" || !geojsonLayer || !window.baseStyle || !window.drawRoutes || !window.applyIntent) { if (tries++ < 600) return setTimeout(wait, 100); return; }
    hookCountries(); hookRoutes(); hookDrill(); hookSelectors();
    window._reflowInfo = reflowInfo;
    var oh = window.hideInfoPanel;
    window.hideInfoPanel = function () { var r = oh.apply(this, arguments); unselect(); return r; };
    var os = window.showInfoPanel;
    window.showInfoPanel = function () {
      var r = os.apply(this, arguments);
      patPanel.classList.add("collapsed"); patPanel.querySelector(".uip-t").textContent = "+";
      reflowInfo(); return r;
    };
    if (!window.prevOn) window.togglePrevalence(true);
    (function key() { var ob = $("#overlayBox"); if (!ob || ob.getAttribute("data-built") !== "1" || !$("#facFilter")) return setTimeout(key, 300); buildKey(); })();
    var pc0 = $("#prevChk"); if (pc0) pc0.addEventListener("change", function () { if (pc0.checked && OVON) ovSet(null); shadeLegend(); });
    theme(bmKey()); (window.__bmListeners = window.__bmListeners || []).push(function (k) { theme(k); });
    (function bases() {
      var bs = $("#bmBody .bases"); if (!bs) return setTimeout(bases, 300);
      var rs = [].slice.call(bs.querySelectorAll("input[name=basemap]"));
      var sel = mk('<select id="bmSel" aria-label="Basemap">' + rs.map(function (r) { return '<option value="' + esc(r.value) + '"' + (r.checked ? " selected" : "") + '>' + esc(r.parentNode.textContent.trim()) + '</option>'; }).join("") + '</select>');
      bs.style.display = "none"; bs.parentNode.insertBefore(sel, bs);
      sel.addEventListener("change", function () { rs.forEach(function (r) { if (r.value === sel.value) { r.checked = true; r.dispatchEvent(new Event("change", { bubbles: true })); } }); });
      rs.forEach(function (r) { r.addEventListener("change", function () { if (r.checked) sel.value = r.value; }); });
      placeBar();
    })();
    placeBar(); setTimeout(placeBar, 1500);
    /* patterns panel heading carries the count and the "what is this" button */
    (function pat() {
      var host = $("#cnPatHost"), hd = host && host.querySelector(".psec");
      if (!hd) return setTimeout(pat, 300);
      var n = hd.querySelector(".mute"), ib = hd.querySelector(".ib"), h = patPanel.querySelector(".uip-h span");
      if (n) h.textContent = "Patterns behind the scenes " + n.textContent;
      if (ib) patPanel.querySelector(".uip-h").insertBefore(ib, patPanel.querySelector(".uip-t"));
      hd.remove();
    })();
  })();
})();
