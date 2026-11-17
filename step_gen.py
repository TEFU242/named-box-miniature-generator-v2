#!/usr/bin/env python3
"""RoofLamp STEP 產生器（build123d / OpenCascade，精確 B-rep，不是網格）。
用法：echo '<json>' | python step_gen.py out.step
json: {"kind":"lamp","p":{...}} 或 {"kind":"brick","p":{...}}
座標：Z 向上，+X 右，前牆朝 −Y（對應網頁 3D 的 +Z 前牆）。
"""
import sys, json, math
from build123d import (Box, Cylinder, Pos, Rot, Axis, Align, Vector, Wire, Face, Solid, Location, Plane,
                       export_step, Compound)

MIN = Align.MIN


def dedupe(pts):
    out = []
    for q in pts:
        if not out or math.hypot(q[0] - out[-1][0], q[1] - out[-1][1]) > 1e-6:
            out.append(q)
    if len(out) > 1 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    return out


def prism_y(pts, length):
    """XZ 輪廓沿 Y 擠出，Y 置中。"""
    pts = dedupe(pts)
    face = Face(Wire.make_polygon([Vector(x, 0, z) for x, z in pts], close=True))
    return Solid.extrude(face, Vector(0, length, 0)).translate((0, -length / 2, 0))


def prism_x(pts, length):
    """YZ 輪廓沿 X 擠出，X 置中。"""
    pts = dedupe(pts)
    face = Face(Wire.make_polygon([Vector(0, y, z) for y, z in pts], close=True))
    return Solid.extrude(face, Vector(length, 0, 0)).translate((-length / 2, 0, 0))


def outer_solid(roof, W, D, H, R, L):
    if roof == 'flat':
        return prism_y([(-W / 2, 0), (W / 2, 0), (W / 2, H), (-W / 2, H)], D)
    if roof == 'shed':
        return prism_y([(-W / 2, 0), (W / 2, 0), (W / 2, H), (-W / 2, H + R)], D)
    if roof == 'gable':
        return prism_y([(-W / 2, 0), (W / 2, 0), (W / 2, H), (0, H + R), (-W / 2, H)], D)
    a = prism_y([(-W / 2, 0), (W / 2, 0), (W / 2, H), (0, H + R), (-W / 2, H)], D)
    b = prism_x([(-D / 2, 0), (D / 2, 0), (D / 2, H), (L / 2, H + R), (-L / 2, H + R), (-D / 2, H)], W)
    return a & b


def win_layout(L, t, n, ww0):
    if not n:
        return []
    span = L - 2 * t
    ww = min(ww0, (span - (n + 1) * 3) / n)
    if ww < 2:
        return []
    gap = (span - n * ww) / (n + 1)
    return [(-span / 2 + gap * (i + 1) + ww * i + ww / 2, ww) for i in range(n)]


SQ3 = math.sqrt(3)


def lamp_grid(n, m, span, span_s, d_req, shape, layout):
    vext = 2 / SQ3 if shape == 'hex' else 1
    hon = layout == 'honey'
    gap = 1.6
    pts = []
    if hon:
        h = 0.5 if m > 1 else 0
        rk = 1 if shape == 'square' else SQ3 / 2
        k = (m - 1) * rk
        d = min(d_req, (span - 2 - (n - 1 + h) * gap) / (n + h), (span_s - 2 - k * gap) / (k + vext))
        pa = d + gap
        pb = pa * rk
        for j in range(m):
            for i in range(n):
                pts.append(((i - (n - 1) / 2) * pa + (pa / 2 if j % 2 else 0) - (pa / 4 if m > 1 else 0),
                            (j - (m - 1) / 2) * pb))
    else:
        d = min(d_req, (span_s - 2) / vext, span - 2,
                span / n - 3 if n > 1 else 1e9, (span_s / m - 3) / vext if m > 1 else 1e9)
        for j in range(m):
            for i in range(n):
                pts.append((0 if n == 1 else -span / 2 + span * (i + 0.5) / n,
                            0 if m == 1 else -span_s / 2 + span_s * (j + 0.5) / m))
    return d, pts


def lamp_list(p, t):
    """回傳 [(x, z, d, shape, rot)]，座標與網頁 3D 相同（z 為網頁 Z）。"""
    if not p.get('lampOn', True) or p['lampD'] <= 0:
        return []
    n = max(1, int(round(p.get('lampN', 1))))
    m = max(1, int(round(p.get('lampRows', 1))))
    along_x = p['width'] >= p['depth']
    Lw, S = (p['width'], p['depth']) if along_x else (p['depth'], p['width'])
    shape = p.get('lampShape', 'circle')
    layout = p.get('lampLayout', 'grid')
    d, pts = lamp_grid(n, m, Lw - 2 * t, S - 2 * t, p['lampD'], shape, layout)
    if d <= 1:
        return []
    ax = max(0, (p['width'] - 2 * t - d) / 2)
    az = max(0, (p['depth'] - 2 * t - d) / 2)
    b = {'center': (0, 0), 'front': (0, .6 * az), 'back': (0, -.6 * az),
         'left': (-.6 * ax, 0), 'right': (.6 * ax, 0)}.get(p.get('lampPos', 'center'), (p.get('lampX', 0), p.get('lampZ', 0)))
    single = layout != 'honey' or (n == 1 and m == 1)
    out = []
    for a, c in pts:
        if single:
            if n == 1:
                a = b[0] if along_x else b[1]
            if m == 1:
                c = b[1] if along_x else b[0]
        out.append((a, c, d, shape, 0) if along_x else (c, a, d, shape, 90))
    return out


def lamp_cutter(x, z, d, shape, rot, h, zc):
    """通孔刀具：中心 (x, -z, zc)，高度 h。"""
    if shape == 'square':
        return Pos(x, -z, zc) * Box(d, d, h)
    if shape == 'hex':
        R = d / SQ3
        off = 0 if rot else math.pi / 2  # 尖角朝向行方向（rot=0 時沿 Y）
        pts = [Vector(R * math.cos(off + k * math.pi / 3), R * math.sin(off + k * math.pi / 3), 0) for k in range(6)]
        face = Face(Wire.make_polygon(pts, close=True))
        return Solid.extrude(face, Vector(0, 0, h)).translate((x, -z, zc - h / 2))
    return Pos(x, -z, zc) * Cylinder(d / 2, h)


def win_cutters(wd, w, d, t):
    """窗／門的刀具清單（款式：fixed / hung / cross / arch）。座標：前牆 −Y、後牆 +Y、左牆 −X、右牆 +X。"""
    door = wd['y0'] <= 0.01
    y0 = -2 if door else wd['y0']
    y1 = wd['y0'] + wd['h']
    hh = y1 - y0
    wall = wd['wall']
    zw = wall in ('front', 'back')
    pos = {'front': -d / 2, 'back': d / 2, 'left': -w / 2, 'right': w / 2}[wall]
    T4, c, ww = t * 4, wd['c'], wd['w']

    def box(a, zc, wid, h):
        if zw:
            return Pos(c + a, pos, zc) * Box(wid, T4, h)
        return Pos(pos, -(c + a), zc) * Box(T4, wid, h)

    def cyl(zc, r):
        if zw:
            return Pos(c, pos, zc) * Rot(90, 0, 0) * Cylinder(r, T4)
        return Pos(pos, -c, zc) * Rot(0, 90, 0) * Cylinder(r, T4)

    st = 'fixed' if (door and not wd.get('main')) else wd.get('style', 'fixed')
    if st == 'dbl':
        bar = 1.4
        pw = (ww - bar) / 2
        return [box(-(pw + bar) / 2, (y0 + y1) / 2, pw, hh), box((pw + bar) / 2, (y0 + y1) / 2, pw, hh)]
    if st == 'hung':
        bar = 1.4
        ph = (hh - bar) / 2
        return [box(0, y0 + ph / 2, ww, ph), box(0, y1 - ph / 2, ww, ph)]
    if st == 'grid':
        bar = 1.0
        cols, rows = 3, 2
        pw, ph = (ww - (cols - 1) * bar) / cols, (hh - (rows - 1) * bar) / rows
        return [box(-ww / 2 + pw / 2 + i * (pw + bar), y0 + ph / 2 + j * (ph + bar), pw, ph) for i in range(cols) for j in range(rows)]
    if st == 'cross':
        bar = 1.2
        pw, ph = (ww - bar) / 2, (hh - bar) / 2
        return [box(sx * (pw + bar) / 2, (y0 + y1) / 2 + sy * (ph + bar) / 2, pw, ph) for sx in (-1, 1) for sy in (-1, 1)]
    if st == 'arch' and hh > ww / 2 + 2:
        r = ww / 2
        bh = hh - r
        return [box(0, y0 + bh / 2, ww, bh), cyl(y0 + bh, r)]
    return [box(0, (y0 + y1) / 2, ww, hh)]


def iw_span(p, iw, t, w, d):
    iwT = p.get('iwT', 1.6)
    half = ((w - 2 * t) if iw['axis'] == 'x' else (d - 2 * t)) / 2
    lim = max(0, ((d - 2 * t) if iw['axis'] == 'x' else (w - 2 * t)) / 2 - iwT / 2)
    if 'a0' in iw:
        a0, a1 = iw['a0'], iw['a1']
    else:
        ln = iw['len'] if iw.get('len', 0) > 0 else 2 * half
        c = iw.get('c', 0)
        a0, a1 = c - ln / 2, c + ln / 2
    if a0 > a1:
        a0, a1 = a1, a0
    return max(-half, a0), min(half, a1), max(-lim, min(lim, iw['pos']))


def solid_under(planes, fx, fy, z0, ztop, shift):
    """CAD 座標（Z 向上）：footprint ±fx × ±fy，位於所有屋頂平面（下移 shift）之下。
    平面（網頁 3D 座標）y = a*x + b*z + c  →  CAD：Z = a*X - b*Y + c。"""
    s = Pos(0, 0, (z0 + ztop) / 2) * Box(2 * fx, 2 * fy, ztop - z0)
    for pl in planes:
        a, b, c = pl['a'], pl['b'], pl['c']
        n = Vector(-a, b, 1).normalized()
        hs = (Pos(0, 0, 3000) * Box(6000, 6000, 6000)).moved(Location(Plane(origin=(0, 0, c - shift), z_dir=n)))
        s = s - hs
    return s


def top_y(planes, x, z):
    return min(pl['a'] * x + pl['b'] * z + pl['c'] for pl in planes)


def make_lamp(p):
    w, d, H, t = p['width'], p['depth'], p['wallH'], p['wall']
    if p.get('plateMode'):  # 牆高 < 3mm：平板
        plate = Box(w, d, t, align=(Align.CENTER, Align.CENTER, MIN))
        for x, z, dia, shp, rot in lamp_list(p, t):
            plate = plate - lamp_cutter(x, z, dia, shp, rot, t * 3, t / 2)
        return plate
    roof = p['roof']
    R = 0 if roof == 'flat' else p['rise']
    swap = w > d
    W, D = (d, w) if swap else (w, d)
    planes, v = p['roofPlanes'], p['roofV']
    eX, eZ = p.get('eaveX', 0), p.get('eaveZ', 0)
    ytop = H + R + 6

    # 本體（牆）：外框柱體在屋頂下緣之下，扣掉底部開口的空腔
    body = solid_under(planes, W / 2, D / 2, 0, ytop, v) - solid_under(planes, W / 2 - t, D / 2 - t, -3, ytop, v - 0.5)
    # 屋頂厚板（含外伸）：頂面與下緣之間
    fx, fy = W / 2 + eX, D / 2 + eZ
    z0 = max(-3, min(top_y(planes, cx, cz) for cx in (-fx, fx) for cz in (-fy, fy)) - v - 3)
    slab = solid_under(planes, fx, fy, z0, ytop, 0) - solid_under(planes, fx, fy, z0, ytop, v)
    if swap:
        body = body.rotate(Axis.Z, 90)
        slab = slab.rotate(Axis.Z, 90)
    for ex in p.get('roofExtras', []):  # 屋脊蓋、煙囪（最終座標：網頁 y→Z、網頁 z→−Y）
        slab = slab + Pos(ex['x'], -ex['z'], (ex['y0'] + ex['y1']) / 2) * Box(ex['w'], ex['d'], ex['y1'] - ex['y0'])
    if p.get('lampOn', True) and p.get('lampTarget', 'floor') == 'roof':
        top = H + R + 10
        for x, z, dia, shp, rot in lamp_list(p, t):
            slab = slab - lamp_cutter(x, z, dia, shp, rot, top * 2, top / 2)
    shell = body

    for wd in p.get('wins', []):
        for cut in win_cutters(wd, w, d, t):
            shell = shell - cut

    # 地板／樓板（嵌入外牆 0.25mm）；燈孔（預設）開在底層地板
    floors = max(1, int(round(p.get('floors', 1))))
    Hf = p.get('floorH', H)
    FT = p.get('floorT', 2)
    levels = ([0] if p.get('floorEff', p.get('floorOn')) else []) + (list(range(1, floors)) if p.get('slabOn') else [])
    for f in levels:
        slab_f = Pos(0, 0, f * Hf + FT / 2) * Box(w - 2 * t + 0.5, d - 2 * t + 0.5, FT)
        if f == 0 and p.get('lampOn', True) and p.get('lampTarget', 'floor') != 'roof':
            for x, z, dia, shp, rot in lamp_list(p, t):
                slab_f = slab_f - lamp_cutter(x, z, dia, shp, rot, FT * 3, FT / 2)
        for hb in p.get('stairBoxes', {}).get('holes', []):
            if hb['level'] == f:
                slab_f = slab_f - Pos(hb['cx'], -hb['cz'], hb['cy']) * Box(hb['sx'], hb['sz'], hb['sy'])
        shell = shell + slab_f
    for sb in p.get('stairBoxes', {}).get('steps', []) + p.get('stairBoxes', {}).get('rails', []):  # 樓梯踏步、平台、扶手
        shell = shell + Pos(sb['cx'], -sb['cz'], sb['cy']) * Box(sb['sx'], sb['sz'], sb['sy'])

    # 窗框＋窗台（外加實體，嵌入牆面 0.3mm）
    if p.get('frameOn'):
        fw, fd = p.get('frameW', 2), p.get('frameD', 1.2)
        for wd in p.get('wins', []):
            door = wd['y0'] <= 0.01
            y0 = wd['y0']
            y1 = y0 + wd['h']
            c, ww, wall = wd['c'], wd['w'], wd['wall']
            zw = wall in ('front', 'back')
            surf = {'front': -d / 2, 'back': d / 2, 'left': -w / 2, 'right': w / 2}[wall]
            dr = {'front': -1, 'back': 1, 'left': -1, 'right': 1}[wall]

            def bar(a, zc, wid, h, prot):
                th = prot + 0.3
                off = surf + dr * (prot - 0.3) / 2
                if zw:
                    return Pos(c + a, off, zc) * Box(wid, th, h)
                return Pos(off, -(c + a), zc) * Box(th, wid, h)

            bars = [bar(0, y1 + fw / 2, ww + 2 * fw, fw, fd),
                    bar(-(ww / 2 + fw / 2), (y0 + y1) / 2, fw, wd['h'], fd),
                    bar(ww / 2 + fw / 2, (y0 + y1) / 2, fw, wd['h'], fd)]
            if not door:
                bars.append(bar(0, y0 - fw / 2, ww + 2 * fw, fw, fd + 1.2 if p.get('sillOn', True) else fd))
            for bb in bars:
                shell = shell + bb

    # 室內牆：獨立樓層圖層（floor）或舊版貫穿；先挖門，再與外殼融合（兩端嵌入 0.25mm）
    for iw in p.get('iwalls', []):
        lo, hi, pos = iw_span(p, iw, t, w, d)
        if hi - lo < 2:
            continue
        iwT = p.get('iwT', 1.6)
        lo -= 0.25
        hi += 0.25
        L, mid = hi - lo, (lo + hi) / 2
        fl = iw.get('floor')
        if fl is None:
            yb, yt, fs = 0, H, list(range(floors))
        else:
            fl = max(0, min(floors - 1, int(fl)))
            yb, yt, fs = fl * Hf, (fl + 1) * Hf + (0.3 if (fl < floors - 1 and p.get('slabOn')) else 0), [fl]
        hh = yt - yb
        wall = Pos(mid, -pos, yb + hh / 2) * Box(L, iwT, hh) if iw['axis'] == 'x' else Pos(pos, -mid, yb + hh / 2) * Box(iwT, L, hh)
        for f in fs:
            for dr in iw.get('doors', []):
                y0 = f * Hf
                y1 = y0 + min(dr['h'], Hf - 1.5)
                z0 = -2 if y0 <= 0.01 else y0
                zc, zh = (z0 + y1) / 2, y1 - z0
                cut = (Pos(dr['c'], -pos, zc) * Box(dr['w'], iwT * 3, zh)) if iw['axis'] == 'x' \
                    else (Pos(pos, -dr['c'], zc) * Box(iwT * 3, dr['w'], zh))
                wall = wall - cut
        shell = shell + wall

    # 周邊小型建築（附屬車庫、工具棚、門廊、車棚）：各自以同一套屋頂平面組建構後融合到本體
    for an in p.get('annexes', []):
        sub = dict(an['p'])
        sub.update({'lampOn': False, 'roofSplit': False, 'iwalls': [], 'wins': [], 'stairs': [], 'floorEff': False,
                    'frameOn': False, 'part': 'all', 'stairBoxes': {}, 'annexes': [], 'roofExtras': []})
        if an.get('roofOnly'):
            sub['roofSplit'] = True
            sub['part'] = 'roof'
        shp = make_lamp(sub)
        if an.get('door'):
            dd = an['door']
            shp = shp - Pos(0, -an['fz'] / 2, dd['h'] / 2) * Box(dd['w'], sub['wall'] * 4, dd['h'])
        shp = Pos(an['cx'], -an['cz'], 0) * shp
        for pb in an.get('posts', []):
            shp = shp + Pos(pb['cx'], -pb['cz'], (pb['y0'] + pb['y1']) / 2) * Box(pb['sx'], pb['sz'], pb['y1'] - pb['y0'])
        if an.get('deck'):
            dk = an['deck']
            shp = shp + Pos(dk['cx'], -dk['cz'], (dk['y0'] + dk['y1']) / 2) * Box(dk['sx'], dk['sz'], dk['y1'] - dk['y0'])
        shell = shell + shp

    # 屋頂分離：本體與屋頂各自為獨立實體
    part = p.get('part', 'all')
    if p.get('roofSplit'):
        if part == 'roof':
            return slab
        if part == 'body':
            return shell
        return Compound([shell, slab])
    shell = shell + slab
    return shell


def rnd(i, j):
    s = math.sin(i * 12.9898 + j * 78.233) * 43758.5453
    return s - math.floor(s)


def make_brick(p):
    pw, ph, relief, base = p['pw'], p['ph'], p['relief'], p['pbase']
    L, Hb, m = 18.0, 5.4, 1.0
    solid = Box(pw, ph, base, align=(MIN, MIN, MIN))
    rows = int(math.ceil(ph / (Hb + m)))
    for r in range(rows):
        off = (r % 2) * (L + m) / 2
        col = -1
        x = -off
        while x < pw:
            col += 1
            x0, x1 = max(0, x), min(pw, x + L)
            y0, y1 = r * (Hb + m), min(ph, r * (Hb + m) + Hb)
            if x1 - x0 >= 1.0 and y1 - y0 >= 1.0:
                h = relief * (0.85 + 0.15 * rnd(col, r))
                b = Box(x1 - x0, y1 - y0, h, align=(MIN, MIN, MIN)).translate((x0, y0, base))
                try:
                    cm = min(0.3, h * 0.45, (x1 - x0) * 0.2, (y1 - y0) * 0.2)
                    b = b.chamfer(cm, None, b.faces().sort_by(Axis.Z)[-1].edges())
                except Exception:
                    pass
                solid = solid + b
            x += L + m
    return solid


def main():
    out = sys.argv[1]
    req = json.load(sys.stdin)
    kind, p = req['kind'], req['p']
    part = make_lamp(p) if kind == 'lamp' else make_brick(p)
    export_step(part, out)


if __name__ == '__main__':
    main()
