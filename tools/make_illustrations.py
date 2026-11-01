#!/usr/bin/env python3
"""Draw the three illustrations of the workflow page (preprocessing, alignment, parameterization) as SVG, in the colors of the logo.

They are drawings of an idea, not output of the program, and the page says so.  Needs numpy and scipy.  Usage:  python tools/make_illustrations.py
"""
import math
import os

import numpy as np
from scipy.spatial import Delaunay

NAVY, BLUE, SKY, ORANGE, PALE = "#0e2a63", "#1f82ca", "#9ccbf0", "#e2693e", "#fdeee7"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "img")


def outline(n=120, phase=0.0, bump=0.0):
    """A closed bean-like outline (not symmetric, so that a rotation can be seen)."""
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    r = 1 + 0.16 * np.sin(2 * t + phase) + 0.09 * np.sin(3 * t + 1.3) + bump * np.exp(-((t - 0.9) ** 2) / 0.08)
    return np.c_[r * np.cos(t) * 1.15, r * np.sin(t) * 0.82]


def inside(poly, pts):
    from matplotlib.path import Path
    return Path(poly).contains_points(pts)


def mesh_blob(cx, cy, scale, rot=0.0, color=BLUE, hole=None, seed=1, stroke="#ffffff", extra=""):
    """A blob drawn like a triangle mesh; ``hole``: (x, y, r) in blob units, a hole through it."""
    rng = np.random.default_rng(seed)
    poly = outline()
    pts = rng.uniform(-1.7, 1.7, (260, 2))
    pts = pts[inside(poly * 0.97, pts)]
    pts = np.vstack([pts, poly[::5]])
    tri = Delaunay(pts)
    keep = []
    for s in tri.simplices:
        c = pts[s].mean(axis=0)
        if not inside(poly, c[None])[0]:
            continue
        if hole and (c[0] - hole[0]) ** 2 + (c[1] - hole[1]) ** 2 < hole[2] ** 2:
            continue
        keep.append(s)
    ca, sa = math.cos(rot), math.sin(rot)
    f = lambda p: (cx + scale * (ca * p[0] - sa * p[1]), cy + scale * (sa * p[0] + ca * p[1]))
    out = [f"<g {extra}>"]
    for s in keep:
        pp = [f(pts[i]) for i in s]
        out.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pp)}" fill="{color}" fill-opacity="0.92" stroke="{stroke}" stroke-opacity="0.55" stroke-width="0.8" stroke-linejoin="round"/>')
    if hole:
        hx, hy = f((hole[0], hole[1]))
        out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{hole[2] * scale:.1f}" fill="none" stroke="{ORANGE}" stroke-width="3" stroke-dasharray="6 5"/>')
    out.append("</g>")
    return "\n".join(out)


def arrow(x1, y1, x2, y2, color=NAVY, width=3):
    ang = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 11 * math.cos(ang), y2 - 11 * math.sin(ang)
    px, py = -math.sin(ang), math.cos(ang)
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {hx + 7 * px:.1f},{hy + 7 * py:.1f} {hx - 7 * px:.1f},{hy - 7 * py:.1f}" fill="{color}"/>')


def svg(title, desc, body, w=480, h=260):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">\n<title id="t">{title}</title><desc id="d">{desc}</desc>\n'
            f'<rect width="{w}" height="{h}" rx="14" fill="#f5f8fc"/>\n{body}\n</svg>\n')


def label(x, y, text, color="#4a5a75", size=14, anchor="middle", weight=600):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{text}</text>'


def preprocess():
    body = [mesh_blob(125, 125, 68, rot=0.2, color=BLUE, hole=(0.25, 0.1, 0.34), seed=3),
            arrow(205, 125, 275, 125),
            mesh_blob(360, 125, 68, rot=0.2, color=BLUE, hole=None, seed=3),
            label(125, 232, "holes and debris"), label(360, 232, "a clean closed mesh")]
    return svg("Preprocessing", "A mesh with a hole becomes a clean closed mesh.", "\n".join(body))


def align():
    body = []
    cols = [BLUE, "#2aa7a0", "#6b5fc7"]
    for k, (x, y, r, c) in enumerate([(78, 92, 0.2, cols[0]), (122, 160, 1.3, cols[1]), (62, 175, -0.7, cols[2])]):
        body.append(mesh_blob(x, y, 40, rot=r, color=c, seed=5, extra='opacity="0.9"'))
    body.append(arrow(185, 125, 250, 125))
    for k, c in enumerate(cols):
        body.append(mesh_blob(365, 120, 54 - 0, rot=0.2, color=c, seed=5, extra=f'opacity="{0.55 if k else 0.9}"'))
    body.append(f'<g stroke="{ORANGE}" stroke-width="2.4" stroke-linecap="round"><line x1="351" y1="120" x2="379" y2="120"/><line x1="365" y1="106" x2="365" y2="134"/></g>')
    body += [label(110, 232, "different poses"), label(365, 232, "one common pose")]
    return svg("Alignment", "Three copies of a shape in different positions and orientations are brought into one common pose.", "\n".join(body))


def chart_sphere(cx, cy, r):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SKY}" stroke="{NAVY}" stroke-width="2.4"/>']
    for k in (0.35, 0.7):
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * k:.1f}" fill="none" stroke="{NAVY}" stroke-opacity="0.5" stroke-width="1.4"/>')
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r * k:.1f}" ry="{r}" fill="none" stroke="{NAVY}" stroke-opacity="0.5" stroke-width="1.4"/>')
    return "\n".join(out)


def chart_torus(cx, cy, r):
    out = [f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * 0.62:.1f}" fill="{SKY}" stroke="{NAVY}" stroke-width="2.4"/>',
           f'<ellipse cx="{cx}" cy="{cy + 2}" rx="{r * 0.42:.1f}" ry="{r * 0.2:.1f}" fill="#f5f8fc" stroke="{NAVY}" stroke-width="2"/>']
    for k in range(1, 6):
        a = k * math.pi / 6
        out.append(f'<ellipse cx="{cx + (r * 0.72) * math.cos(a) * 0:.1f}" cy="{cy}" rx="{r * (0.2 + 0.8 * abs(math.cos(a))):.1f}" ry="{r * 0.62:.1f}" fill="none" stroke="{NAVY}" stroke-opacity="0.28" stroke-width="1.2"/>')
    return "\n".join(out)


def chart_disk(cx, cy, r):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SKY}" stroke="{NAVY}" stroke-width="2.4"/>']
    for k in (0.33, 0.66):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * k:.1f}" fill="none" stroke="{NAVY}" stroke-opacity="0.5" stroke-width="1.4"/>')
    for k in range(8):
        a = k * math.pi / 4
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(a):.1f}" y2="{cy + r * math.sin(a):.1f}" stroke="{NAVY}" stroke-opacity="0.5" stroke-width="1.4"/>')
    return "\n".join(out)


def param():
    body = [mesh_blob(78, 110, 46, rot=0.2, color=BLUE, seed=7), arrow(140, 110, 200, 110),
            chart_sphere(268, 62, 38), label(268, 122, "sphere"), label(268, 138, "genus 0", size=12, weight=500),
            chart_torus(402, 62, 48), label(402, 122, "flat torus"), label(402, 138, "genus 1", size=12, weight=500),
            chart_disk(268, 196, 34), label(268, 246, "disk", size=14), label(402, 222, "any surface:", size=13), label(402, 240, "no chart needed", size=13, weight=500),
            label(78, 232, "your mesh")]
    return svg("Parameterization", "A mesh is mapped onto a sphere, a flat torus or a disk, depending on its kind.", "\n".join(body), h=262)


if __name__ == "__main__":
    for name, fn in (("step-preprocess.svg", preprocess), ("step-align.svg", align), ("step-parameterize.svg", param)):
        path = os.path.join(OUT, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(fn())
        print("wrote", os.path.normpath(path), os.path.getsize(path) // 1024, "KB")
