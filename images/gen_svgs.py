"""Generate blueprint-style SVG illustrations: cream fine lines on oxblood.

Each tile is 800x500. Shared frame = background, vignette, grain, faint grid.
"""
import math, os, random

W, H = 800, 500
OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)

import sys
# Palette presets: name -> (base, light-centre, dark-edge, ink)
PALETTES = {
    "oxblood":   ("#4a150e", "#5a1d13", "#360e09", "#efe3cf"),
    "pine":      ("#243a2f", "#2d4639", "#182a21", "#efe3cf"),
    "umber":     ("#3a2a1e", "#463428", "#2a1d14", "#efe3cf"),
    "parchment": ("#efe4cf", "#f4ebd9", "#e3d5ba", "#4a3426"),
}
PAL = sys.argv[1] if len(sys.argv) > 1 else "pine"
BG, BG_LIGHT, BG_DARK, INK = PALETTES[PAL]
GRAIN_RGB = "1 0.9 0.8" if PAL != "parchment" else "0.3 0.2 0.1"
OUT = sys.argv[2] if len(sys.argv) > 2 else OUT
os.makedirs(OUT, exist_ok=True)

def frame(body, seed=1):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">
<defs>
  <radialGradient id="vig" cx="50%" cy="45%" r="75%">
    <stop offset="0" stop-color="{BG_LIGHT}"/>
    <stop offset="0.7" stop-color="{BG}"/>
    <stop offset="1" stop-color="{BG_DARK}"/>
  </radialGradient>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{seed}" stitchTiles="stitch"/>
    <feColorMatrix type="matrix" values="0 0 0 0 {GRAIN_RGB.split()[0]}  0 0 0 0 {GRAIN_RGB.split()[1]}  0 0 0 0 {GRAIN_RGB.split()[2]}  0 0 0 0.14 0"/>
  </filter>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M40 0H0V40" fill="none" stroke="{INK}" stroke-width="0.5" opacity="0.07"/>
  </pattern>
  <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
    <line x1="0" y1="0" x2="0" y2="6" stroke="{INK}" stroke-width="0.8" opacity="0.9"/>
  </pattern>
</defs>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<rect width="{W}" height="{H}" fill="url(#grid)"/>
<g fill="none" stroke="{INK}" stroke-linecap="round" stroke-linejoin="round" font-family="ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace" font-size="9" letter-spacing="0.5">
{body}
</g>
<rect width="{W}" height="{H}" filter="url(#grain)" opacity="0.9"/>
</svg>
'''

# stroke classes
def main(d, w=1.4, o=0.92):  return f'<path d="{d}" stroke-width="{w}" opacity="{o}"/>'
def sec(d, w=0.9, o=0.6):    return f'<path d="{d}" stroke-width="{w}" opacity="{o}"/>'
def cons(d, w=0.6, o=0.32):  return f'<path d="{d}" stroke-width="{w}" opacity="{o}" stroke-dasharray="3 4"/>'
def thin(d, w=0.6, o=0.45):  return f'<path d="{d}" stroke-width="{w}" opacity="{o}"/>'
def label(x, y, t, o=0.7, anchor="start"):
    return f'<text x="{x}" y="{y}" fill="{INK}" stroke="none" opacity="{o}" text-anchor="{anchor}">{t}</text>'
def hatched(d, o=1):
    return f'<path d="{d}" fill="url(#hatch)" stroke="none" opacity="{o}"/>'

def dim_h(x1, x2, y, text, tick=5):
    """horizontal dimension line with end ticks and label above"""
    s = thin(f"M{x1} {y}H{x2}") + thin(f"M{x1} {y-tick}V{y+tick} M{x2} {y-tick}V{y+tick}")
    s += thin(f"M{x1} {y}l6 -2.5v5z M{x2} {y}l-6 -2.5v5z", o=0.6)
    s += label((x1+x2)/2, y-5, text, anchor="middle")
    return s

def dim_v(x, y1, y2, text, tick=5):
    s = thin(f"M{x} {y1}V{y2}") + thin(f"M{x-tick} {y1}H{x+tick} M{x-tick} {y2}H{x+tick}")
    s += thin(f"M{x} {y1}l-2.5 6h5z M{x} {y2}l-2.5 -6h5z", o=0.6)
    s += f'<text x="{x+6}" y="{(y1+y2)/2+3}" fill="{INK}" stroke="none" opacity="0.7">{text}</text>'
    return s

def circle(cx, cy, r, w=1.0, o=0.8, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke-width="{w}" opacity="{o}"{da}/>'

def crosshair(cx, cy, r=10, o=0.5):
    return thin(f"M{cx-r} {cy}H{cx+r} M{cx} {cy-r}V{cx+r if False else cy+r}", o=o)

# isometric helpers --------------------------------------------------------
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
def iso(x, y, z, ox=400, oy=300, s=1.0):
    return (ox + s*(C30*x - C30*y), oy + s*(S30*x + S30*y - z))
def P(*pts): return " ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
def poly(pts, close=True):
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + ("Z" if close else "")
    return d
def iso_box(x, y, z, dx, dy, dz, **k):
    """return list of three visible face paths (top, left(front-y), right(front-x))"""
    p = lambda a, b, c: iso(a, b, c, **k)
    top = poly([p(x,y,z+dz), p(x+dx,y,z+dz), p(x+dx,y+dy,z+dz), p(x,y+dy,z+dz)])
    front = poly([p(x+dx,y,z), p(x+dx,y+dy,z), p(x+dx,y+dy,z+dz), p(x+dx,y,z+dz)])   # x = x+dx face
    side = poly([p(x,y+dy,z), p(x+dx,y+dy,z), p(x+dx,y+dy,z+dz), p(x,y+dy,z+dz)])    # y = y+dy face
    return top, front, side
def iso_circle_xz(cx, cy, cz, r, w=1.2, o=0.9, **k):
    """circle lying in a plane of constant y (wheel), drawn as transformed circle"""
    ex, ey = iso(0, cy, 0, **k)
    s = k.get("s", 1.0)
    # 2D (u,v)=(x,z) -> screen = (C30*u*s, (S30*u - v)*s) + (ex0, ey0)
    e, f = iso(0, cy, 0, **k)
    return (f'<g transform="matrix({C30*s:.4f} {S30*s:.4f} 0 {-s:.4f} {e:.2f} {f:.2f})">'
            f'<circle cx="{cx}" cy="{cz}" r="{r}" stroke-width="{w/s:.2f}" opacity="{o}" vector-effect="non-scaling-stroke"/></g>')
def iso_circle_xy(cx, cy, cz, r, w=1.0, o=0.8, **k):
    s = k.get("s", 1.0)
    e, f = iso(0, 0, cz, **k)
    return (f'<g transform="matrix({C30*s:.4f} {S30*s:.4f} {-C30*s:.4f} {S30*s:.4f} {e:.2f} {f:.2f})">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke-width="{w:.2f}" opacity="{o}" vector-effect="non-scaling-stroke"/></g>')

# =========================================================================
# 1. SDF paper — documents -> network -> rings of generalisation
# =========================================================================
def svg_sdf():
    b = []
    # construction circles behind
    b.append(circle(560, 250, 150, w=0.6, o=0.25, dash="2 5"))
    b.append(circle(560, 250, 105, w=0.6, o=0.3, dash="2 5"))
    b.append(circle(560, 250, 60, w=0.6, o=0.35, dash="2 5"))
    b.append(label(560, 97, "HOP 3", anchor="middle", o=0.5))
    b.append(label(560, 142, "HOP 2", anchor="middle", o=0.5))
    b.append(label(560, 187, "HOP 1", anchor="middle", o=0.5))
    # stack of documents (left), slightly fanned
    for i, (dx, dy, rot) in enumerate([(0, 0, -6), (14, -10, -2), (28, -20, 3)]):
        x, y = 70 + dx, 150 + dy
        g = f'<g transform="rotate({rot} {x+60} {y+80})">'
        g += main(f"M{x} {y}h90l30 30v130h-120z", o=0.9 if i == 2 else 0.6)
        g += sec(f"M{x+90} {y}v30h30")
        for k in range(7):
            yy = y + 48 + k*15
            g += thin(f"M{x+14} {yy}h{random.Random(i*10+k).randint(50, 92)}", o=0.5)
        g += "</g>"
        b.append(g)
    b.append(label(70, 330, "FINETUNING DOCUMENTS", o=0.6))
    b.append(cons("M70 338H230"))
    # arrows docs -> network
    b.append(sec("M225 215 C260 215 270 240 300 240"))
    b.append(sec("M225 225 C260 225 270 260 300 260"))
    b.append(thin("M300 240l-7 -3v6z M300 260l-7 -3v6z", o=0.8))
    # network layers (centre)
    layers = [(320, 5), (380, 7), (440, 7), (500, 5)]
    pts = []
    for (lx, n) in layers:
        ys = [250 + (j - (n-1)/2)*34 for j in range(n)]
        pts.append([(lx, y) for y in ys])
    for a, bb in zip(pts, pts[1:]):
        for (x1, y1) in a:
            for (x2, y2) in bb:
                b.append(thin(f"M{x1} {y1}L{x2} {y2}", w=0.45, o=0.28))
    for layer in pts:
        for (x, y) in layer:
            b.append(circle(x, y, 7, w=1.1, o=0.9))
            b.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{BG}" stroke="none" opacity="0.7"/>')
            b.append(circle(x, y, 7, w=1.1, o=0.9))
    b.append(cons("M310 118V382 M510 118V382"))
    b.append(dim_h(320, 500, 395, "4 LAYERS"))
    # output rays to rings (right)
    rnd = random.Random(7)
    for (x, y) in pts[-1]:
        for r_i, r in enumerate([60, 105, 150]):
            ang = math.radians(rnd.uniform(-70, 70))
            tx, ty = 560 + r*math.cos(ang), 250 + r*math.sin(ang)
            b.append(thin(f"M{x} {y}L{tx:.1f} {ty:.1f}", w=0.5, o=0.22 + 0.1*(2-r_i)))
            b.append(f'<rect x="{tx-3:.1f}" y="{ty-3:.1f}" width="6" height="6" stroke-width="0.9" opacity="{0.9 - 0.25*r_i}" transform="rotate(45 {tx:.1f} {ty:.1f})"/>')
    b.append(label(720, 250, "UNRELATED", o=0.5, anchor="middle"))
    b.append(label(720, 262, "TASKS", o=0.5, anchor="middle"))
    b.append(label(40, 470, "FIG. 1 — GENERALISATION FROM NARROW FINETUNING", o=0.55))
    b.append(label(760, 470, "SHEET 1/3", o=0.45, anchor="end"))
    return frame("\n".join(b), seed=3)

# =========================================================================
# 2. Agent cyber-capability evaluation — phone cutaway + many agents + shield
# =========================================================================
def svg_cyber():
    b = []
    # phone body
    x, y, w, h = 300, 60, 200, 380
    b.append(main(f"M{x+22} {y}h{w-44}a22 22 0 0 1 22 22v{h-44}a22 22 0 0 1 -22 22h-{w-44}a22 22 0 0 1 -22 -22v-{h-44}a22 22 0 0 1 22 -22z"))
    b.append(sec(f"M{x+12} {y+26}h{w-24}v{h-52}h-{w-24}z"))  # screen
    b.append(thin(f"M{x+w/2-18} {y+13}h36", o=0.6))  # speaker
    b.append(circle(x+w/2, y+h-14, 4, w=0.8, o=0.6))
    # cutaway: lower-right of screen removed showing board
    cut = f"M{x+w/2} {y+h-26}V{y+200}C{x+w/2+30} {y+190} {x+w-40} {y+210} {x+w-12} {y+185}V{y+h-26}z"
    b.append(f'<path d="{cut}" fill="{BG}" stroke="none" opacity="0.8"/>')
    b.append(main(cut, w=1.1, o=0.8))
    b.append(hatched(f"M{x+w/2} {y+h-26}V{y+200}C{x+w/2+30} {y+190} {x+w-40} {y+210} {x+w-12} {y+185}V{y+h-26}z", o=0.25))
    # chips & traces inside cutaway
    b.append(sec(f"M{x+w/2+16} {y+230}h40v40h-40z"))
    b.append(sec(f"M{x+w/2+70} {y+250}h28v28h-28z"))
    b.append(sec(f"M{x+w/2+20} {y+300}h70v22h-70z"))
    for i in range(6):
        b.append(thin(f"M{x+w/2+16+i*7} {y+270}v12", o=0.6))
        b.append(thin(f"M{x+w/2+16+i*7} {y+230}v-10", o=0.6))
    b.append(thin(f"M{x+w/2+56} {y+250}h14 M{x+w/2+56} {y+260}h14 M{x+w/2+84} {y+278}v22 M{x+w/2+36} {y+322}v12h50v-12", o=0.6))
    b.append(circle(x+w/2+70, y+350, 10, w=0.9, o=0.7))
    b.append(circle(x+w/2+70, y+350, 3, w=0.9, o=0.7))
    # app grid on intact screen
    for r in range(4):
        for c in range(4):
            cx, cy = x+36+c*42, y+60+r*42
            if cy + 14 > y+200 and cx > x+w/2 - 10:
                continue
            b.append(thin(f"M{cx-13} {cy-13}h26v26h-26z", o=0.55))
    # swarm of agent nodes on the left, converging on phone
    rnd = random.Random(11)
    nodes = [(80 + rnd.randint(0, 110), 90 + rnd.randint(0, 320)) for _ in range(14)]
    for (nx, ny) in nodes:
        b.append(circle(nx, ny, 6, w=1.0, o=0.85))
        b.append(f'<circle cx="{nx}" cy="{ny}" r="1.6" fill="{INK}" stroke="none" opacity="0.8"/>')
        ty = y + 40 + (ny - 90) * 0.75
        b.append(thin(f"M{nx+6} {ny}C{nx+80} {ny} {x-80} {ty} {x-2} {ty}", w=0.55, o=0.4))
        b.append(thin(f"M{x-2} {ty}l-7 -3v6z", o=0.7))
    for (a, c) in [(0, 3), (1, 5), (2, 7), (4, 9), (6, 11), (8, 12), (10, 13)]:
        (x1, y1), (x2, y2) = nodes[a], nodes[c]
        b.append(cons(f"M{x1} {y1}L{x2} {y2}", o=0.25))
    b.append(label(80, 470, "AGENT SWARM  N=14", o=0.6))
    # shield on right with lock
    sx, sy = 640, 190
    shield = f"M{sx} {sy-70}C{sx+40} {sy-50} {sx+60} {sy-60} {sx+70} {sy-62}V{sy+10}C{sx+70} {sy+60} {sx+30} {sy+90} {sx} {sy+105}C{sx-30} {sy+90} {sx-70} {sy+60} {sx-70} {sy+10}V{sy-62}C{sx-60} {sy-60} {sx-40} {sy-50} {sx} {sy-70}Z"
    b.append(main(shield))
    b.append(cons(f"M{sx} {sy-80}V{sy+120}"))
    b.append(sec(f"M{sx-22} {sy}h44v38h-44z"))
    b.append(sec(f"M{sx-13} {sy}v-16a13 13 0 0 1 26 0v16"))
    b.append(circle(sx, sy+16, 4, w=0.9, o=0.8))
    b.append(thin(f"M{sx} {sy+20}v10", o=0.8))
    # arrows from phone to shield (probe)
    for dy in (-30, 0, 30):
        b.append(thin(f"M{x+w+8} {sy+dy}H{sx-78}", o=0.5))
        b.append(thin(f"M{sx-78} {sy+dy}l-7 -3v6z", o=0.7))
    # dimensions
    b.append(dim_v(x+w+30, y, y+h, "H"))
    b.append(dim_h(x, x+w, y+h+22, "W"))
    b.append(cons(f"M{x} {y+h}V{y+h+30} M{x+w} {y+h}V{y+h+30}"))
    b.append(label(sx, sy+150, "DEFENCE UNDER TEST", o=0.55, anchor="middle"))
    b.append(label(760, 470, "SHEET 2/3", o=0.45, anchor="end"))
    return frame("\n".join(b), seed=5)

# =========================================================================
# 3. IDP robot — isometric wheeled robot with sensor mast and gripper
# =========================================================================
def svg_robot():
    b = []
    k = dict(ox=340, oy=288, s=1.2)
    # ground construction grid (iso)
    for i in range(-3, 6):
        b.append(cons(poly([iso(-80, i*40, 0, **k), iso(260, i*40, 0, **k)], False), o=0.18))
    for i in range(-2, 7):
        b.append(cons(poly([iso(i*40, -80, 0, **k), iso(i*40, 180, 0, **k)], False), o=0.18))
    X, Y, Z, DX, DY, DZ = 0, 0, 30, 170, 110, 55
    top, front, side = iso_box(X, Y, Z, DX, DY, DZ, **k)
    # far wheel first (behind body), y = -12
    for d in (top, front, side):
        b.append(main(d, w=1.3))
    # hidden edges
    b.append(cons(poly([iso(X, Y, Z, **k), iso(X, Y, Z+DZ, **k)], False)))
    b.append(cons(poly([iso(X, Y, Z, **k), iso(X+DX, Y, Z, **k)], False)))
    b.append(cons(poly([iso(X, Y, Z, **k), iso(X, Y+DY, Z, **k)], False)))
    # near drive wheel on side face (y = DY), rear-ish at x=50
    wy, wx, wr = Y+DY, 50, 38
    b.append(iso_circle_xz(wx, wy+2, wr, wr, w=0.9, o=0.55, **k))
    b.append(iso_circle_xz(wx, wy+16, wr, wr, w=1.3, o=0.95, **k))
    b.append(iso_circle_xz(wx, wy+16, wr, 28, w=0.8, o=0.6, **k))
    b.append(iso_circle_xz(wx, wy+16, wr, 7, w=0.9, o=0.85, **k))
    for ang in range(100, 300, 25):
        a = math.radians(ang)
        p1 = iso(wx + wr*math.cos(a), wy+2, wr + wr*math.sin(a), **k)
        p2 = iso(wx + wr*math.cos(a), wy+16, wr + wr*math.sin(a), **k)
        b.append(thin(poly([p1, p2], False), o=0.55))
    for ang in range(0, 360, 60):
        a = math.radians(ang)
        p1 = iso(wx + 7*math.cos(a), wy+16, wr + 7*math.sin(a), **k)
        p2 = iso(wx + 27*math.cos(a), wy+16, wr + 27*math.sin(a), **k)
        b.append(thin(poly([p1, p2], False), o=0.5))
    # caster at front (x = DX-16), centre of width
    b.append(sec(poly([iso(DX-16, DY/2, Z, **k), iso(DX-16, DY/2, 26, **k)], False)))
    b.append(iso_circle_xz(DX-16, DY/2+6, 13, 13, w=1.0, o=0.85, **k))
    b.append(iso_circle_xz(DX-16, DY/2+6, 13, 3, w=0.8, o=0.6, **k))
    # sensor mast at rear-left of top (x=25, y=30)
    mx, my = 25, 30
    b.append(main(poly([iso(mx, my, Z+DZ, **k), iso(mx, my, Z+DZ+70, **k)], False), w=1.2))
    b.append(sec(poly([iso(mx+5, my, Z+DZ, **k), iso(mx+5, my, Z+DZ+70, **k)], False)))
    ht, hf, hs = iso_box(mx-14, my-10, Z+DZ+70, 30, 22, 16, **k)
    for d in (ht, hf, hs): b.append(main(d, w=1.1))
    # camera lens on front face of head (x = mx+16 face) -> draw in YZ plane via small ellipse approx using xy circle rotated: use 3 concentric iso-xz? Simpler: square aperture
    b.append(sec(poly([iso(mx+16, my-4, Z+DZ+74, **k), iso(mx+16, my+8, Z+DZ+74, **k), iso(mx+16, my+8, Z+DZ+84, **k), iso(mx+16, my-4, Z+DZ+84, **k)]), o=0.8))
    # lidar puck on head
    b.append(iso_circle_xy(mx+1, my+1, Z+DZ+86, 13, w=1.0, o=0.9, **k))
    b.append(iso_circle_xy(mx+1, my+1, Z+DZ+94, 13, w=1.0, o=0.9, **k))
    b.append(sec(poly([iso(mx+1-13*C30, my+1+13*C30, Z+DZ+86, **k), iso(mx+1-13*C30, my+1+13*C30, Z+DZ+94, **k)], False)))
    b.append(sec(poly([iso(mx+1+13*C30, my+1-13*C30, Z+DZ+86, **k), iso(mx+1+13*C30, my+1-13*C30, Z+DZ+94, **k)], False)))
    for ang in range(-40, 80, 20):
        a = math.radians(ang)
        p1 = iso(mx+1, my+1, Z+DZ+90, **k)
        p2 = iso(mx+1 + 160*math.cos(a), my+1 + 160*math.sin(a), Z+DZ+90, **k)
        b.append(cons(poly([p1, p2], False), o=0.2))
    # gripper at the front (x from DX to DX+70)
    ay, az = DY/2, Z + 28
    for yy in (ay-20, ay+20):
        b.append(main(poly([iso(DX, yy, az, **k), iso(DX+68, yy, az, **k), iso(DX+68, yy, az-16, **k)], False), w=1.1))
        b.append(sec(poly([iso(DX, yy, az+6, **k), iso(DX+68, yy, az+6, **k)], False), o=0.5))
    b.append(sec(poly([iso(DX+68, ay-20, az, **k), iso(DX+68, ay+20, az, **k)], False)))
    b.append(sec(poly([iso(DX+34, ay-20, az, **k), iso(DX+34, ay+20, az, **k)], False)))
    # block being gripped
    bt, bf, bs = iso_box(DX+44, ay-12, 0, 24, 24, 24, **k)
    for d in (bt, bf, bs): b.append(sec(d, w=0.9, o=0.8))
    b.append(hatched(bs, o=0.35))
    # panel on side face
    b.append(sec(poly([iso(95, DY, 44, **k), iso(160, DY, 44, **k), iso(160, DY, 72, **k), iso(95, DY, 72, **k)]), o=0.55))
    for i in range(4):
        b.append(thin(poly([iso(104 + i*14, DY, 50, **k), iso(104 + i*14, DY, 66, **k)], False), o=0.5))
    # vents on front face
    for i in range(5):
        b.append(thin(poly([iso(DX, 18 + i*8, 60, **k), iso(DX, 18 + i*8, 76, **k)], False), o=0.5))
    # button + marking on top
    b.append(iso_circle_xy(70, 70, Z+DZ, 11, w=0.9, o=0.7, **k))
    b.append(iso_circle_xy(70, 70, Z+DZ, 4, w=0.9, o=0.7, **k))
    b.append(cons(poly([iso(70-30, 70, Z+DZ, **k), iso(70+30, 70, Z+DZ, **k)], False), o=0.35))
    b.append(cons(poly([iso(70, 70-30, Z+DZ, **k), iso(70, 70+30, Z+DZ, **k)], False), o=0.35))
    # dimensions
    p1, p2 = iso(X, Y+DY+46, 0, **k), iso(X+DX, Y+DY+46, 0, **k)
    b.append(thin(poly([p1, p2], False)))
    b.append(thin(poly([iso(X, Y+DY+38, 0, **k), iso(X, Y+DY+54, 0, **k)], False)))
    b.append(thin(poly([iso(X+DX, Y+DY+38, 0, **k), iso(X+DX, Y+DY+54, 0, **k)], False)))
    b.append(cons(poly([iso(X, Y+DY, 0, **k), iso(X, Y+DY+58, 0, **k)], False), o=0.3))
    b.append(cons(poly([iso(X+DX, Y+DY, 0, **k), iso(X+DX, Y+DY+58, 0, **k)], False), o=0.3))
    b.append(label((p1[0]+p2[0])/2 - 40, (p1[1]+p2[1])/2 + 16, "L = 170", o=0.65))
    q1, q2 = iso(X+DX+100, Y, 0, **k), iso(X+DX+100, Y+DY, 0, **k)
    b.append(thin(poly([q1, q2], False)))
    b.append(cons(poly([iso(X+DX, Y, Z, **k), iso(X+DX+110, Y, 0, **k)], False), o=0.3))
    b.append(cons(poly([iso(X+DX, Y+DY, Z, **k), iso(X+DX+110, Y+DY, 0, **k)], False), o=0.3))
    b.append(label((q1[0]+q2[0])/2 + 14, (q1[1]+q2[1])/2 - 6, "W = 110", o=0.65))
    r1, r2 = iso(X-30, Y+DY+10, 0, **k), iso(X-30, Y+DY+10, Z+DZ, **k)
    b.append(thin(poly([r1, r2], False)))
    b.append(thin(poly([(r1[0]-5, r1[1]), (r1[0]+5, r1[1])], False)))
    b.append(thin(poly([(r2[0]-5, r2[1]), (r2[0]+5, r2[1])], False)))
    b.append(label(r1[0] - 8, (r1[1]+r2[1])/2 + 3, "H = 85", o=0.65, anchor="end"))
    b.append(label(40, 60, "ISOMETRIC — SCALE 1:4", o=0.6))
    b.append(label(40, 74, "DRIVE: DIFFERENTIAL, 2 × DC", o=0.45))
    b.append(label(40, 86, "SENSORS: LIDAR, CAM, LINE ×2", o=0.45))
    b.append(label(760, 470, "SHEET 3/3", o=0.45, anchor="end"))
    return frame("\n".join(b), seed=9)

# =========================================================================
# 4. Evaluations essay — vernier caliper measuring an undefined object
# =========================================================================
def svg_evals():
    b = []
    # main beam
    bx, by = 120, 200
    b.append(main(f"M{bx} {by}h540v34h-540z"))
    for i in range(0, 55):
        xx = bx + 20 + i*9.6
        hgt = 12 if i % 10 == 0 else (8 if i % 5 == 0 else 5)
        b.append(thin(f"M{xx:.1f} {by}v{hgt}", o=0.75 if i % 5 == 0 else 0.5))
        if i % 10 == 0:
            b.append(label(xx, by+26, str(i//10), anchor="middle", o=0.6))
    # fixed jaw (left)
    b.append(main(f"M{bx} {by}v-110h26v110 M{bx} {by+34}v70h26v-70"))
    b.append(hatched(f"M{bx} {by-110}h26v110h-26z", o=0.3))
    # sliding jaw
    sx = 330
    b.append(main(f"M{sx} {by-14}h70v62h-70z"))
    b.append(main(f"M{sx} {by-14}v-96h26v96 M{sx} {by+48}v56h26v-56"))
    b.append(hatched(f"M{sx} {by-110}h26v96h-26z", o=0.3))
    # vernier scale on slider
    for i in range(11):
        xx = sx + 6 + i*5.8
        b.append(thin(f"M{xx:.1f} {by+48}v-{9 if i%5==0 else 5}", o=0.7))
    b.append(circle(sx+50, by+20, 8, w=1.0, o=0.8))   # thumb wheel
    b.append(thin(f"M{sx+44} {by+20}h12 M{sx+50} {by+14}v12", o=0.5))
    b.append(sec(f"M{sx+70} {by+2}h20v24h-20z"))   # lock screw
    # measured object: dashed uncertain blob between jaws
    ox1, ox2 = bx+26, sx
    cx, cy = (ox1+ox2)/2, by-50
    b.append(cons(f"M{ox1+4} {cy-30}C{ox1+10} {cy-60} {ox2-20} {cy-62} {ox2-4} {cy-34}C{ox2+2} {cy-10} {ox2-14} {cy+30} {ox2-6} {cy+42}C{ox2-30} {cy+58} {ox1+24} {cy+56} {ox1+4} {cy+38}C{ox1-4} {cy+10} {ox1-2} {cy-6} {ox1+4} {cy-30}Z", w=1.1, o=0.7))
    b.append(f'<text x="{cx}" y="{cy+10}" fill="{INK}" stroke="none" opacity="0.8" text-anchor="middle" font-size="34" font-family="Georgia, serif">?</text>')
    # depth rod extends right
    b.append(sec(f"M{bx+540} {by+12}h60v8h-60", o=0.7))
    # dimension: reading
    b.append(dim_h(ox1, ox2, by-125, "x = ?"))
    b.append(cons(f"M{ox1} {by-110}V{by-135} M{ox2} {by-110}V{by-135}"))
    # magnified detail circle of the vernier
    b.append(circle(640, 380, 72, w=1.0, o=0.8))
    b.append(cons(f"M{sx+30} {by+48}L580 330", o=0.4))
    b.append(cons(f"M{sx+60} {by+48}L600 320", o=0.4))
    g = '<g clip-path="url(#c1)">'
    b.append(f'<clipPath id="c1"><circle cx="640" cy="380" r="72"/></clipPath>')
    g += thin("M570 380h140", o=0.7)
    for i in range(15):
        xx = 575 + i*9.4
        g += thin(f"M{xx:.1f} 380v{-14 if i%5==0 else -8}", o=0.8)
    for i in range(11):
        xx = 580 + i*8.5
        g += thin(f"M{xx:.1f} 380v{14 if i%5==0 else 8}", o=0.8)
    g += '</g>'
    b.append(g)
    b.append(label(640, 468, "DETAIL A — VERNIER, 0.02", anchor="middle", o=0.6))
    b.append(label(40, 470, "FIG. — DEFINE THE QUANTITY BEFORE MEASURING IT", o=0.55))
    return frame("\n".join(b), seed=13)

# =========================================================================
# 5. Pilled — exploded capsule in section with granules
# =========================================================================
def svg_pilled():
    b = []
    # axis
    b.append(cons("M60 250H740", o=0.4))
    b.append(label(70, 242, "C/L", o=0.5))
    # capsule halves: left half (cap) and right half (body), separated along axis
    cy, r = 250, 58
    # left cap: x from 150 to 330, rounded left end
    b.append(main(f"M330 {cy-r}H{210}A{r} {r} 0 0 0 210 {cy+r}H330"))
    b.append(main(f"M330 {cy-r}V{cy+r}", w=1.0, o=0.6))
    # section view of cap: show wall thickness via inner contour
    b.append(sec(f"M330 {cy-r+8}H212A{r-8} {r-8} 0 0 0 212 {cy+r-8}H330", o=0.6))
    b.append(hatched(f"M330 {cy-r}H210A{r} {r} 0 0 0 210 {cy+r}H330V{cy+r-8}H212A{r-8} {r-8} 0 0 1 212 {cy-r+8}H330Z", o=0.35))
    # right body: x from 400 to 600, rounded right end, slightly smaller radius
    r2 = r - 6
    b.append(main(f"M400 {cy-r2}H540A{r2} {r2} 0 0 1 540 {cy+r2}H400"))
    b.append(main(f"M400 {cy-r2}V{cy+r2}", w=1.0, o=0.6))
    b.append(sec(f"M400 {cy-r2+7}H538A{r2-7} {r2-7} 0 0 1 538 {cy+r2-7}H400", o=0.6))
    b.append(hatched(f"M400 {cy-r2}H540A{r2} {r2} 0 0 1 540 {cy+r2}H400V{cy+r2-7}H538A{r2-7} {r2-7} 0 0 0 538 {cy-r2+7}H400Z", o=0.35))
    # granules spilling from body toward cap
    rnd = random.Random(21)
    for _ in range(90):
        gx = rnd.uniform(345, 530); gy = rnd.uniform(cy-40, cy+40)
        if gx > 400 and abs(gy-cy) > r2-12: continue
        rr = rnd.uniform(1.2, 3.2)
        b.append(circle(gx, gy, rr, w=0.7, o=rnd.uniform(0.4, 0.9)))
    # exploded-view guide lines
    b.append(cons(f"M330 {cy-r-20}V{cy+r+20} M400 {cy-r-20}V{cy+r+20}", o=0.35))
    b.append(dim_h(330, 400, cy-r-30, "GAP"))
    b.append(dim_h(210, 598, cy+r+40, "L = 388"))
    b.append(cons(f"M210 {cy+r}V{cy+r+50} M598 {cy+r2}V{cy+r+50}", o=0.35))
    b.append(dim_v(640, cy-r, cy+r, "Ø 116"))
    # end view circle (left)
    b.append(circle(110, 400, 40, w=1.1, o=0.9))
    b.append(circle(110, 400, 32, w=0.8, o=0.6))
    b.append(hatched("M70 400a40 40 0 1 0 80 0a40 40 0 1 0 -80 0z M78 400a32 32 0 1 1 64 0a32 32 0 1 1 -64 0z", o=0.35))
    b.append(cons("M110 350V450 M60 400H160", o=0.4))
    b.append(label(165, 404, "SECTION A-A", o=0.6))
    b.append(cons("M110 360L210 290", o=0.3))
    # small text block
    b.append(label(560, 90, "ITEM  QTY  DESCRIPTION", o=0.55))
    b.append(thin("M560 95h200", o=0.4))
    b.append(label(560, 110, "1     1    CAP, GELATIN", o=0.5))
    b.append(label(560, 124, "2     1    BODY, GELATIN", o=0.5))
    b.append(label(560, 138, "3     —    FILL, ASSORTED IDEAS", o=0.5))
    b.append(label(40, 470, "FIG. — EXPLODED VIEW", o=0.55))
    for n, (lx, ly, tx, ty) in enumerate([(270, cy-r, 260, 120), (470, cy-r2, 500, 150), (372, cy, 420, 380)]):
        b.append(thin(f"M{lx} {ly}L{tx} {ty}", o=0.5))
        b.append(circle(tx, ty, 9, w=0.9, o=0.8))
        b.append(label(tx, ty+3, str(n+1), anchor="middle", o=0.8))
    return frame("\n".join(b), seed=17)

# =========================================================================
# 6. Flashcards — stack of index cards in perspective, top card fanned
# =========================================================================
def svg_flashcards():
    b = []
    # stack: oblique projection cards
    def card(x, y, w, h, skew=0.35, lines=True, o=0.9, wd=1.2):
        dx = h*skew
        d = f"M{x} {y}H{x+w}L{x+w-dx} {y+h}H{x-dx}Z"
        s = main(d, w=wd, o=o)
        if lines:
            # header rule
            s += sec(f"M{x-dx*0.18} {y+h*0.18}H{x+w-dx*0.18}", o=0.5)
            for i in range(1, 5):
                yy = y + h*0.18 + i*(h*0.78/5)
                t = (yy - y)/h
                s += thin(f"M{x-dx*t+10} {yy:.1f}H{x+w-dx*t-10}", o=0.35)
        return s
    # bottom stack edges
    for i in range(10):
        yy = 335 - i*5
        b.append(thin(f"M{150} {yy}H{470}", o=0.35 + 0.03*i))
        b.append(thin(f"M{150} {yy}l-10 10", o=0.2) if False else "")
    b.append(card(185, 220, 320, 110, lines=False, o=0.6, wd=1.0))
    b.append(card(185, 220, 320, 110, lines=True, o=0.9))
    b.append(thin("M150 335V330M470 335V330", o=0.5))
    # side face of stack
    b.append(main("M150 330H470V335H150Z", w=1.0, o=0.8))
    b.append(main("M185 220L150 330", w=1.0, o=0.6))
    b.append(main("M505 220L470 330", w=1.0, o=0.6))
    # top card lifted & rotated
    g = '<g transform="translate(40 -70) rotate(-14 420 240)">'
    g += card(230, 190, 320, 110, lines=True, o=0.95, wd=1.4)
    # handwritten-ish squiggle "Q" and "A"
    g += sec("M262 206c6 -8 18 -6 20 2s-8 10 -12 4", o=0.7)
    g += sec("M300 206c4 -8 16 -8 20 0", o=0.7)
    g += sec("M240 250c10 -6 20 2 30 -2s16 -6 26 0 20 4 30 -2", o=0.6)
    g += sec("M236 268c12 -4 22 4 32 0s18 -4 28 2", o=0.6)
    g += '</g>'
    b.append(g)
    b.append(cons("M270 130L250 200", o=0.3))
    # pencil lying across lower right
    px, py = 540, 390
    g = f'<g transform="rotate(-22 {px} {py})">'
    g += main(f"M{px} {py-8}h150v16h-150z", w=1.2)
    g += main(f"M{px} {py-8}l-28 8l28 8", w=1.2)
    g += thin(f"M{px-28} {py}l-8 0", o=0.9)
    g += thin(f"M{px} {py-2.5}h150 M{px} {py+2.5}h150", o=0.4)
    g += sec(f"M{px+150} {py-8}h14a4 4 0 0 1 0 16h-14", o=0.8)
    g += thin(f"M{px+130} {py-8}v16", o=0.6)
    g += hatched(f"M{px} {py-8}l-28 8l28 8z", o=0.4)
    g += '</g>'
    b.append(g)
    # dimensions
    b.append(dim_h(150, 470, 365, "127 (5 IN)"))
    b.append(dim_v(530, 220, 330, "76 (3 IN)"))
    b.append(cons("M470 330H540 M505 220H540", o=0.35))
    b.append(dim_v(96, 285, 335, "STACK"))
    b.append(cons("M150 285H90 M150 335H90", o=0.35))
    # small tally marks
    b.append(label(600, 90, "REVIEWS", o=0.55))
    b.append(thin("M600 95h120", o=0.4))
    b.append(thin("M604 112v16 M612 112v16 M620 112v16 M628 112v16 M600 128l32 -16", o=0.7))
    b.append(thin("M652 112v16 M660 112v16", o=0.7))
    b.append(label(600, 150, "RETAINED: n/a", o=0.45))
    b.append(label(40, 470, "FIG. — INDEX CARD, 3 × 5, RULED (UNUSED)", o=0.55))
    return frame("\n".join(b), seed=23)

files = {
    "sdf.svg": svg_sdf,
    "cyber.svg": svg_cyber,
    "robot.svg": svg_robot,
    "evals.svg": svg_evals,
    "pilled.svg": svg_pilled,
    "flashcards.svg": svg_flashcards,
}
for name, fn in files.items():
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(fn())
    print(name, os.path.getsize(os.path.join(OUT, name)))
