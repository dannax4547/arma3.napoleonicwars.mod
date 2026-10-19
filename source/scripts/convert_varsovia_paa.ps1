# Converts the textures of the Duchy of Warsaw test addon hcl_varsovia (PNG sources) to .paa with the official
# ImageToPAA and checks each header (_nohq DXT5, the others DXT1). Copy of convert_suica_paa.ps1; writes only into
# source/textures/hcl_varsovia_paa/. Sources: coats hcl_uniforme_varsovia(_elite) (_co per variant; _nohq/_smdi the
# French ones, same mesh and UV), czapka hcl_czapka_varsovia, bearskin hcl_bonnet_varsovia.
#   powershell -ExecutionPolicy Bypass -File convert_varsovia_paa.ps1 <project root>
param([string]$root)
$tool = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe"
$t = Join-Path $root "source\textures"
$dst = "$t\hcl_varsovia_paa"
$jobs = @()
foreach ($n in "l1810", "r09", "r07", "r13", "r15") { $jobs += , @("$t\hcl_uniforme_varsovia\hcl_u_varsovia1810_${n}_co.png", "$dst\hcl_u_varsovia1810_${n}_co.paa") }
foreach ($s in "nohq", "smdi") { $jobs += , @("$t\hcl_uniforme_fr\hcl_u_fr1812_${s}.png", "$dst\hcl_u_varsovia1810_${s}.paa") }
foreach ($k in "gr", "vo", "fu01", "gr13", "vo13", "gr15", "vo15") { $jobs += , @("$t\hcl_uniforme_varsovia_elite\hcl_u_varsovia1810_elite_${k}_co.png", "$dst\hcl_u_varsovia1810_elite_${k}_co.paa") }
foreach ($s in "nohq", "smdi") { $jobs += , @("$t\hcl_uniforme_fr_elite\hcl_u_fr1812_elite_${s}.png", "$dst\hcl_u_varsovia1810_elite_${s}.paa") }
foreach ($g in "fuzileiro", "voltigeur", "fuzileiro_kita") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$t\hcl_czapka_varsovia\hcl_czapka_varsovia_${g}_${s}.png", "$dst\hcl_czapka_varsovia_${g}_${s}.paa") }
}
# numbered fusilier czapkas (numerar_placa_varsovia.py): _co only, model and _nohq/_smdi of the base czapka
foreach ($n in "02","03","05","06","07","08","09","11","12","14","15","16","17") { $jobs += , @("$t\hcl_czapka_varsovia\hcl_czapka_varsovia_fuzileiro_rgt${n}_co.png", "$dst\hcl_czapka_varsovia_fuzileiro_rgt${n}_co.paa") }
$jobs += , @("$t\hcl_czapka_varsovia\hcl_czapka_varsovia_fuzileiro_kita_rgt01_co.png", "$dst\hcl_czapka_varsovia_fuzileiro_kita_rgt01_co.paa")
foreach ($g in "granadeiro_gala", "granadeiro_campanha", "granadeiro_r05", "granadeiro_r06", "granadeiro_lisa") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$t\hcl_bonnet_varsovia\hcl_bonnet_varsovia_${g}_${s}.png", "$dst\hcl_bonnet_varsovia_${g}_${s}.paa") }
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
