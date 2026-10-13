param([string]$dir, [string]$out)
# Read-only catalogue of the coat tiles of the Eras Mod infantry atlases prussia1813_01..03 (512 px tiles, same
# layout in every tile). Samples the colour of each piece at fixed tile positions (calibrated on atlas 01, tile
# col 0 row 1) and writes a contact sheet with swatches plus a CSV.
Add-Type -AssemblyName System.Drawing
$POS = [ordered]@{ casaca = @(40, 140, 30, 40); vira = @(14, 270, 16, 50); punho = @(262, 360, 20, 60);
                 platina = @(322, 470, 14, 12); botao = @(199, 37, 5, 5); calca_ref = @(0, 0, 0, 0) }
function Avg($img, $x0, $y0, $w, $h) {
    $r = 0; $g = 0; $b = 0; $n = 0
    for ($x = $x0; $x -lt $x0 + $w; $x += 2) { for ($y = $y0; $y -lt $y0 + $h; $y += 2) {
        $c = $img.GetPixel($x, $y); $r += $c.R; $g += $c.G; $b += $c.B; $n++ } }
    if ($n -eq 0) { return [System.Drawing.Color]::Black }
    return [System.Drawing.Color]::FromArgb([int]($r / $n), [int]($g / $n), [int]($b / $n))
}
$rows = @()
$sheet = New-Object System.Drawing.Bitmap (6 * 260), (12 * 300)
$gs = [System.Drawing.Graphics]::FromImage($sheet)
$gs.Clear([System.Drawing.Color]::FromArgb(40, 40, 40))
$font = New-Object System.Drawing.Font "Arial", 11
$k = 0
foreach ($a in "01", "02", "03") {
    $img = [System.Drawing.Bitmap]::FromFile((Join-Path $dir "prussia1813_${a}_diffuse.png"))
    for ($row = 0; $row -lt 4; $row++) {
        for ($col = 0; $col -lt 6; $col++) {
            $ox = $col * 512; $oy = $row * 512
            $line = [ordered]@{ atlas = $a; col = $col; row = $row }
            foreach ($name in "casaca", "vira", "punho", "platina", "botao") {
                $q = $POS[$name]; $c = Avg $img ($ox + $q[0]) ($oy + $q[1]) $q[2] $q[3]
                $line[$name] = "#{0:X2}{1:X2}{2:X2}" -f $c.R, $c.G, $c.B
            }
            $rows += [pscustomobject]$line
            $tx = ($k % 6) * 260; $ty = [math]::Floor($k / 6) * 300
            $tile = $img.Clone((New-Object System.Drawing.Rectangle $ox, $oy, 512, 512), $img.PixelFormat)
            $gs.DrawImage($tile, $tx + 2, $ty + 2, 256, 256); $tile.Dispose()
            $sx = $tx + 2
            foreach ($name in "casaca", "vira", "punho", "platina", "botao") {
                $c = [System.Drawing.ColorTranslator]::FromHtml($line[$name])
                $gs.FillRectangle((New-Object System.Drawing.SolidBrush $c), $sx, $ty + 260, 48, 18); $sx += 51
            }
            $gs.DrawString("$a c$col r$row", $font, [System.Drawing.Brushes]::White, $tx + 4, $ty + 280)
            $k++
        }
    }
    $img.Dispose()
}
$sheet.Save($out)
$rows | Export-Csv -NoTypeInformation -Encoding UTF8 ([System.IO.Path]::ChangeExtension($out, ".csv"))
$rows | Format-Table -AutoSize | Out-String -Width 200
