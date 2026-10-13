# Converts the textures of the Swiss test addon hcl_suica (PNG sources) to .paa with the official ImageToPAA and checks
# each header (_nohq DXT5, the others DXT1). Copy of convert_fr_paa.ps1. Writes only inside the project, into
# source/textures/hcl_suica_paa/ (one folder for the whole addon). Sources:
#   Swiss coats: hcl_uniforme_suica / hcl_uniforme_suica_elite (_co per variant, painted by generate_uniform_textures_v2.py)
#   _nohq / _smdi of the coats: the French ones (same mesh and UV), converted under the Swiss name
#   shakos: the French 1812 fusilier (companies 1-4) and voltigeur textures (hcl_shako_fr), under the name hcl_shako_suica_*
#   bearskin: hcl_bonnet_suica (texturizar_shako_fr.py raiz=SU_)
#   powershell -ExecutionPolicy Bypass -File convert_suica_paa.ps1 <project root>
param([string]$root)
$tool = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe"
$t = Join-Path $root "source\textures"
$dst = "$t\hcl_suica_paa"
$jobs = @()
foreach ($n in 1..4) { $jobs += , @("$t\hcl_uniforme_suica\hcl_u_suica1812_s${n}_co.png", "$dst\hcl_u_suica1812_s${n}_co.paa") }
foreach ($s in "nohq", "smdi") { $jobs += , @("$t\hcl_uniforme_fr\hcl_u_fr1812_${s}.png", "$dst\hcl_u_suica1812_${s}.paa") }
foreach ($k in "gr", "vo") {
    foreach ($n in 1..4) { $jobs += , @("$t\hcl_uniforme_suica_elite\hcl_u_suica1812_elite_${k}${n}_co.png", "$dst\hcl_u_suica1812_elite_${k}${n}_co.paa") }
}
foreach ($s in "nohq", "smdi") { $jobs += , @("$t\hcl_uniforme_fr_elite\hcl_u_fr1812_elite_${s}.png", "$dst\hcl_u_suica1812_elite_${s}.paa") }
foreach ($g in "fuzileiro_1a_comp", "voltigeur_gala", "voltigeur_campanha") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$t\hcl_shako_fr\hcl_shako_fr_${g}_${s}.png", "$dst\hcl_shako_suica_${g}_${s}.paa") }
}
foreach ($c in 2..4) { $jobs += , @("$t\hcl_shako_fr\hcl_shako_fr_fuzileiro_${c}a_comp_co.png", "$dst\hcl_shako_suica_fuzileiro_${c}a_comp_co.paa") }
foreach ($g in "granadeiro_gala", "granadeiro_campanha") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$t\hcl_bonnet_suica\hcl_bonnet_suica_${g}_${s}.png", "$dst\hcl_bonnet_suica_${g}_${s}.paa") }
}

$fail = 0
New-Item -ItemType Directory -Force $dst | Out-Null
foreach ($j in $jobs) {
    $src, $out = $j
    if (-not (Test-Path $src)) { "MISSING  $src"; $fail++; continue }
    & $tool $src $out | Out-Null
    $code = $LASTEXITCODE
    if (-not (Test-Path $out)) { "FAILED   $src (exit $code)"; $fail++; continue }
    $h = [System.IO.File]::ReadAllBytes($out)[0..1]
    $tag = "0x{0:X2}{1:X2}" -f $h[1], $h[0]
    $fmt = @{ "0xFF01" = "DXT1"; "0xFF05" = "DXT5" }[$tag]
    $want = if ($out -match '_nohq\.paa$') { "DXT5" } else { "DXT1" }
    $ok = if ($fmt -eq $want) { "OK" } else { $fail++; "WRONG" }
    "{0,-5} {1} {2,-5} {3,10:N0} B  {4}" -f $ok, $tag, $fmt, (Get-Item $out).Length, $out.Substring($root.Length + 1)
}
"jobs: $($jobs.Count); failures: $fail"
