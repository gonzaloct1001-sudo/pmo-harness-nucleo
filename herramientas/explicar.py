#!/usr/bin/env python3
"""Explicación visual: convierte un Markdown simple, con bloques de cifras, gráficos y pasos, en una página web de un
solo archivo que se abre con doble clic (sin internet), se ve bien en claro y oscuro, y se puede imprimir.

Uso:
    python herramientas/explicar.py <entrada.md> [--proyecto proyectos/<slug>] [--salida <ruta.html>] [--abrir] [--borrador]

El Markdown admite títulos (#, ##, ###), párrafos, viñetas, listas numeradas, tablas (las celdas Verde, Amarillo o
Rojo llevan su punto de color), **negrita**, *cursiva*, `código`, citas con `>` (recuadro destacado) e imágenes
`![pie](ruta.png)` (quedan dentro del archivo). Puede partir con un bloque `---` con `titulo`, `subtitulo` y `fecha`.
Bloques especiales, entre ``` con su nombre:

    ```cifras                         ```pasos                          ```tiempo
    Avance: 62 % | plan 70 %          Recibir: llegan las bases         2026-11-20: Entrega del informe
    Caja: $ 48 M | 2,1 meses          Revisar: se arma la matriz        2026-12-05: Comité
    ```                               ```                               ```

    ```grafico
    tipo: barras            # barras | columnas | lineas | tornado | histograma
    titulo: Avance por frente
    unidad: "%"
    datos: {Obras civiles: 80, Montaje: 55, Puesta en marcha: 10}
    ```
- barras y columnas: `datos: {etiqueta: valor}`, o varias series con `series: [Plan, Real]` y `datos: {etiqueta: [70, 62]}`.
- lineas: `categorias: [ene, feb, mar]` y `series: {Plan: [10, 20, 30], Real: [8, 19, 26]}`.
- tornado: `base: 120` y `datos: {Precio: [90, 150], Costo: [135, 100]}` (el resultado con la variable en su valor
  bajo y en su valor alto); se ordena solo, de la variable que más mueve el resultado a la que menos.
- histograma: `valores: [...]`; opcional `meta: 100` con `sentido: mayor | menor` (calcula y muestra la probabilidad
  de cumplirla) y `marcas: {P10: 80, P90: 130}`.
Cada gráfico trae su tabla de datos plegada («Ver los datos») y muestra el valor al pasar el cursor. Hasta 4 series
por gráfico: con más, se agrupa en «Otros» o se divide en dos gráficos.

Con --proyecto, la página sale con la marca del proyecto en `<proyecto>/explicaciones/<fecha>-<titulo>.html`; sin
él, junto al Markdown. Los números se escriben tal como vienen: deben salir de los datos del proyecto o de un script,
nunca de memoria. Un `[PENDIENTE` impide generar, salvo con --borrador.
"""
import argparse
import base64
import html
import math
import re
import sys
import unicodedata
import webbrowser
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SERIES_MAX = 4
ANCHO = 720
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".svg": "image/svg+xml"}

CSS = """
:root{color-scheme:light;--plano:#f9f9f7;--sup:#fcfcfb;--tinta:#0b0b0b;--tinta2:#52514e;--mudo:#898781;--grid:#e1e0d9;--eje:#c3c2b7;
--borde:rgba(11,11,11,.10);--serie-1:#2a78d6;--serie-2:#eb6834;--serie-3:#1baf7a;--serie-4:#eda100;--suave:#86b6ef;
--bien:#0ca30c;--alerta:#fab219;--critico:#d03b3b;--marca:#MARCA}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;--plano:#0d0d0d;--sup:#1a1a19;--tinta:#f0efec;
--tinta2:#c3c2b7;--grid:#2c2c2a;--eje:#383835;--borde:rgba(255,255,255,.10);--serie-1:#3987e5;--serie-2:#d95926;--serie-3:#199e70;
--serie-4:#c98500;--suave:#184f95}}
:root[data-theme="dark"]{color-scheme:dark;--plano:#0d0d0d;--sup:#1a1a19;--tinta:#f0efec;--tinta2:#c3c2b7;--grid:#2c2c2a;--eje:#383835;
--borde:rgba(255,255,255,.10);--serie-1:#3987e5;--serie-2:#d95926;--serie-3:#199e70;--serie-4:#c98500;--suave:#184f95}
*{box-sizing:border-box}body{margin:0;background:var(--plano);color:var(--tinta);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:860px;margin:0 auto;padding:0 16px 64px}header{border-top:5px solid var(--marca);padding:26px 0 6px}
header img{max-height:44px;max-width:180px;float:right;margin-left:16px}h1{font-size:28px;line-height:1.2;margin:0}
.sub{color:var(--tinta2);margin:6px 0 0}h2{font-size:20px;margin:34px 0 8px}h3{font-size:16px;margin:22px 0 6px}p{margin:10px 0}
ul,ol{padding-left:24px;margin:10px 0}li{margin:4px 0}code{background:var(--sup);border:1px solid var(--borde);border-radius:4px;padding:0 4px;font-size:.92em}
pre{background:var(--sup);border:1px solid var(--borde);border-radius:8px;padding:12px;overflow-x:auto}a{color:inherit}
.tabla{overflow-x:auto;background:var(--sup);border:1px solid var(--borde);border-radius:10px;margin:12px 0}
table{border-collapse:collapse;width:100%}th,td{text-align:left;vertical-align:top;padding:8px 12px;border-bottom:1px solid var(--grid)}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--tinta2);font-weight:600}tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.est{white-space:nowrap}.est i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}
.est-verde i{background:var(--bien)}.est-amarillo i{background:var(--alerta)}.est-rojo i{background:var(--critico)}
aside{background:var(--sup);border:1px solid var(--borde);border-left:4px solid var(--marca);border-radius:8px;padding:10px 14px;margin:14px 0}
.cifras{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:14px 0}
.cifra{background:var(--sup);border:1px solid var(--borde);border-radius:10px;padding:12px 14px}
.cifra span{display:block;color:var(--tinta2);font-size:13px}.cifra b{display:block;font-size:26px;font-weight:600;line-height:1.25}
.cifra small{color:var(--tinta2)}
.pasos,.tiempo{list-style:none;padding:0;margin:14px 0}.pasos li,.tiempo li{position:relative;margin:0;padding:0 0 16px 44px}
.pasos li:before{content:counter(p);counter-increment:p;position:absolute;left:0;top:0;width:28px;height:28px;border-radius:50%;
background:var(--sup);border:1px solid var(--eje);text-align:center;line-height:26px;font-weight:600;font-size:14px}
.pasos{counter-reset:p}.pasos li:after,.tiempo li:after{content:"";position:absolute;left:13.5px;top:30px;bottom:2px;width:1px;background:var(--eje)}
.pasos li:last-child:after,.tiempo li:last-child:after{display:none}.pasos b,.tiempo b{display:block}
.tiempo li:before{content:"";position:absolute;left:9px;top:6px;width:10px;height:10px;border-radius:50%;background:var(--serie-1);
box-shadow:0 0 0 2px var(--sup)}.tiempo li:after{top:20px}.tiempo time{color:var(--tinta2);font-size:13px;font-variant-numeric:tabular-nums}
figure{background:var(--sup);border:1px solid var(--borde);border-radius:10px;padding:14px 16px 8px;margin:16px 0}
figcaption{margin-bottom:6px}figcaption b{font-size:15px}figcaption span{color:var(--tinta2);font-size:13px;margin-left:8px}
figure img{max-width:100%;height:auto;display:block;margin:0 auto}figure.img figcaption{margin:8px 0 2px;color:var(--tinta2);font-size:14px}
svg{display:block;width:100%;height:auto;overflow:visible}svg text{font:12px system-ui,-apple-system,"Segoe UI",sans-serif;fill:var(--tinta2)}
svg .et{fill:var(--tinta);font-size:13px}svg .val{fill:var(--tinta);font-size:12px;font-variant-numeric:tabular-nums}
svg .tick{fill:var(--mudo);font-variant-numeric:tabular-nums}.grid{stroke:var(--grid);stroke-width:1}.eje{stroke:var(--eje);stroke-width:1}
.s1{fill:var(--serie-1)}.s2{fill:var(--serie-2)}.s3{fill:var(--serie-3)}.s4{fill:var(--serie-4)}.sv{fill:var(--suave)}
.l1,.l2,.l3,.l4{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.l1{stroke:var(--serie-1)}.l2{stroke:var(--serie-2)}.l3{stroke:var(--serie-3)}.l4{stroke:var(--serie-4)}
.pt{stroke:var(--sup);stroke-width:2}.marca-l{stroke:var(--tinta2);stroke-width:1}.hit{fill:transparent;outline:none}
.banda .cruz,.banda .pt-h{opacity:0}.banda:hover .cruz,.banda:focus-within .cruz,.banda:hover .pt-h,.banda:focus-within .pt-h{opacity:1}
.banda:hover .m,.banda:focus-within .m{filter:brightness(1.12)}.cruz{stroke:var(--mudo);stroke-width:1}
.ley{display:flex;flex-wrap:wrap;gap:4px 16px;font-size:13px;color:var(--tinta2);margin:2px 0 8px}
.ley i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.ley i.li{height:2px;width:16px;border-radius:1px;vertical-align:4px}
.k1{background:var(--serie-1)}.k2{background:var(--serie-2)}.k3{background:var(--serie-3)}.k4{background:var(--serie-4)}.kv{background:var(--suave)}
.nota{color:var(--tinta2);font-size:14px;margin:6px 0}
details{margin:6px 0 4px;font-size:14px}summary{cursor:pointer;color:var(--tinta2)}details table{margin-top:6px}
.tip{position:fixed;z-index:9;pointer-events:none;background:var(--sup);color:var(--tinta);border:1px solid var(--borde);border-radius:8px;
box-shadow:0 4px 18px rgba(0,0,0,.18);padding:8px 10px;font-size:13px;max-width:280px}.tip-t{color:var(--tinta2);margin-bottom:2px}
.tip-f span{color:var(--tinta2)}.tip-k{display:inline-block;width:12px;height:2px;border-radius:1px;margin-right:6px;vertical-align:4px}
footer{color:var(--mudo);font-size:13px;border-top:1px solid var(--grid);margin-top:40px;padding-top:10px}
@media print{body{background:#fff}main{max-width:none}figure,.cifra,aside,.tabla{break-inside:avoid}.tip{display:none}details>summary{display:none}}
@media print,(forced-colors:active){.s2{fill:url(#tx45)}.s4{fill:url(#tx135)}}
"""

JS = """
(function(){var t=document.createElement('div');t.className='tip';t.hidden=true;document.body.appendChild(t);
function mostrar(el,x,y){var p=el.getAttribute('data-tip').split('||');t.textContent='';
var h=document.createElement('div');h.className='tip-t';h.textContent=p[0];t.appendChild(h);
for(var i=1;i<p.length;i++){var s=p[i].split('::'),f=document.createElement('div');f.className='tip-f';
if(s[2]){var k=document.createElement('i');k.className='tip-k k'+s[2];f.appendChild(k);}
var v=document.createElement('b');v.textContent=s[1];f.appendChild(v);
if(s[0]){var n=document.createElement('span');n.textContent=' '+s[0];f.appendChild(n);}t.appendChild(f);}
t.hidden=false;var w=t.offsetWidth,a=t.offsetHeight;
t.style.left=Math.max(8,Math.min(x+14,window.innerWidth-w-8))+'px';t.style.top=(y+a+22>window.innerHeight?Math.max(8,y-a-12):y+16)+'px';}
function de(e){return e.target&&e.target.closest?e.target.closest('[data-tip]'):null;}
document.addEventListener('pointermove',function(e){var el=de(e);if(el){mostrar(el,e.clientX,e.clientY);}else{t.hidden=true;}});
document.addEventListener('focusin',function(e){var el=de(e);if(el){var b=el.getBoundingClientRect();mostrar(el,b.left+b.width/2,b.top+b.height/2);}});
document.addEventListener('focusout',function(){t.hidden=true;});})();
"""

TEXTURAS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
            '<pattern id="tx45" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<rect width="6" height="6" fill="#eb6834"/><line x1="0" y1="0" x2="0" y2="6" stroke="#a8431a" stroke-width="2"/></pattern>'
            '<pattern id="tx135" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(135)">'
            '<rect width="6" height="6" fill="#eda100"/><line x1="0" y1="0" x2="0" y2="6" stroke="#a87200" stroke-width="2"/></pattern>'
            '</defs></svg>')


class Problema(Exception):
    """Algo del Markdown que impide generar la página; el mensaje dice qué corregir."""


# ------------------------------------------------------------------------------------------------ utilidades
def esc(x):
    return html.escape(str(x), quote=True)


def slug(texto):
    t = "".join(c for c in unicodedata.normalize("NFD", str(texto)) if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60] or "explicacion"


def num(v, unidad=""):
    """Número como se escribe en Chile (1.234,5), con su unidad pegada si es un símbolo corto."""
    if v is None:
        return ""
    v = float(v)
    dec = 0 if abs(v) >= 100 or v == int(v) else (1 if abs(v) >= 10 else 2)
    t = f"{v:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    if dec and "," in t:
        t = t.rstrip("0").rstrip(",")
    u = str(unidad or "").strip()
    if u == "$":
        return "$ " + t
    return t + (u if len(u) == 1 else "")


def compacto(v):
    """Número de eje: completo bajo 10.000; después, en miles o millones."""
    a = abs(v)
    if a >= 1_000_000:
        return num(v / 1_000_000) + " M"
    if a >= 10_000:
        return num(v / 1_000) + " mil"
    return num(v)


def marcas_eje(vmin, vmax, n=5):
    """Valores redondos que cubren [vmin, vmax]."""
    if vmax <= vmin:
        vmax = vmin + 1
    bruto = (vmax - vmin) / max(1, n)
    mag = 10 ** math.floor(math.log10(bruto))
    paso = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= bruto)
    ini, fin = math.floor(vmin / paso) * paso, math.ceil(vmax / paso) * paso
    return [round(ini + i * paso, 10) for i in range(int(round((fin - ini) / paso)) + 1)]


def ancho_texto(t, px=13):
    return len(str(t)) * px * 0.56


def cortar(t, ancho, px=12):
    t = str(t)
    caben = max(3, int(ancho / (px * 0.56) + 0.01))
    return t if len(t) <= caben else t[:caben - 1].rstrip() + "…"


def numero(v, donde):
    try:
        return float(str(v).replace(",", ".")) if not isinstance(v, (int, float)) else float(v)
    except (TypeError, ValueError):
        raise Problema(f"{donde}: «{v}» no es un número")


# ---------------------------------------------------------------------------------------------- gráficos
def barra_h(xb, xe, y, h):
    r = min(4, abs(xe - xb), h / 2)
    s = 1 if xe >= xb else -1
    return f"M{xb:.1f},{y:.1f}H{xe - s * r:.1f}Q{xe:.1f},{y:.1f} {xe:.1f},{y + r:.1f}V{y + h - r:.1f}Q{xe:.1f},{y + h:.1f} {xe - s * r:.1f},{y + h:.1f}H{xb:.1f}Z"


def barra_v(x, w, yb, ye):
    r = min(4, abs(ye - yb), w / 2)
    s = 1 if ye <= yb else -1
    return f"M{x:.1f},{yb:.1f}V{ye + s * r:.1f}Q{x:.1f},{ye:.1f} {x + r:.1f},{ye:.1f}H{x + w - r:.1f}Q{x + w:.1f},{ye:.1f} {x + w:.1f},{ye + s * r:.1f}V{yb:.1f}Z"


def series_de(spec, donde):
    """(categorías, nombres de serie, {serie: [valores]}) desde las formas que admite un bloque de gráfico."""
    datos, series = spec.get("datos"), spec.get("series")
    if isinstance(series, dict):
        cats = [str(c) for c in (spec.get("categorias") or range(1, max(len(v) for v in series.values()) + 1))]
        nombres = [str(k) for k in series]
        valores = {str(k): [numero(x, donde) for x in v] for k, v in series.items()}
        if any(len(v) != len(cats) for v in valores.values()):
            raise Problema(f"{donde}: cada serie debe traer un valor por categoría ({len(cats)})")
    elif isinstance(datos, dict) and datos:
        cats = [str(c) for c in datos]
        primero = next(iter(datos.values()))
        if isinstance(primero, (list, tuple)):
            nombres = [str(s) for s in (series or [f"Serie {i + 1}" for i in range(len(primero))])]
            valores = {n: [numero(datos[c][i], donde) for c in datos] for i, n in enumerate(nombres)}
        elif isinstance(primero, dict):
            nombres = [str(s) for s in primero]
            valores = {n: [numero((datos[c] or {}).get(n, 0), donde) for c in datos] for n in nombres}
        else:
            nombres = [str(spec.get("serie") or spec.get("titulo") or "Valor")]
            valores = {nombres[0]: [numero(v, donde) for v in datos.values()]}
    else:
        raise Problema(f"{donde}: faltan los datos (`datos: {{etiqueta: valor}}` o `categorias` y `series`)")
    if len(nombres) > SERIES_MAX:
        raise Problema(f"{donde}: {len(nombres)} series son demasiadas para leerlas (máximo {SERIES_MAX}): agrupa las "
                       "menores en «Otros» o divide en dos gráficos")
    if not cats:
        raise Problema(f"{donde}: sin categorías")
    return cats, nombres, valores


def pista(titulo, filas):
    """Texto del globo de un elemento: título y filas (nombre, valor, serie)."""
    return esc("||".join([str(titulo)] + [f"{n}::{v}::{k}" for n, v, k in filas]))


def leyenda(nombres, linea=False, clases=None):
    if len(nombres) < 2:
        return ""
    clases = clases or [f"k{i + 1}" for i in range(len(nombres))]
    return '<div class="ley">' + "".join(f'<span><i class="{c}{" li" if linea else ""}"></i>{esc(n)}</span>'
                                         for n, c in zip(nombres, clases)) + "</div>"


def tabla_datos(encabezados, filas):
    cab = "".join(f'<th{" class=n" if i else ""}>{esc(h)}</th>' for i, h in enumerate(encabezados))
    cuerpo = "".join("<tr>" + "".join(f'<td{" class=n" if i else ""}>{esc(c)}</td>' for i, c in enumerate(f)) + "</tr>" for f in filas)
    return f'<details><summary>Ver los datos</summary><div class="tabla"><table><thead><tr>{cab}</tr></thead><tbody>{cuerpo}</tbody></table></div></details>'


def figura(spec, svg, ley, tabla, nota=""):
    titulo, unidad = spec.get("titulo") or "", str(spec.get("unidad") or "").strip()
    cap = f'<figcaption><b>{esc(titulo)}</b>' + (f"<span>en {esc(unidad)}</span>" if len(unidad) > 1 else "") + "</figcaption>" if titulo else ""
    nota = nota or (esc(spec["nota"]) if spec.get("nota") else "")
    return f'<figure>{cap}{ley}{svg}' + (f'<p class="nota">{nota}</p>' if nota else "") + f"{tabla}</figure>"


def g_barras(spec, donde):
    cats, nombres, val = series_de(spec, donde)
    if len(cats) < 2:
        raise Problema(f"{donde}: una sola barra no es un gráfico; usa un bloque `cifras`")
    u, k = spec.get("unidad", ""), len(nombres)
    izq = min(240, max(60, max(ancho_texto(c) for c in cats) + 14))
    der, sup, grosor = 70, 6, (18 if k == 1 else 12)
    banda = k * grosor + (k - 1) * 2 + 16
    alto = sup + len(cats) * banda + 26
    todos = [v for n in nombres for v in val[n]]
    ms = marcas_eje(min(0, min(todos)), max(0, max(todos)))
    pw = ANCHO - izq - der
    x = lambda v: izq + (v - ms[0]) / (ms[-1] - ms[0]) * pw  # noqa: E731
    o = [f'<line class="grid" x1="{x(m):.1f}" y1="{sup}" x2="{x(m):.1f}" y2="{alto - 24}"/>'
         f'<text class="tick" x="{x(m):.1f}" y="{alto - 8}" text-anchor="middle">{esc(compacto(m))}</text>' for m in ms]
    for i, c in enumerate(cats):
        y0 = sup + i * banda
        g = [f'<text class="et" x="{izq - 10:.1f}" y="{y0 + banda / 2 + 4:.1f}" text-anchor="end">{esc(cortar(c, izq - 14, 13))}</text>']
        for j, n in enumerate(nombres):
            v, y = val[n][i], y0 + 8 + j * (grosor + 2)
            g.append(f'<path class="m s{j + 1}" d="{barra_h(x(0), x(v), y, grosor)}"/>')
            if k <= 2:
                g.append(f'<text class="val" x="{x(v) + (6 if v >= 0 else -6):.1f}" y="{y + grosor / 2 + 4:.1f}" '
                         f'text-anchor="{"start" if v >= 0 else "end"}">{esc(num(v, u))}</text>')
        tip = pista(c, [(n if k > 1 else "", num(val[n][i], u), j + 1) for j, n in enumerate(nombres)])
        g.append(f'<rect class="hit" tabindex="0" x="0" y="{y0}" width="{ANCHO}" height="{banda}" data-tip="{tip}"/>')
        o.append(f'<g class="banda">{"".join(g)}</g>')
    o.append(f'<line class="eje" x1="{x(0):.1f}" y1="{sup}" x2="{x(0):.1f}" y2="{alto - 24}"/>')
    svg = f'<svg viewBox="0 0 {ANCHO} {alto}" role="img" aria-label="{esc(spec.get("titulo") or "Gráfico de barras")}">{"".join(o)}</svg>'
    tabla = tabla_datos([spec.get("categoria") or ""] + nombres, [[c] + [num(val[n][i], u) for n in nombres] for i, c in enumerate(cats)])
    return figura(spec, svg, leyenda(nombres), tabla)


def g_columnas(spec, donde, clases=None, etiquetas=True, aire=10):
    cats, nombres, val = series_de(spec, donde)
    if len(cats) < 2:
        raise Problema(f"{donde}: una sola columna no es un gráfico; usa un bloque `cifras`")
    u, k = spec.get("unidad", ""), len(nombres)
    izq, der, sup, ph = 56, 12, 20, 220
    alto, pw = sup + ph + 40, ANCHO - izq - der
    hueco = pw / len(cats)
    grosor = max(2, min(24, (hueco - aire - (k - 1) * 2) / k))
    todos = [v for n in nombres for v in val[n]]
    ms = marcas_eje(min(0, min(todos)), max(0, max(todos)))
    y = lambda v: sup + ph - (v - ms[0]) / (ms[-1] - ms[0]) * ph  # noqa: E731
    o = [f'<line class="grid" x1="{izq}" y1="{y(m):.1f}" x2="{ANCHO - der}" y2="{y(m):.1f}"/>'
         f'<text class="tick" x="{izq - 8}" y="{y(m) + 4:.1f}" text-anchor="end">{esc(compacto(m))}</text>' for m in ms]
    cada = max(1, math.ceil(len(cats) / max(1, int(pw / 70))))
    for i, c in enumerate(cats):
        x0 = izq + i * hueco
        ini = x0 + (hueco - (k * grosor + (k - 1) * 2)) / 2
        g = []
        for j, n in enumerate(nombres):
            v = val[n][i]
            clase = clases[i] if clases else f"s{j + 1}"
            g.append(f'<path class="m {clase}" d="{barra_v(ini + j * (grosor + 2), grosor, y(0), y(v))}"/>')
            if k == 1 and len(cats) <= 12 and not clases:
                g.append(f'<text class="val" x="{ini + grosor / 2:.1f}" y="{y(v) - 6 if v >= 0 else y(v) + 14:.1f}" text-anchor="middle">{esc(num(v, u))}</text>')
        if etiquetas and i % cada == 0:
            g.append(f'<text class="et" x="{x0 + hueco / 2:.1f}" y="{sup + ph + 18}" text-anchor="middle">{esc(cortar(c, hueco * cada - 6, 13))}</text>')
        tip = pista(c, [(n if k > 1 else "", num(val[n][i], u), (j + 1) if not clases else ("1" if clases[i] == "s1" else "v")) for j, n in enumerate(nombres)])
        g.append(f'<rect class="hit" tabindex="0" x="{x0:.1f}" y="{sup}" width="{hueco:.1f}" height="{ph + 26}" data-tip="{tip}"/>')
        o.append(f'<g class="banda">{"".join(g)}</g>')
    o.append(f'<line class="eje" x1="{izq}" y1="{y(0):.1f}" x2="{ANCHO - der}" y2="{y(0):.1f}"/>')
    return cats, nombres, val, "".join(o), alto, (izq, der, sup, ph, pw)


def fig_columnas(spec, donde):
    cats, nombres, val, cuerpo, alto, _ = g_columnas(spec, donde)
    u = spec.get("unidad", "")
    svg = f'<svg viewBox="0 0 {ANCHO} {alto}" role="img" aria-label="{esc(spec.get("titulo") or "Gráfico de columnas")}">{cuerpo}</svg>'
    tabla = tabla_datos([spec.get("categoria") or ""] + nombres, [[c] + [num(val[n][i], u) for n in nombres] for i, c in enumerate(cats)])
    return figura(spec, svg, leyenda(nombres), tabla)


def g_lineas(spec, donde):
    cats, nombres, val = series_de(spec, donde)
    if len(cats) < 2:
        raise Problema(f"{donde}: una línea necesita al menos dos puntos")
    u, k = spec.get("unidad", ""), len(nombres)
    todos = [v for n in nombres for v in val[n]]
    vmin, vmax = min(todos), max(todos)
    ms = marcas_eje(0 if 0 <= vmin < (vmax - vmin) else vmin, vmax)
    izq, sup, ph = 56, 14, 240
    y = lambda v: sup + ph - (v - ms[0]) / (ms[-1] - ms[0]) * ph  # noqa: E731
    finales = sorted(y(val[n][-1]) for n in nombres)
    con_nombre = k >= 2 and all(b - a >= 15 for a, b in zip(finales, finales[1:]))  # si chocan, quedan la leyenda y el globo
    der = 16 + (max(ancho_texto(n, 12) for n in nombres) + 14 if con_nombre else (ancho_texto(num(val[nombres[0]][-1], u), 12) + 14 if k == 1 else 0))
    pw, alto = ANCHO - izq - der, sup + ph + 34
    x = lambda i: izq + i * pw / (len(cats) - 1)  # noqa: E731
    o = [f'<line class="grid" x1="{izq}" y1="{y(m):.1f}" x2="{izq + pw:.1f}" y2="{y(m):.1f}"/>'
         f'<text class="tick" x="{izq - 8}" y="{y(m) + 4:.1f}" text-anchor="end">{esc(compacto(m))}</text>' for m in ms]
    o.append(f'<line class="eje" x1="{izq}" y1="{sup + ph}" x2="{izq + pw:.1f}" y2="{sup + ph}"/>')
    for j, n in enumerate(nombres):
        puntos = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(val[n]))
        o.append(f'<polyline class="l{j + 1}" points="{puntos}"/>')
        xf, yf = x(len(cats) - 1), y(val[n][-1])
        o.append(f'<circle class="pt s{j + 1}" cx="{xf:.1f}" cy="{yf:.1f}" r="4"/>')
        if con_nombre:
            o.append(f'<text class="et" style="font-size:12px" x="{xf + 10:.1f}" y="{yf + 4:.1f}">{esc(n)}</text>')
        elif k == 1:
            o.append(f'<text class="val" x="{xf + 10:.1f}" y="{yf + 4:.1f}">{esc(num(val[n][-1], u))}</text>')
    cada = max(1, math.ceil(len(cats) / max(1, int(pw / 80))))
    medio = pw / (len(cats) - 1)
    for i, c in enumerate(cats):
        g = [f'<line class="cruz" x1="{x(i):.1f}" y1="{sup}" x2="{x(i):.1f}" y2="{sup + ph}"/>']
        g += [f'<circle class="pt pt-h s{j + 1}" cx="{x(i):.1f}" cy="{y(val[n][i]):.1f}" r="4"/>' for j, n in enumerate(nombres)]
        if i % cada == 0:
            g.append(f'<text class="tick" x="{x(i):.1f}" y="{sup + ph + 18}" text-anchor="middle">{esc(cortar(c, 80 * cada - 6))}</text>')
        tip = pista(c, [(n if k > 1 else "", num(val[n][i], u), j + 1) for j, n in enumerate(nombres)])
        g.append(f'<rect class="hit" tabindex="0" x="{x(i) - medio / 2:.1f}" y="{sup}" width="{medio:.1f}" height="{ph + 22}" data-tip="{tip}"/>')
        o.append(f'<g class="banda">{"".join(g)}</g>')
    svg = f'<svg viewBox="0 0 {ANCHO} {alto}" role="img" aria-label="{esc(spec.get("titulo") or "Gráfico de líneas")}">{"".join(o)}</svg>'
    tabla = tabla_datos([spec.get("categoria") or ""] + nombres, [[c] + [num(val[n][i], u) for n in nombres] for i, c in enumerate(cats)])
    return figura(spec, svg, leyenda(nombres, linea=True), tabla)


def g_tornado(spec, donde):
    datos = spec.get("datos")
    if not isinstance(datos, dict) or len(datos) < 2 or spec.get("base") is None:
        raise Problema(f"{donde}: un tornado necesita `base:` y al menos dos variables en `datos: {{variable: [resultado bajo, resultado alto]}}`")
    base, u = numero(spec["base"], donde), spec.get("unidad", "")
    filas = []
    for var, par in datos.items():
        par = [par.get("bajo"), par.get("alto")] if isinstance(par, dict) else list(par or [])
        if len(par) != 2:
            raise Problema(f"{donde}: «{var}» debe traer dos resultados: con el valor bajo y con el valor alto de la variable")
        filas.append((str(var), numero(par[0], donde), numero(par[1], donde)))
    filas.sort(key=lambda f: -abs(f[2] - f[1]))
    nombres = [str(s) for s in (spec.get("etiquetas") or ["Con el valor bajo de la variable", "Con el valor alto"])][:2]
    izq = min(220, max(70, max(ancho_texto(f[0]) for f in filas) + 14))
    borde, sup, banda, grosor = 62, 24, 34, 18
    alto, pw = sup + len(filas) * banda + 26, ANCHO - izq - 2 * borde
    ms = marcas_eje(min([base] + [min(f[1], f[2]) for f in filas]), max([base] + [max(f[1], f[2]) for f in filas]))
    x = lambda v: izq + borde + (v - ms[0]) / (ms[-1] - ms[0]) * pw  # noqa: E731
    o = [f'<line class="grid" x1="{x(m):.1f}" y1="{sup}" x2="{x(m):.1f}" y2="{alto - 24}"/>'
         f'<text class="tick" x="{x(m):.1f}" y="{alto - 8}" text-anchor="middle">{esc(compacto(m))}</text>' for m in ms]
    for i, (var, bajo, alto_v) in enumerate(filas):
        y0 = sup + i * banda
        g = [f'<text class="et" x="{izq - 10:.1f}" y="{y0 + banda / 2 + 4:.1f}" text-anchor="end">{esc(cortar(var, izq - 14, 13))}</text>']
        for j, v in enumerate((bajo, alto_v)):
            if v != base:
                g.append(f'<path class="m s{j + 1}" d="{barra_h(x(base), x(v), y0 + 8, grosor)}"/>')
                g.append(f'<text class="val" x="{x(v) + (6 if v > base else -6):.1f}" y="{y0 + 8 + grosor / 2 + 4:.1f}" '
                         f'text-anchor="{"start" if v > base else "end"}">{esc(num(v, u))}</text>')
        tip = pista(var, [(nombres[0], num(bajo, u), 1), (nombres[1], num(alto_v, u), 2), ("de amplitud", num(abs(alto_v - bajo), u), "")])
        g.append(f'<rect class="hit" tabindex="0" x="0" y="{y0}" width="{ANCHO}" height="{banda}" data-tip="{tip}"/>')
        o.append(f'<g class="banda">{"".join(g)}</g>')
    o.append(f'<line class="eje" x1="{x(base):.1f}" y1="{sup - 6}" x2="{x(base):.1f}" y2="{alto - 24}"/>'
             f'<text class="et" style="font-size:12px" x="{x(base):.1f}" y="{sup - 10}" text-anchor="middle">Base: {esc(num(base, u))}</text>')
    svg = f'<svg viewBox="0 0 {ANCHO} {alto}" role="img" aria-label="{esc(spec.get("titulo") or "Gráfico de tornado")}">{"".join(o)}</svg>'
    tabla = tabla_datos(["Variable"] + nombres + ["Amplitud"], [[v, num(b, u), num(a, u), num(abs(a - b), u)] for v, b, a in filas])
    nota = f"Ordenado de la variable que más mueve el resultado a la que menos. La que más pesa: <b>{esc(filas[0][0])}</b>."
    return figura(spec, svg, leyenda(nombres), tabla, nota)


def g_histograma(spec, donde):
    if isinstance(spec.get("clases"), dict):
        return fig_columnas({**spec, "datos": spec["clases"]}, donde)
    valores = sorted(numero(v, donde) for v in (spec.get("valores") or []))
    if len(valores) < 5:
        raise Problema(f"{donde}: un histograma necesita `valores: [...]` (al menos 5)")
    u, n = spec.get("unidad", ""), len(valores)
    bordes = marcas_eje(valores[0], valores[-1], int(spec.get("clases") or max(6, min(26, n // 5))))
    paso = bordes[1] - bordes[0]
    cuentas = [0] * (len(bordes) - 1)
    for v in valores:
        cuentas[min(len(cuentas) - 1, int((v - bordes[0]) / paso))] += 1
    meta = numero(spec["meta"], donde) if spec.get("meta") is not None else None
    mayor = not str(spec.get("sentido") or "mayor").strip().lower().startswith("men")
    clases = None
    if meta is not None:
        cumple = lambda i: (bordes[i] + paso / 2 >= meta) if mayor else (bordes[i] + paso / 2 <= meta)  # noqa: E731
        clases = ["s1" if cumple(i) else "sv" for i in range(len(cuentas))]
    etiquetas = [f"{num(bordes[i])} a {num(bordes[i + 1])}" for i in range(len(cuentas))]
    falso = {"titulo": spec.get("titulo"), "datos": dict(zip(etiquetas, cuentas)), "serie": "casos"}
    _, _, _, cuerpo, alto, (izq, der, sup, ph, pw) = g_columnas(falso, donde, clases=clases or ["s1"] * len(cuentas), etiquetas=False, aire=2)
    x = lambda v: izq + (v - bordes[0]) / (bordes[-1] - bordes[0]) * pw  # noqa: E731
    baja = 30 if spec.get("marcas") or meta is not None else 0  # espacio sobre el gráfico para rotular las marcas
    o = [cuerpo]
    cada = max(1, math.ceil(len(bordes) / 8))
    o += [f'<text class="tick" x="{x(b):.1f}" y="{sup + ph + 18}" text-anchor="middle">{esc(compacto(b))}</text>' for i, b in enumerate(bordes) if i % cada == 0]
    lineas = dict(spec.get("marcas") or {})
    if meta is not None:
        lineas = {**{"Meta": meta}, **lineas}
    for i, (nombre, v) in enumerate(lineas.items()):
        v = numero(v, donde)
        if bordes[0] <= v <= bordes[-1]:
            yt = -baja + 11 + (i % 2) * 14
            o.append(f'<line class="marca-l" x1="{x(v):.1f}" y1="{yt + 4}" x2="{x(v):.1f}" y2="{sup + ph}"/>'
                     f'<text class="et" style="font-size:12px" x="{x(v) + 5:.1f}" y="{yt + 4}">{esc(nombre)}: {esc(num(v, u))}</text>')
    svg = (f'<svg viewBox="0 0 {ANCHO} {alto + baja}" role="img" aria-label="{esc(spec.get("titulo") or "Histograma")}">'
           f'<g transform="translate(0,{baja})">{"".join(o)}</g></svg>')
    media = sum(valores) / n
    pct = lambda q: valores[min(n - 1, int(q * n))]  # noqa: E731
    nota = f"{num(n)} casos · promedio {esc(num(media, u))} · la mitad queda bajo {esc(num(pct(0.5), u))} · 8 de cada 10 entre {esc(num(pct(0.1), u))} y {esc(num(pct(0.9), u))}."
    ley = ""
    if meta is not None:
        prob = sum(1 for v in valores if (v >= meta if mayor else v <= meta)) / n
        ley = leyenda(["Cumple la meta", "No la cumple"], clases=["k1", "kv"])
        nota = (f"<b>Probabilidad de {'alcanzar o superar' if mayor else 'quedar en o bajo'} {esc(num(meta, u))}: "
                f"{num(prob * 100)} %</b> ({num(round(prob * n))} de {num(n)} casos). " + nota)
    tabla = tabla_datos(["Rango", "Casos", "% del total"], [[e, num(c), num(c / n * 100) + " %"] for e, c in zip(etiquetas, cuentas)])
    return figura(spec, svg, ley, tabla, nota)


GRAFICOS = {"barras": g_barras, "columnas": fig_columnas, "lineas": g_lineas, "líneas": g_lineas, "tornado": g_tornado, "histograma": g_histograma}


def bloque_grafico(texto, donde):
    import yaml
    try:
        spec = yaml.safe_load(texto) or {}
    except yaml.YAMLError as e:
        raise Problema(f"{donde}: el bloque no se puede leer ({str(e).splitlines()[0]})")
    if not isinstance(spec, dict):
        raise Problema(f"{donde}: el bloque debe ser una lista de claves (`tipo:`, `datos:`…)")
    tipo = str(spec.get("tipo") or "").strip().lower()
    if tipo not in GRAFICOS:
        raise Problema(f"{donde}: `tipo` debe ser uno de: barras, columnas, lineas, tornado, histograma")
    return GRAFICOS[tipo](spec, donde)


def partir_lineas(texto):
    filas = []
    for linea in texto.splitlines():
        if linea.strip():
            cab, _, resto = linea.partition(":")
            filas.append((cab.strip(), resto.strip()))
    return filas


def bloque_cifras(texto, donde):
    tarjetas = []
    for etiqueta, resto in partir_lineas(texto):
        valor, _, nota = resto.partition("|")
        tarjetas.append(f'<div class="cifra"><span>{inline(etiqueta)}</span><b>{inline(valor.strip())}</b>'
                        + (f"<small>{inline(nota.strip())}</small>" if nota.strip() else "") + "</div>")
    if not tarjetas:
        raise Problema(f"{donde}: un bloque `cifras` lleva una línea por cifra: `Etiqueta: valor | nota`")
    return f'<div class="cifras">{"".join(tarjetas)}</div>'


def bloque_pasos(texto, donde):
    pasos = [f"<li><b>{inline(t)}</b>{inline(d)}</li>" for t, d in partir_lineas(texto)]
    if not pasos:
        raise Problema(f"{donde}: un bloque `pasos` lleva una línea por paso: `Título: detalle`")
    return f'<ol class="pasos">{"".join(pasos)}</ol>'


def bloque_tiempo(texto, donde):
    hitos = []
    for cuando, que in partir_lineas(texto):
        try:
            f = datetime.strptime(cuando[:10], "%Y-%m-%d").date()
        except ValueError:
            raise Problema(f"{donde}: «{cuando}» no es una fecha AAAA-MM-DD")
        hitos.append((f, que))
    if not hitos:
        raise Problema(f"{donde}: un bloque `tiempo` lleva una línea por hito: `AAAA-MM-DD: qué pasa`")
    return '<ol class="tiempo">' + "".join(f'<li><time datetime="{f.isoformat()}">{f:%d-%m-%Y}</time><b>{inline(q)}</b></li>'
                                           for f, q in sorted(hitos)) + "</ol>"


BLOQUES = {"grafico": bloque_grafico, "gráfico": bloque_grafico, "cifras": bloque_cifras, "pasos": bloque_pasos, "tiempo": bloque_tiempo}


# ---------------------------------------------------------------------------------------------- Markdown
def inline(texto):
    t = esc(texto)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<![*\w])\*([^*\s][^*]*)\*(?![*\w])", r"<i>\1</i>", t)
    return re.sub(r"\[([^\]]+)\]\(((?:https?://|mailto:)[^)\s]+)\)", r'<a href="\2" rel="noopener">\1</a>', t)


def celda(texto):
    t = texto.strip()
    if t.lower() in ("verde", "amarillo", "rojo"):
        return f'<span class="est est-{t.lower()}"><i></i>{esc(t)}</span>'
    return inline(t)


def imagen(alt, ruta, base, n):
    p = (base / ruta).resolve()
    if not p.is_file():
        raise Problema(f"no existe la imagen «{ruta}» (se busca junto al Markdown)")
    if p.suffix.lower() not in MIME:
        raise Problema(f"la imagen «{ruta}» debe ser png, jpg, gif o svg")
    if p.stat().st_size > 3_000_000:
        raise Problema(f"la imagen «{ruta}» pesa más de 3 MB: redúcela antes de incluirla")
    datos = base64.b64encode(p.read_bytes()).decode("ascii")
    return (f'<figure class="img"><img alt="{esc(alt)}" src="data:{MIME[p.suffix.lower()]};base64,{datos}">'
            f"<figcaption>Figura {n}. {inline(alt)}</figcaption></figure>")


def encabezado(md):
    """(datos del bloque inicial `---`, resto del Markdown)."""
    m = re.match(r"\A\s*---\s*\n(.*?)\n---\s*\n", md, re.S)
    if not m:
        return {}, md
    datos = {}
    for linea in m.group(1).splitlines():
        k = re.match(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$", linea)
        if k:
            datos[k.group(1)] = k.group(2).strip().strip("\"'")
    return datos, md[m.end():]


def convertir(md, base, con_titulo=False):
    """(html del cuerpo, título) desde el Markdown. El primer `#` es el título de la página, salvo que el bloque inicial
    ya traiga uno (`con_titulo`): entonces todos los títulos bajan un nivel."""
    lineas, o, i, titulo, n_bloque, n_fig = md.splitlines(), [], 0, "", 0, 0
    parrafo = []

    def cerrar():
        if parrafo:
            o.append("<p>" + inline(" ".join(parrafo)) + "</p>")
            parrafo.clear()

    while i < len(lineas):
        linea = lineas[i]
        s = linea.strip()
        cerca = re.match(r"^```\s*([\wáéíóú]*)\s*$", s)
        if cerca:
            cerrar()
            nombre, cuerpo, i = cerca.group(1).lower(), [], i + 1
            while i < len(lineas) and not lineas[i].strip().startswith("```"):
                cuerpo.append(lineas[i])
                i += 1
            n_bloque += 1
            texto = "\n".join(cuerpo)
            o.append(BLOQUES[nombre](texto, f"bloque {n_bloque} (`{nombre}`)") if nombre in BLOQUES else f"<pre>{esc(texto)}</pre>")
        elif not s:
            cerrar()
        elif re.match(r"^#{1,3}\s+", s):
            cerrar()
            nivel, texto = len(s) - len(s.lstrip("#")), s.lstrip("#").strip()
            if nivel == 1 and not con_titulo and not titulo:
                titulo = texto
            else:
                h = min(3, nivel + 1) if con_titulo else max(2, nivel)
                o.append(f"<h{h}>{inline(texto)}</h{h}>")
        elif s.startswith("|"):
            cerrar()
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                filas.append([c for c in lineas[i].strip().strip("|").split("|")])
                i += 1
            i -= 1
            cuerpo = [f for f in filas if not all(re.fullmatch(r"\s*:?-{2,}:?\s*", c) for c in f)]
            if cuerpo:
                cab = "".join(f"<th>{inline(c.strip())}</th>" for c in cuerpo[0])
                resto = "".join("<tr>" + "".join(f"<td>{celda(c)}</td>" for c in f) + "</tr>" for f in cuerpo[1:])
                o.append(f'<div class="tabla"><table><thead><tr>{cab}</tr></thead><tbody>{resto}</tbody></table></div>')
        elif re.match(r"^([-*]|\d+[.)])\s+", s):
            cerrar()
            ordenada, items = bool(re.match(r"^\d", s)), []
            while i < len(lineas) and re.match(r"^([-*]|\d+[.)])\s+", lineas[i].strip()):
                items.append(re.sub(r"^([-*]|\d+[.)])\s+", "", lineas[i].strip()))
                i += 1
            i -= 1
            o.append(f"<{'ol' if ordenada else 'ul'}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{'ol' if ordenada else 'ul'}>")
        elif s.startswith(">"):
            cerrar()
            cita = []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                cita.append(lineas[i].strip().lstrip(">").strip())
                i += 1
            i -= 1
            o.append("<aside>" + inline(" ".join(cita)) + "</aside>")
        elif re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", s):
            cerrar()
            m = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", s)
            n_fig += 1
            o.append(imagen(m.group(1), m.group(2), base, n_fig))
        else:
            parrafo.append(s)
        i += 1
    cerrar()
    return "\n".join(o), titulo


def pagina(cuerpo, titulo, subtitulo, cfg, raiz_proyecto, hoy):
    fmt = cfg.get("formato") or {}
    marca = re.sub(r"[^0-9a-fA-F]", "", str(fmt.get("color_primario") or "1F3864"))[:6] or "1F3864"
    autor = ((cfg.get("autoria") or {}).get("nombre") or (cfg.get("responsable") or {}).get("nombre") or "").strip()
    logo = ""
    ruta_logo = fmt.get("logo")
    if ruta_logo and raiz_proyecto:
        p = Path(ruta_logo) if Path(str(ruta_logo)).is_absolute() else Path(raiz_proyecto) / str(ruta_logo)
        if p.is_file() and p.suffix.lower() in MIME and p.stat().st_size < 600_000:
            logo = f'<img alt="" src="data:{MIME[p.suffix.lower()]};base64,{base64.b64encode(p.read_bytes()).decode("ascii")}">'
    pie = " · ".join(x for x in (str(fmt.get("pie_de_pagina") or "").strip(), autor, f"{hoy:%d-%m-%Y}") if x)
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(titulo)}</title>' + (f'<meta name="author" content="{esc(autor)}">' if autor else "")
            + f'<style>{CSS.replace("#MARCA", "#" + marca)}</style></head><body>{TEXTURAS}<main><header>{logo}<h1>{esc(titulo)}</h1>'
            + (f'<p class="sub">{inline(subtitulo)}</p>' if subtitulo else "") + f"</header>\n{cuerpo}\n<footer>{esc(pie)}</footer></main>"
            f"<script>{JS}</script></body></html>\n")


def generar(md, base, cfg=None, raiz_proyecto=None, hoy=None, borrador=False):
    """El HTML completo y su título. Lanza Problema si el Markdown no se puede convertir."""
    if "[PENDIENTE" in md and not borrador:
        raise Problema("el texto tiene marcadores [PENDIENTE: …]: complétalos, o usa --borrador para una página de uso interno")
    datos, resto = encabezado(md)
    cuerpo, titulo_md = convertir(resto, Path(base), con_titulo=bool(datos.get("titulo")))
    titulo = datos.get("titulo") or titulo_md or "Explicación"
    hoy = hoy or date.today()
    if datos.get("fecha"):
        try:
            hoy = datetime.strptime(datos["fecha"][:10], "%Y-%m-%d").date()
        except ValueError:
            pass
    return pagina(cuerpo, titulo, datos.get("subtitulo") or "", cfg or {}, raiz_proyecto, hoy), titulo


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("--proyecto", help="carpeta del proyecto (marca, autoría y carpeta de salida)")
    ap.add_argument("--salida", help="ruta del .html (por defecto, <proyecto>/explicaciones/<fecha>-<titulo>.html o junto al Markdown)")
    ap.add_argument("--abrir", action="store_true", help="abrir la página en el navegador")
    ap.add_argument("--borrador", action="store_true", help="permitir marcadores [PENDIENTE] (uso interno)")
    ap.add_argument("--hoy", help="fecha AAAA-MM-DD (pruebas)")
    a = ap.parse_args()
    entrada = Path(a.entrada)
    if not entrada.is_file():
        sys.exit(f"No existe {a.entrada}")
    cfg, raiz_proyecto = {}, None
    if a.proyecto:
        import _config
        raiz_proyecto = Path(a.proyecto)
        if not (raiz_proyecto / "proyecto.yaml").exists():
            sys.exit(f"{a.proyecto} no es un proyecto (falta proyecto.yaml)")
        cfg = _config.cargar(raiz_proyecto)
    hoy = datetime.strptime(a.hoy, "%Y-%m-%d").date() if a.hoy else date.today()
    try:
        pagina_html, titulo = generar(entrada.read_text(encoding="utf-8-sig"), entrada.parent, cfg, raiz_proyecto, hoy, a.borrador)
    except Problema as e:
        sys.exit(f"No se generó la página: {e}")
    if a.salida:
        salida = Path(a.salida)
    elif raiz_proyecto:
        salida = raiz_proyecto / "explicaciones" / f"{hoy.isoformat()}-{slug(titulo)}.html"
    else:
        salida = entrada.with_suffix(".html")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(pagina_html, encoding="utf-8")
    print(f"Página generada: {salida.as_posix()} ({salida.stat().st_size // 1024 + 1} KB, un solo archivo; se abre con doble clic)")
    if a.abrir:
        webbrowser.open(salida.resolve().as_uri())
    return 0


if __name__ == "__main__":
    import _consola
    _consola.preparar()
    sys.exit(main())
