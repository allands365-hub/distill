# Flip Distill's agents to Lemma's native runtime (system:lemma) for the demo /
# judging, or as a fallback if the BYO OpenAI runtime hangs. More reliable; uses
# Lemma credits. Run `demo/runtime_dev.ps1` to switch back to the BYO OpenAI key.
# (repro_runner always stays on system:lemma — WORKSPACE_CLI requires it.)
$env:PATH = "C:\Users\Allan\.local\bin;$env:PATH"
foreach ($a in 'triage','reproduction','release_notes','assistant') {
  lemma agent update $a --pod distill --data '{"agent_runtime":{"profile_id":"system:lemma"}}' | Out-Null
  Write-Host "$a -> system:lemma"
}
