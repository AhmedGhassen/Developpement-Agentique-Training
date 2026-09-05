# GABARIT — atelier A5. Hook PreToolUse sur Bash.
#
# Contrat des hooks : la charge utile arrive en JSON sur stdin.
#   - la commande se lit dans tool_input.command
#   - code de sortie 0 = autorise, 2 = REFUSE (seul 2 bloque ; 1 ne bloque pas)
#   - le message doit partir sur stderr, pas sur stdout
#
# Il n'existe pas de variable d'environnement $CLAUDE_FILE_PATHS : tout passe
# par le JSON de stdin.
#
# Test manuel, AVANT de brancher le hook :
#   '{"tool_input":{"command":"git push origin main"}}' | powershell -NoProfile -ExecutionPolicy Bypass -File .claude\hooks\guard-bash.ps1
#   $LASTEXITCODE     # doit valoir 2

$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
$cmd = $payload.tool_input.command
if (-not $cmd) { exit 0 }

$interdits = @(
  'git push',
  'git reset --hard',
  'rm -rf',
  'chmod 777',
  'curl ',
  'wget ',
  'pip uninstall',
  'docker system prune',
  'DROP TABLE',
  'TRUNCATE'
)

foreach ($bad in $interdits) {
  if ($cmd -like "*$bad*") {
    [Console]::Error.WriteLine("Refuse par la politique du depot : '$bad' n'est pas autorise depuis l'agent.")
    [Console]::Error.WriteLine("Si cette action est reellement necessaire, elle doit etre faite par un humain.")
    exit 2
  }
}

exit 0
