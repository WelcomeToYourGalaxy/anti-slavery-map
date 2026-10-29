#!/usr/bin/env python3
"""inline.py -- put the map engine into index.html.

    python3 engine/inline.py

The map's own code is written against Leaflet. engine/leaflet-on-maplibre.js answers those calls
with MapLibre GL, so the map can be shown as a globe or a flat map on the Culprits basemaps
(engine/basemaps.js). engine/child.js and engine/child.css are the child abuse networks layer.
This script places all four inside index.html between the ENGINE markers, so index.html stays one
self-contained file. Run it after editing anything in engine/.
"""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
P = os.path.join(ROOT, 'index.html')
ML = '5.24.0'

def rd(n):
    p = os.path.join(HERE, n)
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''

def block(tag, body):
    return '<%s>\n%s\n</%s>' % (tag, body.replace('</script', '<\\/script'), tag)

html = open(P, encoding='utf-8').read()
head = ('<!--ENGINE:head-->\n<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@%s/dist/maplibre-gl.css">\n' % ML
        + (block('style', rd('child.css')) + '\n' if rd('child.css') else '') + (block('style', rd('ui.css')) + '\n' if rd('ui.css') else '') + '<!--/ENGINE:head-->')
eng = ('<!--ENGINE:js-->\n<script src="https://unpkg.com/maplibre-gl@%s/dist/maplibre-gl.js"></script>\n' % ML
       + ('<script>window.SHIM_PLATE="data:image/webp;base64,%s";</script>\n' % __import__('base64').b64encode(open(os.path.join(HERE, 'plate-antislavery.webp'), 'rb').read()).decode() if os.path.exists(os.path.join(HERE, 'plate-antislavery.webp')) else '')
       + block('script', rd('basemaps.js')) + '\n' + block('script', rd('leaflet-on-maplibre.js')) + '\n<!--/ENGINE:js-->')
tail = ('<!--ENGINE:tail-->\n' + (block('script', rd('ui.js')) + '\n' if rd('ui.js') else '') + (block('script', rd('child.js')) if rd('child.js') else '') + '\n<!--/ENGINE:tail-->')

def put(html, name, new, anchor_re, where):
    pat = re.compile(r'<!--ENGINE:%s-->.*?<!--/ENGINE:%s-->' % (name, name), re.S)
    if pat.search(html):
        return pat.sub(lambda m: new, html, count=1)
    m = re.search(anchor_re, html)
    assert m, anchor_re
    return html[:m.start()] + new + html[m.start():] if where == 'before' else html[:m.end()] + new + html[m.end():]

LEAF = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>'
html = html.replace(LEAF + '\n', '').replace(LEAF, '')
html = put(html, 'head', head, r'<link rel="stylesheet" href="https://cdnjs\.cloudflare\.com/ajax/libs/leaflet/1\.9\.4/leaflet\.min\.css"/?>', 'after')
html = put(html, 'js', eng, r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/topojson/3\.0\.2/topojson\.min\.js"></script>', 'after')
html = put(html, 'tail', tail, r'</body>', 'before')
# The old Leaflet plate is no longer drawn (engine/plate-antislavery.webp is); keep the variable, drop the 0.5 MB picture.
html = re.sub(r'var PLATE_IMG = "data:image/webp;base64,[^"]*"', 'var PLATE_IMG = ""', html, count=1)
open(P, 'w', encoding='utf-8').write(html)
print('index.html', round(len(html) / 1e6, 2), 'MB')
