# Read-only contact sheet of a mod unit atlas (PNG converted from the .dds): every 512 px tile scaled to 256 px with its
# label "<tag> c<col> r<row>", so tiles can be cited exactly in the spec sheets. Writes one sheet per atlas.
#   powershell -File folha_contato_atlas.ps1 <atlas png> <out png> <tag> [rows=0-7]
param([string]$atlas, [string]$out, [string]$tag, [string]$rows = "0-7")
Add-Type -AssemblyName System.Drawing
$r0, $r1 = $rows.Split("-") | ForEach-Object { [int]$_ }
$img = [System.Drawing.Bitmap]::FromFile($atlas)
$T = 512; $S = 256; $n = [int]($img.Width / $T)
$sheet = New-Object System.Drawing.Bitmap ($n * ($S + 4)), (($r1 - $r0 + 1) * ($S + 22))
$g = [System.Drawing.Graphics]::FromImage($sheet)
$g.Clear([System.Drawing.Color]::FromArgb(30, 30, 30))
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$font = New-Object System.Drawing.Font "Arial", 11
for ($row = $r0; $row -le $r1; $row++) {
    for ($col = 0; $col -lt $n; $col++) {
        $x = $col * ($S + 4); $y = ($row - $r0) * ($S + 22)
        $g.DrawImage($img, (New-Object System.Drawing.Rectangle $x, $y, $S, $S), (New-Object System.Drawing.Rectangle ($col * $T), ($row * $T), $T, $T), [System.Drawing.GraphicsUnit]::Pixel)
        $g.DrawString("$tag c$col r$row", $font, [System.Drawing.Brushes]::White, $x + 2, $y + $S + 2)
    }
}
$sheet.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $sheet.Dispose(); $img.Dispose()
"OK $out"
