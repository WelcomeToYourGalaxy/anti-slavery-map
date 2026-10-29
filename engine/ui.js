/* ui.js -- panel layout and click behaviour for the anti-slavery map.
   Runs after the page's own script and before engine/child.js. It builds the boxes the child layer mounts into,
   moves the help and about text into popups, and replaces hover highlighting with click selection. */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var mk = function (html) { var d = document.createElement("div"); d.innerHTML = html.trim(); return d.firstChild; };

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
    col.appendChild(keyPanel); col.appendChild(patPanel); document.body.appendChild(col);
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
  var RAMP = ["#c9cda3", "#a6ad78", "#8a8653", "#93673f", "#77392b"], CUTS = [2, 4, 6, 9];
  function prevClass(rate) { for (var i = 0; i < CUTS.length; i++) if (rate < CUTS[i]) return i; return 4; }
  window.prevColour = function (rate) { if (!rate) return null; return { fill: RAMP[prevClass(rate)], op: 0.55 }; };
  function style(f) {
    var a3 = NUM2A3[f.id] || "", s = origStyle(f) || {};
    var has = s.color === "#ffd24a" || s.color === "#9fd0e6";
    var o = has ? { color: "#c8bf9a", weight: 1.3, opacity: 0.8 } : { color: "rgba(210,215,200,0.26)", weight: 0.5, opacity: 0.22 };
    var rate = window.prevOn && window.PREV_RATE && window.PREV_RATE[a3];
    o.fillColor = rate ? RAMP[prevClass(rate)] : "#c8bf9a"; o.fillOpacity = rate ? 0.55 : 0;
    if (OVON) { rate = 0; var oc = ovColour(OVON, a3); o.fillColor = oc || "#c8bf9a"; o.fillOpacity = oc ? 0.62 : 0; if (oc) rate = 1; }
    if (LINKED && LINKED[a3]) { o.color = "#8fc1dc"; o.weight = 2.6; o.opacity = 0.95; if (!rate) { o.fillColor = "#8fc1dc"; o.fillOpacity = 0.2; } }
    if (SEL === a3) { o.color = "#f4f1e4"; o.weight = 3.4; o.opacity = 1; if (!rate) { o.fillColor = "#f4f1e4"; o.fillOpacity = 0.12; } }
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

  /* ---------- map key ---------- */
  var SEVC = { 2: "#a8e06a", 3: "#ffd24a", 4: "#ffa53d", 5: "#ff6b4a" };
  function dots(list) { return list.map(function (k) { return '<span class="sw-d" style="background:' + SEVC[k] + '"></span>'; }).join(""); }
  var HOW = {
    "projects.json": ["dots", "markers"], "points.json": ["dots", "markers"], "infra.json": ["dots", "markers"], "vessels.json": ["dots", "markers"],
    "suspected.json": ["dots", "markers, mostly dashed rings for a region"], "sites.json": ["dots", "markers"], "wire.json": ["dots", "markers for news reports"],
    "bulk.json": ["dots", "markers, plus country figures in the clicked country's summary"], "companies.json": ["box", "the clicked country's summary"],
    "cases.json": ["box", "the clicked country's summary"], "law.json": ["box", "the clicked country's summary"],
    "directory.json": ["list", "the clicked country's list of resources"], "prevalence.json": ["ramp", "country shading"], "routes.json": ["lines", "corridor lines"]
  };
  function swatch(kind) {
    if (kind === "dots") return dots([2, 3, 4, 5]);
    if (kind === "ramp") return RAMP.map(function (c) { return '<span class="sw-o" style="background:' + c + ';width:7px;border-radius:0"></span>'; }).join("");
    if (kind === "lines") return '<span class="sw-l" style="border-color:#7fb3d0;width:9px"></span><span class="sw-l" style="border-color:#c98ac0;width:9px"></span><span class="sw-l" style="border-color:#c0a86a;width:9px"></span>';
    if (kind === "list") return '<span class="sw-o" style="border:1px solid #c8bf9a;background:repeating-linear-gradient(180deg,#c8bf9a 0 1px,transparent 1px 3px)"></span>';
    return '<span class="sw-o" style="border:2px solid #f4f1e4"></span>';
  }
  function hookDataStatus() {
    window.renderDataStatus = function () {
      var el = document.getElementById("dataStatus"); if (!el) return;
      var rows = "", missing = 0, loaded = 0, total = 0;
      DATA_LAYERS.forEach(function (L) {
        var s = window.DATA_STATUS[L.f], how = HOW[L.f] || ["box", ""];
        if (s && s.ok) { loaded++; total += s.n; rows += '<div class="ds-row ds-ok"><span class="ds-sw">' + swatch(how[0]) + '</span>' + esc(L.label) + ' <span class="ds-n">' + s.n.toLocaleString() + '</span><span class="ds-how">Shown as ' + esc(how[1]) + '</span></div>'; }
        else if (s) { missing++; rows += '<div class="ds-row ds-no"><span class="ds-sw" style="opacity:.35">' + swatch(how[0]) + '</span>' + esc(L.label) + ' <span class="ds-n">not loaded</span></div>'; }
      });
      el.innerHTML = '<div class="ds-head">Data layers: ' + loaded + ' loaded, ' + missing + ' not loaded' + (total ? ' · ' + total.toLocaleString() + ' records' : '') + '</div>' + rows +
        (missing ? '<div class="ds-note">A layer that is not loaded has not been collected yet. It does not mean there is nothing to find.</div>' : '');
    };
    try { renderDataStatus(); } catch (e) {}
  }
  function keyText() {
    /* the prevalence note becomes a legend for the ramp and the country outlines */
    var pc = $("#prevChk"), hintEl = pc && pc.closest("label") && pc.closest("label").nextElementSibling;
    if (hintEl && hintEl.classList.contains("facf-hint")) {
      hintEl.outerHTML = '<div class="ukey">Walk Free’s estimate of people in modern slavery per 1,000 people (2023), so large countries do not dominate.' +
        '<div class="ramp">' + RAMP.map(function (c) { return '<span style="background:' + c + '"></span>'; }).join("") + '</div>' +
        '<div class="rl"><span>under 2</span><span>2–4</span><span>4–6</span><span>6–9</span><span>9 or more</span></div>' +
        '<div class="ur" style="margin-top:6px"><span class="sw-o" style="border:1.5px solid #c8bf9a"></span>Outlined: has resources for your current filters</div>' +
        '<div class="ur"><span class="sw-o" style="border:2.5px solid #f4f1e4"></span>White: the country you clicked</div>' +
        '<div class="ur"><span class="sw-o" style="border:2.5px solid #8fc1dc"></span>Blue: the other end of its corridors, or both ends of a clicked corridor</div></div>';
    }
    /* the marker colour note says what it is about */
    document.querySelectorAll("#legBody .proj-size > .facf-hint").forEach(function (h) {
      if (!/Marker colours/.test(h.textContent)) return;
      h.outerHTML = '<div class="ukey"><b>Case and site markers</b> are coloured by severity:' +
        '<div class="ur">' + dots([2]) + 'a news report, before any raid, rescue or charge</div>' +
        '<div class="ur">' + dots([3]) + 'Documented: in a named public source, or a raid, rescue or charge</div>' +
        '<div class="ur">' + dots([4]) + 'Systemic: across a sector or region, or involving children</div>' +
        '<div class="ur">' + dots([5]) + 'Gravest: state-imposed, a whole national industry, or deaths</div>' +
        'A pin is a known site. A dashed ring stands for a country or region, with no exact site in the source.</div>';
    });
  }

  /* ---------- context overlays ---------- */
  var OVR = ["#cdd8d1", "#a3bdb4", "#769d93", "#517d76", "#2f5b57"];
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
      if (c) { for (var i = 0; i < m.cats.length; i++) if (m.cats[i][0] === c.v) return OVR[m.cats[i][2]]; }
      if (d.eu_note && d.eu_note.members && d.eu_note.members.indexOf(a3) >= 0) return OVR[0];
      return null;
    }
    if (!c || c.v == null) return null;
    for (var j = 0; j < m.bins.length; j++) if (c.v >= m.bins[j][0] && c.v <= m.bins[j][1]) return OVR[j];
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
    var rows = m.cats ? m.cats.map(function (c) { return '<div class="ur"><span class="sw-o" style="background:' + OVR[c[2]] + '"></span>' + esc(c[1]) + '</div>'; }).join("")
      : '<div class="ramp">' + m.bins.map(function (b, i) { return '<span style="background:' + OVR[i] + '"></span>'; }).join("") + '</div><div class="rl">' + m.bins.map(function (b) { return '<span>' + esc(b[2]) + '</span>'; }).join("") + '</div>';
    if (m.k === "corridors") rows += '<div class="ur" style="margin-top:4px"><span class="sw-l" style="border-color:#517d76"></span>corridor; thicker means more workers</div>';
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
      var pl = L.polyline(pts, { color: "#517d76", weight: w, opacity: 0.85, dashArray: l.v ? null : "4 4" });
      pl.bindPopup('<div class="popup-country">' + esc(nm(l.from)) + ' → ' + esc(nm(l.to)) + '</div><div class="tracker-desc">' + esc(l.text) + (l.url ? '<br><a href="' + esc(l.url) + '" target="_blank" rel="noopener">Source</a>' : '') + '</div>');
      g.addLayer(pl);
    });
    ovLines = g.addTo(map);
  }
  function ovSet(k) {
    OVON = k || null;
    document.querySelectorAll("#overlayBox input[data-uov]").forEach(function (cb) { cb.checked = cb.dataset.uov === OVON; });
    document.querySelectorAll("#overlayBox .uov-leg").forEach(function (el) { el.style.display = el.dataset.uov === OVON ? "" : "none"; });
    if (OVON && window.prevOn) window.togglePrevalence(false);
    ovDrawLines(OVON === "corridors" ? OVD.corridors : null);
    restyle();
    if (SEL) select(SEL, nm(SEL));
  }
  function ovLoad(k) {
    if (OVD[k]) return Promise.resolve(OVD[k]);
    return fetch("data/overlays/" + k + ".json").then(function (r) { if (!r.ok) throw 0; return r.json(); })
      .catch(function () { return (window.__BUNDLED && window.__BUNDLED["data/overlays/" + k + ".json"]) || null; })
      .then(function (d) { if (d) OVD[k] = d; return d; });
  }
  function hookOverlays() {
    var box = $("#overlayBox"); if (!box || box.getAttribute("data-built") !== "1") return setTimeout(hookOverlays, 400);
    var h = '<div class="psrc-head" onclick="this.parentNode.classList.toggle(\'open\')"><span>Context layers (shade the countries; one at a time)</span><span class="psrc-tog">▾</span></div><div class="psrc-body">';
    OVS.forEach(function (m) {
      h += '<label class="psrc-row"><input type="checkbox" data-uov="' + m.k + '"> <span class="psrc-l">' + esc(m.label) + '<span class="ov-status" data-uovs="' + m.k + '"></span></span><span class="psrc-d">' + esc(m.note) + '</span></label>' +
        '<div class="uov-leg ukey" data-uov="' + m.k + '" style="display:none;margin-left:18px"></div>';
    });
    box.innerHTML = h + '</div>'; box.classList.add("open");
    box.querySelectorAll("input[data-uov]").forEach(function (cb) {
      cb.addEventListener("change", function () {
        var k = cb.dataset.uov, st = box.querySelector('[data-uovs="' + k + '"]');
        if (!cb.checked) { if (OVON === k) ovSet(null); return; }
        st.textContent = " loading…";
        ovLoad(k).then(function (d) {
          st.textContent = d ? "" : " — not available";
          if (!d) { cb.checked = false; return; }
          var lg = box.querySelector('.uov-leg[data-uov="' + k + '"]'), m = ovMeta(k);
          lg.innerHTML = ovLegend(m) + '<div class="mute" style="margin-top:3px">' + esc(d.source) + ', ' + esc(d.as_of) + '. Click a country for its entry.</div>';
          ovSet(k);
        });
      });
    });
    var pc = $("#prevChk"); if (pc) pc.addEventListener("change", function () { if (pc.checked && OVON) ovSet(null); });
  }

  /* ---------- boot ---------- */
  layout();
  var tries = 0;
  (function wait() {
    if (typeof geojsonLayer === "undefined" || !geojsonLayer || !window.baseStyle || !window.drawRoutes || !window.applyIntent) { if (tries++ < 600) return setTimeout(wait, 100); return; }
    hookCountries(); hookRoutes(); hookDrill(); hookSelectors(); hookDataStatus(); keyText(); hookOverlays();
    window._reflowInfo = reflowInfo;
    var oh = window.hideInfoPanel;
    window.hideInfoPanel = function () { var r = oh.apply(this, arguments); unselect(); return r; };
    var os = window.showInfoPanel;
    window.showInfoPanel = function () {
      var r = os.apply(this, arguments);
      keyPanel.classList.add("collapsed"); patPanel.classList.add("collapsed");
      [keyPanel, patPanel].forEach(function (p) { p.querySelector(".uip-t").textContent = "+"; });
      reflowInfo(); return r;
    };
    if (!window.prevOn) window.togglePrevalence(true);
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
