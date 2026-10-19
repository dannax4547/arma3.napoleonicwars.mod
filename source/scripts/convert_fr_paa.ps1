# Converts the French test-addon textures (PNG sources) to .paa with the official ImageToPAA and checks each header
# (_nohq DXT5, the others DXT1). Only writes inside the project (paa/ folders next to the sources).
#   powershell -File convert_fr_paa.ps1 <project root>
param([string]$root)
$tool = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe"
$uni = Join-Path $root "source\textures\hcl_uniforme_fr"
$shk = Join-Path $root "source\textures\hcl_shako_fr"
$eq = Join-Path $root "source\textures\hcl_equipamento_fr"
$jobs = @()
foreach ($k in 1..4) {
    $jobs += , @(("$uni\hcl_u_fr1812_v{0:D2}_co.png" -f $k), ("$uni\paa\hcl_u_fr1812_v{0:D2}_co.paa" -f $k))
}
foreach ($s in "nohq", "smdi") { $jobs += , @("$uni\hcl_u_fr1812_${s}.png", "$uni\paa\hcl_u_fr1812_${s}.paa") }
# winter: greatcoat (build_capote_fr.py), _co per variant, shared _nohq / _smdi
$cap = Join-Path $root "source\textures\hcl_capote_fr"
foreach ($k in 1..5) {                                     # W05 (2026-10-13): Old Guard blue campaign greatcoat
    $jobs += , @(("$cap\hcl_u_fr1812_capote_w{0:D2}_co.png" -f $k), ("$cap\paa\hcl_u_fr1812_capote_w{0:D2}_co.paa" -f $k))
}
foreach ($s in "nohq", "smdi") { $jobs += , @("$cap\hcl_u_fr1812_capote_${s}.png", "$cap\paa\hcl_u_fr1812_capote_${s}.paa") }
# elite companies: coat with epaulettes (build_casaca_elite_fr.py), _co per variant, shared _nohq / _smdi
$eli = Join-Path $root "source\textures\hcl_uniforme_fr_elite"
# lc01 / lk01 / lv01: light infantry chasseur / carabinier / voltigeur (2026-10-13)
foreach ($v in "gr01", "vo01", "lc01", "lk01", "lv01", "gr01v") { $jobs += , @("$eli\hcl_u_fr1812_elite_${v}_co.png", "$eli\paa\hcl_u_fr1812_elite_${v}_co.paa") }
foreach ($s in "nohq", "smdi") { $jobs += , @("$eli\hcl_u_fr1812_elite_${s}.png", "$eli\paa\hcl_u_fr1812_elite_${s}.paa") }
foreach ($t in "fuzileiro_1a_comp", "granadeiro_gala", "granadeiro_campanha", "voltigeur_gala", "voltigeur_campanha", "oficial_coronel",
               "fuzileiro_losango", "fuzileiro_losango_branco", "ligeira_carabineiro_gala", "ligeira_voltigeur_gala") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$shk\hcl_shako_fr_${t}_${s}.png", "$shk\paa\hcl_shako_fr_${t}_${s}.paa") }
}
# fusilier companies 2-4 (variantes_pompom_fr.py): _co only, the model and its _nohq/_smdi are the 1st company's
foreach ($t in "fuzileiro_2a_comp", "fuzileiro_3a_comp", "fuzileiro_4a_comp",
               "fuzileiro_losango_2a_comp", "fuzileiro_losango_3a_comp", "fuzileiro_losango_4a_comp",
               "fuzileiro_losango_branco_2a_comp", "fuzileiro_losango_branco_3a_comp", "fuzileiro_losango_branco_4a_comp",
               "linha_018", "linha_046", "linha_057", "linha_084",       # numbered line regiments (numerar_placa_fr.py)
               "ligeira_carabineiro_gala_azul") {                        # dark blue carabinier (variantes_cor_shako_fr.py)
    $jobs += , @("$shk\hcl_shako_fr_${t}_co.png", "$shk\paa\hcl_shako_fr_${t}_co.paa")
}
# Old Guard: bearskins (one texture set each) and the long-tailed habit (_co per variant, shared _nohq/_smdi)
$bon = Join-Path $root "source\textures\hcl_bonnet_fr"
foreach ($t in "granadeiro_gala", "granadeiro_campanha", "cacador_gala") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$bon\hcl_bonnet_fr_${t}_${s}.png", "$bon\paa\hcl_bonnet_fr_${t}_${s}.paa") }
}
$gua = Join-Path $root "source\textures\hcl_uniforme_fr_guarda"
foreach ($v in "gr01", "ch01") { $jobs += , @("$gua\hcl_u_fr1812_guarda_${v}_co.png", "$gua\paa\hcl_u_fr1812_guarda_${v}_co.paa") }
foreach ($s in "nohq", "smdi") { $jobs += , @("$gua\hcl_u_fr1812_guarda_${s}.png", "$gua\paa\hcl_u_fr1812_guarda_${s}.paa") }
foreach ($b in "hcl_v_fr1812_correame", "hcl_b_fr1812_havresac") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$eq\${b}_${s}.png", "$eq\paa\${b}_${s}.paa") }
}

$fail = 0
foreach ($j in $jobs) {
    $src, $dst = $j
    if (-not (Test-Path $src)) { "MISSING  $src"; $fail++; continue }
    New-Item -ItemType Directory -Force (Split-Path $dst) | Out-Null
    & $tool $src $dst | Out-Null
    $code = $LASTEXITCODE
    if (-not (Test-Path $dst)) { "FAILED   $src (exit $code)"; $fail++; continue }
    $h = [System.IO.File]::ReadAllBytes($dst)[0..1]
    $tag = "0x{0:X2}{1:X2}" -f $h[1], $h[0]
    $fmt = @{ "0xFF01" = "DXT1"; "0xFF05" = "DXT5" }[$tag]
    $want = if ($dst -match '_nohq\.paa$') { "DXT5" } else { "DXT1" }
    $ok = if ($fmt -eq $want) { "OK" } else { $fail++; "WRONG" }
    "{0,-5} {1} {2,-5} {3,10:N0} B  {4}" -f $ok, $tag, $fmt, (Get-Item $dst).Length, $dst.Substring($root.Length + 1)
}
"jobs: $($jobs.Count); failures: $fail"
