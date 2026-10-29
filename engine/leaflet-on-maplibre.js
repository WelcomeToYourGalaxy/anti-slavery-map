/* leaflet-on-maplibre.js
 * The part of the Leaflet 1.9 API this map uses, drawn by MapLibre GL 5 so the map can be a globe
 * or a flat map on the Culprits basemaps (engine/basemaps.js). The map's own code is unchanged:
 * it still calls L.map, L.geoJSON, L.polyline, L.circleMarker, L.marker, L.popup, L.Layer.extend.
 *
 * Zoom: Leaflet counts zoom on 256-pixel tiles and MapLibre on 512, so Leaflet zoom z is MapLibre
 * zoom z - 1. Everything below takes and returns Leaflet zoom, so the map's thresholds keep meaning
 * what they meant.
 *
 * Vectors: every path (polygon, line, circle) becomes one feature in a GeoJSON source per pane, styled
 * by feature-state, so setStyle is cheap and nothing is re-tiled on hover. Custom canvas layers
 * (L.Layer.extend) draw into pane <div>s laid over the map, as in Leaflet. On the globe, points on the
 * far side project off-screen so those canvases skip them.
 */
(function () {
"use strict";
if (typeof window === "undefined" || !window.maplibregl || !window.CulpritsBasemaps) return;
var ml = window.maplibregl;
(function () { var st = document.createElement("style"); st.textContent = ".shim-pane{pointer-events:none !important}.shim-pane canvas{pointer-events:none !important}.leaflet-container .maplibregl-marker.leaflet-popup{margin:0}.leaflet-control-container .leaflet-top,.leaflet-control-container .leaflet-bottom{z-index:800}"; document.head.appendChild(st); })();
var ZO = 1;                       // leaflet zoom = maplibre zoom + ZO
var PANE_Z = { tilePane: 200, overlayPane: 400, shadowPane: 500, markerPane: 600, tooltipPane: 650, popupPane: 700 };

/* ---------- small types ---------- */
function LatLng(lat, lng) { this.lat = +lat; this.lng = +lng; }
LatLng.prototype.equals = function (o) { o = toLatLng(o); return !!o && Math.abs(o.lat - this.lat) < 1e-9 && Math.abs(o.lng - this.lng) < 1e-9; };
LatLng.prototype.toString = function () { return "LatLng(" + this.lat + ", " + this.lng + ")"; };
LatLng.prototype.wrap = function () { var l = this.lng; while (l > 180) l -= 360; while (l < -180) l += 360; return new LatLng(this.lat, l); };
LatLng.prototype.distanceTo = function (o) { o = toLatLng(o); var R = 6371000, r = Math.PI / 180, a = Math.sin((o.lat - this.lat) * r / 2), b = Math.sin((o.lng - this.lng) * r / 2); var h = a * a + Math.cos(this.lat * r) * Math.cos(o.lat * r) * b * b; return 2 * R * Math.asin(Math.min(1, Math.sqrt(h))); };
function toLatLng(a, b) {
  if (a == null) return null;
  if (a instanceof LatLng) return a;
  if (Array.isArray(a)) return a.length >= 2 ? new LatLng(a[0], a[1]) : null;
  if (typeof a === "object" && "lat" in a) return new LatLng(a.lat, "lng" in a ? a.lng : a.lon);
  if (b !== undefined) return new LatLng(a, b);
  return null;
}
function Point(x, y) { this.x = x; this.y = y; }
Point.prototype.distanceTo = function (o) { return Math.hypot(o.x - this.x, o.y - this.y); };
Point.prototype.add = function (o) { return new Point(this.x + o.x, this.y + o.y); };
Point.prototype.subtract = function (o) { return new Point(this.x - o.x, this.y - o.y); };
function toPoint(a, b) { if (a instanceof Point) return a; if (Array.isArray(a)) return new Point(a[0], a[1]); if (a && typeof a === "object") return new Point(a.x, a.y); return new Point(a, b); }

function LatLngBounds(a, b) {
  this._sw = null; this._ne = null;
  if (!a) return;
  var list = b ? [a, b] : a;
  if (list instanceof LatLngBounds) { this.extend(list); return; }
  if (Array.isArray(list) && list.length && (Array.isArray(list[0]) || (list[0] && typeof list[0] === "object"))) for (var i = 0; i < list.length; i++) this.extend(list[i]);
  else this.extend(list);
}
LatLngBounds.prototype.extend = function (o) {
  if (!o) return this;
  var sw, ne;
  if (o instanceof LatLngBounds) { sw = o._sw; ne = o._ne; if (!sw) return this; }
  else { var ll = toLatLng(o); if (!ll) return this; sw = ne = ll; }
  if (!this._sw) { this._sw = new LatLng(sw.lat, sw.lng); this._ne = new LatLng(ne.lat, ne.lng); }
  else { this._sw.lat = Math.min(sw.lat, this._sw.lat); this._sw.lng = Math.min(sw.lng, this._sw.lng); this._ne.lat = Math.max(ne.lat, this._ne.lat); this._ne.lng = Math.max(ne.lng, this._ne.lng); }
  return this;
};
LatLngBounds.prototype.isValid = function () { return !!(this._sw && this._ne); };
LatLngBounds.prototype.getSouthWest = function () { return this._sw; };
LatLngBounds.prototype.getNorthEast = function () { return this._ne; };
LatLngBounds.prototype.getNorthWest = function () { return new LatLng(this._ne.lat, this._sw.lng); };
LatLngBounds.prototype.getSouthEast = function () { return new LatLng(this._sw.lat, this._ne.lng); };
LatLngBounds.prototype.getNorth = function () { return this._ne.lat; };
LatLngBounds.prototype.getSouth = function () { return this._sw.lat; };
LatLngBounds.prototype.getEast = function () { return this._ne.lng; };
LatLngBounds.prototype.getWest = function () { return this._sw.lng; };
LatLngBounds.prototype.getCenter = function () { return new LatLng((this._sw.lat + this._ne.lat) / 2, (this._sw.lng + this._ne.lng) / 2); };
LatLngBounds.prototype.pad = function (r) { var h = (this._ne.lat - this._sw.lat) * r, w = (this._ne.lng - this._sw.lng) * r; return new LatLngBounds([this._sw.lat - h, this._sw.lng - w], [this._ne.lat + h, this._ne.lng + w]); };
LatLngBounds.prototype.contains = function (o) {
  if (o instanceof LatLngBounds) return this.contains(o._sw) && this.contains(o._ne);
  var ll = toLatLng(o); return !!ll && ll.lat >= this._sw.lat && ll.lat <= this._ne.lat && ll.lng >= this._sw.lng && ll.lng <= this._ne.lng;
};
LatLngBounds.prototype.intersects = function (b) { b = toBounds(b); return b._ne.lat >= this._sw.lat && b._sw.lat <= this._ne.lat && b._ne.lng >= this._sw.lng && b._sw.lng <= this._ne.lng; };
LatLngBounds.prototype.toBBoxString = function () { return [this._sw.lng, this._sw.lat, this._ne.lng, this._ne.lat].join(","); };
function toBounds(a, b) { return a instanceof LatLngBounds ? a : new LatLngBounds(a, b); }

/* ---------- events ---------- */
var Evented = {
  on: function (types, fn, ctx) {
    if (types && typeof types === "object") { for (var t in types) this.on(t, types[t], fn); return this; }
    var ev = this._ev || (this._ev = {});
    String(types).split(/\s+/).forEach(function (t) { if (t) (ev[t] = ev[t] || []).push({ fn: fn, ctx: ctx }); });
    return this;
  },
  off: function (types, fn, ctx) {
    if (!this._ev) return this;
    if (!types) { this._ev = {}; return this; }
    if (typeof types === "object") { for (var t in types) this.off(t, types[t], fn); return this; }
    var ev = this._ev;
    String(types).split(/\s+/).forEach(function (t) { if (!ev[t]) return; ev[t] = fn ? ev[t].filter(function (h) { return !(h.fn === fn && (ctx === undefined || h.ctx === ctx)); }) : []; });
    return this;
  },
  once: function (t, fn, ctx) { var self = this; var w = function (e) { self.off(t, w); fn.call(ctx || self, e); }; return this.on(t, w); },
  fire: function (t, data, propagate) {
    var e = Object.assign({}, data || {}, { type: t, target: this, sourceTarget: (data && data.sourceTarget) || this });
    var hs = this._ev && this._ev[t];
    if (hs && hs.length) hs.slice().forEach(function (h) { try { h.fn.call(h.ctx || this, e); } catch (err) { console.error(err); } }, this);
    if (propagate && this._parents) for (var i = 0; i < this._parents.length; i++) this._parents[i].fire(t, Object.assign({}, e, { layer: e.layer || this, propagatedFrom: this }), true);
    return this;
  },
  listens: function (t) { return !!(this._ev && this._ev[t] && this._ev[t].length) || !!(this._parents && this._parents.some(function (p) { return p.listens(t); })); },
};
function mix(C) { Object.keys(Evented).forEach(function (k) { C.prototype[k] = Evented[k]; }); return C; }

/* ---------- the map ---------- */
var THE_MAP = null;
function LMap(id, opts) {
  opts = opts || {};
  var self = this;
  this.options = opts;
  this._container = typeof id === "string" ? document.getElementById(id) : id;
  this._layers = [];
  this._panes = {};
  this._popup = null;
  this._loaded = false;
  this._readyQ = [];
  THE_MAP = this;
  var c = opts.center ? toLatLng(opts.center) : new LatLng(20, 0);
  this._bm = window.CulpritsBasemaps.create(this._container, {
    initial: opts.basemap || window.SHIM_BASEMAP || "atlas", projection: opts.projection || "globe", plate: window.SHIM_PLATE || undefined,
    center: [c.lng, c.lat], zoom: Math.max(0, (opts.zoom == null ? 3 : opts.zoom) - ZO),
    onApply: function (k) { self._basemap = k; (window.__bmListeners || []).forEach(function (f) { try { f(k); } catch (e) { console.error(e); } }); self._reorder(); },
    onReady: function () { self._setup(); },
  });
  var m = this._ml = this._bm.maplibre;
  window.__BM = this._bm; window.__ml = m; window.__lmap = this;
  if (opts.minZoom != null) m.setMinZoom(Math.max(0, opts.minZoom - ZO - 0.6));
  if (opts.maxZoom != null) m.setMaxZoom(Math.min(16, opts.maxZoom - ZO));
  this._zoomStart = this.getZoom();
  ["dragstart", "drag", "dragend", "movestart", "move", "moveend", "zoomstart", "zoom", "zoomend", "resize"].forEach(function (t) {
    m.on(t, function (e) { self.fire(t, { originalEvent: e && e.originalEvent }); });
  });
  m.on("mousemove", function (e) { self._onMove(e); });
  m.on("mouseout", function () { self._setHover(null, null); self._hideTip(); });
  m.on("click", function (e) { self._onClick(e); });
  m.on("dblclick", function (e) { self.fire("dblclick", self._evt(e)); });
  m.on("contextmenu", function (e) { self.fire("contextmenu", self._evt(e)); });
  this._controls();
}
mix(LMap);
/* Canvas layers (L.Layer.extend with a _draw that paints dots on a <canvas>). Leaflet slides such a canvas with the
   map during a drag; MapLibre cannot, and redrawing by hand on every frame is too slow and wrong on a globe. So each
   _draw is run in "record" mode: the positions it asks for are noted, the circles it paints are captured, and the
   result is handed to MapLibre as native circles, which then move, wrap round the globe and hide behind it by
   themselves. The layer's own click code still uses real screen positions. */
var CV_ID = 1;
function recorder(items) {
  var path = [], st = { fillStyle: "#000", strokeStyle: "#000", globalAlpha: 1, lineWidth: 1 };
  var ctx = {
    canvas: null,
    clearRect: function () {}, fillRect: function () {}, strokeRect: function () {}, save: function () {}, restore: function () {},
    setLineDash: function () {}, moveTo: function () {}, lineTo: function () {}, closePath: function () {}, fillText: function () {}, strokeText: function () {},
    measureText: function () { return { width: 0 }; }, translate: function () {}, scale: function () {}, rotate: function () {}, setTransform: function () {},
    beginPath: function () { path = []; },
    arc: function (x, y, r) { path.push({ i: Math.round(x), ok: y < -9e6, r: r }); },
    fill: function () { path.forEach(function (a) { if (a.ok) items.push({ i: a.i, r: a.r, fc: String(st.fillStyle), fo: st.globalAlpha, w: 0 }); }); },
    stroke: function () { path.forEach(function (a) { if (!a.ok) return; var last = items[items.length - 1];
      if (last && last.i === a.i && Math.abs(last.r - a.r) < 1e-6 && !last.w) { last.sc = String(st.strokeStyle); last.w = st.lineWidth; last.so = st.globalAlpha; }
      else items.push({ i: a.i, r: a.r, fc: "rgba(0,0,0,0)", fo: 0, sc: String(st.strokeStyle), w: st.lineWidth, so: st.globalAlpha }); }); },
  };
  Object.keys(st).forEach(function (k) { Object.defineProperty(ctx, k, { get: function () { return st[k]; }, set: function (v) { st[k] = v; } }); });
  return ctx;
}
LMap.prototype._wrapCanvasLayer = function (l) {
  if (l._cvWrapped || typeof l._draw !== "function") return;
  var self = this, orig = l._draw;
  l._cvWrapped = true; l._cvId = "cv-" + (CV_ID++);
  l._draw = function () { return self._record(l, orig, arguments); };
};
LMap.prototype._record = function (l, draw, args) {
  if (!this._loaded) { var me = this; this.whenReady(function () { me._record(l, draw, args); }); return; }
  var self = this, pts = [], items = [], cv = l._cv;
  var ctx = recorder(items), realGet = cv && cv.getContext, realL2C = this.latLngToContainerPoint, realB = this.getBounds;
  if (cv) cv.getContext = function () { return ctx; };
  this.latLngToContainerPoint = function (ll) { ll = toLatLng(ll); pts.push(ll); return new Point(pts.length - 1, -1e7); };
  this.getBounds = function () { var b = realB.call(self), z = self.getZoom(); return z < 5 ? new LatLngBounds([-85, -180], [85, 180]) : b.pad(0.75); };
  try { draw.apply(l, args || []); } catch (e) { console.warn("[canvas layer]", e); }
  finally { this.latLngToContainerPoint = realL2C; this.getBounds = realB; if (cv) cv.getContext = realGet; }
  var feats = [];
  for (var k = 0; k < items.length; k++) { var it = items[k], ll = pts[it.i]; if (!ll) continue;
    feats.push({ type: "Feature", properties: { k: k, r: it.r, fc: it.fc, fo: it.fo, sc: it.sc || "rgba(0,0,0,0)", w: it.w || 0, so: it.so == null ? 1 : it.so }, geometry: { type: "Point", coordinates: [ll.lng, ll.lat] } }); }
  this._cvLayer(l, feats);
};
LMap.prototype._cvLayer = function (l, feats) {
  var m = this._ml, id = l._cvId;
  if (!m.getSource(id)) {
    m.addSource(id, { type: "geojson", data: { type: "FeatureCollection", features: [] } });
    m.addLayer({ id: id, type: "circle", source: id, layout: { "circle-sort-key": ["get", "k"] }, paint: {
      "circle-radius": ["get", "r"], "circle-color": ["get", "fc"], "circle-opacity": ["get", "fo"],
      "circle-stroke-color": ["get", "sc"], "circle-stroke-width": ["get", "w"], "circle-stroke-opacity": ["get", "so"], "circle-pitch-alignment": "map" } }, m.getLayer("anchor-top") ? "anchor-top" : undefined);
    (this._cvIds = this._cvIds || []).push({ id: id, pane: l._cvPane || "overlayPane" });
    this._reorder();
  }
  m.getSource(id).setData({ type: "FeatureCollection", features: feats });
};
LMap.prototype._cvClear = function (l) { var m = this._ml; if (l._cvId && m.getSource(l._cvId)) m.getSource(l._cvId).setData({ type: "FeatureCollection", features: [] }); };
LMap.prototype._evt = function (e) { var ll = e.lngLat ? new LatLng(e.lngLat.lat, e.lngLat.lng) : null; return { latlng: ll, containerPoint: e.point ? new Point(e.point.x, e.point.y) : null, layerPoint: e.point ? new Point(e.point.x, e.point.y) : null, originalEvent: e.originalEvent }; };
LMap.prototype._setup = function () {
  var m = this._ml;
  this._loaded = true;
  this._ensureAnchors();
  this._layers.slice().forEach(function (l) { if (l._needsMl) l._mlAdd(); });
  this._flushAll();
  this._reorder();
  var q = this._readyQ; this._readyQ = [];
  q.forEach(function (f) { try { f.fn.call(f.ctx || this, { target: this }); } catch (e) { console.error(e); } }, this);
  this.fire("load");
  var cont = this._container, fold = function () { var a = cont.querySelector(".maplibregl-ctrl-attrib"); if (a) { a.classList.remove("maplibregl-compact-show"); a.removeAttribute("open"); } };
  m.once("idle", fold); setTimeout(fold, 2500);
  (window.__shimReady || []).forEach(function (f) { try { f(); } catch (e) { console.error(e); } });
  window.__shimIsReady = true;
};
LMap.prototype.whenReady = function (fn, ctx) { if (this._loaded) fn.call(ctx || this, { target: this }); else this._readyQ.push({ fn: fn, ctx: ctx }); return this; };
LMap.prototype._ensureAnchors = function () {
  var m = this._ml;
  ["anchor-mid", "anchor-top"].forEach(function (id) { if (!m.getLayer(id)) m.addLayer({ id: id, type: "background", paint: { "background-color": "#000", "background-opacity": 0 } }); });
};
/* Stack, bottom to top: basemap pictures | anchor-mid, the child layer's country fills | this map's vectors |
   anchor-top, the child layer's lines and dots | the basemap's names. */
LMap.prototype._reorder = function () {
  var m = this._ml; if (!this._loaded || !m.getStyle()) return;
  this._ensureAnchors();
  var cn = window.__cnLayers || { bottom: [], top: [] };
  var mine = {}; ["anchor-mid", "anchor-top"].concat(cn.bottom, cn.top, this._mlIds(), (this._cvIds || []).map(function (x) { return x.id; })).forEach(function (id) { mine[id] = 1; });
  var st = m.getStyle().layers, first = null;
  for (var i = 0; i < st.length; i++) { var l = st[i]; if (!mine[l.id] && (l.type === "symbol" || l.id === "labels")) { first = l.id; break; } }
  var cvs = (this._cvIds || []).map(function (x) { return x.id; });
  var seq = ["anchor-mid"].concat(cn.bottom, this._mlIds(), cvs, ["anchor-top"], cn.top);
  seq.forEach(function (id) { if (m.getLayer(id)) try { m.moveLayer(id, first || undefined); } catch (e) {} });
};
LMap.prototype._mlIds = function () { var out = []; var ps = Object.keys(this._vpanes || {}).sort(function (a, b) { return paneZ(a) - paneZ(b); }); ps.forEach(function (p) { out.push("v-" + p + "-fill", "v-" + p + "-line", "v-" + p + "-dash", "v-" + p + "-circle"); }); return out; };
function paneZ(name) { var m = THE_MAP, el = m && m._panes[name]; if (el && el.style.zIndex) return +el.style.zIndex; return PANE_Z[name] || 400; }

/* view */
LMap.prototype.getZoom = function () { return this._ml.getZoom() + ZO; };
LMap.prototype.getMinZoom = function () { return this._ml.getMinZoom() + ZO; };
LMap.prototype.getMaxZoom = function () { return this._ml.getMaxZoom() + ZO; };
LMap.prototype.setZoom = function (z, o) { this._ml.easeTo({ zoom: z - ZO, duration: o && o.animate === false ? 0 : 400 }); return this; };
LMap.prototype.zoomIn = function (d) { this._ml.zoomIn(); return this; };
LMap.prototype.zoomOut = function (d) { this._ml.zoomOut(); return this; };
LMap.prototype.getCenter = function () { var c = this._ml.getCenter(); return new LatLng(c.lat, c.lng); };
LMap.prototype.setView = function (ll, z, o) { ll = toLatLng(ll); var a = { center: [ll.lng, ll.lat] }; if (z != null) a.zoom = z - ZO; if (o && o.animate) this._ml.easeTo(a); else this._ml.jumpTo(a); return this; };
LMap.prototype.panTo = function (ll) { ll = toLatLng(ll); this._ml.easeTo({ center: [ll.lng, ll.lat] }); return this; };
LMap.prototype.flyTo = function (ll, z, o) { ll = toLatLng(ll); var a = { center: [ll.lng, ll.lat], essential: true }; if (z != null) a.zoom = z - ZO; a.duration = o && o.duration != null ? o.duration * 1000 : 1200; this._ml.flyTo(a); return this; };
LMap.prototype.flyToBounds = function (b, o) { return this.fitBounds(b, o); };
LMap.prototype.panBy = function (off, o) { off = toPoint(off); this._ml.panBy([off.x, off.y], { duration: o && o.duration != null ? o.duration * 1000 : (o && o.animate === false ? 0 : 300) }); return this; };
LMap.prototype.fitBounds = function (b, o) {
  b = toBounds(b); if (!b.isValid()) return this; o = o || {};
  var pad = { top: 0, bottom: 0, left: 0, right: 0 };
  if (o.padding) { var p = toPoint(o.padding); pad = { top: p.y, bottom: p.y, left: p.x, right: p.x }; }
  if (o.paddingTopLeft) { var tl = toPoint(o.paddingTopLeft); pad.left = tl.x; pad.top = tl.y; }
  if (o.paddingBottomRight) { var br = toPoint(o.paddingBottomRight); pad.right = br.x; pad.bottom = br.y; }
  var sz = this.getSize();
  if (pad.left + pad.right > sz.x - 60) { var k = (sz.x - 60) / (pad.left + pad.right); pad.left *= k; pad.right *= k; }
  if (pad.top + pad.bottom > sz.y - 60) { var k2 = (sz.y - 60) / (pad.top + pad.bottom); pad.top *= k2; pad.bottom *= k2; }
  var w = b.getWest(), e = b.getEast(), s = Math.max(-85, b.getSouth()), n = Math.min(85, b.getNorth());
  if (e - w > 360) { w = -180; e = 180; }
  var cam = null;
  try { cam = this._ml.cameraForBounds([[w, s], [e, n]], { padding: pad, maxZoom: o.maxZoom != null ? o.maxZoom - ZO : 15 }); } catch (err) { cam = null; }
  if (!cam || !cam.center) { var c = b.getCenter(); cam = { center: [c.lng, c.lat], zoom: Math.max(0, Math.min(this._ml.getZoom(), 3)) }; }
  if (o.maxZoom != null && cam.zoom > o.maxZoom - ZO) cam.zoom = o.maxZoom - ZO;
  cam.duration = o.animate === false ? 0 : 700;
  this._ml.easeTo(cam);
  return this;
};
LMap.prototype.setMaxBounds = function () { return this; };
LMap.prototype.invalidateSize = function () { this._ml.resize(); return this; };
LMap.prototype.getSize = function () { var c = this._container; return new Point(c.clientWidth, c.clientHeight); };
LMap.prototype.getBounds = function () {
  var m = this._ml, z = m.getZoom();
  var globe = (m.getProjection && m.getProjection() && m.getProjection().type === "globe");
  if (globe && z < 2.2) {
    var c = m.getCenter(), span = 180 / Math.pow(2, Math.max(0, z)) + 95;
    return new LatLngBounds([Math.max(-85, c.lat - 95), c.lng - Math.min(180, span)], [Math.min(85, c.lat + 95), c.lng + Math.min(180, span)]);
  }
  var b = m.getBounds();
  return new LatLngBounds([Math.max(-85, b.getSouth()), b.getWest()], [Math.min(85, b.getNorth()), b.getEast()]);
};
LMap.prototype.getContainer = function () { return this._container; };
LMap.prototype.latLngToContainerPoint = function (ll) {
  ll = toLatLng(ll); if (!ll) return new Point(-99999, -99999);
  var m = this._ml, lng = ll.lng;
  try { if (m.transform && m.transform.isLocationOccluded && m.transform.isLocationOccluded(new ml.LngLat(((lng + 540) % 360) - 180, ll.lat))) return new Point(-99999, -99999); } catch (e) {}
  var p = m.project([lng, ll.lat]); return new Point(p.x, p.y);
};
LMap.prototype.containerPointToLatLng = function (p) { p = toPoint(p); var ll = this._ml.unproject([p.x, p.y]); return new LatLng(ll.lat, ll.lng); };
LMap.prototype.latLngToLayerPoint = LMap.prototype.latLngToContainerPoint;
LMap.prototype.layerPointToLatLng = LMap.prototype.containerPointToLatLng;
LMap.prototype.containerPointToLayerPoint = function (p) { return toPoint(p); };
LMap.prototype.layerPointToContainerPoint = function (p) { return toPoint(p); };
LMap.prototype.mouseEventToContainerPoint = function (ev) { var r = this._container.getBoundingClientRect(); return new Point(ev.clientX - r.left - this._container.clientLeft, ev.clientY - r.top - this._container.clientTop); };
LMap.prototype.mouseEventToLatLng = function (ev) { return this.containerPointToLatLng(this.mouseEventToContainerPoint(ev)); };
LMap.prototype.distance = function (a, b) { return toLatLng(a).distanceTo(toLatLng(b)); };

/* panes: plain <div>s over the map canvas. They never take pointer events themselves
   (a pane set to "auto" would swallow the map's drags); the value code sets is read as a flag instead. */
LMap.prototype.createPane = function (name, container) {
  if (this._panes[name]) return this._panes[name];
  var d = document.createElement("div");
  d.className = "leaflet-pane leaflet-" + name.replace(/Pane$/, "") + "-pane shim-pane";
  d.style.cssText = "position:absolute;left:0;top:0;width:100%;height:100%;";
  if (PANE_Z[name]) d.style.zIndex = PANE_Z[name];
  (container || this._container).appendChild(d);
  this._panes[name] = d;
  return d;
};
LMap.prototype.getPane = function (name) { if (name && typeof name !== "string") return name; name = name || "overlayPane"; if (!this._panes[name] && PANE_Z[name]) return this.createPane(name); return this._panes[name]; };
LMap.prototype.getPanes = function () { return this._panes; };

/* layers */
LMap.prototype.addLayer = function (l) { if (!l) return this; if (this._layers.indexOf(l) >= 0) return this; this._layers.push(l); l._map = this; if (l._onAddTo) l._onAddTo(this); else if (l.onAdd) { this._wrapCanvasLayer(l); l.onAdd(this); } if (l.fire) l.fire("add"); return this; };
LMap.prototype.removeLayer = function (l) { var i = this._layers.indexOf(l); if (i < 0) return this; this._layers.splice(i, 1); if (l._onRemoveFrom) l._onRemoveFrom(this); else if (l.onRemove) { l.onRemove(this); this._cvClear(l); } l._map = null; if (l.fire) l.fire("remove"); return this; };
LMap.prototype.hasLayer = function (l) { return !!l && this._layers.indexOf(l) >= 0; };
LMap.prototype.eachLayer = function (fn, ctx) { this._layers.slice().forEach(function (l) { fn.call(ctx, l); }); return this; };
LMap.prototype.openPopup = function (p, ll) { if (!(p instanceof Popup)) { p = new Popup().setContent(p); if (ll) p.setLatLng(ll); } p.openOn(this); return this; };
LMap.prototype.closePopup = function (p) { var cur = this._popup; if (!cur) return this; if (p && p !== cur) return this; cur._close(); return this; };
LMap.prototype.remove = function () { this._ml.remove(); return this; };
LMap.prototype.stop = function () { this._ml.stop(); return this; };

/* ---------- vectors ---------- */
var PATH_ID = 1, GROUP_STYLING = 0;
LMap.prototype._vp = function (pane) {
  var vp = this._vpanes || (this._vpanes = {});
  if (!vp[pane]) { vp[pane] = { paths: {}, dirty: true, src: null }; if (this._loaded) this._mlPane(pane); }
  return vp[pane];
};
LMap.prototype._mlPane = function (pane) {
  var m = this._ml, sid = "v-" + pane, vp = this._vpanes[pane];
  if (m.getSource(sid)) return;
  m.addSource(sid, { type: "geojson", data: { type: "FeatureCollection", features: [] }, promoteId: "pid", tolerance: 0.25 });
  var self = this;
  m.on("sourcedata", function (e) {
    if (e.sourceId !== sid || !vp.reapply || !m.isSourceLoaded(sid)) return;
    vp.reapply--; clearTimeout(vp._rt);
    vp._rt = setTimeout(function () { for (var q in vp.paths) vp.paths[q]._stateDirty = true; self._schedule(); }, 30);
  });
  var fs = function (k, d) { return ["coalesce", ["feature-state", k], d]; };
  var before = m.getLayer("anchor-top") ? "anchor-top" : undefined;
  m.addLayer({ id: sid + "-fill", type: "fill", source: sid, filter: ["==", ["get", "g"], "poly"], paint: { "fill-color": fs("fa", "rgba(0,0,0,0)") } }, before);  // opacity is folded into "fa": a feature-state fill-opacity is not drawn by MapLibre here
  m.addLayer({ id: sid + "-line", type: "line", source: sid, filter: ["all", ["!=", ["get", "g"], "pt"], ["!=", ["get", "dash"], 1]], layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": fs("c", "#3388ff"), "line-width": fs("w", 1), "line-opacity": fs("o", 1) } }, before);
  m.addLayer({ id: sid + "-dash", type: "line", source: sid, filter: ["all", ["!=", ["get", "g"], "pt"], ["==", ["get", "dash"], 1]], paint: { "line-color": fs("c", "#3388ff"), "line-width": fs("w", 1), "line-opacity": fs("o", 1), "line-dasharray": [2, 2] } }, before);
  m.addLayer({ id: sid + "-circle", type: "circle", source: sid, filter: ["==", ["get", "g"], "pt"], paint: {
    "circle-radius": fs("r", 5), "circle-color": fs("fc", "#3388ff"), "circle-opacity": fs("fo", 0.2),
    "circle-stroke-color": fs("c", "#3388ff"), "circle-stroke-width": fs("w", 1), "circle-stroke-opacity": fs("o", 1), "circle-pitch-alignment": "map" } }, before);
  vp.dirty = true;
  this._reorder();
};
LMap.prototype._flushAll = function () { var vp = this._vpanes || {}; for (var p in vp) { if (!this._ml.getSource("v-" + p)) this._mlPane(p); vp[p].dirty = true; } this._schedule(); };
LMap.prototype._schedule = function () {
  if (this._raf || !this._loaded) return;
  var self = this;
  this._raf = requestAnimationFrame(function () { self._raf = null; self._flush(); });
};
LMap.prototype._flush = function () {
  var m = this._ml, vp = this._vpanes || {};
  for (var pane in vp) {
    var P = vp[pane], src = m.getSource("v-" + pane);
    if (!src) { this._mlPane(pane); src = m.getSource("v-" + pane); }
    if (P.dirty) {
      var feats = [];
      for (var id in P.paths) { var f = P.paths[id]._feature(); if (f) feats.push(f); }
      src.setData({ type: "FeatureCollection", features: feats });
      P.dirty = false;
      for (var id2 in P.paths) P.paths[id2]._stateDirty = true;
      // States set while new data is still being tiled can be dropped from what is drawn (the query still sees them).
      // Set them again once the map has finished loading the new data.
      P.reapply = 3;
    }
    var fillChanged = false;
    for (var id3 in P.paths) { var pa = P.paths[id3]; if (pa._stateDirty) { pa._stateDirty = false; try { var ns = pa._state(); if (ns.fa !== pa._lastFa) { fillChanged = true; pa._lastFa = ns.fa; } m.setFeatureState({ source: "v-" + pane, id: pa._pid }, ns); } catch (e) {} } }
    // A changed fill colour in feature state is not redrawn until the layer's paint is evaluated again, so nudge it.
    if (fillChanged && m.getLayer("v-" + pane + "-fill")) { P._nudge = !P._nudge; try { m.setPaintProperty("v-" + pane + "-fill", "fill-color", ["coalesce", ["feature-state", "fa"], P._nudge ? "rgba(0,0,0,0)" : "rgba(0,0,0,0.0)"]); } catch (e) {} }
  }
};
var PATH_DEF = { stroke: true, color: "#3388ff", weight: 3, opacity: 1, fill: false, fillColor: null, fillOpacity: 0.2, interactive: true };

function Path() {}
mix(Path);
Path.prototype._initPath = function (opts, fillDefault) {
  this.options = Object.assign({}, PATH_DEF, { fill: !!fillDefault }, opts || {});
  this._pid = PATH_ID++;
  this._parents = [];
};
Path.prototype._paneName = function () { var p = this.options.pane; if (!p && this.options.renderer && this.options.renderer.options && this.options.renderer.options.pane) p = this.options.renderer.options.pane; return p || "overlayPane"; };
var RGBA_CACHE = {}, RGBA_CTX = null;
function rgbaOf(col, a) {
  var k = col + "|" + a; if (RGBA_CACHE[k]) return RGBA_CACHE[k];
  var r = 0, g = 0, b = 0, a0 = 1, m;
  if ((m = /^#([0-9a-f]{3,8})$/i.exec(col))) { var h = m[1]; if (h.length < 6) h = h.split("").map(function (x) { return x + x; }).join(""); r = parseInt(h.slice(0, 2), 16); g = parseInt(h.slice(2, 4), 16); b = parseInt(h.slice(4, 6), 16); if (h.length === 8) a0 = parseInt(h.slice(6, 8), 16) / 255; }
  else if ((m = /^rgba?\(([^)]+)\)$/i.exec(col))) { var p = m[1].split(",").map(parseFloat); r = p[0]; g = p[1]; b = p[2]; if (p.length > 3) a0 = p[3]; }
  else { try { RGBA_CTX = RGBA_CTX || document.createElement("canvas").getContext("2d"); RGBA_CTX.fillStyle = "#000"; RGBA_CTX.fillStyle = col; return rgbaOf(RGBA_CTX.fillStyle, a); } catch (e) {} }
  return (RGBA_CACHE[k] = "rgba(" + r + "," + g + "," + b + "," + Math.max(0, Math.min(1, a * a0)).toFixed(3) + ")");
}
Path.prototype._state = function () {
  var o = this.options, st = o.stroke !== false;
  var fc = o.fillColor || o.color || "#3388ff", fo = o.fill ? (o.fillOpacity == null ? 0.2 : o.fillOpacity) : 0;
  return { c: o.color || "#3388ff", w: st ? (o.weight == null ? 3 : o.weight) : 0, o: st ? (o.opacity == null ? 1 : o.opacity) : 0,
    fc: fc, fo: fo, fa: rgbaOf(String(fc), fo), r: this._radius != null ? this._radius : 5 };
};
Path.prototype._touch = function (geom) { var m = this._map; if (!m) return; var P = m._vp(this._paneName()); if (geom) P.dirty = true; this._stateDirty = true; m._schedule(); };
Path.prototype._onAddTo = function (map) { this._map = map; var P = map._vp(this._paneName()); P.paths[this._pid] = this; P.dirty = true; map._schedule(); };
Path.prototype._onRemoveFrom = function (map) { var P = map._vp(this._paneName()); delete P.paths[this._pid]; P.dirty = true; map._schedule(); if (map._hover === this) map._hover = null; };
Path.prototype.addTo = function (map) { map.addLayer(this); return this; };
Path.prototype.remove = function () { if (this._map) this._map.removeLayer(this); return this; };
Path.prototype.setStyle = function (s) {
  var group = GROUP_STYLING > 0;
  if (this._inHover && this._hoverStyle && !group) Object.assign(this._hoverStyle, s || {});
  Object.assign(this.options, s || {});
  if (group && this._hoverStyle && this._map && this._map._hover === this) Object.assign(this.options, this._hoverStyle); if ("dashArray" in (s || {})) this._touch(true); else this._touch(false); return this; };
Path.prototype.bringToFront = function () { return this; };
Path.prototype.bringToBack = function () { return this; };
Path.prototype.redraw = function () { this._touch(true); return this; };
Path.prototype.bindPopup = function (c, o) { this._popupContent = c; this._popupOpts = o || {}; return this; };
Path.prototype.unbindPopup = function () { this._popupContent = null; return this; };
Path.prototype.openPopup = function (ll) { if (!this._map || this._popupContent == null) return this; var p = new Popup(this._popupOpts); p.setContent(typeof this._popupContent === "function" ? this._popupContent(this) : this._popupContent); p.setLatLng(ll || this.getCenter()); p.openOn(this._map); return this; };
Path.prototype.closePopup = function () { if (this._map) this._map.closePopup(); return this; };
Path.prototype.bindTooltip = function (c, o) { this._tipContent = c; this._tipOpts = o || {}; return this; };
Path.prototype.openTooltip = function (ll) { if (this._map) this._map._showTip(this._tipContent, this._tipOpts, ll); return this; };
Path.prototype.closeTooltip = function () { if (this._map) this._map._hideTip(); return this; };
Path.prototype.getCenter = function () { return this.getBounds().getCenter(); };
Path.prototype._props = function () { return { pid: this._pid, dash: this.options.dashArray ? 1 : 0 }; };

/* polygons and lines from GeoJSON geometry */
function GeoPath(feature, opts) { this._initPath(opts, true); this.feature = feature; }
GeoPath.prototype = Object.create(Path.prototype);
GeoPath.prototype._feature = function () {
  var g = this.feature && this.feature.geometry; if (!g) return null;
  var t = g.type, gg = (t === "Polygon" || t === "MultiPolygon") ? "poly" : (t === "LineString" || t === "MultiLineString") ? "line" : (t === "Point" ? "pt" : "line");
  if (t === "GeometryCollection") return null;
  var p = this._props(); p.g = gg;
  return { type: "Feature", id: this._pid, properties: p, geometry: g };
};
GeoPath.prototype.getBounds = function () { return geomBounds(this.feature && this.feature.geometry); };
GeoPath.prototype.toGeoJSON = function () { return this.feature; };
function geomBounds(g) {
  var b = new LatLngBounds();
  (function walk(c) { if (!c) return; if (typeof c[0] === "number") { b.extend([c[1], c[0]]); return; } for (var i = 0; i < c.length; i++) walk(c[i]); })(g && (g.coordinates || (g.geometries && g.geometries.map(function (x) { return x.coordinates; }))));
  return b;
}

function Polyline(latlngs, opts) { this._initPath(opts, false); this.setLatLngs(latlngs, true); }
Polyline.prototype = Object.create(Path.prototype);
Polyline.prototype.setLatLngs = function (lls, quiet) { this._latlngs = (lls || []).map(function (x) { return Array.isArray(x) && Array.isArray(x[0]) ? x.map(toLatLng) : toLatLng(x); }); if (!quiet) this._touch(true); return this; };
Polyline.prototype.getLatLngs = function () { return this._latlngs; };
Polyline.prototype._isPoly = false;
Polyline.prototype._feature = function () {
  var ls = this._latlngs; if (!ls.length) return null;
  var multi = Array.isArray(ls[0]);
  var co = function (arr) { return arr.filter(Boolean).map(function (l) { return [l.lng, l.lat]; }); };
  var p = this._props(), geom;
  if (this._isPoly) { var rings = multi ? ls.map(co) : [co(ls)]; rings.forEach(function (r) { if (r.length && (r[0][0] !== r[r.length - 1][0] || r[0][1] !== r[r.length - 1][1])) r.push(r[0]); }); geom = { type: "Polygon", coordinates: rings }; p.g = "poly"; }
  else { geom = multi ? { type: "MultiLineString", coordinates: ls.map(co) } : { type: "LineString", coordinates: co(ls) }; p.g = "line"; }
  return { type: "Feature", id: this._pid, properties: p, geometry: geom };
};
Polyline.prototype.getBounds = function () { var b = new LatLngBounds(); (function w(a) { a.forEach(function (x) { if (Array.isArray(x)) w(x); else b.extend(x); }); })(this._latlngs); return b; };
function Polygon(latlngs, opts) { Polyline.call(this, latlngs, Object.assign({ fill: true }, opts || {})); this.options.fill = !(opts && opts.fill === false); }
Polygon.prototype = Object.create(Polyline.prototype);
Polygon.prototype._isPoly = true;

function CircleMarker(ll, opts) { this._initPath(Object.assign({ weight: 3 }, opts), true); this.options.fill = !(opts && opts.fill === false); this._latlng = toLatLng(ll); this._radius = (opts && opts.radius != null) ? opts.radius : 10; }
CircleMarker.prototype = Object.create(Path.prototype);
CircleMarker.prototype.setStyle = function (s) { if (s && s.radius != null) this._radius = s.radius; return Path.prototype.setStyle.call(this, s); };
CircleMarker.prototype.setRadius = function (r) { this._radius = r; this._touch(false); return this; };
CircleMarker.prototype.getRadius = function () { return this._radius; };
CircleMarker.prototype.setLatLng = function (ll) { this._latlng = toLatLng(ll); this._touch(true); return this; };
CircleMarker.prototype.getLatLng = function () { return this._latlng; };
CircleMarker.prototype.getBounds = function () { return new LatLngBounds(this._latlng, this._latlng); };
CircleMarker.prototype.getCenter = function () { return this._latlng; };
CircleMarker.prototype._feature = function () { if (!this._latlng) return null; var p = this._props(); p.g = "pt"; return { type: "Feature", id: this._pid, properties: p, geometry: { type: "Point", coordinates: [this._latlng.lng, this._latlng.lat] } }; };

/* groups */
function LayerGroup(layers, opts) { this.options = opts || {}; this._ls = []; this._parents = []; (layers || []).forEach(this.addLayer, this); }
mix(LayerGroup);
LayerGroup.prototype.addLayer = function (l) { if (!l || this._ls.indexOf(l) >= 0) return this; this._ls.push(l); if (l._parents) l._parents.push(this); if (this._map) this._map.addLayer(l); return this; };
LayerGroup.prototype.removeLayer = function (l) { var i = this._ls.indexOf(l); if (i < 0) return this; this._ls.splice(i, 1); if (l._parents) l._parents.splice(l._parents.indexOf(this), 1); if (this._map) this._map.removeLayer(l); return this; };
LayerGroup.prototype.hasLayer = function (l) { return this._ls.indexOf(l) >= 0; };
LayerGroup.prototype.clearLayers = function () { this._ls.slice().forEach(this.removeLayer, this); return this; };
LayerGroup.prototype.eachLayer = function (fn, ctx) { this._ls.slice().forEach(function (l) { fn.call(ctx, l); }); return this; };
LayerGroup.prototype.getLayers = function () { return this._ls.slice(); };
LayerGroup.prototype._onAddTo = function (map) { this._map = map; this._ls.forEach(function (l) { map.addLayer(l); }); };
LayerGroup.prototype._onRemoveFrom = function (map) { this._ls.forEach(function (l) { map.removeLayer(l); }); this._map = null; };
LayerGroup.prototype.addTo = function (map) { map.addLayer(this); return this; };
LayerGroup.prototype.remove = function () { if (this._map) this._map.removeLayer(this); return this; };
LayerGroup.prototype.setStyle = function (s) { GROUP_STYLING++; try { this._ls.forEach(function (l) { if (l.setStyle) l.setStyle(typeof s === "function" ? s(l.feature) : s); }); } finally { GROUP_STYLING--; } return this; };
LayerGroup.prototype.bringToFront = function () { return this; };
LayerGroup.prototype.bringToBack = function () { return this; };
LayerGroup.prototype.getBounds = function () { var b = new LatLngBounds(); this._ls.forEach(function (l) { if (l.getBounds) b.extend(l.getBounds()); else if (l.getLatLng) b.extend(l.getLatLng()); }); return b; };
LayerGroup.prototype.bindPopup = function (c, o) { this._ls.forEach(function (l) { if (l.bindPopup) l.bindPopup(c, o); }); return this; };
LayerGroup.prototype.redraw = function () { this._ls.forEach(function (l) { if (l.redraw) l.redraw(); }); return this; };

function GeoJSON(data, opts) {
  LayerGroup.call(this, [], opts);
  this.options = opts || {};
  if (data) this.addData(data);
}
GeoJSON.prototype = Object.create(LayerGroup.prototype);
GeoJSON.prototype.addData = function (data) {
  var feats = Array.isArray(data) ? data : data.type === "FeatureCollection" ? data.features : data.type === "Feature" ? [data] : [{ type: "Feature", properties: {}, geometry: data }];
  var o = this.options, self = this;
  feats.forEach(function (f) {
    if (!f || !f.geometry) return;
    if (o.filter && !o.filter(f)) return;
    var l;
    if (f.geometry.type === "Point") {
      var ll = new LatLng(f.geometry.coordinates[1], f.geometry.coordinates[0]);
      l = o.pointToLayer ? o.pointToLayer(f, ll) : new CircleMarker(ll, { radius: 5, pane: o.pane });
      l.feature = f;
    } else {
      l = new GeoPath(f, Object.assign({ pane: o.pane, renderer: o.renderer, interactive: o.interactive }, typeof o.style === "function" ? o.style(f) : (o.style || {})));
    }
    l.defaultOptions = Object.assign({}, l.options);
    if (o.onEachFeature) o.onEachFeature(f, l);
    self.addLayer(l);
  });
  return this;
};
GeoJSON.prototype.resetStyle = function (l) {
  var o = this.options, apply = function (x) { if (!x.setStyle) return; var base = Object.assign({}, x.defaultOptions || {}); var s = typeof o.style === "function" ? o.style(x.feature) : (o.style || {}); x.options = Object.assign({}, PATH_DEF, base, s); if (x._hoverStyle && x._map && x._map._hover === x && !l) Object.assign(x.options, x._hoverStyle); x._touch(false); };
  if (l) apply(l); else this._ls.forEach(apply);
  return this;
};
GeoJSON.prototype.setStyle = function (s) {
  GROUP_STYLING++; try { this._setStyle(s); } finally { GROUP_STYLING--; } return this;
};
GeoJSON.prototype._setStyle = function (s) {
  if (typeof s === "function") { this._ls.forEach(function (l) { if (l.setStyle) l.setStyle(s(l.feature)); }); this.options.style = this.options.style || s; }
  else this._ls.forEach(function (l) { if (l.setStyle) l.setStyle(s); });
  return this;
};
GeoJSON.prototype.toGeoJSON = function () { return { type: "FeatureCollection", features: this._ls.map(function (l) { return l.feature; }).filter(Boolean) }; };

/* ---------- hit testing: pointer events on vectors ---------- */
LMap.prototype._hit = function (pt) {
  var m = this._ml, vp = this._vpanes || {}, best = null, bz = -1;
  var panes = Object.keys(vp);
  for (var i = 0; i < panes.length; i++) {
    var pane = panes[i], el = this._panes[pane];
    if (el && el.style.pointerEvents === "none" && pane !== "overlayPane") continue;
    var ids = ["v-" + pane + "-circle", "v-" + pane + "-line", "v-" + pane + "-dash", "v-" + pane + "-fill"].filter(function (x) { return m.getLayer(x); });
    if (!ids.length) continue;
    // Leaflet hits a line or a circle only on its painted stroke, and a polygon anywhere inside it.
    var fs = [];
    try {
      var near = m.queryRenderedFeatures([[pt.x - 3, pt.y - 3], [pt.x + 3, pt.y + 3]], { layers: ids.filter(function (x) { return !/-fill$/.test(x); }) });
      near = near.filter(function (f) { var pa = vp[pane].paths[f.properties.pid]; if (!pa) return false; var st = pa._state();
        if (f.layer.type === "circle") { var c = f.geometry.coordinates, q = m.project(c); return Math.hypot(q.x - pt.x, q.y - pt.y) <= st.r + Math.max(1, st.w / 2) + 1; }
        return st.w > 0 && st.o > 0 && distToLine(m, f, pt) <= Math.max(0.35, st.w / 2); });
      fs = near.concat(m.queryRenderedFeatures([pt.x, pt.y], { layers: ids.filter(function (x) { return /-fill$/.test(x); }) }));
    } catch (e) { fs = []; }
    var z = paneZ(pane);
    for (var j = 0; j < fs.length; j++) {
      var f = fs[j], path = vp[pane].paths[f.properties.pid];
      if (!path || path.options.interactive === false) continue;
      var st = path._state();
      if (f.layer.type === "fill" && st.fo <= 0 && !path.listens("click") && !path.listens("mouseover") && !path._popupContent) continue;
      var rank = z * 10 + (f.layer.type === "circle" ? 3 : f.layer.type === "line" ? 2 : 1);
      if (rank > bz) { bz = rank; best = path; }
      break;
    }
  }
  return best;
};
function distToLine(m, f, pt) {
  var g = f.geometry, lines = g.type === "LineString" ? [g.coordinates] : g.type === "MultiLineString" ? g.coordinates : g.type === "Polygon" ? g.coordinates : g.type === "MultiPolygon" ? [].concat.apply([], g.coordinates) : [];
  var best = 1e9;
  for (var i = 0; i < lines.length; i++) { var L0 = lines[i], prev = null;
    for (var j = 0; j < L0.length; j++) { var q = m.project(L0[j]);
      if (prev) { var dx = q.x - prev.x, dy = q.y - prev.y, l2 = dx * dx + dy * dy, t = l2 ? Math.max(0, Math.min(1, ((pt.x - prev.x) * dx + (pt.y - prev.y) * dy) / l2)) : 0; var d = Math.hypot(pt.x - (prev.x + t * dx), pt.y - (prev.y + t * dy)); if (d < best) best = d; }
      prev = q; } }
  return best;
}
LMap.prototype._setHover = function (path, e) {
  var old = this._hover;
  if (old === path) { if (path && e) path.fire("mousemove", e, true); return; }
  this._hover = path;
  if (old) { old._hoverStyle = null; old._inHover = false; }
  if (old && e !== undefined) old.fire("mouseout", e || {}, true);
  if (path) {
    // Whatever the mouseover handler styles the path with is its hover style. In Leaflet a later restyle of the
    // whole layer would wipe it; here it is put back, so a highlighted country stays highlighted while the pointer is on it.
    path._hoverStyle = {}; path._inHover = true;
    path.fire("mouseover", e, true);
    path._inHover = false;
    if (path._hoverStyle && !Object.keys(path._hoverStyle).length) path._hoverStyle = null;
  }
  this._ml.getCanvas().style.cursor = path && (path.listens("click") || path._popupContent) ? "pointer" : "";
};
LMap.prototype._onMove = function (e) {
  var ev = this._evt(e);
  if (window.__cnClaimMove && window.__cnClaimMove(e)) { this._setHover(null, ev); this._hideTip(); this.fire("mousemove", ev); return; }
  var p = this._hit(e.point);
  this._setHover(p, ev);
  if (this._tip && this._tip.style.display === "block" && this._tipSticky) this._placeTip(e.point);
  this.fire("mousemove", ev);
};
LMap.prototype._onClick = function (e) {
  var ev = this._evt(e);
  if (window.__cnClaimClick && window.__cnClaimClick(e)) return;
  var p = this._hit(e.point);
  // As in Leaflet, a click that a layer listens for goes to that layer and not to the map.
  if (p && (p.listens("click") || p._popupContent != null)) {
    p.fire("click", ev, true);
    if (p._popupContent != null) p.openPopup(ev.latlng);
    return;
  }
  this.fire("click", ev);
};

/* tooltips: one element that follows the pointer */
LMap.prototype._showTip = function (content, o, ll) {
  var t = this._tip;
  if (!t) { t = this._tip = document.createElement("div"); t.className = "leaflet-tooltip leaflet-tooltip-top shim-tip"; t.style.cssText = "position:absolute;z-index:660;pointer-events:none;display:none"; this._container.appendChild(t); }
  t.innerHTML = typeof content === "function" ? content() : String(content == null ? "" : content);
  t.style.display = "block";
  this._tipSticky = !(o && o.sticky === false);
  if (ll) { var p = this.latLngToContainerPoint(ll); this._placeTip(p); }
};
LMap.prototype._placeTip = function (p) { var t = this._tip; if (!t) return; t.style.left = (p.x - t.offsetWidth / 2) + "px"; t.style.top = (p.y - t.offsetHeight - 12) + "px"; };
LMap.prototype._hideTip = function () { if (this._tip) this._tip.style.display = "none"; };

/* ---------- markers ---------- */
function DivIcon(o) { this.options = Object.assign({ className: "leaflet-div-icon", html: "", iconSize: [12, 12] }, o || {}); }
DivIcon.prototype.createIcon = function () {
  var o = this.options, d = document.createElement("div");
  d.className = "leaflet-marker-icon " + (o.className || "");
  if (typeof o.html === "string") d.innerHTML = o.html; else if (o.html) d.appendChild(o.html);
  var s = o.iconSize ? toPoint(o.iconSize) : null;
  if (s) { d.style.width = s.x + "px"; d.style.height = s.y + "px"; }
  return d;
};
function Marker(ll, o) { this.options = Object.assign({ interactive: true }, o || {}); this._latlng = toLatLng(ll); this._parents = []; }
mix(Marker);
Marker.prototype._onAddTo = function (map) {
  var self = this, icon = this.options.icon || new DivIcon({ html: '<div style="width:12px;height:12px;border-radius:50%;background:#ffd24a;border:2px solid #06090a"></div>', className: "", iconSize: [12, 12] });
  var el = this._el = icon.createIcon();
  var o = icon.options, s = o.iconSize ? toPoint(o.iconSize) : new Point(12, 12), a = o.iconAnchor ? toPoint(o.iconAnchor) : new Point(s.x / 2, s.y / 2);
  this._mk = new ml.Marker({ element: el, anchor: "top-left", offset: [-a.x, -a.y], opacityWhenCovered: "0" }).setLngLat([this._latlng.lng, this._latlng.lat]).addTo(map._ml);
  if (this.options.interactive !== false) {
    el.style.cursor = "pointer";
    el.addEventListener("click", function (ev) { ev.stopPropagation(); var e = { latlng: self._latlng, originalEvent: ev, containerPoint: map.mouseEventToContainerPoint(ev) }; if (self.listens("click") || self._popupContent != null) { self.fire("click", e, true); if (self._popupContent != null) self.openPopup(); } else map.fire("click", e); });
    el.addEventListener("mouseenter", function (ev) { self.fire("mouseover", { latlng: self._latlng, originalEvent: ev }, true); });
    el.addEventListener("mouseleave", function (ev) { self.fire("mouseout", { latlng: self._latlng, originalEvent: ev }, true); });
  }
};
Marker.prototype._onRemoveFrom = function () { if (this._mk) this._mk.remove(); this._mk = null; };
Marker.prototype.addTo = function (map) { map.addLayer(this); return this; };
Marker.prototype.remove = function () { if (this._map) this._map.removeLayer(this); return this; };
Marker.prototype.getLatLng = function () { return this._latlng; };
Marker.prototype.setLatLng = function (ll) { this._latlng = toLatLng(ll); if (this._mk) this._mk.setLngLat([this._latlng.lng, this._latlng.lat]); return this; };
Marker.prototype.setIcon = function (ic) { this.options.icon = ic; if (this._map) { var m = this._map; this._onRemoveFrom(m); this._onAddTo(m); } return this; };
Marker.prototype.setOpacity = function (o) { if (this._el) this._el.style.opacity = o; return this; };
Marker.prototype.setZIndexOffset = function () { return this; };
Marker.prototype.getElement = function () { return this._el; };
Marker.prototype.bindPopup = function (c, o) { this._popupContent = c; this._popupOpts = o || {}; return this; };
Marker.prototype.openPopup = function () { if (!this._map || this._popupContent == null) return this; var p = new Popup(this._popupOpts).setContent(this._popupContent).setLatLng(this._latlng); p.openOn(this._map); return this; };
Marker.prototype.bindTooltip = function (c, o) { this._tipContent = c; return this; };
Marker.prototype.getBounds = function () { return new LatLngBounds(this._latlng, this._latlng); };

/* ---------- popups, built in Leaflet's own markup so the page's popup styles apply ---------- */
function Popup(o) { this.options = Object.assign({ maxWidth: 300, minWidth: 50, autoPan: true, closeButton: true }, o || {}); this._parents = []; }
mix(Popup);
Popup.prototype.setLatLng = function (ll) { this._latlng = toLatLng(ll); if (this._mk) this._mk.setLngLat([this._latlng.lng, this._latlng.lat]); return this; };
Popup.prototype.getLatLng = function () { return this._latlng; };
Popup.prototype.setContent = function (c) { this._content = c; if (this._body) this._fill(); return this; };
Popup.prototype.getContent = function () { return this._content; };
Popup.prototype.getElement = function () { return this._el; };
Popup.prototype.isOpen = function () { return !!this._mk; };
Popup.prototype._fill = function () {
  var c = this._content, b = this._body; b.innerHTML = "";
  if (typeof c === "function") c = c(this);
  if (typeof c === "string") b.innerHTML = c; else if (c) b.appendChild(c);
  var o = this.options;
  b.style.maxHeight = o.maxHeight ? o.maxHeight + "px" : "";
  if (o.maxHeight) { b.style.overflowY = "auto"; this._el.classList.add("leaflet-popup-scrolled"); }
};
Popup.prototype.openOn = function (map) {
  if (map._popup && map._popup !== this) map._popup._close();
  if (this._mk) this._close(true);
  var self = this, o = this.options;
  var el = this._el = document.createElement("div");
  el.className = "leaflet-popup " + (o.className || "");
  var wrap = document.createElement("div"); wrap.className = "leaflet-popup-content-wrapper";
  var body = this._body = document.createElement("div"); body.className = "leaflet-popup-content";
  body.style.width = "auto"; body.style.maxWidth = (o.maxWidth || 300) + "px"; body.style.minWidth = (o.minWidth || 50) + "px";
  wrap.appendChild(body); el.appendChild(wrap);
  var tc = document.createElement("div"); tc.className = "leaflet-popup-tip-container"; var tip = document.createElement("div"); tip.className = "leaflet-popup-tip"; tc.appendChild(tip); el.appendChild(tc);
  if (o.closeButton !== false) { var x = document.createElement("a"); x.className = "leaflet-popup-close-button"; x.href = "#close"; x.setAttribute("role", "button"); x.innerHTML = "<span aria-hidden=\"true\">&#215;</span>"; x.addEventListener("click", function (ev) { ev.preventDefault(); ev.stopPropagation(); map.closePopup(self); }); el.appendChild(x); }
  ["mousedown", "click", "dblclick", "wheel", "touchstart"].forEach(function (t) { el.addEventListener(t, function (ev) { ev.stopPropagation(); }); });
  this._fill();
  this._map = map; map._popup = this;
  var ll = this._latlng || map.getCenter();
  this._mk = new ml.Marker({ element: el, anchor: "bottom", offset: [0, -20] }).setLngLat([ll.lng, ll.lat]).addTo(map._ml);
  el.style.zIndex = 700;
  if (this._mk.getElement()) this._mk.getElement().style.zIndex = 700;
  if (o.autoPan !== false) setTimeout(function () { try { var r = el.getBoundingClientRect(), c = map._container.getBoundingClientRect(), dx = 0, dy = 0; if (r.top < c.top + 10) dy = r.top - c.top - 10; if (r.left < c.left + 10) dx = r.left - c.left - 10; if (r.right > c.right - 10) dx = r.right - c.right + 10; if (dx || dy) map._ml.panBy([dx, dy], { duration: 250 }); } catch (e) {} }, 0);
  map.fire("popupopen", { popup: this });
  return this;
};
Popup.prototype._close = function (quiet) { if (this._mk) { this._mk.remove(); this._mk = null; } var m = this._map; if (m && m._popup === this) { m._popup = null; if (!quiet) m.fire("popupclose", { popup: this }); } };
Popup.prototype.close = function () { this._close(); return this; };
Popup.prototype.remove = Popup.prototype.close;
Popup.prototype.addTo = function (map) { return this.openOn(map); };

/* ---------- custom layers (L.Layer.extend) and controls ---------- */
function Layer() {}
mix(Layer);
Layer.prototype.addTo = function (map) { map.addLayer(this); return this; };
Layer.prototype.remove = function () { if (this._map) this._map.removeLayer(this); return this; };
Layer.prototype.getPane = function (n) { return this._map ? this._map.getPane(n || (this.options && this.options.pane) || "overlayPane") : null; };
Layer.extend = function (proto) {
  var Parent = this;
  function C() { if (this.initialize) this.initialize.apply(this, arguments); }
  C.prototype = Object.create(Parent.prototype);
  Object.keys(proto || {}).forEach(function (k) { C.prototype[k] = proto[k]; });
  C.prototype.constructor = C;
  C.extend = Layer.extend;
  return C;
};

function Control(o) { this.options = Object.assign({ position: "topright" }, o || {}); }
Control.prototype.addTo = function (map) {
  this._map = map;
  var el = this._el = this.onAdd ? this.onAdd(map) : document.createElement("div");
  el.classList.add("leaflet-control");
  var corner = map._corner(this.options.position);
  if (this.options.position.indexOf("bottom") >= 0) corner.insertBefore(el, corner.firstChild); else corner.appendChild(el);
  return this;
};
Control.prototype.remove = function () { if (this._el && this._el.parentNode) this._el.parentNode.removeChild(this._el); if (this.onRemove) this.onRemove(this._map); return this; };
Control.prototype.getContainer = function () { return this._el; };
Control.extend = function (proto) { function C(o) { Control.call(this, o); } C.prototype = Object.create(Control.prototype); Object.assign(C.prototype, proto || {}); if (proto && proto.options) C.prototype.options = proto.options; return C; };
LMap.prototype._corner = function (pos) {
  if (!this._corners) {
    var cc = this._cc = document.createElement("div"); cc.className = "leaflet-control-container"; this._container.appendChild(cc);
    this._corners = {};
    ["topleft", "topright", "bottomleft", "bottomright"].forEach(function (p) { var d = document.createElement("div"); d.className = "leaflet-" + (p.indexOf("top") === 0 ? "top" : "bottom") + " leaflet-" + (p.indexOf("left") > 0 ? "left" : "right"); cc.appendChild(d); this._corners[p] = d; }, this);
  }
  return this._corners[pos] || this._corners.topright;
};
LMap.prototype._controls = function () {
  var self = this;
  this._container.classList.add("leaflet-container");
  if (this.options.zoomControl !== false) {
    var z = new Control({ position: "topleft" });
    z.onAdd = function () {
      var d = document.createElement("div"); d.className = "leaflet-control-zoom leaflet-bar";
      [["leaflet-control-zoom-in", "+", "Zoom in", function () { self._ml.zoomIn(); }], ["leaflet-control-zoom-out", "&#x2212;", "Zoom out", function () { self._ml.zoomOut(); }]].forEach(function (b) {
        var a = document.createElement("a"); a.className = b[0]; a.href = "#"; a.title = b[2]; a.setAttribute("role", "button"); a.innerHTML = '<span aria-hidden="true">' + b[1] + "</span>";
        a.addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); b[3](); }); d.appendChild(a);
      });
      return d;
    };
    z.addTo(this);
  }
};

/* ---------- inert stand-ins: imagery and the painted plate now come from the basemaps ---------- */
function Inert(url, o) { this._url = url; this.options = o || {}; this._parents = []; }
mix(Inert);
Inert.prototype._onAddTo = function (map) {
  var self = this;
  map.whenReady(function () { setTimeout(function () { self.fire("load"); self.fire("tileload", {}); }, 50); });
};
Inert.prototype._onRemoveFrom = function () {};
Inert.prototype.addTo = function (map) { map.addLayer(this); return this; };
Inert.prototype.remove = function () { if (this._map) this._map.removeLayer(this); return this; };
Inert.prototype.setOpacity = function () { return this; };
Inert.prototype.setUrl = function () { return this; };
Inert.prototype.bringToFront = Inert.prototype.bringToBack = function () { return this; };

/* ---------- DOM helpers ---------- */
var DomUtil = {
  create: function (tag, cls, parent) { var e = document.createElement(tag); if (cls) e.className = cls; if (parent) parent.appendChild(e); return e; },
  remove: function (e) { if (e && e.parentNode) e.parentNode.removeChild(e); },
  get: function (id) { return typeof id === "string" ? document.getElementById(id) : id; },
  addClass: function (e, c) { e.classList.add.apply(e.classList, String(c).split(/\s+/).filter(Boolean)); },
  removeClass: function (e, c) { e.classList.remove.apply(e.classList, String(c).split(/\s+/).filter(Boolean)); },
  hasClass: function (e, c) { return e.classList.contains(c); },
  setPosition: function (e, p) { p = toPoint(p); e._leaflet_pos = p; e.style.transform = "translate3d(" + p.x + "px," + p.y + "px,0)"; },
  getPosition: function (e) { return e._leaflet_pos || new Point(0, 0); },
  setOpacity: function (e, o) { e.style.opacity = o; },
  toFront: function (e) { if (e.parentNode) e.parentNode.appendChild(e); },
  toBack: function (e) { if (e.parentNode) e.parentNode.insertBefore(e, e.parentNode.firstChild); },
};
var DomEvent = {
  on: function (el, types, fn, ctx) { if (typeof types === "object") { for (var t in types) DomEvent.on(el, t, types[t], fn); return this; } String(types).split(/\s+/).forEach(function (t) { if (t) el.addEventListener(t, ctx ? fn.bind(ctx) : fn); }); return this; },
  off: function (el, types, fn) { String(types).split(/\s+/).forEach(function (t) { if (t) el.removeEventListener(t, fn); }); return this; },
  stopPropagation: function (e) { if (e && e.stopPropagation) e.stopPropagation(); if (e && e.originalEvent && e.originalEvent.stopPropagation) e.originalEvent.stopPropagation(); return this; },
  preventDefault: function (e) { if (e && e.preventDefault) e.preventDefault(); return this; },
  stop: function (e) { DomEvent.preventDefault(e); DomEvent.stopPropagation(e); return this; },
  disableScrollPropagation: function (el) { el.addEventListener("wheel", function (e) { e.stopPropagation(); }, { passive: true }); return this; },
  disableClickPropagation: function (el) { ["mousedown", "touchstart", "dblclick", "contextmenu"].forEach(function (t) { el.addEventListener(t, function (e) { e.stopPropagation(); }); }); return this; },
  getMousePosition: function (e, c) { if (!c) return new Point(e.clientX, e.clientY); var r = c.getBoundingClientRect(); return new Point(e.clientX - r.left, e.clientY - r.top); },
};

/* ---------- the L namespace ---------- */
var L = window.L = {
  version: "1.9.4-on-maplibre",
  map: function (id, o) { return new LMap(id, o); },
  Map: LMap,
  latLng: toLatLng, LatLng: LatLng,
  latLngBounds: toBounds, LatLngBounds: LatLngBounds,
  point: toPoint, Point: Point,
  polyline: function (ll, o) { return new Polyline(ll, o); }, Polyline: Polyline,
  polygon: function (ll, o) { return new Polygon(ll, o); }, Polygon: Polygon,
  circleMarker: function (ll, o) { return new CircleMarker(ll, o); }, CircleMarker: CircleMarker,
  circle: function (ll, o) { return new CircleMarker(ll, Object.assign({ radius: 6 }, o)); },
  geoJSON: function (d, o) { return new GeoJSON(d, o); }, geoJson: function (d, o) { return new GeoJSON(d, o); }, GeoJSON: GeoJSON,
  layerGroup: function (ls, o) { return new LayerGroup(ls, o); }, featureGroup: function (ls, o) { return new LayerGroup(ls, o); }, LayerGroup: LayerGroup, FeatureGroup: LayerGroup,
  marker: function (ll, o) { return new Marker(ll, o); }, Marker: Marker,
  divIcon: function (o) { return new DivIcon(o); }, DivIcon: DivIcon, icon: function (o) { return new DivIcon({ html: o && o.iconUrl ? '<img src="' + o.iconUrl + '" style="width:100%;height:100%">' : "", iconSize: o && o.iconSize, iconAnchor: o && o.iconAnchor, className: (o && o.className) || "" }); },
  popup: function (o) { return new Popup(o); }, Popup: Popup,
  tooltip: function (o) { return { setContent: function () { return this; } }; },
  control: function (o) { return new Control(o); }, Control: Control,
  tileLayer: function (u, o) { return new Inert(u, o); },
  imageOverlay: function (u, b, o) { return new Inert(u, o); },
  canvas: function (o) { return { options: o || {}, _renderer: "canvas" }; },
  svg: function (o) { return { options: o || {}, _renderer: "svg" }; },
  Layer: Layer,
  DomUtil: DomUtil, DomEvent: DomEvent,
  Util: { extend: Object.assign, bind: function (f, c) { return f.bind(c); }, stamp: function (o) { return o._leaflet_id || (o._leaflet_id = PATH_ID++); } },
  Browser: { mobile: /Mobi|Android/i.test(navigator.userAgent), touch: "ontouchstart" in window, retina: (window.devicePixelRatio || 1) > 1 },
};
})();
