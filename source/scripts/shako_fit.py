# Approved fit and dimensions of the Prussian shako (blockout approved by the user on 2026-10-09).
# Single source of truth for the production scripts. Values are derived from:
#   - spec docs/specs/shako_prussiano_infantaria.md v1.1 (photo R2 proportions, base width 0.180 m assumed)
#   - the official head band measured on Arma 3 Samples A3_headgear_example.p3d (see docs/reports/shako_pruss_blockout.md)
import math, os
import numpy as np
from mathutils import Matrix, Vector
from p3d_mlod import read_mlod, to_blender

SPEC_BASE_W, SPEC_H, SPEC_TOP_W = 0.180, 0.200, 0.243
SPEC = dict(band=0.025, binding=0.010, cockade_r=0.022, cockade_z=0.175, loop_w=0.014, loop_bottom=0.125,
            cipher_w=0.081, cipher_h=0.077, cipher_z=0.081, button_r=0.007, button_z=0.012, visor_chord=0.162)
DEPTH_RATIO = 1.13                  # assumption (no side view)
VISOR_LEN, VISOR_DROP = 0.068, math.radians(55)   # approved with the blockout
TILT = math.radians(8)              # approved with the blockout (back lower)
WALL, CLEAR = 0.004, 0.002


def compute(samples_dir):
    cap = read_mlod(os.path.join(samples_dir, "A3_headgear_example.p3d"))[0]
    cp = np.array([to_blender(p) for p in cap["points"]])
    zmin = cp[:, 2].min()
    crown = cp[(cp[:, 2] > zmin + 0.02) & (cp[:, 2] < zmin + 0.10) & (cp[:, 1] > -0.115)]
    head_hw = max(abs(crown[:, 0].min()), crown[:, 0].max())
    y_front, y_back = crown[:, 1].min(), crown[:, 1].max()
    head_cy, head_hd = (y_front + y_back) / 2, (y_back - y_front) / 2
    z_forehead = cp[(cp[:, 1] < y_front + 0.02) & (cp[:, 1] > -0.115), 2].min()
    z_head_top = cp[:, 2].max()
    base_hw = max(SPEC_BASE_W / 2, head_hw + WALL + CLEAR)
    k = base_hw / (SPEC_BASE_W / 2)
    base_hd = max(base_hw * DEPTH_RATIO, head_hd + WALL + CLEAR)
    top_hw = SPEC_TOP_W / 2 * k
    f = dict(head_hw=head_hw, head_cy=head_cy, head_hd=head_hd, z_forehead=z_forehead, z_head_top=z_head_top,
             k=k, H=SPEC_H * k, base_hw=base_hw, base_hd=base_hd, top_hw=top_hw, top_hd=top_hw * base_hd / base_hw,
             S={key: v * k for key, v in SPEC.items()})
    f["root"] = Matrix.Translation(Vector((0.0, head_cy, z_forehead - 0.004))) @ Matrix.Rotation(-TILT, 4, 'X')
    return f
