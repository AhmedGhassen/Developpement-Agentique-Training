# GABARIT — atelier A5. Hook PostToolUse sur Edit|Write.
#
# Le chemin du fichier edite se lit dans tool_input.file_path, sur stdin.
# La variable $CLAUDE_FILE_PATHS n'existe pas : ne l'utilisez pas.
#
# Prerequis : pip install ruff
#
# Test manuel :
#   '{"tool_input":{"file_path":"app.py"}}' | powershell -NoProfile -ExecutionPolicy Bypass -File .claude\hooks\format-python.ps1

$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
$file = $payload.tool_input.file_path
if (-not $file) { exit 0 }
if ($file -notlike '*.py') { exit 0 }
if (-not (Test-Path -LiteralPath $file)) { exit 0 }

ruff format -- "$file"      2>&1 | Out-Null
ruff check --fix -- "$file" 2>&1 | Out-Null

# On sort toujours en 0 : un formatage rate ne doit pas bloquer l'edition.
exit 0
