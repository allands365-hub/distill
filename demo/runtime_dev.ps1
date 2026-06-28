# Flip Distill's agents back to the BYO OpenAI runtime (conserves Lemma credits) —
# the default for day-to-day building. Use `demo/runtime_demo.ps1` to switch to
# Lemma's native runtime for the demo/judging or as a fallback.
$env:PATH = "C:\Users\Allan\.local\bin;$env:PATH"
$PROFILE_ID = "019f0ccf-773d-74e1-9ae6-1116c57d1134"  # OpenAI BYO runtime profile
foreach ($a in 'triage','reproduction','release_notes','assistant') {
  lemma agent update $a --pod distill --data ('{"agent_runtime":{"profile_id":"' + $PROFILE_ID + '"}}') | Out-Null
  Write-Host "$a -> OpenAI BYO"
}
