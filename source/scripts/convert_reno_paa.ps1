# Converts the textures of the Confederation of the Rhine test addon hcl_reno (PNG sources) to .paa with the official
# ImageToPAA and checks each header (_nohq DXT5, the others DXT1). Copy of convert_italia_paa.ps1; writes only into
# source/textures/hcl_reno_paa/. Sources: coats hcl_uniforme_reno (_co per variant, the list read from
# variantes_reno.json; _nohq/_smdi the French ones, same mesh and UV), crested helmets hcl_raupenhelm.
#   powershell -ExecutionPolicy Bypass -File convert_reno_paa.ps1 <project root> <variants dir>
param([string]$root, [string]$vdir)
$tool = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools\ImageToPAA\ImageToPAA.exe"
$t = Join-Path $root "source\textures"
$dst = "$t\hcl_reno_paa"
$jobs = @()
$var = Get-Content -Raw -Encoding UTF8 (Join-Path $vdir "variantes_reno.json") | ConvertFrom-Json
foreach ($p in $var.PSObject.Properties) {
    $pre = $p.Value.prefixo
    $jobs += , @("$t\hcl_uniforme_reno\${pre}_co.png", "$dst\${pre}_co.paa")
}
foreach ($s in "nohq", "smdi") { $jobs += , @("$t\hcl_uniforme_fr\hcl_u_fr1812_${s}.png", "$dst\hcl_u_reno1811_${s}.paa") }
foreach ($g in "wurttemberg", "baviera") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$t\hcl_raupenhelm\hcl_raupenhelm_${g}_${s}.png", "$dst\hcl_raupenhelm_${g}_${s}.paa") }
}
# lot 2 (2026-10-27): Saxon shakos 1810 (texturizar_aliados.py raiz=SX_ into source/textures/hcl_shako_reno)
foreach ($g in "fuzileiro", "fuzileiro_koenig", "granadeiro_gala", "ligeira", "jaeger") {
    foreach ($s in "co", "nohq", "smdi") { $jobs += , @("$t\hcl_shako_reno\hcl_shako_saxonia_${g}_${s}.png", "$dst\hcl_shako_saxonia_${g}_${s}.paa") }
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
