# Converts the British test-addon textures (PNG sources) to .paa with the official ImageToPAA and checks each header
# (_nohq DXT5, the others DXT1), like convert_fr_paa.ps1. Only writes inside the project (paa/ folders next to the
# sources).
#   powershell -File convert_uk_paa.ps1 <project root>
param([string]$root)
$tool = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe"
$uni = Join-Path $root "source\textures\hcl_uniforme_uk"
$shk = Join-Path $root "source\textures\hcl_shako_uk"
$eq = Join-Path $root "source\textures\hcl_equipamento_uk"
$jobs = @()
# jackets: _co per variant, shared _nohq / _smdi per model (linha, flanco, rifles)
foreach ($k in 1..4) {
    foreach ($m in "linha", "flanco") {
        $jobs += , @(("$uni\hcl_u_uk1812_${m}_v{0:D2}_co.png" -f $k), ("$uni\paa\hcl_u_uk1812_${m}_v{0:D2}_co.paa" -f $k))
    }
}
$jobs += , @("$uni\hcl_u_uk1812_rifles_v01_co.png", "$uni\paa\hcl_u_uk1812_rifles_v01_co.paa")
foreach ($k in 1..2) {                                     # Highland dress (build_kilt_uk.py)
    $jobs += , @(("$uni\hcl_u_uk1812_kilt_v{0:D2}_co.png" -f $k), ("$uni\paa\hcl_u_uk1812_kilt_v{0:D2}_co.paa" -f $k))
}
foreach ($m in "linha", "flanco", "rifles", "kilt") {
    foreach ($s in "nohq", "smdi") { $jobs += , @("$uni\hcl_u_uk1812_${m}_${s}.png", "$uni\paa\hcl_u_uk1812_${m}_${s}.paa") }
}
foreach ($t in "belgic_batalhao", "belgic_granadeiro", "belgic_ligeira", "stovepipe_batalhao", "stovepipe_granadeiro",
               "stovepipe_ligeira", "stovepipe_28th", "stovepipe_rifles") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$shk\hcl_shako_uk_${t}_${s}.png", "$shk\paa\hcl_shako_uk_${t}_${s}.paa") }
}
# Highland feather bonnet (texturizar_shako_uk.py nome=HCL_UK_ textura=hcl_uk_)
foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$shk\hcl_uk_bonnet_highland_${s}.png", "$shk\paa\hcl_uk_bonnet_highland_${s}.paa") }
foreach ($b in "hcl_v_uk1812_correame", "hcl_b_uk1812_mochila") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$eq\${b}_${s}.png", "$eq\paa\${b}_${s}.paa") }
}
# Rifles: black crossbelts (generate_equipment_textures_uk.py couro=preto), _co only (same model)
$jobs += , @("$eq\hcl_v_uk1812_correame_preto_co.png", "$eq\paa\hcl_v_uk1812_correame_preto_co.paa")
# Portugal (docs/specs/portugal_1812.md): 24 line + 12 Cacadores jackets, 4 stovepipes, 36 number bands
foreach ($k in 1..24) {
    $jobs += , @(("$uni\hcl_u_por1812_linha_v{0:D2}_co.png" -f $k), ("$uni\paa\hcl_u_por1812_linha_v{0:D2}_co.paa" -f $k))
    $jobs += , @(("$shk\numeros\hcl_por_numero_l{0:D2}_co.png" -f $k), ("$shk\paa\hcl_por_numero_l{0:D2}_co.paa" -f $k))
}
foreach ($k in 1..12) {
    $jobs += , @(("$uni\hcl_u_por1812_cacadores_v{0:D2}_co.png" -f $k), ("$uni\paa\hcl_u_por1812_cacadores_v{0:D2}_co.paa" -f $k))
    $jobs += , @(("$shk\numeros\hcl_por_numero_c{0:D2}_co.png" -f $k), ("$shk\paa\hcl_por_numero_c{0:D2}_co.paa" -f $k))
}
foreach ($m in "linha", "cacadores") {
    foreach ($s in "nohq", "smdi") { $jobs += , @("$uni\hcl_u_por1812_${m}_${s}.png", "$uni\paa\hcl_u_por1812_${m}_${s}.paa") }
}
# Brunswick 1815 (docs/specs/kgl_brunswick_1815.md 4): 8 dolmans, 4 "Kiwer" shakos, 3 white-metal number bands
foreach ($k in 1..8) {
    $jobs += , @(("$uni\hcl_u_bru1815_dolman_v{0:D2}_co.png" -f $k), ("$uni\paa\hcl_u_bru1815_dolman_v{0:D2}_co.paa" -f $k))
}
foreach ($s in "nohq", "smdi") { $jobs += , @("$uni\hcl_u_bru1815_dolman_${s}.png", "$uni\paa\hcl_u_bru1815_dolman_${s}.paa") }
foreach ($k in 1..3) { $jobs += , @("$shk\numeros\hcl_bru_numero_b${k}_co.png", "$shk\paa\hcl_bru_numero_b${k}_co.paa") }
# Brunswick knapsack: the Trotter texture with the Welfenross stamped on the flap (carimbo_mochila_bru.py)
$jobs += , @("$eq\hcl_b_bru1815_mochila_co.png", "$eq\paa\hcl_b_bru1815_mochila_co.paa")
foreach ($t in "bru_leib", "bru_ligeiro", "bru_linha", "bru_avantgarde") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$shk\hcl_shako_uk_${t}_${s}.png", "$shk\paa\hcl_shako_uk_${t}_${s}.paa") }
}
foreach ($t in "por_batalhao", "por_granadeiro", "por_ligeira", "por_cacadores") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$shk\hcl_shako_uk_${t}_${s}.png", "$shk\paa\hcl_shako_uk_${t}_${s}.paa") }
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
