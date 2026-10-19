# Writes the text sources of the in-game TEST addon hcl_uk (British infantry 1812-1815): config.cpp, model.cfg and the
# materials (.rvmat). Same classes and conventions as gen_config_fr.py (copied structure; that file is left
# untouched): every class written out, no macros; the skeleton part of model.cfg is taken from the Prussian addon's
# model.cfg (copied from the official Samples). Display names in English (nomes_en_uk.py).
#   python gen_config_uk.py <project root>
# The variant JSONs are read next to this script (source/textures/hcl_uniforme_uk in the repository, which may be a
# git worktree); everything is written under <project root>.
import sys, os, json, re

ROOT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
JS = os.path.join(HERE, "..", "textures", "hcl_uniforme_uk")
SRC = os.path.join(ROOT, r"source\addon\hcl\hcl_uk")
os.makedirs(os.path.join(SRC, "data"), exist_ok=True)
P = r"\hcl\hcl_uk"
GROUPS = []                        # (variants, p3d, soldier base class, nation tag of the class names)
for fn, p3d, base, nat in (("variantes_uk_linha.json", "hcl_u_uk1812_linha", "HCL_UK1812_Soldado_Base", "UK1812"),
                           ("variantes_uk_flanco.json", "hcl_u_uk1812_flanco", "HCL_UK1812_Soldado_Flanco_Base", "UK1812"),
                           ("variantes_uk_rifles.json", "hcl_u_uk1812_rifles", "HCL_UK1812_Soldado_Rifles_Base", "UK1812"),
                           ("variantes_uk_kilt.json", "hcl_u_uk1812_kilt", "HCL_UK1812_Soldado_Kilt_Base", "UK1812"),
                           # Portugal (docs/specs/portugal_1812.md): 24 line regiments, 12 Cacadores battalions
                           ("variantes_por_linha.json", "hcl_u_por1812_linha", "HCL_POR1812_Soldado_Base", "POR1812"),
                           ("variantes_por_cacadores.json", "hcl_u_por1812_cacadores", "HCL_POR1812_Soldado_Cacadores_Base",
                            "POR1812"),
                           # Brunswick 1815 (docs/specs/kgl_brunswick_1815.md section 4): black dolman B01..B08
                           ("variantes_bru_dolman.json", "hcl_u_bru1815_dolman", "HCL_BRU1815_Soldado_Base", "BRU1815"),
                           # KGL and Hanover (kgl_brunswick_1815.md 2-3): the British / Portuguese meshes, new textures
                           ("variantes_kgl_linha.json", "hcl_u_uk1812_linha", "HCL_KGL1812_Soldado_Base", "KGL1812"),
                           ("variantes_kgl_flanco.json", "hcl_u_uk1812_flanco", "HCL_KGL1812_Soldado_Flanco_Base", "KGL1812"),
                           ("variantes_kgl_ligeira.json", "hcl_u_uk1812_rifles", "HCL_KGL1812_Soldado_Ligeira_Base", "KGL1812"),
                           ("variantes_han.json", "hcl_u_por1812_linha", "HCL_HAN1815_Soldado_Base", "HAN1815")):
    GROUPS.append((json.load(open(os.path.join(JS, fn), encoding="utf-8")), p3d, base, nat))
# caps: P3D tag -> class suffix (blockout_shako_uk.py VARIANTS)
CAPS = [("belgic_batalhao", "Belgic_Batalhao"), ("belgic_granadeiro", "Belgic_Granadeiro"), ("belgic_ligeira", "Belgic_Ligeira"),
        ("stovepipe_batalhao", "Stovepipe_Batalhao"), ("stovepipe_granadeiro", "Stovepipe_Granadeiro"),
        ("stovepipe_ligeira", "Stovepipe_Ligeira"), ("stovepipe_28th", "Stovepipe_28th"), ("stovepipe_rifles", "Stovepipe_Rifles")]
HEAD = [(f"hcl_h_uk_{tg}", f"hcl_shako_uk_{tg}", f"HCL_H_UK1812_{cls}", None) for tg, cls in CAPS]
# Highland feather bonnet (bonnet_highland_uk.py; textures hcl_uk_bonnet_highland_*)
HEAD.append(("hcl_h_uk_bonnet_highland", "hcl_uk_bonnet_highland", "HCL_H_UK1812_Bonnet_Highland", None))
# Portuguese stovepipes: one class per regiment / battalion, the number band in the hidden selection "numero"
# (gen_numeros_por.py: hcl_por_numero_lNN / cNN)
for tg, cls in (("por_batalhao", "Batalhao"), ("por_granadeiro", "Granadeiro"), ("por_ligeira", "Ligeira")):
    for n in range(1, 25):
        HEAD.append((f"hcl_h_uk_{tg}", f"hcl_shako_uk_{tg}", f"HCL_H_POR1812_Stovepipe_{cls}_{n:02d}", f"hcl_por_numero_l{n:02d}"))
# Brunswick "Kiwer" shakos; the line cap has one class per battalion (number band, hcl_bru_numero_b1..b3)
for tg, cls in (("bru_leib", "Leib"), ("bru_ligeiro", "Ligeiro"), ("bru_avantgarde", "Avantgarde")):
    HEAD.append((f"hcl_h_uk_{tg}", f"hcl_shako_uk_{tg}", f"HCL_H_BRU1815_Kiwer_{cls}", None))
for n in range(1, 4):
    HEAD.append(("hcl_h_uk_bru_linha", "hcl_shako_uk_bru_linha", f"HCL_H_BRU1815_Kiwer_Linha_{n}", f"hcl_bru_numero_b{n}"))
# KGL line Belgic caps: one class per battalion 1-8 (brass number band, the Portuguese brass numbers l01..l08);
# KGL light battalions: the 95th's stovepipe (bugle, green cords); Hanover: stovepipe with the oval GR plate
for tg, cls in (("kgl_belgic_batalhao", "Batalhao"), ("kgl_belgic_granadeiro", "Granadeiro"), ("kgl_belgic_ligeira", "Ligeira")):
    for n in range(1, 9):
        HEAD.append((f"hcl_h_uk_{tg}", f"hcl_shako_uk_{tg}", f"HCL_H_KGL1812_Belgic_{cls}_{n}", f"hcl_por_numero_l{n:02d}"))
HEAD.append(("hcl_h_uk_stovepipe_rifles", "hcl_shako_uk_stovepipe_rifles", "HCL_H_KGL1812_Stovepipe_Ligeira", None))
HEAD.append(("hcl_h_uk_han_stovepipe", "hcl_shako_uk_han_stovepipe", "HCL_H_HAN1815_Stovepipe", None))
for n in range(1, 13):
    HEAD.append(("hcl_h_uk_por_cacadores", "hcl_shako_uk_por_cacadores", f"HCL_H_POR1812_Stovepipe_Cacadores_{n:02d}",
                 f"hcl_por_numero_c{n:02d}"))
V_P3D, B_P3D = "hcl_v_uk1812_correame", "hcl_b_uk1812_mochila"

# ---------------------------------------------------------------- config.cpp
o = []
w = o.append
w("// Historical Clothing - TEST addon hcl_uk (PBO prefix hcl\\hcl_uk). Personal use, in-game test only.")
w("// Generated by source/scripts/gen_config_uk.py, same base classes as hcl_pruss / hcl_fr (checked in the game")
w("// configs and in the official sample Test_Character_01). No faction: the soldier classes are scope 1 (an Arma")
w("// uniform needs a soldier model); the items are scope 2 (Arsenal).")
w("")
w("class CfgPatches\n{\n\tclass HCL_UK_Teste\n\t{")
w('\t\tauthor = "Historical Clothing";')
units = ["HCL_B_UK1812_Mochila", "HCL_B_BRU1815_Tornister"]
w("\t\tunits[] = {" + ", ".join(f'"{x}"' for x in units) + "};")
weapons = [f"HCL_U_{nat}_{v}" for g, _, _, nat in GROUPS for v in sorted(g)] + [h[2] for h in HEAD] + \
    ["HCL_V_UK1812_Correame", "HCL_V_UK1812_Correame_Preto"]
w("\t\tweapons[] = {" + ", ".join(f'"{x}"' for x in weapons) + "};")
w("\t\trequiredVersion = 0.1;")
w('\t\trequiredAddons[] = {"A3_Characters_F", "A3_Weapons_F_Ammoboxes"};')
w("\t};\n};\n")

w("class CfgVehicles\n{")
w("\tclass B_Soldier_base_F;\n\tclass Bag_Base;\n")
first = True
nsold = 0
for var, p3d, base, nat in GROUPS:
    ids = sorted(var)
    parent = "B_Soldier_base_F" if first else "HCL_UK1812_Soldado_Base"
    w(f"\tclass {base}: {parent}\n\t{{")
    if first:
        w('\t\tauthor = "Historical Clothing";')
        w("\t\tscope = 1;")
    w('\t\tdisplayName = "x";')
    w(f'\t\tmodel = "{P}\\{p3d}.p3d";')
    if first:
        w("\t\tmodelSides[] = {0, 1, 2, 3};")
    w(f'\t\tuniformClass = "HCL_U_{nat}_{ids[0]}";')
    if first:
        w('\t\thiddenSelections[] = {"Camo"};')
    w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{var[ids[0]]["prefixo"]}_co.paa"}};')
    if first:
        w('\t\tweapons[] = {"Throw", "Put"};\n\t\trespawnWeapons[] = {"Throw", "Put"};')
        w("\t\tmagazines[] = {};\n\t\trespawnMagazines[] = {};\n\t\tItems[] = {};\n\t\tRespawnItems[] = {};")
        w('\t\tlinkedItems[] = {"ItemMap", "ItemCompass", "ItemWatch"};')
        w('\t\trespawnLinkedItems[] = {"ItemMap", "ItemCompass", "ItemWatch"};')
    w("\t};")
    for v in ids:
        w(f"\tclass HCL_{nat}_Soldado_{v}: {base}\n\t{{")
        w('\t\tdisplayName = "x";')
        w(f'\t\tuniformClass = "HCL_U_{nat}_{v}";')
        w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{var[v]["prefixo"]}_co.paa"}};')
        w("\t};")
        nsold += 1
    first = False
w("\tclass HCL_B_UK1812_Mochila: Bag_Base\n\t{")
w('\t\tauthor = "Historical Clothing";\n\t\tscope = 2;')
w('\t\tdisplayName = "x";')
w('\t\tpicture = "\\A3\\Weapons_F\\Ammoboxes\\Bags\\data\\ui\\backpack_CA.paa";')
w(f'\t\tmodel = "{P}\\{B_P3D}.p3d";')
w('\t\thiddenSelections[] = {"camo"};')
w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{B_P3D}_co.paa"}};')
w("\t\tmaximumLoad = 160;\n\t\tmass = 20;")
w("\t};")
# Brunswick 1815: the same knapsack, black, with the white-metal Welfenross on the flap (carimbo_mochila_bru.py;
# Brigade-Uniformtafel Nr. 176)
w("\tclass HCL_B_BRU1815_Tornister: HCL_B_UK1812_Mochila\n\t{")
w('\t\tdisplayName = "x";')
w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\hcl_b_bru1815_mochila_co.paa"}};')
w("\t};")
w("};\n")

w("class CfgWeapons\n{")
w("\tclass ItemCore;\n\tclass UniformItem;\n\tclass Uniform_Base;")
w("\tclass H_HelmetB: ItemCore\n\t{\n\t\tclass ItemInfo;\n\t};")
w("\tclass Vest_Camo_Base: ItemCore\n\t{\n\t\tclass ItemInfo;\n\t};\n")
for var, p3d, base, nat in GROUPS:
    for v in sorted(var):
        w(f"\tclass HCL_U_{nat}_{v}: Uniform_Base\n\t{{")
        w('\t\tauthor = "Historical Clothing";\n\t\tscope = 2;')
        w('\t\tdisplayName = "x";')
        w('\t\tpicture = "\\A3\\characters_f\\data\\ui\\icon_U_BasicBody_ca.paa";')
        w('\t\tmodel = "\\A3\\Characters_F\\Common\\Suitpacks\\suitpack_universal_F.p3d";')
        w('\t\thiddenSelections[] = {"camo"};')
        w('\t\thiddenSelectionsTextures[] = {"\\A3\\Characters_F\\Common\\Suitpacks\\data\\suitpack_soldier_blufor_co.paa"};')
        w("\t\tclass ItemInfo: UniformItem\n\t\t{")
        w('\t\t\tuniformModel = "-";')
        w(f'\t\t\tuniformClass = "HCL_{nat}_Soldado_{v}";')
        w('\t\t\tcontainerClass = "Supply40";\n\t\t\tmass = 40;')
        w("\t\t};\n\t};")
for p3d_base, mat_base, cls, num in HEAD:
    p3d = p3d_base + ".p3d"
    sels = '{"camo", "numero"}' if num else '{"camo"}'
    w(f"\tclass {cls}: H_HelmetB\n\t{{")
    w('\t\tauthor = "Historical Clothing";\n\t\tscope = 2;')
    w('\t\tdisplayName = "x";')
    w('\t\tdescriptionShort = "HCL test - no protection";')
    w('\t\tpicture = "\\A3\\characters_f\\Data\\UI\\icon_H_helmet_plain_ca.paa";')
    w(f'\t\tmodel = "{P}\\{p3d}";')
    w(f'\t\thiddenSelections[] = {sels};')
    texs = f'"{P}\\data\\{mat_base}_co.paa"' + (f', "{P}\\data\\{num}_co.paa"' if num else "")
    w(f'\t\thiddenSelectionsTextures[] = {{{texs}}};')
    w("\t\tclass ItemInfo: ItemInfo\n\t\t{")
    w("\t\t\tmass = 15;")
    w(f'\t\t\tuniformModel = "{P}\\{p3d}";')
    w("\t\t\tmodelSides[] = {0, 1, 2, 3};")
    w(f'\t\t\thiddenSelections[] = {sels};')
    w("\t\t\tclass HitpointsProtectionInfo\n\t\t\t{\n\t\t\t\tclass Head\n\t\t\t\t{")
    w('\t\t\t\t\thitpointName = "HitHead";\n\t\t\t\t\tarmor = 0;\n\t\t\t\t\tpassThrough = 1;')
    w("\t\t\t\t};\n\t\t\t};\n\t\t};\n\t};")
for cls, co in (("HCL_V_UK1812_Correame", V_P3D), ("HCL_V_UK1812_Correame_Preto", V_P3D + "_preto")):
    w(f"\tclass {cls}: Vest_Camo_Base\n\t{{")
    w('\t\tauthor = "Historical Clothing";\n\t\tscope = 2;')
    w('\t\tdisplayName = "x";')
    w('\t\tdescriptionShort = "HCL test - no protection";')
    w('\t\tpicture = "\\A3\\characters_f\\Data\\UI\\icon_V_BandollierB_CA.paa";')
    w('\t\thiddenSelections[] = {"camo"};')
    w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{co}_co.paa"}};')
    w("\t\tclass ItemInfo: ItemInfo\n\t\t{")
    w(f'\t\t\tuniformModel = "{P}\\{V_P3D}.p3d";')
    w('\t\t\thiddenSelections[] = {"camo"};')
    w('\t\t\tcontainerClass = "Supply100";\n\t\t\tmass = 15;')
    w("\t\t};\n\t};")
w("};")
txt = "\n".join(o) + "\n"
assert all(ord(c) < 128 for c in txt), "config must be ASCII"
sys.path.insert(0, HERE)
import nomes_en_uk
txt = nomes_en_uk.apply(txt)
assert 'displayName = "x"' not in txt
open(os.path.join(SRC, "config.cpp"), "w", encoding="ascii", newline="\r\n").write(txt)
print("OK config.cpp", len(txt), "bytes;", len(weapons), "items +", nsold, "soldier classes +", len(units), "backpacks")

# ---------------------------------------------------------------- model.cfg: skeleton from hcl_pruss, our classes
mc = open(os.path.join(ROOT, r"source\addon\hcl\hcl_pruss\model.cfg"), encoding="latin-1").read()
models = list(dict.fromkeys(p3d for _, p3d, _, _ in GROUPS)) + sorted({h[0] for h in HEAD}) + [V_P3D, B_P3D]   # dedupe: KGL / Hanover reuse meshes
mc = re.sub(r"(\tclass hcl_\w+: ArmaMan \{\};\r?\n)+", "".join(f"\tclass {m}: ArmaMan {{}};\n" for m in models), mc)
mc = mc.replace("test addon hcl_pruss", "test addon hcl_uk")
assert all(f"class {m}: ArmaMan" in mc for m in models) and "hcl_pruss" not in mc
open(os.path.join(SRC, "model.cfg"), "w", encoding="ascii", newline="\r\n").write(mc.replace("\r\n", "\n"))
print("OK model.cfg:", len(models), "CfgModels classes")

# ---------------------------------------------------------------- materials (structure of the hcl_pruss materials)
STAGE = """class Stage{n}
{{
	texture="{tex}";
	uvSource="tex";
	class uvTransform
	{{
		aside[]={{1.0,0.0,0.0}};
		up[]={{0.0,1.0,0.0}};
		dir[]={{0.0,0.0,0.0}};
		pos[]={{0.0,0.0,0.0}};
	}};
}};
"""


def rvmat(base, spec, power):
    d = "hcl\\hcl_uk\\data\\"
    s = ["// Historical Clothing - test addon. Structure of the official Arma 3 Samples material",
         '// (Addons\\Test_scope3D_01\\Data\\nodiffuse.rvmat, "Super" shader); textures and colour values are ours.',
         "ambient[]={1,1,1,1};", "diffuse[]={1,1,1,1};", "forcedDiffuse[]={0,0,0,0};", "emmisive[]={0,0,0,1};",
         f"specular[]={{{spec},{spec},{spec},1}};", f"specularPower={power};",
         'PixelShaderID="Super";', 'VertexShaderID="Super";']
    t = "\n".join(s) + "\n"
    t += STAGE.format(n=1, tex=d + base + "_nohq.paa")
    t += STAGE.format(n=2, tex="#(argb,8,8,3)color(0.5,0.5,0.5,0.5,DT)")
    t += STAGE.format(n=3, tex="#(argb,8,8,3)color(1,1,1,0.0,MC)")
    t += STAGE.format(n=4, tex="#(argb,8,8,3)color(1,1,1,1,AS)")
    t += STAGE.format(n=5, tex=d + base + "_smdi.paa")
    t += 'class Stage6\n{\n\ttexture="#(ai,64,64,1)fresnel(1.4,0.1)";\n\tuvSource="none";\n};\n'
    t += STAGE.format(n=7, tex="A3\\Data_f\\env_land_co.tga").replace('\tuvSource="tex";', '\tuseWorldEnvMap=false;\n\tuvSource="tex";')
    return t


MATS = [(p3d, "0.4", 50) for p3d in dict.fromkeys(p3d for _, p3d, _, _ in GROUPS)] + \
    [(m, "0.6", 40) if "bonnet" in m else (m, "1.0", 80) for m in sorted({h[1] for h in HEAD})] + \
    [(V_P3D, "0.6", 60), (B_P3D, "0.6", 60)]
for base, spec, power in MATS:
    open(os.path.join(SRC, "data", base + ".rvmat"), "w", encoding="ascii", newline="\r\n").write(rvmat(base, spec, power))
# number band of the Portuguese caps: flat brass, procedural normal and specular maps (no _nohq / _smdi files)
num_mat = rvmat("x", "1.0", 80).replace("hcl\\hcl_uk\\data\\x_nohq.paa", "#(argb,8,8,3)color(0.5,0.5,1,1,NOHQ)") \
    .replace("hcl\\hcl_uk\\data\\x_smdi.paa", "#(argb,8,8,3)color(1,0.85,0.72,1,SMDI)")
assert "x_nohq" not in num_mat and "x_smdi" not in num_mat
open(os.path.join(SRC, "data", "hcl_por_numero.rvmat"), "w", encoding="ascii", newline="\r\n").write(num_mat)
print("OK", len(MATS) + 1, "rvmat")
