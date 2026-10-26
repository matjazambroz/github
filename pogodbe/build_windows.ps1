# Zgradi samostojno Windows aplikacijo (mapa dist\PregledPogodb + ZIP), s priloženim Tesseract OCR.
# Zahteve: Python 3.10+, Tesseract OCR (npr. `choco install tesseract`).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python -m pip install -r requirements.txt pyinstaller
python -m pyinstaller --noconfirm --clean --windowed --name PregledPogodb `
  --collect-submodules pregled_pogodb run.py

$tess = "$env:ProgramFiles\Tesseract-OCR"
if (-not (Test-Path "$tess\tesseract.exe")) { throw "Tesseract ni nameščen v $tess" }
$dst = "dist\PregledPogodb\tesseract"
New-Item -ItemType Directory -Force "$dst\tessdata" | Out-Null
Copy-Item "$tess\tesseract.exe", "$tess\*.dll" $dst
foreach ($f in "eng", "osd") { Copy-Item "$tess\tessdata\$f.traineddata" "$dst\tessdata" -ErrorAction SilentlyContinue }
# slovenski jezikovni model (tessdata_best)
Invoke-WebRequest "https://github.com/tesseract-ocr/tessdata_best/raw/main/slv.traineddata" -OutFile "$dst\tessdata\slv.traineddata"
# C++ runtime, če ga ciljni računalnik nima
foreach ($d in "msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll") {
  if (Test-Path "$env:SystemRoot\System32\$d") { Copy-Item "$env:SystemRoot\System32\$d" $dst -ErrorAction SilentlyContinue }
}
Copy-Item "NAVODILA.md" "dist\PregledPogodb\" 
Compress-Archive -Path "dist\PregledPogodb" -DestinationPath "dist\PregledPogodb-windows.zip" -Force
Write-Host "Končano: dist\PregledPogodb-windows.zip"
