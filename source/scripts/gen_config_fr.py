# Writes the text sources of the in-game TEST addon hcl_fr (French line infantry 1812): config.cpp, model.cfg and the
# materials (.rvmat). Same classes and conventions as gen_config_pruss.py (every class written out, no macros); the
# skeleton part of model.cfg is taken from the Prussian addon's model.cfg (copied from the official Samples).
#   python gen_config_fr.py <project root>
import sys, os, json, re

ROOT = sys.argv[1]
SRC = os.path.join(ROOT, r"source\addon\hcl\hcl_fr")
os.makedirs(os.path.join(SRC, "data"), exist_ok=True)
# variants dir: optional 2nd argument (2026-10-19: a git worktree builds with its own JSONs), default as before
VDIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, r"source\textures\hcl_uniforme_fr")
VAR = json.load(open(os.path.join(VDIR, r"variantes_fr.json"), encoding="utf-8"))
P = r"\hcl\hcl_fr"
ASCII = str.maketrans("áâãàéêíóôõúçÁÂÃÀÉÊÍÓÔÕÚÇ", "aaaaeeiooouc" + "AAAAEEIOOOUC")
# shako P3D tag -> class suffix, display name (technical: company / dress, as in docs/reports/barretina_fr_blockout.md)
SHAKOS = [("fuzileiro_1a_comp", "Fuzileiro_1aComp", "fuzileiro, 1a companhia"),
          ("granadeiro_gala", "Granadeiro_Gala", "granadeiro, gala (plumet)"),
          ("granadeiro_campanha", "Granadeiro_Campanha", "granadeiro, campanha (pompom)"),
          ("voltigeur_gala", "Voltigeur_Gala", "voltigeur, gala (plumet)"),
          ("voltigeur_campanha", "Voltigeur_Campanha", "voltigeur, campanha (pompom)"),
          ("oficial_coronel", "Oficial_Coronel", "oficial, coronel"),
          # lote 2 (2026-10-12): 1810 lozenge plate of the mod art (brass, white metal)
          ("fuzileiro_losango", "Fuzileiro_Losango_1aComp", "fuzileiro, placa em losango, 1a companhia"),
          ("fuzileiro_losango_branco", "Fuzileiro_LosangoBranco_1aComp", "fuzileiro, placa em losango de metal branco, 1a companhia"),
          # lote 3 (2026-10-13): light infantry elite companies (white metal, lozenge plate)
          ("ligeira_carabineiro_gala", "Ligeira_Carabineiro_Gala", "infantaria ligeira, carabineiro, gala"),
          ("ligeira_voltigeur_gala", "Ligeira_Voltigeur_Gala", "infantaria ligeira, voltigeur, gala")]
# headgear entries: (p3d file, material base, class, display name, _co base); texture-only variants reuse a model
HEAD = [(f"hcl_h_fr_{tg}", f"hcl_shako_fr_{tg}", f"HCL_H_Fr1812_{cls}", f"Barretina francesa 1812 - {nome}", f"hcl_shako_fr_{tg}")
        for tg, cls, nome in SHAKOS]
# light infantry carabinier in dark blue instead of red (user 2026-10-19; variantes_cor_shako_fr.py): same model
HEAD.append(("hcl_h_fr_ligeira_carabineiro_gala", "hcl_shako_fr_ligeira_carabineiro_gala", "HCL_H_Fr1812_Ligeira_Carabineiro_Gala_Azul",
             "Barretina francesa 1812 - infantaria ligeira, carabineiro, gala, azul-escuro", "hcl_shako_fr_ligeira_carabineiro_gala_azul"))
# fusilier companies 2-4 (pompom sky blue, aurore, violet; variantes_pompom_fr.py): same model as the 1st company
for tg, cls, nome in (("fuzileiro_1a_comp", "Fuzileiro", "fuzileiro"), ("fuzileiro_losango", "Fuzileiro_Losango", "fuzileiro, placa em losango"),
                      ("fuzileiro_losango_branco", "Fuzileiro_LosangoBranco", "fuzileiro, placa em losango de metal branco")):
    for c in (2, 3, 4):
        co = f"hcl_shako_fr_{tg.replace('1a_comp', f'{c}a_comp')}" if tg.endswith("1a_comp") else f"hcl_shako_fr_{tg}_{c}a_comp"
        HEAD.append((f"hcl_h_fr_{tg}", f"hcl_shako_fr_{tg}", f"HCL_H_Fr1812_{cls}_{c}aComp", f"Barretina francesa 1812 - {nome}, {c}a companhia", co))
# numbered line regiments (numerar_placa_fr.py: the number cut out of the 1812 eagle plate), fusilier model
for n in (18, 46, 57, 84):
    HEAD.append(("hcl_h_fr_fuzileiro_1a_comp", "hcl_shako_fr_fuzileiro_1a_comp", f"HCL_H_Fr1812_Linha_{n:03d}",
                 f"Barretina francesa 1812 - regimento {n}", f"hcl_shako_fr_linha_{n:03d}"))
# Old Guard bearskins (blockout_bonnet_guarda.py): technical names + the unit the user asked for
for tg, cls, nome in (("granadeiro_gala", "Granadeiro_Gala", "granadeiro, gala (placa, cordoes, pluma)"),
                      ("granadeiro_campanha", "Granadeiro_Campanha", "granadeiro, campanha (placa)"),
                      ("cacador_gala", "Cacador_Gala", "cacador, gala (cordoes, pluma)")):
    HEAD.append((f"hcl_h_fr_bonnet_{tg}", f"hcl_bonnet_fr_{tg}", f"HCL_H_Fr1812_Guarda_Bonnet_{cls}",
                 f"Chapeu de pele da Velha Guarda - {nome}", f"hcl_bonnet_fr_{tg}"))
VIDS = sorted(VAR)
# winter: the greatcoat (build_capote_fr.py), its own model and texture set
CAP = json.load(open(os.path.join(ROOT, r"source\textures\hcl_capote_fr\variantes_capote_fr.json"), encoding="utf-8"))
CIDS = sorted(CAP)
U_P3D, V_P3D, B_P3D = "hcl_u_fr1812", "hcl_v_fr1812_correame", "hcl_b_fr1812_havresac"
C_P3D = "hcl_u_fr1812_capote"
# elite companies: the coat with epaulettes (build_casaca_elite_fr.py), its own model and texture set
ELI = json.load(open(os.path.join(VDIR, r"variantes_fr_elite.json"), encoding="utf-8"))
EIDS = sorted(ELI)
E_P3D = "hcl_u_fr1812_elite"
# Old Guard: long-tailed habit (build_uniforme_fr.py hem=0.64 + build_casaca_elite_fr.py), its own model and textures
GUA = json.load(open(os.path.join(VDIR, r"variantes_fr_guarda.json"), encoding="utf-8"))
GIDS = sorted(GUA)
G_P3D = "hcl_u_fr1812_guarda"

# ---------------------------------------------------------------- config.cpp
o = []
w = o.append
w("// Historical Clothing - TEST addon hcl_fr (PBO prefix hcl\\hcl_fr). Personal use, in-game test only.")
w("// Generated by source/scripts/gen_config_fr.py, same base classes as hcl_pruss (checked in the game configs and in")
w("// the official sample Test_Character_01). No faction: the soldier class is scope 1 (an Arma uniform needs a soldier")
w("// model); the items are scope 2 (Arsenal). Names are technical.")
w("")
w("class CfgPatches\n{\n\tclass HCL_Fr_Teste\n\t{")
w('\t\tauthor = "Historical Clothing";')
units = ["HCL_B_Fr1812_Havresac"]
w("\t\tunits[] = {" + ", ".join(f'"{x}"' for x in units) + "};")
weapons = [f"HCL_U_Fr1812_{v}" for v in VIDS] + [f"HCL_U_Fr1812_Capote_{v}" for v in CIDS] + \
    [f"HCL_U_Fr1812_{v}" for v in EIDS] + [f"HCL_U_Fr1812_{v}" for v in GIDS] + \
    [h[2] for h in HEAD] + ["HCL_V_Fr1812_Correame"]
w("\t\tweapons[] = {" + ", ".join(f'"{x}"' for x in weapons) + "};")
w("\t\trequiredVersion = 0.1;")
w('\t\trequiredAddons[] = {"A3_Characters_F", "A3_Weapons_F_Ammoboxes"};')
w("\t};\n};\n")

w("class CfgVehicles\n{")
w("\tclass B_Soldier_base_F;\n\tclass Bag_Base;\n")
w("\tclass HCL_Fr1812_Soldado_Base: B_Soldier_base_F\n\t{")
w('\t\tauthor = "Historical Clothing";')
w("\t\tscope = 1;")
w('\t\tdisplayName = "Soldado frances 1812 (teste HCL)";')
w(f'\t\tmodel = "{P}\\{U_P3D}.p3d";')
w("\t\tmodelSides[] = {0, 1, 2, 3};")
w(f'\t\tuniformClass = "HCL_U_Fr1812_{VIDS[0]}";')
w('\t\thiddenSelections[] = {"Camo"};')
w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{VAR[VIDS[0]]["prefixo"]}_co.paa"}};')
w('\t\tweapons[] = {"Throw", "Put"};\n\t\trespawnWeapons[] = {"Throw", "Put"};')
w("\t\tmagazines[] = {};\n\t\trespawnMagazines[] = {};\n\t\tItems[] = {};\n\t\tRespawnItems[] = {};")
w('\t\tlinkedItems[] = {"ItemMap", "ItemCompass", "ItemWatch"};')
w('\t\trespawnLinkedItems[] = {"ItemMap", "ItemCompass", "ItemWatch"};')
w("\t};")
for v in VIDS:
    w(f"\tclass HCL_Fr1812_Soldado_{v}: HCL_Fr1812_Soldado_Base\n\t{{")
    w(f'\t\tdisplayName = "Soldado frances 1812 {v} (teste HCL)";')
    w(f'\t\tuniformClass = "HCL_U_Fr1812_{v}";')
    w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{VAR[v]["prefixo"]}_co.paa"}};')
    w("\t};")
w("\tclass HCL_Fr1812_Soldado_Capote_Base: HCL_Fr1812_Soldado_Base\n\t{")
w('\t\tdisplayName = "Soldado frances 1812, capote (teste HCL)";')
w(f'\t\tmodel = "{P}\\{C_P3D}.p3d";')
w(f'\t\tuniformClass = "HCL_U_Fr1812_Capote_{CIDS[0]}";')
w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{CAP[CIDS[0]]["prefixo"]}_co.paa"}};')
w("\t};")
for v in CIDS:
    w(f"\tclass HCL_Fr1812_Soldado_Capote_{v}: HCL_Fr1812_Soldado_Capote_Base\n\t{{")
    w(f'\t\tdisplayName = "Soldado frances 1812 capote {v} (teste HCL)";')
    w(f'\t\tuniformClass = "HCL_U_Fr1812_Capote_{v}";')
    w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{CAP[v]["prefixo"]}_co.paa"}};')
    w("\t};")
w("\tclass HCL_Fr1812_Soldado_Elite_Base: HCL_Fr1812_Soldado_Base\n\t{")
w('\t\tdisplayName = "Soldado frances 1812, companhia de elite (teste HCL)";')
w(f'\t\tmodel = "{P}\\{E_P3D}.p3d";')
w(f'\t\tuniformClass = "HCL_U_Fr1812_{EIDS[0]}";')
w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{ELI[EIDS[0]]["prefixo"]}_co.paa"}};')
w("\t};")
for v in EIDS:
    w(f"\tclass HCL_Fr1812_Soldado_{v}: HCL_Fr1812_Soldado_Elite_Base\n\t{{")
    w(f'\t\tdisplayName = "Soldado frances 1812 {v} (teste HCL)";')
    w(f'\t\tuniformClass = "HCL_U_Fr1812_{v}";')
    w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{ELI[v]["prefixo"]}_co.paa"}};')
    w("\t};")
w("\tclass HCL_Fr1812_Soldado_Guarda_Base: HCL_Fr1812_Soldado_Base\n\t{")
w('\t\tdisplayName = "Soldado frances, Velha Guarda (teste HCL)";')
w(f'\t\tmodel = "{P}\\{G_P3D}.p3d";')
w(f'\t\tuniformClass = "HCL_U_Fr1812_{GIDS[0]}";')
w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{GUA[GIDS[0]]["prefixo"]}_co.paa"}};')
w("\t};")
for v in GIDS:
    w(f"\tclass HCL_Fr1812_Soldado_{v}: HCL_Fr1812_Soldado_Guarda_Base\n\t{{")
    w(f'\t\tdisplayName = "Soldado frances {v} (teste HCL)";')
    w(f'\t\tuniformClass = "HCL_U_Fr1812_{v}";')
    w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{GUA[v]["prefixo"]}_co.paa"}};')
    w("\t};")
w("\tclass HCL_B_Fr1812_Havresac: Bag_Base\n\t{")
w('\t\tauthor = "Historical Clothing";\n\t\tscope = 2;')
w('\t\tdisplayName = "[HCL] Mochila francesa 1812 (havresac, teste)";')
w('\t\tpicture = "\\A3\\Weapons_F\\Ammoboxes\\Bags\\data\\ui\\backpack_CA.paa";')
w(f'\t\tmodel = "{P}\\{B_P3D}.p3d";')
w('\t\thiddenSelections[] = {"camo"};')
w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{B_P3D}_co.paa"}};')
w("\t\tmaximumLoad = 160;\n\t\tmass = 20;")
w("\t};")
w("};\n")

w("class CfgWeapons\n{")
w("\tclass ItemCore;\n\tclass UniformItem;\n\tclass Uniform_Base;")
w("\tclass H_HelmetB: ItemCore\n\t{\n\t\tclass ItemInfo;\n\t};")
w("\tclass Vest_Camo_Base: ItemCore\n\t{\n\t\tclass ItemInfo;\n\t};\n")
for v, cls, soldier, label in [(v, f"HCL_U_Fr1812_{v}", f"HCL_Fr1812_Soldado_{v}", VAR[v]) for v in VIDS] + \
        [(v, f"HCL_U_Fr1812_Capote_{v}", f"HCL_Fr1812_Soldado_Capote_{v}", CAP[v]) for v in CIDS] + \
        [(v, f"HCL_U_Fr1812_{v}", f"HCL_Fr1812_Soldado_{v}", ELI[v]) for v in EIDS] + \
        [(v, f"HCL_U_Fr1812_{v}", f"HCL_Fr1812_Soldado_{v}", GUA[v]) for v in GIDS]:
    nome = label.get("curto", label["nome"]).translate(ASCII)
    w(f"\tclass {cls}: Uniform_Base\n\t{{")
    w('\t\tauthor = "Historical Clothing";\n\t\tscope = 2;')
    w(f'\t\tdisplayName = "[HCL] Uniforme frances 1812 {v} - {nome}";')
    w('\t\tpicture = "\\A3\\characters_f\\data\\ui\\icon_U_BasicBody_ca.paa";')
    w('\t\tmodel = "\\A3\\Characters_F\\Common\\Suitpacks\\suitpack_universal_F.p3d";')
    w('\t\thiddenSelections[] = {"camo"};')
    w('\t\thiddenSelectionsTextures[] = {"\\A3\\Characters_F\\Common\\Suitpacks\\data\\suitpack_soldier_blufor_co.paa"};')
    w("\t\tclass ItemInfo: UniformItem\n\t\t{")
    w('\t\t\tuniformModel = "-";')
    w(f'\t\t\tuniformClass = "{soldier}";')
    w('\t\t\tcontainerClass = "Supply40";\n\t\t\tmass = 40;')
    w("\t\t};\n\t};")
for p3d_base, _, cls, nome, co in HEAD:
    p3d = p3d_base + ".p3d"
    w(f"\tclass {cls}: H_HelmetB\n\t{{")
    w('\t\tauthor = "Historical Clothing";\n\t\tscope = 2;')
    w(f'\t\tdisplayName = "[HCL] {nome}";')
    w('\t\tdescriptionShort = "Teste HCL - sem protecao";')
    w('\t\tpicture = "\\A3\\characters_f\\Data\\UI\\icon_H_helmet_plain_ca.paa";')
    w(f'\t\tmodel = "{P}\\{p3d}";')
    w('\t\thiddenSelections[] = {"camo"};')
    w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{co}_co.paa"}};')
    w("\t\tclass ItemInfo: ItemInfo\n\t\t{")
    w("\t\t\tmass = 15;")
    w(f'\t\t\tuniformModel = "{P}\\{p3d}";')
    w("\t\t\tmodelSides[] = {0, 1, 2, 3};")
    w('\t\t\thiddenSelections[] = {"camo"};')
    w("\t\t\tclass HitpointsProtectionInfo\n\t\t\t{\n\t\t\t\tclass Head\n\t\t\t\t{")
    w('\t\t\t\t\thitpointName = "HitHead";\n\t\t\t\t\tarmor = 0;\n\t\t\t\t\tpassThrough = 1;')
    w("\t\t\t\t};\n\t\t\t};\n\t\t};\n\t};")
w("\tclass HCL_V_Fr1812_Correame: Vest_Camo_Base\n\t{")
w('\t\tauthor = "Historical Clothing";\n\t\tscope = 2;')
w('\t\tdisplayName = "[HCL] Correame frances 1812 (teste)";')
w('\t\tdescriptionShort = "Teste HCL - sem protecao";')
w('\t\tpicture = "\\A3\\characters_f\\Data\\UI\\icon_V_BandollierB_CA.paa";')
w('\t\thiddenSelections[] = {"camo"};')
w(f'\t\thiddenSelectionsTextures[] = {{"{P}\\data\\{V_P3D}_co.paa"}};')
w("\t\tclass ItemInfo: ItemInfo\n\t\t{")
w(f'\t\t\tuniformModel = "{P}\\{V_P3D}.p3d";')
w('\t\t\thiddenSelections[] = {"camo"};')
w('\t\t\tcontainerClass = "Supply100";\n\t\t\tmass = 15;')
w("\t\t};\n\t};")
w("};")
txt = "\n".join(o) + "\n"
assert all(ord(c) < 128 for c in txt), "config must be ASCII"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nomes_en
txt = nomes_en.apply(txt)   # English display names (2026-10-13)
open(os.path.join(SRC, "config.cpp"), "w", encoding="ascii", newline="\r\n").write(txt)
print("OK config.cpp", len(txt), "bytes;", len(weapons), "items +", len(VIDS) + len(CIDS) + len(EIDS) + len(GIDS), "soldier classes +", len(units), "backpacks")

# ---------------------------------------------------------------- model.cfg: skeleton from hcl_pruss, our classes
mc = open(os.path.join(ROOT, r"source\addon\hcl\hcl_pruss\model.cfg"), encoding="latin-1").read()
models = [U_P3D, C_P3D, E_P3D, G_P3D] + sorted({h[0] for h in HEAD}) + [V_P3D, B_P3D]
mc = re.sub(r"(\tclass hcl_\w+: ArmaMan \{\};\r?\n)+", "".join(f"\tclass {m}: ArmaMan {{}};\n" for m in models), mc)
mc = mc.replace("test addon hcl_pruss", "test addon hcl_fr")
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
    d = "hcl\\hcl_fr\\data\\"
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


MATS = [(U_P3D, "0.4", 50), (C_P3D, "0.4", 50), (E_P3D, "0.4", 50), (G_P3D, "0.4", 50)] + [
    (m, "0.6", 40) if "bonnet" in m else (m, "1.0", 80) for m in sorted({h[1] for h in HEAD})] + [(V_P3D, "0.6", 60), (B_P3D, "0.6", 60)]
for base, spec, power in MATS:
    open(os.path.join(SRC, "data", base + ".rvmat"), "w", encoding="ascii", newline="\r\n").write(rvmat(base, spec, power))
print("OK", len(MATS), "rvmat")
