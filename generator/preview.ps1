# Exporte chaque slide d'un .pptx en PNG (via PowerPoint) pour contrôle visuel.
#   powershell -File preview.ps1 <chemin.pptx> <dossier_sortie>
param(
  [Parameter(Mandatory = $true)][string]$Pptx,
  [Parameter(Mandatory = $true)][string]$Out
)

$Pptx = (Resolve-Path $Pptx).Path
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$Out = (Resolve-Path $Out).Path
Get-ChildItem $Out -Filter *.PNG -ErrorAction SilentlyContinue | Remove-Item -Force

$ppt = New-Object -ComObject PowerPoint.Application
$pres = $ppt.Presentations.Open($Pptx, $true, $false, $false)
$pres.Export($Out, "PNG", 1500, 844)
$pres.Close()
$ppt.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
"$((Get-ChildItem $Out -Filter *.PNG).Count) slides exportees dans $Out"
