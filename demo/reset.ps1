# Reset the distill pod for a fresh demo: delete all issues + releases rows.
$env:PATH = "C:\Users\Allan\.local\bin;$env:PATH"
foreach ($tbl in @('issues', 'releases')) {
  $ids = (lemma --json records list $tbl --pod distill --limit 500 | ConvertFrom-Json).items.id
  foreach ($id in $ids) { lemma records delete $tbl $id --pod distill -y | Out-Null }
  Write-Host "$tbl cleared"
}
