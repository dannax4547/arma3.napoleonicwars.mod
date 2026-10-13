# Read-only: statistics of the bone weights stored in an MLOD LOD (selection byte per point).
# Reports how many bone selections each point belongs to, which byte values occur, and the bones used.
#   python inspect_weights.py <file.p3d> [lod_index] [skeleton_bones_csv]
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p3d_mlod import read_mlod

path = sys.argv[1]
li = int(sys.argv[2]) if len(sys.argv) > 2 else 0
lod = read_mlod(path)[li]
npts = len(lod["points"])

# Bone names of OFP2_ManSkeleton (Arma 3 Samples model.cfg), compared case-insensitively
BONES = """Pelvis Spine Spine1 Spine2 Spine3 Camera weapon launcher neck neck1 head
LeftShoulder LeftArm LeftArmRoll LeftForeArm LeftForeArmRoll LeftHand LeftHandRing LeftHandRing1 LeftHandRing2
LeftHandRing3 LeftHandPinky1 LeftHandPinky2 LeftHandPinky3 LeftHandMiddle1 LeftHandMiddle2 LeftHandMiddle3
LeftHandIndex1 LeftHandIndex2 LeftHandIndex3 LeftHandThumb1 LeftHandThumb2 LeftHandThumb3
RightShoulder RightArm RightArmRoll RightForeArm RightForeArmRoll RightHand RightHandRing RightHandRing1
RightHandRing2 RightHandRing3 RightHandPinky1 RightHandPinky2 RightHandPinky3 RightHandMiddle1 RightHandMiddle2
RightHandMiddle3 RightHandIndex1 RightHandIndex2 RightHandIndex3 RightHandThumb1 RightHandThumb2 RightHandThumb3
LeftUpLeg LeftUpLegRoll LeftLeg LeftLegRoll LeftFoot LeftToeBase RightUpLeg RightUpLegRoll RightLeg RightLegRoll
RightFoot RightToeBase""".split()
bones_lc = {b.lower() for b in BONES}

proxy_pts = set()
for n, blob in lod["selections"].items():
    if n.startswith("proxy:") or n.startswith("-"):
        proxy_pts.update(i for i, b in enumerate(blob) if b)

used = [n for n in lod["selections"] if n.lower() in bones_lc]
per_point = [[] for _ in range(npts)]
values = collections.Counter()
for n in used:
    blob = lod["selections"][n]
    for i in range(npts):
        b = blob[i]
        if b:
            per_point[i].append((n, b))
            values[b] += 1

body = [i for i in range(npts) if i not in proxy_pts]
hist = collections.Counter(len(per_point[i]) for i in body)
print(f"{os.path.basename(path)} LOD {li}: {npts} points ({len(body)} outside proxies); bone selections used: {len(used)}")
print("bones per point (histogram):", dict(sorted(hist.items())))
print("distinct weight byte values:", len(values), " most common:", values.most_common(12))
multi = [i for i in body if len(per_point[i]) >= 2][:8]
for i in multi:
    print(f"  point {i}: " + ", ".join(f"{n}={b}" for n, b in per_point[i]))
missing = [b for b in BONES if b.lower() not in {u.lower() for u in used}]
print("skeleton bones without a selection in this LOD:", ", ".join(missing))
