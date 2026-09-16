# -*- coding: utf-8 -*-
"""
MANUAL DE MONTAGEM - Collar Console
Gera hardware/MANUAL-MONTAGEM.pdf

Filosofia: Silencio Isometrico (ver FILOSOFIA-DE-DESIGN.md)
  - projecao axonometrica isometrica, 30 graus, sem excecao
  - tres valores por solido: face superior clara, frontal media, lateral escura
  - grafite sobre papel frio; um unico acento, reservado ao gesto ativo
  - numerais condensados monumentais + anotacao monoespacada minima
  - margem inviolavel: toda cena e enquadrada por calculo, nunca por tentativa
"""
import math, os
from reportlab.pdfgen import canvas as rlcanvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONTS = (r"C:\Users\ramal\AppData\Roaming\Claude\local-agent-mode-sessions\skills-plugin"
         r"\08807779-30c8-4af7-b924-220b71af157e\e740342e-a2a5-48a4-880b-2737085f46d3"
         r"\skills\canvas-design\canvas-fonts")
for alias, fn in [("Big", "BigShoulders-Bold.ttf"), ("Sans", "InstrumentSans-Regular.ttf"),
                  ("SansB", "InstrumentSans-Bold.ttf"), ("Mono", "GeistMono-Regular.ttf"),
                  ("MonoB", "GeistMono-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(alias, os.path.join(FONTS, fn)))

PAPER = (0.949, 0.953, 0.945)
INK   = (0.086, 0.098, 0.106)
SOFT  = (0.365, 0.392, 0.404)
RULE  = (0.765, 0.784, 0.773)
FAINT = (0.878, 0.890, 0.878)
ROSA  = (1.000, 0.176, 0.471)

W, H = A4
ML, MR, MT, MB = 18*mm, 18*mm, 16*mm, 15*mm
CW = W - ML - MR
FOOT = MB + 16          # nada de conteudo abaixo desta linha

def g(v):
    v = max(0.0, min(1.0, v)); return (v, v, v)

# ---------------------------------------------------------------- isometria
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))

def projector(ox, oy, s):
    def P(x, y, z):
        return (ox + (x - y) * C30 * s, oy + ((x + y) * S30 + z) * s)
    return P

class _NullPath:
    def __getattr__(self, n): return lambda *a, **k: None

class _NullCanvas:
    """Canvas mudo: aceita qualquer chamada e nao desenha nada.
    Serve para percorrer uma cena so para medir seus limites reais."""
    def beginPath(self): return _NullPath()
    def __getattr__(self, n): return lambda *a, **k: None

def scene_bounds(draw):
    """Limites projetados reais da cena, colhidos ponto a ponto.
    Caixas de contorno declaradas a mao mentem: seus cantos sao espaco vazio."""
    pts = []
    def P(x, y, z):
        q = ((x - y)*C30, (x + y)*S30 + z); pts.append(q); return q
    draw(_NullCanvas(), P)
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    return min(xs), max(xs), min(ys), max(ys)

def fit(rect, draw, fill=0.94, anchor="center"):
    """Enquadra a cena medida dentro do retangulo. Devolve (projetor, altura usada)."""
    x0, x1, y0, y1 = scene_bounds(draw)
    rx, ry, rw, rh = rect
    s = min(rw/max(x1-x0, 1e-6), rh/max(y1-y0, 1e-6))*fill
    oy = (ry + rh - y1*s) if anchor == "top" else (ry + rh/2 - (y0+y1)/2*s)
    ox = rx + rw/2 - (x0+x1)/2*s
    used = (ox + x0*s, oy + y0*s, (x1-x0)*s, (y1-y0)*s)
    return projector(ox, oy, s), used

def poly(c, P, pts3, fill=None, stroke=INK, lw=0.5):
    p = c.beginPath()
    x0, y0 = P(*pts3[0]); p.moveTo(x0, y0)
    for q in pts3[1:]:
        x, y = P(*q); p.lineTo(x, y)
    p.close()
    if fill: c.setFillColorRGB(*fill)
    if stroke: c.setStrokeColorRGB(*stroke); c.setLineWidth(lw)
    c.drawPath(p, stroke=1 if stroke else 0, fill=1 if fill else 0)

def box(c, P, x, y, z, dx, dy, dz, v=0.60, lw=0.45, edge=INK):
    poly(c, P, [(x, y, z), (x, y+dy, z), (x, y+dy, z+dz), (x, y, z+dz)], g(v-0.15), edge, lw)
    poly(c, P, [(x, y, z), (x+dx, y, z), (x+dx, y, z+dz), (x, y, z+dz)], g(v), edge, lw)
    poly(c, P, [(x, y, z+dz), (x+dx, y, z+dz), (x+dx, y+dy, z+dz), (x, y+dy, z+dz)],
         g(v+0.19), edge, lw)

def helix(c, P, cx, cy, z0, r, turns, pitch, col=g(0.50), lw=1.5):
    n = int(turns*26); pth = c.beginPath()
    for i in range(n+1):
        t = i/26.0*2*math.pi
        px, py = P(cx + r*math.cos(t), cy + r*math.sin(t), z0 + pitch*i/26.0)
        (pth.moveTo if i == 0 else pth.lineTo)(px, py)
    c.setStrokeColorRGB(*col); c.setLineWidth(lw); c.setLineCap(1)
    c.drawPath(pth, stroke=1, fill=0)

def wire(c, P, a, b, col=ROSA, lw=1.8, sag=10):
    x1, y1 = P(*a); x2, y2 = P(*b)
    c.setStrokeColorRGB(*col); c.setLineWidth(lw); c.setLineCap(1)
    p = c.beginPath(); p.moveTo(x1, y1)
    p.curveTo(x1+(x2-x1)*0.28, y1-sag, x1+(x2-x1)*0.72, y2-sag, x2, y2)
    c.drawPath(p, stroke=1, fill=0)

def leader(c, P, anchor3, lx, ly, label, sub=None, side="r"):
    ax, ay = P(*anchor3)
    c.setStrokeColorRGB(*INK); c.setLineWidth(0.4)
    elbow = lx + 7 if side == "r" else lx - 7
    p = c.beginPath(); p.moveTo(ax, ay); p.lineTo(elbow, ly + 2.0); p.lineTo(lx, ly + 2.0)
    c.drawPath(p, stroke=1, fill=0)
    c.setFillColorRGB(*INK); c.circle(ax, ay, 1.15, stroke=0, fill=1)
    c.setFont("MonoB", 6.6); c.setFillColorRGB(*INK)
    (c.drawString if side == "r" else c.drawRightString)(lx + (3 if side == "r" else -3), ly, label)
    if sub:
        c.setFont("Mono", 5.4); c.setFillColorRGB(*SOFT)
        (c.drawString if side == "r" else c.drawRightString)(
            lx + (3 if side == "r" else -3), ly - 5.4, sub)

# ---------------------------------------------------------------- tipografia
def wrap(txt, font, size, width):
    out, line = [], ""
    for w_ in txt.split():
        t = (line + " " + w_).strip()
        if pdfmetrics.stringWidth(t, font, size) <= width: line = t
        else: out.append(line); line = w_
    if line: out.append(line)
    return out

def para(c, x, y, width, txt, font="Sans", size=8.0, lead=10.8, col=INK):
    c.setFont(font, size); c.setFillColorRGB(*col)
    for ln in wrap(txt, font, size, width):
        c.drawString(x, y, ln); y -= lead
    return y + lead

def hrule(c, x, y, w_, col=RULE, lw=0.5):
    c.setStrokeColorRGB(*col); c.setLineWidth(lw); c.line(x, y, x + w_, y)

def notes_h(blocks, size=8.0, lead=10.8):
    gap = 7*mm; cw = (CW - gap*(len(blocks)-1))/len(blocks)
    return 22 + max(len(wrap(b, "Sans", size, cw)) for _, b in blocks)*lead

def notes(c, ytop, blocks, size=8.0, lead=10.8):
    gap = 7*mm; cw = (CW - gap*(len(blocks)-1))/len(blocks)
    for i, (t, body) in enumerate(blocks):
        x = ML + i*(cw + gap)
        c.setStrokeColorRGB(*ROSA); c.setLineWidth(1.7); c.line(x, ytop+1, x+12, ytop+1)
        c.setFont("MonoB", 6.4); c.setFillColorRGB(*INK); c.drawString(x, ytop-10, t.upper())
        para(c, x, ytop-22, cw, body, "Sans", size, lead)
    return ytop - notes_h(blocks, size, lead)

# ---------------------------------------------------------------- pecas
def esp32(c, P, ox=0, oy=0, oz=0, hot=None, side=0):
    box(c, P, ox, oy, oz, 48, 25.5, 1.6, v=0.30)
    box(c, P, ox+3, oy+0.6, oz+1.6, 18, 24.3, 3.1, v=0.70)
    box(c, P, ox+23.5, oy+9.5, oz+1.6, 5.5, 6.5, 1.1, v=0.44)
    box(c, P, ox+45.4, oy+9, oz+1.6, 5.2, 7.5, 2.7, v=0.74)
    box(c, P, ox+33, oy+1.4, oz+1.6, 4, 3.4, 2.2, v=0.40)
    box(c, P, ox+33, oy+20.7, oz+1.6, 4, 3.4, 2.2, v=0.40)
    for sy in (oy+0.2, oy+22.8):
        box(c, P, ox+5.6, sy, oz+1.6, 38.1, 2.54, 2.4, v=0.16)
    for i in range(15):
        for k, sy in enumerate((oy+1.2, oy+23.8)):
            on = hot and (k == side) and (i in hot)
            box(c, P, ox+6.9+i*2.54, sy, oz+4.0, 0.7, 0.7, 1.9,
                v=0.88 if on else 0.62, lw=0.3, edge=ROSA if on else INK)

def fs1000a(c, P, ox=0, oy=0, oz=0, hot=False):
    box(c, P, ox, oy, oz, 19, 19, 1.5, v=0.34)
    box(c, P, ox+6.5, oy+7, oz+1.5, 6.2, 3.2, 1.9, v=0.76)
    box(c, P, ox+3.2, oy+13, oz+1.5, 2.6, 2.4, 1.3, v=0.46)
    box(c, P, ox+13.5, oy+13.4, oz+1.5, 2.2, 2.0, 0.9, v=0.46)
    box(c, P, ox+4.9, oy+0.4, oz+1.5, 7.62, 2.54, 2.3, v=0.16)
    for i in range(3):
        box(c, P, ox+5.8+i*2.54, oy+1.3, oz+3.8, 0.7, 0.7, 1.9,
            v=0.88 if hot else 0.62, lw=0.3, edge=ROSA if hot else INK)

def rxb6(c, P, ox=0, oy=0, oz=0, hot=False):
    box(c, P, ox, oy, oz, 43, 11.5, 1.5, v=0.34)
    box(c, P, ox+4, oy+4.2, oz+1.5, 11, 5.4, 2.6, v=0.70)
    box(c, P, ox+18.5, oy+4.6, oz+1.5, 5.2, 3.0, 2.2, v=0.76)
    box(c, P, ox+27, oy+4.8, oz+1.5, 3.2, 3.0, 3.0, v=0.50)
    box(c, P, ox+33.5, oy+5.2, oz+1.5, 2.4, 2.2, 1.0, v=0.46)
    box(c, P, ox+2.2, oy+0.3, oz+1.5, 20.32, 2.54, 2.3, v=0.16)
    for i in range(8):
        box(c, P, ox+3.1+i*2.54, oy+1.2, oz+3.8, 0.7, 0.7, 1.9,
            v=0.88 if hot else 0.62, lw=0.3, edge=ROSA if hot else INK)

def antena(c, P, cx, cy, z0, col=g(0.50)):
    x1, y1 = P(cx, cy, z0-3.4); x2, y2 = P(cx, cy, z0)
    c.setStrokeColorRGB(*col); c.setLineWidth(1.5); c.line(x1, y1, x2, y2)
    helix(c, P, cx, cy, z0, 2.3, 13, 1.5, col)

def jumper_pair(c, P, a, b, col=ROSA, sag=11):
    for pt in (a, b):
        box(c, P, pt[0]-1.3, pt[1]-1.3, pt[2], 2.6, 2.6, 5.2, v=0.18, lw=0.35)
    wire(c, P, (a[0], a[1], a[2]+5.2), (b[0], b[1], b[2]+5.2), col, 1.8, sag)

def coleira(c, P, ox=0, oy=0, oz=0):
    box(c, P, ox, oy+7, oz, 62, 5.5, 2.2, v=0.22)
    box(c, P, ox+22, oy+2.5, oz+2.2, 20, 15, 7.5, v=0.66)
    box(c, P, ox+27, oy+5.5, oz+9.7, 9, 9, 0.9, v=0.80)
    box(c, P, ox+75, oy+1, oz, 17, 18, 34, v=0.72)
    box(c, P, ox+78, oy+0.6, oz+22, 11, 1.2, 8, v=0.14)
    box(c, P, ox+80.5, oy+0.6, oz+13, 6, 1.2, 5, v=0.30)

def cabo_usb(c, P, ox, oy, oz):
    box(c, P, ox, oy, oz, 12, 9, 4.5, v=0.20)
    box(c, P, ox+12, oy+2.6, oz+1.1, 5, 3.8, 2.2, v=0.74)
    x1, y1 = P(ox, oy+4.5, oz+2.2); x2, y2 = P(ox-36, oy+4.5, oz+2.2)
    c.setStrokeColorRGB(*g(0.28)); c.setLineWidth(2.2); c.setLineCap(1)
    p = c.beginPath(); p.moveTo(x1, y1)
    p.curveTo(x1-15, y1-10, x2+17, y2+8, x2, y2)
    c.drawPath(p, stroke=1, fill=0)

# ---------------------------------------------------------------- chrome
def bg(c):
    c.setFillColorRGB(*PAPER); c.rect(0, 0, W, H, stroke=0, fill=1)

def footer(c, n, total, right=""):
    hrule(c, ML, MB + 7, CW, FAINT)
    c.setFont("Mono", 5.8); c.setFillColorRGB(*SOFT)
    c.drawString(ML, MB, "COLLAR CONSOLE  /  MANUAL DE MONTAGEM  /  RADIO 433,92 MHZ")
    if right: c.drawCentredString(W/2 + 20, MB, right)
    c.setFont("MonoB", 5.8); c.setFillColorRGB(*INK)
    c.drawRightString(W - MR, MB, "%02d / %02d" % (n, total))

def head(c, num, title, sub, code):
    """Cabecalho. num=None para paginas sem etapa. Devolve a base da banda util."""
    top = H - MT
    x = ML
    if num is not None:
        c.setFont("Big", 46); c.setFillColorRGB(*INK)
        c.drawString(ML, top - 34, "%02d" % num)
        nw = pdfmetrics.stringWidth("%02d" % num, "Big", 46)
        c.setStrokeColorRGB(*ROSA); c.setLineWidth(2.2)
        c.line(ML, top - 40, ML + nw, top - 40)
        x = ML + nw + 12
    else:
        c.setStrokeColorRGB(*ROSA); c.setLineWidth(2.6); c.line(ML, top - 9, ML + 26, top - 9)
        x = ML + 36
    c.setFont("SansB", 13.5); c.setFillColorRGB(*INK)
    c.drawString(x, top - 14, title)
    c.setFont("Sans", 8.4); c.setFillColorRGB(*SOFT)
    for i, ln in enumerate(wrap(sub, "Sans", 8.4, CW - (x - ML) - 34*mm)):
        c.drawString(x, top - 26 - i*10.4, ln)
    c.setFont("Mono", 6.0); c.setFillColorRGB(*SOFT)
    c.drawRightString(W - MR, top - 14, code)
    base = top - 48
    hrule(c, ML, base, CW, RULE, 0.7)
    return base

def table(c, ytop, heads, rows, cols, accent_last=False):
    IND = 11
    c.setFont("MonoB", 6.2); c.setFillColorRGB(*SOFT)
    for lbl, off in zip(heads, cols):
        c.drawString(ML + IND + off, ytop + 10, lbl)
    hrule(c, ML, ytop + 5, CW, RULE)
    for i, r in enumerate(rows):
        yy = ytop - 7 - i*13.2
        c.setFillColorRGB(*ROSA); c.circle(ML + 2.4, yy + 2.6, 1.7, stroke=0, fill=1)
        for j, cell in enumerate(r):
            last = (j == len(r) - 1)
            if last and accent_last:
                c.setFont("MonoB", 6.6); c.setFillColorRGB(*ROSA)
            elif j >= 2:
                c.setFont("Sans", 8.0); c.setFillColorRGB(*SOFT)
            else:
                c.setFont("SansB", 8.6); c.setFillColorRGB(*INK)
            c.drawString(ML + IND + cols[j], yy, cell)
        hrule(c, ML, yy - 4.6, CW, FAINT)
    return ytop - 7 - len(rows)*13.2 - 6

# ---------------------------------------------------------------- paginas
def p_capa(c, total):
    bg(c)
    c.setFont("Mono", 6.2); c.setFillColorRGB(*SOFT)
    c.drawString(ML, H - MT - 4, "C O L L A R   C O N S O L E")
    c.drawRightString(W - MR, H - MT - 4, "ED. 01  /  2026")
    hrule(c, ML, H - MT - 12, CW, INK, 1.0)
    c.setFont("Big", 72); c.setFillColorRGB(*INK)
    c.drawString(ML, H - MT - 74, "MANUAL DE")
    c.drawString(ML, H - MT - 128, "MONTAGEM")
    c.setStrokeColorRGB(*ROSA); c.setLineWidth(3)
    c.line(ML, H - MT - 140, ML + 92, H - MT - 140)
    c.setFont("Sans", 9.6); c.setFillColorRGB(*SOFT)
    c.drawString(ML, H - MT - 157,
                 "Ponte de radio 433,92 MHz  ·  ESP32  ·  seis fios  ·  nenhum ponto de solda")

    stats_y = FOOT + 34
    band = (ML + 9*mm, stats_y + 30, CW - 18*mm, (H - MT - 180) - (stats_y + 30))
    def cena(c, P):
        esp32(c, P, 0, 0, 0)
        fs1000a(c, P, -24, 18, 17); antena(c, P, -24+16, 18+16, 18.5)
        rxb6(c, P, 26, -20, 15); antena(c, P, 26+39, -20+6, 16.5)
        for i in range(3):
            wire(c, P, (-24+5.8+i*2.54, 18+1.3, 18.5), (6.9+(i+2)*2.54, 1.2, 5.9), g(0.60), 0.9, 8)
            wire(c, P, (26+3.1+i*2.54, -20+1.2, 16.5), (6.9+(i+2)*2.54, 23.8, 5.9), g(0.60), 0.9, 8)
    P, art = fit(band, cena, 0.99)
    cena(c, P)
    lxl, lxr = art[0] - 8, art[0] + art[2] + 8
    leader(c, P, (26, 12, 4.7), lxl, art[1] + art[3]*0.16, "A", "ESP32", "r")
    leader(c, P, (-24+9, 18+9, 18.5), lxl, art[1] + art[3]*0.62, "B", "FS1000A", "r")
    leader(c, P, (26+20, -20+6, 16.5), lxr, art[1] + art[3]*0.20, "C", "RXB6", "l")
    leader(c, P, (-24+16, 18+16, 18.5+19), lxl, art[1] + art[3]*0.92, "D", "ANTENA", "r")

    hrule(c, ML, stats_y + 16, CW, RULE)
    for i, (k, v) in enumerate([("PECAS", "07"), ("FIOS", "06"), ("SOLDA", "00"), ("TEMPO", "25 MIN")]):
        x = ML + i*(CW/4)
        c.setFont("Mono", 5.8); c.setFillColorRGB(*SOFT); c.drawString(x, stats_y + 6, k)
        c.setFont("Big", 21); c.setFillColorRGB(*INK); c.drawString(x, stats_y - 12, v)
    footer(c, 1, total, "CAPA")

def p_pecas(c, total):
    bg(c)
    y0 = head(c, None, "Conteudo da caixa",
              "Confira todas as pecas antes de comecar. Cada uma recebe um codigo "
              "usado nas etapas seguintes.", "INVENTARIO")
    items = [
        ("A", "Placa ESP32 DevKit", "30 pinos, soldados", "1", "R$ 35,88",
         lambda c, P: esp32(c, P)),
        ("B", "Transmissor FS1000A", "433 MHz, 3 pinos", "1", "R$ 20,90",
         lambda c, P: fs1000a(c, P)),
        ("C", "Receptor RXB6", "super-heterodino", "1", "R$ 35,05",
         lambda c, P: rxb6(c, P)),
        ("D", "Antena helicoidal", "SW433-TH22", "2", "R$ 25,78",
         lambda c, P: (antena(c, P, 0, 0, 3), antena(c, P, 15, 15, 3))),
        ("E", "Jumper femea-femea", "40 unidades", "6", "R$ 17,97",
         lambda c, P: (jumper_pair(c, P, (0, 0, 0), (28, 2, 0), g(0.38), 12),
                       jumper_pair(c, P, (0, 12, 0), (28, 14, 0), g(0.58), 12))),
        ("F", "Cabo micro USB", "de dados, 1,5 m", "1", "a comprar",
         lambda c, P: cabo_usb(c, P, 0, 0, 0)),
        ("G", "Coleira e controle", "PuPoPan, 0 a 99", "1", "R$ 74,44",
         lambda c, P: coleira(c, P)),
    ]
    cellw = CW/2 - 5*mm
    cellh = (y0 - FOOT - 6) / 4
    for i, (code, nome, det, qtd, preco, draw) in enumerate(items):
        cx = ML + (i % 2)*(CW/2)
        cy = y0 - 8 - (i//2)*cellh
        c.setStrokeColorRGB(*FAINT); c.setLineWidth(0.5)
        c.rect(cx, cy - cellh + 8, cellw, cellh - 10, stroke=1, fill=0)
        c.setFont("Big", 17); c.setFillColorRGB(*ROSA); c.drawString(cx + 7, cy - 19, code)
        c.setFont("SansB", 8.6); c.setFillColorRGB(*INK); c.drawString(cx + 22, cy - 17, nome)
        c.setFont("Mono", 5.8); c.setFillColorRGB(*SOFT); c.drawString(cx + 22, cy - 26, det.upper())
        c.setFont("MonoB", 6.4); c.setFillColorRGB(*INK)
        c.drawRightString(cx + cellw - 7, cy - 17, "x" + qtd)
        c.setFont("Mono", 5.6); c.setFillColorRGB(*SOFT)
        c.drawRightString(cx + cellw - 7, cy - 26, preco.upper())
        draw(c, fit((cx + 8, cy - cellh + 14, cellw - 16, cellh - 48), draw, 0.90)[0])
    footer(c, 2, total, "PECAS")

def _step(c, n, total, num, title, sub, code, draw, tbl=None, blocks=None, foot=""):
    """Tres blocos: cena, tabela, notas. As notas ficam ancoradas embaixo; a folga
    que sobra e repartida em partes iguais entre os blocos, nunca num vao unico."""
    bg(c)
    y0 = head(c, num, title, sub, code)
    H_NOT = notes_h(blocks) if blocks else 0
    H_TAB = (15 + len(tbl[1])*13.2) if tbl else 0
    top, ny = y0 - 12, FOOT + 8 + (notes_h(blocks) if blocks else 0)
    reserve = ny + H_TAB + (24 if tbl else 0)
    band = (ML, reserve, CW, top - reserve)
    P, used = fit(band, lambda cc, PP: draw(cc, PP, (0, 0, 1, 1)), 0.94, "top")
    art_h = used[3]
    n_gaps = 2 if tbl else 1
    slack = max(0.0, (top - ny) - art_h - H_TAB)
    gap = min(76.0, slack / n_gaps)
    # a cena desce metade da folga que lhe cabe, para nao colar no cabecalho
    drop = (slack - gap*n_gaps) / 2.0
    P, used = fit((band[0], band[1], band[2], band[3] - drop), 
                  lambda cc, PP: draw(cc, PP, (0, 0, 1, 1)), 0.94, "top")
    draw(c, P, used)
    if tbl:
        table(c, used[1] - gap - 15, tbl[0], tbl[1], tbl[2])
    if blocks:
        notes(c, ny, blocks)
    footer(c, n, total, foot)

def p_etapa1(c, total):
    def draw(c, P, band):
        # ordem de profundidade: maior x+y esta atras e e pintado primeiro
        rxb6(c, P, 38, -8, 0); antena(c, P, 38+39, -8+6, 1.5)
        fs1000a(c, P, 0, 0, 0); antena(c, P, 16, 16, 1.5)
        leader(c, P, (16, 16, 21), ML, band[1] + band[3]*0.90, "D", "ANTENA", "r")
        leader(c, P, (9, 9, 1.5), ML, band[1] + band[3]*0.30, "B", "FS1000A", "r")
        leader(c, P, (38+20, -8+6, 1.5), W - MR, band[1] + band[3]*0.24, "C", "RXB6", "l")
    _step(c, 3, total, 1, "Encaixar as antenas",
          "Sem antena o alcance cai para um ou dois metros. Cada modulo de radio leva a sua.",
          "D  ->  B, C", draw,
          blocks=[("O que fazer",
                   "Enfie a perna da antena helicoidal no furo marcado ANT de cada plaquinha. "
                   "Ela entra por pressao e fica firme sem solda. Deixe a mola reta e apontando "
                   "para cima."),
                  ("Atencao",
                   "Leia a serigrafia impressa na placa, nao conte a posicao do pino. O furo ANT "
                   "fica na borda oposta a barra de pinos. Uma antena por modulo, duas no total.")],
          foot="ETAPA 1 DE 5")

def p_etapa2(c, total):
    def draw(c, P, band):
        esp32(c, P, 0, 0, 0, hot={2, 3, 4}, side=0)
        fs1000a(c, P, -30, 24, 20); antena(c, P, -30+16, 24+16, 21.5)
        for i in range(3):
            jumper_pair(c, P, (-30+5.8+i*2.54, 24+1.3, 21.5), (6.9+(i+2)*2.54, 1.2, 5.9), ROSA, 12)
        leader(c, P, (-30+9, 24+1.3, 24), ML, band[1] + band[3]*0.70, "B", "FS1000A", "r")
        leader(c, P, (6.9+3*2.54, 1.2, 8), W - MR, band[1] + band[3]*0.20, "A", "ESP32  LADO DOS GPIO", "l")
    _step(c, 4, total, 2, "Ligar o transmissor",
          "Tres fios entre o FS1000A e a ESP32. Esta e a ligacao minima: com ela a coleira ja obedece.",
          "B  ->  A", draw,
          tbl=(["FS1000A", "ESP32", "FUNCAO"],
               [("VCC", "3V3", "alimentacao 3,3 V"), ("GND", "GND", "terra comum"),
                ("DATA", "GPIO 4", "sinal de radio")],
               [0, 40*mm, 80*mm]),
          blocks=[("O que fazer",
                   "Use tres jumpers femea-femea. Os dois lados tem pino macho, por isso o conector "
                   "de furo nas duas pontas encaixa direto, sem protoboard."),
                  ("Atencao",
                   "Comece pelo 3V3. Se o alcance ficar curto, mude so o VCC para o pino VIN de 5 V "
                   "e mantenha o DATA no GPIO 4. Nada de 5 V volta para a placa.")],
          foot="ETAPA 2 DE 5")

def p_etapa3(c, total):
    def draw(c, P, band):
        esp32(c, P, 0, 0, 0, hot={2, 3, 4}, side=1)
        rxb6(c, P, 4, -32, 20); antena(c, P, 4+39, -32+6, 21.5)
        for i in range(3):
            jumper_pair(c, P, (4+3.1+i*2.54, -32+1.2, 21.5), (6.9+(i+2)*2.54, 23.8, 5.9), ROSA, 12)
        leader(c, P, (4+20, -32+6, 22), W - MR, band[1] + band[3]*0.72, "C", "RXB6", "l")
        leader(c, P, (6.9+3*2.54, 23.8, 8), ML, band[1] + band[3]*0.24, "A", "ESP32  LADO OPOSTO", "r")
    _step(c, 5, total, 3, "Ligar o receptor",
          "Mais tres fios, do outro lado da placa. So e necessario se a coleira nao responder "
          "ao modo descoberta.",
          "C  ->  A", draw,
          tbl=(["RXB6", "ESP32", "FUNCAO"],
               [("VCC", "VIN (5 V)", "aceita de 3 a 5,5 V"), ("GND", "GND", "segundo pino de terra"),
                ("DATA", "GPIO 5", "captura do sinal")],
               [0, 40*mm, 80*mm]),
          blocks=[("O que fazer",
                   "O RXB6 tem oito pinos e voce usa tres. Alimente pelo VIN para nao disputar o "
                   "unico 3V3, que ja foi para o transmissor. O pino DER nao e usado."),
                  ("Atencao",
                   "O receptor de brinde do kit do FS1000A nao serve para capturar. Ele e "
                   "super-regenerativo e joga ruido continuo na saida mesmo sem sinal.")],
          foot="ETAPA 3 DE 5")

def p_etapa4(c, total):
    def draw(c, P, band):
        cabo_usb(c, P, 52.5, 9, 1.4)
        esp32(c, P, 0, 0, 0)
        fs1000a(c, P, -28, 22, 18); antena(c, P, -28+16, 22+16, 19.5)
        for i in range(3):
            jumper_pair(c, P, (-28+5.8+i*2.54, 22+1.3, 19.5), (6.9+(i+2)*2.54, 1.2, 5.9), g(0.52), 11)
        leader(c, P, (58, 13, 4), W - MR, band[1] + band[3]*0.26, "F", "MICRO USB DE DADOS", "l")
        leader(c, P, (24, 12, 4.7), ML, band[1] + band[3]*0.16, "A", "ESP32", "r")
    _step(c, 6, total, 4, "Energia e dados",
          "Um unico cabo liga tudo ao computador. Ele alimenta a placa, grava o firmware "
          "e leva os comandos.",
          "F  ->  A", draw,
          blocks=[("O que fazer",
                   "Ligue o cabo na ESP32 e numa porta USB do computador. O LED da placa acende e "
                   "no Windows aparece uma porta COM nova, por exemplo COM3."),
                  ("Se nao aparecer",
                   "Quase sempre e cabo so de carga, que nao transmite dados. Troque por um de "
                   "dados. Se ainda assim nada, instale o driver CH340 ou CP2102."),
                  ("Posicao",
                   "Deixe a placa sobre a mesa, com a antena para cima e longe do gabinete. "
                   "Caixa de metal bloqueia 433 MHz e derruba o alcance.")],
          foot="ETAPA 4 DE 5")

def p_etapa5(c, total):
    bg(c)
    y0 = head(c, 5, "Parear a coleira",
              "O modo descoberta percorre os cinco protocolos conhecidos emitindo apenas bipe. "
              "Nenhum choque envolvido.", "A  ->  G")
    blocks = [("Se nenhum responder",
               "A coleira e de uma familia ainda nao documentada. Ai entra o RXB6: capture um "
               "quadro do controle original e decodifique com o mapa da pagina 8."),
              ("Manter o controle original",
               "Em vez de inventar um identificador, capture o do controle de fabrica e use o "
               "mesmo. A coleira nao distingue os dois e ambos passam a funcionar.")]
    seq = [("1", "Ligue a coleira", "um toque no botao, ela apita uma vez"),
           ("2", "Entre em pareamento", "segure o botao ate apitar e o LED piscar rapido"),
           ("3", "Rode o modo descoberta", "testa CaiXianlin, Petrainer, 998DR, T330 e D80"),
           ("4", "Ouca a resposta", "o protocolo certo e aquele em que a coleira apita de volta")]
    def cena_a(c, P):
        esp32(c, P, 0, 0, 0)
        fs1000a(c, P, -26, 20, 16); antena(c, P, -26+16, 20+16, 17.5)
        for i in range(3):
            jumper_pair(c, P, (-26+5.8+i*2.54, 20+1.3, 17.5), (6.9+(i+2)*2.54, 1.2, 5.9), g(0.52), 10)
    cena_b = lambda cc, PP: coleira(cc, PP)

    H_NOT, H_SEQ = notes_h(blocks), 22 + len(seq)*17
    ny = FOOT + 8 + H_NOT
    top = y0 - 12
    reserve = ny + H_SEQ + 26
    band = (ML, reserve, CW, top - reserve)
    Pa, ra = fit((band[0], band[1], band[2]*0.46, band[3]), cena_a, 0.95, "top")
    Pb, rb = fit((band[0] + band[2]*0.54, band[1], band[2]*0.46, band[3]), cena_b, 0.95, "top")
    art_h = max(ra[3], rb[3])
    slack = max(0.0, (top - ny - H_SEQ) - art_h)
    drop = min(40.0, slack/3.0)
    Pa, ra = fit((band[0], band[1], band[2]*0.46, band[3] - drop), cena_a, 0.95, "top")
    Pb, rb = fit((band[0] + band[2]*0.54, band[1], band[2]*0.46, band[3] - drop), cena_b, 0.95, "top")
    cena_a(c, Pa); coleira(c, Pb, 0, 0, 0)

    ax, ay = Pa(30, 12, 22); bx, by = Pb(26, 8, 16)
    apex = max(ay, by) + 34
    c.setStrokeColorRGB(*ROSA); c.setLineWidth(1.2); c.setDash(4, 3)
    pa = c.beginPath(); pa.moveTo(ax, ay)
    pa.curveTo(ax + 40, apex, bx - 40, apex, bx, by)
    c.drawPath(pa, stroke=1, fill=0); c.setDash()
    c.setFont("MonoB", 6.2); c.setFillColorRGB(*ROSA)
    c.drawCentredString((ax + bx)/2, apex - 2, "433,92 MHZ   ASK / OOK   BIPE")

    sy = min(ra[1], rb[1]) - max(20.0, slack/3.0) - 12
    sy = max(sy, ny + H_SEQ - 12)
    for i, (n, t, d) in enumerate(seq):
        yy = sy - i*17
        c.setFont("Big", 13); c.setFillColorRGB(*ROSA); c.drawString(ML, yy, n)
        c.setFont("SansB", 8.6); c.setFillColorRGB(*INK); c.drawString(ML + 15, yy, t)
        c.setFont("Sans", 8.0); c.setFillColorRGB(*SOFT); c.drawString(ML + 62*mm, yy, d)
        hrule(c, ML, yy - 5.5, CW, FAINT)
    notes(c, ny, blocks)
    footer(c, 7, total, "ETAPA 5 DE 5")

def p_ref(c, total):
    """Quatro blocos empilhados. A folga vertical e repartida em partes iguais
    entre eles, nunca acumulada num vao unico."""
    bg(c)
    y0 = head(c, None, "Referencia",
              "Mapa de pinos, tabela completa de ligacoes e o quadro de radio do protocolo "
              "mais provavel.", "APENDICE")
    blocks = [("Verificacao final",
               "Seis fios, duas antenas, um cabo. Confira que nenhum jumper saiu do lugar e que "
               "as antenas estao retas antes de energizar."),
              ("Seguranca",
               "Nunca no pescoco, no peito ou sobre a coluna. Comece em intensidade 5 a 10 com "
               "300 ms. Somente adultos, somente com consentimento.")]
    rows = [("B FS1000A VCC", "A ESP32 3V3", "alimentacao 3,3 V", "02"),
            ("B FS1000A GND", "A ESP32 GND", "terra comum", "02"),
            ("B FS1000A DATA", "A ESP32 GPIO 4", "pulsos de radio, saida", "02"),
            ("C RXB6 VCC", "A ESP32 VIN", "alimentacao 5 V", "03"),
            ("C RXB6 GND", "A ESP32 GND", "terra comum", "03"),
            ("C RXB6 DATA", "A ESP32 GPIO 5", "pulsos de radio, entrada", "03"),
            ("D ANTENA", "B e C, furo ANT", "quarto de onda, 17,3 cm", "01"),
            ("F CABO USB", "A ESP32 micro USB", "energia, gravacao, serial", "04")]
    bh = 20*mm
    H_MAP = 20 + 52 + bh + 52 + 14
    H_TAB = 15 + len(rows)*13.2
    H_WAV = 105
    H_NOT = notes_h(blocks)
    top, bot = y0 - 10, FOOT
    gap = max(10.0, (top - bot - (H_MAP + H_TAB + H_WAV + H_NOT)) / 3.0)

    # ---- bloco 1: mapa de pinos, vista superior
    y = top
    c.setFont("Mono", 5.6); c.setFillColorRGB(*SOFT)
    c.drawString(ML, y - 8, "VISTA SUPERIOR  /  OS SEIS PINOS EM USO")
    c.drawRightString(W - MR, y - 8, "LADO OPOSTO  /  RECEPTOR")
    bw, bx = 76*mm, ML + 49*mm
    by = y - 20 - 52 - bh
    c.setFillColorRGB(*g(0.30)); c.setStrokeColorRGB(*INK); c.setLineWidth(0.6)
    c.roundRect(bx, by, bw, bh, 2.5, stroke=1, fill=1)
    c.setFillColorRGB(*g(0.72)); c.rect(bx + 3.5*mm, by + 3*mm, 24*mm, bh - 6*mm, stroke=1, fill=1)
    c.setFont("Mono", 5.0); c.setFillColorRGB(*g(0.15))
    c.drawCentredString(bx + 15.5*mm, by + bh/2 - 1.8, "ESP32-WROOM-32")
    lower, upper = {2: "GPIO 4", 3: "3V3", 4: "GND"}, {2: "GPIO 5", 3: "VIN", 4: "GND"}
    step = (bw - 9*mm)/14
    for i in range(15):
        px = bx + 4.5*mm + i*step
        for py, mp in ((by - 2.6, lower), (by + bh + 2.6, upper)):
            on = i in mp
            c.setFillColorRGB(*(ROSA if on else g(0.58)))
            c.circle(px, py, 1.7 if on else 1.0, stroke=0, fill=1)
    for row, (py, mp, lx) in enumerate(((by - 2.6, lower, ML), (by + bh + 2.6, upper, W - MR))):
        for k, i in enumerate(sorted(mp)):
            px = bx + 4.5*mm + i*step
            ly = (by - 13 - (2-k)*13) if row == 0 else (by + bh + 13 + k*13)
            c.setStrokeColorRGB(*INK); c.setLineWidth(0.4)
            pa = c.beginPath(); pa.moveTo(px, py)
            pa.lineTo(lx + (44 if row == 0 else -44), ly + 2)
            pa.lineTo(lx + (40 if row == 0 else -40), ly + 2)
            c.drawPath(pa, stroke=1, fill=0)
            c.setFont("MonoB", 6.4); c.setFillColorRGB(*INK)
            (c.drawString if row == 0 else c.drawRightString)(lx, ly, mp[i])
    c.setFont("Mono", 5.6); c.setFillColorRGB(*SOFT)
    c.drawString(ML, by - 52 - 6, "LADO DOS GPIO  /  TRANSMISSOR")

    # ---- bloco 2: tabela de ligacoes
    tab_top = y - H_MAP - gap
    table(c, tab_top - 15, ["ORIGEM", "DESTINO", "SINAL", "ETAPA"], rows,
          [0, 37*mm, 74*mm, 119*mm], True)

    # ---- bloco 3: quadro de radio
    qtop = tab_top - H_TAB - gap
    c.setFont("MonoB", 6.4); c.setFillColorRGB(*INK)
    c.drawString(ML, qtop - 10, "QUADRO CAIXIANLIN  /  O PROTOCOLO MAIS PROVAVEL")
    hrule(c, ML, qtop - 15, CW, RULE)
    gy = qtop - 58
    unit, gx = 0.0215*CW, ML
    seq_bits = [("P", 1400, 750), ("1", 750, 250), ("0", 250, 750), ("1", 750, 250),
                ("1", 750, 250), ("0", 250, 750), ("0", 250, 750), ("1", 750, 250)]
    x = gx; c.setStrokeColorRGB(*INK); c.setLineWidth(1.2)
    pa = c.beginPath(); pa.moveTo(x, gy)
    for _, hi, lo in seq_bits:
        wh, wl = hi/1000.0*unit, lo/1000.0*unit
        pa.lineTo(x, gy+26); pa.lineTo(x+wh, gy+26); pa.lineTo(x+wh, gy); pa.lineTo(x+wh+wl, gy)
        x += wh + wl
    c.drawPath(pa, stroke=1, fill=0)
    x = gx
    for lbl, hi, lo in seq_bits:
        wh, wl = hi/1000.0*unit, lo/1000.0*unit
        c.setFont("MonoB", 6.4); c.setFillColorRGB(*(ROSA if lbl == "P" else INK))
        c.drawCentredString(x + (wh+wl)/2, gy - 10, lbl)
        x += wh + wl
    c.setFont("Mono", 5.6); c.setFillColorRGB(*SOFT)
    c.drawString(gx, gy + 32, "PREAMBULO 1400 / 750 us        BIT 1 = 750 / 250 us        "
                              "BIT 0 = 250 / 750 us")
    c.drawString(gx, gy - 24, "PAYLOAD   [ ID 16 ]  [ CANAL 4 ]  [ TIPO 4 ]  [ INTENSIDADE 8 ]   "
                              "+ CHECKSUM 8   + 3 ZEROS")
    c.drawString(gx, gy - 33, "TIPO   1 CHOQUE    2 VIBRACAO    3 BIPE                "
                              "INTENSIDADE   0 A 99")

    notes(c, FOOT + 8 + H_NOT, blocks)
    footer(c, 8, total, "REFERENCIA")

# ---------------------------------------------------------------- build
def build(path):
    total = 8
    c = rlcanvas.Canvas(path, pagesize=A4)
    c.setTitle("Collar Console - Manual de Montagem")
    c.setAuthor("gunz101")
    c.setSubject("Montagem da ponte de radio 433 MHz")
    for fn in (p_capa, p_pecas, p_etapa1, p_etapa2, p_etapa3, p_etapa4, p_etapa5, p_ref):
        fn(c, total); c.showPage()
    c.save()
    return path

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "MANUAL-MONTAGEM.pdf")
    build(out)
    print("gerado:", out, os.path.getsize(out), "bytes")
