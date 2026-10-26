# Brass mask of a mod-atlas region for trace_badge.py (2026-10-20, Rhine Raupenhelm plates). trace_badge.py reads an
# outline either from the alpha cut-out or from dark ink on a WHITE background; the Wuerttemberg / Bavarian helmet plates
# lie on grey or black leather instead, so this writes a full-size copy of the atlas that is white everywhere except the
# brass of the box (black): brass = warm (R - B high) and not too dark. Small specks are removed and holes closed by a
# few rounds of majority filtering. The box keeps its atlas coordinates, so the traced JSON maps straight back to the
# atlas (UV "arte" of blockout scripts).
#   blender -b --factory-startup --python mascara_latao.py -- <atlas png> <x0> <y0> <x1> <y1> <out png> [warm=0.06] [lum=0.08]
import bpy, sys
import numpy as np

a = sys.argv[sys.argv.index("--") + 1:]
SRC, (X0, Y0, X1, Y1), OUT = a[0], map(int, a[1:5]), a[5]
OPT = dict(x.split("=", 1) for x in a[6:] if "=" in x)
WARM, LUM = float(OPT.get("warm", 0.06)), float(OPT.get("lum", 0.08))
im = bpy.data.images.load(SRC)
W, H = im.size
px = np.array(im.pixels[:], np.float32).reshape(H, W, 4)[::-1]          # y down
c = px[Y0:Y1, X0:X1, :3]
ink = ((c[..., 0] - c[..., 2]) > WARM) & (c.mean(axis=2) > LUM)
for _ in range(3):                                                       # majority filter 3x3
    p = np.pad(ink.astype(np.int32), 1)
    s = sum(p[1 + dy:p.shape[0] - 1 + dy, 1 + dx:p.shape[1] - 1 + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1))
    ink = s >= 5


def grow(m, r):
    for _ in range(r):
        p = np.pad(m, 1)
        m = p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]
    return m


def shrink(m, r):
    return ~grow(~m, r)


def components(m):
    """4-connected labels (small boxes: plain flood fill)."""
    lab = np.zeros(m.shape, np.int32); n = 0
    for y, x in zip(*np.nonzero(m)):
        if lab[y, x]:
            continue
        n += 1; st = [(y, x)]; lab[y, x] = n
        while st:
            cy, cx = st.pop()
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < m.shape[0] and 0 <= nx < m.shape[1] and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n; st.append((ny, nx))
    return lab, n


CLOSE = int(OPT.get("fecho", 0))                     # closing radius (px): joins crown and oval of a plate
if CLOSE:
    ink = shrink(grow(ink, CLOSE), CLOSE)
lab, n = components(ink)                             # keep the largest piece (chains, specks out)
if n > 1:
    sizes = np.bincount(lab.ravel())[1:]
    ink = lab == 1 + int(np.argmax(sizes))
lab, n = components(~ink)                            # fill holes: background not connected to the border
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
ink |= (lab > 0) & ~np.isin(lab, list(border))
out = np.ones((H, W, 4), np.float32)
out[Y0:Y1, X0:X1, :3] = np.where(ink[..., None], 0.0, 1.0)
o = bpy.data.images.new("mascara", W, H, alpha=False)
o.pixels.foreach_set(out[::-1].ravel())
o.filepath_raw = OUT; o.file_format = "PNG"; o.save()
print(f"MASCARA {X1 - X0}x{Y1 - Y0}: {int(ink.sum())} texels de latao ({100 * ink.mean():.0f} %) -> {OUT}")
