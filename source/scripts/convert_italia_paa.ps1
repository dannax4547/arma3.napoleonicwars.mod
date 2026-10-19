# Converts the textures of the Kingdom of Italy / Kingdom of Naples test addon hcl_italia (PNG sources) to .paa with the
# official ImageToPAA and checks each header (_nohq DXT5, the others DXT1). Copy of convert_varsovia_paa.ps1; writes
# only into source/textures/hcl_italia_paa/. Sources: coats hcl_uniforme_italia(_elite) (_co per variant; _nohq/_smdi
# the French ones, same mesh and UV), shakos hcl_shako_italia and hcl_shako_napoles, bearskins hcl_bonnet_italia.
#   powershell -ExecutionPolicy Bypass -File convert_italia_paa.ps1 <project root>
param([string]$root)
$tool = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe"
$t = Join-Path $root "source\textures"
$dst = "$t\hcl_italia_paa"
$jobs = @()
foreach ($n in "it01", "it02", "it03", "it04", "it05", "it06", "it07", "na01", "na02", "na05", "na07") {
    $jobs += , @("$t\hcl_uniforme_italia\hcl_u_italia1812_${n}_co.png", "$dst\hcl_u_italia1812_${n}_co.paa")
}
foreach ($s in "nohq", "smdi") { $jobs += , @("$t\hcl_uniforme_fr\hcl_u_fr1812_${s}.png", "$dst\hcl_u_italia1812_${s}.paa") }
foreach ($k in "it03_gr", "it03_vo", "it05_gr", "it05_vo", "na07_gr", "na07_vo") {
    $jobs += , @("$t\hcl_uniforme_italia_elite\hcl_u_italia1812_elite_${k}_co.png", "$dst\hcl_u_italia1812_elite_${k}_co.paa")
}
foreach ($s in "nohq", "smdi") { $jobs += , @("$t\hcl_uniforme_fr_elite\hcl_u_fr1812_elite_${s}.png", "$dst\hcl_u_italia1812_elite_${s}.paa") }
$shakos = @{ "italia" = @("fuzileiro_1a_comp", "fuzileiro_2a_comp", "fuzileiro_3a_comp", "fuzileiro_4a_comp", "voltigeur_gala");
             "napoles" = @("fuzileiro_r01", "fuzileiro_r02", "fuzileiro_r05", "fuzileiro_r07", "voltigeur_gala") }
foreach ($n in "italia", "napoles") {
    foreach ($g in $shakos[$n]) {
        foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$t\hcl_shako_$n\hcl_shako_${n}_${g}_${s}.png", "$dst\hcl_shako_${n}_${g}_${s}.paa") }
    }
}
foreach ($g in "italia_granadeiro_gala", "italia_granadeiro_campanha", "napoles_granadeiro_gala", "napoles_granadeiro_campanha") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$t\hcl_bonnet_italia\hcl_bonnet_italia_${g}_${s}.png", "$dst\hcl_bonnet_italia_${g}_${s}.paa") }
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
