# Builds the in-game TEST addon hcl_italia (Kingdom of Italy and Kingdom of Naples line infantry, c. 1812) with the
# official Arma 3 Tools, entirely inside the project. Copy of build_mod_varsovia.ps1:
#   source/addon/hcl/hcl_italia   addon source (folders mirror the PBO prefix hcl\hcl_italia)
#   work/build/hcl/hcl_italia     binarized models, config.bin, rapified materials, textures
#   release/@Historical_Clothing/Addons/hcl_italia.pbo   the packed addon (FileBank, prefix hcl\hcl_italia)
# Does not touch the Arma 3 or Arma 3 Tools folders.
#   powershell -ExecutionPolicy Bypass -File build_mod_italia.ps1 <project root> <scripts dir> <variants dir>
param([string]$root, [string]$scripts, [string]$vdir)
$tools = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools"
$samples = "C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Samples"
$blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$py = "C:\Program Files\Blender Foundation\Blender 5.2\5.2\python\bin\python.exe"
$src = "$root\source\addon\hcl\hcl_italia"
$bld = "$root\work\build\hcl\hcl_italia"
$rel = "$root\release\@Historical_Clothing\Addons"

"== 1. P3D (MLOD) on the official templates"
& $blender -b --factory-startup --python "$scripts\build_p3d_italia.py" -- $root $samples $src 2>&1 |
    Select-String "CHECK|UNIFORME|PESOS|BARRETINA|P3D|rror|Traceback" | ForEach-Object { "   $_" }

"== 2. config.cpp, model.cfg, rvmat"
& $py -I "$scripts\gen_config_italia.py" $root $vdir $src

"== 3. textures (PAA, converted earlier with convert_italia_paa.ps1)"
New-Item -ItemType Directory -Force "$src\data" | Out-Null
Copy-Item "$root\source\textures\hcl_italia_paa\*.paa" "$src\data"

"== 4. Binarize (models)"
New-Item -ItemType Directory -Force "$bld\data" | Out-Null                # files are overwritten, nothing is deleted
Push-Location "$root\source\addon"
$log = & "$tools\Binarize\binarize_x64.exe" -silent -norecurse -always "hcl\hcl_italia" $bld 2>&1 | ForEach-Object { "$_" }
$code = $LASTEXITCODE
Pop-Location
[System.IO.File]::WriteAllLines("$root\work\build\binarize_italia_log.txt", [string[]]$log)
"   exit $code; log work\build\binarize_italia_log.txt; material/texture problems:"
$log | Where-Object { $_ -match "Cannot load|not found|rror" } | ForEach-Object { "   " + $_.Substring(0, [math]::Min(160, $_.Length)) }
# every model declared in model.cfg must exist as a fresh SOURCE p3d and get the skeleton when binarized
$declared = [regex]::Matches((Get-Content -Raw "$src\model.cfg"), "class (hcl_\w+): ArmaMan") | ForEach-Object { $_.Groups[1].Value }
foreach ($d in $declared) {
    if (-not (Test-Path "$src\$d.p3d")) { "   ERROR: model.cfg declares $d but $d.p3d was not generated (see step 1)" }
    elseif ((Get-Item "$src\$d.p3d").LastWriteTime -lt (Get-Date).AddHours(-1)) { "   WARNING: $d.p3d is older than 1 hour (step 1 failed?)" }
}
foreach ($m in Get-ChildItem "$bld\*.p3d") {
    $ok = [System.Text.Encoding]::ASCII.GetString([System.IO.File]::ReadAllBytes($m.FullName)).Contains("OFP2_ManSkeleton")
    "   skeleton {0,-5} {1}" -f $ok, $m.Name
    if (-not $ok) { "   ERROR: $($m.Name) has no skeleton - add 'class $($m.BaseName): ArmaMan {};' to model.cfg" }
}

"== 5. config.bin and rapified materials (CfgConvert)"
& "$tools\CfgConvert\CfgConvert.exe" -bin -dst "$bld\config.bin" "$src\config.cpp"
"   config.bin exit $LASTEXITCODE"
foreach ($m in Get-ChildItem "$src\data\*.rvmat") {
    & "$tools\CfgConvert\CfgConvert.exe" -bin -dst "$bld\data\$($m.Name)" $m.FullName
    "   $($m.Name) exit $LASTEXITCODE"
}
Copy-Item "$src\data\*.paa" "$bld\data"

"== 6. PBO (FileBank)"
New-Item -ItemType Directory -Force $rel | Out-Null
# a running Arma 3 keeps the loaded PBO open: then pack into release\_atualizacao (never close the game)
$dst = $rel
if (Test-Path "$rel\hcl_italia.pbo") {
    try { $s = [System.IO.File]::Open("$rel\hcl_italia.pbo", 'Open', 'ReadWrite', 'None'); $s.Close() }
    catch { $dst = "$root\release\_atualizacao"; "   the PBO in Addons is in use (game open?): packing into $dst" }
}
New-Item -ItemType Directory -Force $dst | Out-Null
& "$tools\FileBank\FileBank.exe" -property "prefix=hcl\hcl_italia" -dst $dst $bld
"   exit $LASTEXITCODE"
$stale = "$root\release\_atualizacao\hcl_italia.pbo"
if ($dst -eq $rel -and (Test-Path $stale)) {
    $old = Get-Item $stale
    $arch = "hcl_italia_versao_" + $old.LastWriteTime.ToString("yyyy-MM-dd_HHmm") + ".pbo"
    Rename-Item $stale $arch
    "   older staged PBO renamed to _atualizacao\$arch (the installed one is newer)"
}
Get-Item "$dst\hcl_italia.pbo" | Select-Object FullName, Length, LastWriteTime | Format-List
