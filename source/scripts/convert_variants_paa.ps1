# Converts the regimental-variant textures (PNG sources) to .paa with the official ImageToPAA and checks each header.
# Only writes inside the project (paa/ folders next to the sources). Does not touch the Arma 3 or Arma 3 Tools install.
#   powershell -File convert_variants_paa.ps1 <project root>
# Shako: _co changes per variant; _nohq/_smdi depend only on the badge model (fwr = base files, aguia, estrela), so the
# identical PNGs are converted once, to shared names. Uniform: _co per variant, one shared _nohq and _smdi.
param([string]$root)
$tool = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe"
$shk = Join-Path $root "source\textures\hcl_shako_pruss"
$uni = Join-Path $root "source\textures\hcl_uniforme_pruss"
$jobs = @()
foreach ($v in "fwr_branca", "aguia_amarela", "aguia_branca", "estrela_prata", "estrela_latao",
               "estrela_prata_presilha_preta", "aguia_presilha_preta", "estrela_latao_linha_verde", "aguia_amarela_linha_verde",
               "estrela_latao_linha_latao", "aguia_amarela_linha_latao", "estrela_prata_linha_branca", "aguia_branca_linha_branca") {
    $jobs += , @("$shk\variantes\hcl_shako_pruss_${v}_co.png", "$shk\paa\variantes\hcl_shako_pruss_${v}_co.paa")
}
foreach ($m in @(@("aguia", "aguia_amarela"), @("estrela", "estrela_prata"))) {   # model, one of its identical sources
    foreach ($s in "nohq", "smdi") {
        $jobs += , @("$shk\variantes\hcl_shako_pruss_$($m[1])_${s}.png", "$shk\paa\variantes\hcl_shako_pruss_$($m[0])_${s}.paa")
    }
}
# 2026-10-12: plume texture set (build_plumet_pruss.py) and the cloth cap (one model: _co per colour, shared
# _nohq/_smdi taken from the baked variant azul_faixa_vermelha)
foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$shk\hcl_plumet_pruss_${s}.png", "$shk\paa\hcl_plumet_pruss_${s}.paa") }
$bone = Join-Path $root "source\textures\hcl_bone_pruss"
foreach ($c in "c01_azul_vermelha", "c02_azul_amarela", "c03_verde_preta", "c04_azul_verde", "c05_azul_branca") {
    $jobs += , @("$bone\hcl_bone_pruss_${c}_co.png", "$bone\paa\hcl_bone_pruss_${c}_co.paa")
}
foreach ($s in "nohq", "smdi") { $jobs += , @("$bone\hcl_bone_pruss_azul_faixa_vermelha_${s}.png", "$bone\paa\hcl_bone_pruss_${s}.paa") }
foreach ($k in 1..17) {
    $jobs += , @(("$uni\hcl_u_pruss1813_v{0:D2}_co.png" -f $k), ("$uni\paa\hcl_u_pruss1813_v{0:D2}_co.paa" -f $k))
}
foreach ($s in "nohq", "smdi") { $jobs += , @("$uni\hcl_u_pruss1813_${s}.png", "$uni\paa\hcl_u_pruss1813_${s}.paa") }
# equipment (vest, knapsack): one texture set each
$eq = Join-Path $root "source\textures\hcl_equipamento_pruss"
foreach ($b in "hcl_v_pruss1813_correame", "hcl_b_pruss1813_tornister", "hcl_v_pruss1813_correame_preto",
               "hcl_b_pruss1813_tornister_preto") {
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
"failures: $fail"
