# UV layout of the Prussian shako texture set (2048 x 2048). Single source of truth shared by
# build_shako_production.py (UV assignment) and generate_shako_textures_prod.py (texture painting).
# Coordinates are pixels with top-left origin. Densities in pixels per metre.
TEX = 2048
D_BIG = 1800.0          # body, band, binding, crown, visor, strap
D_LINING = 700.0        # inside (rarely seen)
D_COCKADE = 120.0       # pixels per cockade radius (CR) -> ~5300 px/m
D_LOOP = 4000.0
D_CIPHER = 2400.0
D_BUTTON = 28.0         # pixels per button radius

# body islands: (centre x, bottom y) of each unrolled strip; v grows upwards (towards smaller y)
BAND = dict(cx=770, ybot=424, box=(20, 360, 1500, 66))
FELT = dict(cx=770, ybot=340, box=(20, 20, 1500, 322))
BINDING = dict(cx=790, ybot=488, box=(20, 440, 1540, 50))
CROWN = dict(cx=1230, cy=780, box=(1018, 540, 424, 480))
LINING = dict(cx=300, ybot=965, box=(20, 820, 560, 150))
CEILING = dict(cx=690, cy=920, box=(600, 820, 180, 200))
VISOR_TOP = dict(cx=330, yroot=1272, box=(20, 1140, 620, 134))      # outer rows are ~0.30 m long
VISOR_BOTTOM = dict(cx=970, yroot=1272, box=(660, 1140, 620, 134))
VISOR_EDGE = dict(cx=650, y0=1290, box=(20, 1288, 1260, 14))
VISOR_ROOT = dict(cx=650, y0=1310, box=(20, 1308, 1260, 8))
COCKADE_FRONT = dict(cx=1628, cy=648, box=(1500, 520, 256, 256))
COCKADE_SKIRT = dict(x0=1500, y0=800, w=430, h=10, box=(1500, 798, 434, 14))
COCKADE_BACK = dict(cx=1840, cy=580, scale=55.0, box=(1780, 520, 120, 120))
LOOP_FRONT = dict(cx=1816, y0=664, box=(1780, 660, 72, 112))
LOOP_BACK = dict(cx=1890, y0=664, box=(1858, 660, 64, 112))
LOOP_SIDE = dict(xa=1930, xb=1942, w=6, y0=664, box=(1928, 660, 22, 112))
CIPHER = dict(cx=1610, cy=885, box=(1500, 820, 222, 130))
BUTTON = dict(cx=1772, cy=932, box=(1740, 900, 64, 64))
STRAP_OUTER = dict(x0=20, y0=1040, box=(20, 1036, 1020, 30))
STRAP_INNER = dict(x0=20, y0=1072, box=(20, 1068, 1020, 30))
STRAP_SIDE_R = dict(x0=20, y0=1104, box=(20, 1100, 1020, 10))
STRAP_SIDE_L = dict(x0=20, y0=1114, box=(20, 1110, 1020, 10))
SMALL = dict(x0=1100, y0=1040, cell=24, size=20, cols=38)     # small caps (hidden or tiny end faces)
# everything below y = 1330 (and the free block x 20-1000, y 600-800) is RESERVED for variant parts
# (e.g. eagle plate, Guard star) - see docs/specs/shako_variantes_plano.md
