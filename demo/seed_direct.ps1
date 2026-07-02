# Deterministic demo seed — writes the 6 hero issues DIRECTLY to the table
# (no agents / workflow), so the board is always complete and identical for a
# demo. Use this for a reliable pre-seeded board; use the Triage button / the
# triage_batch workflow to show the real live pipeline.
$env:PATH = "C:\Users\Allan\.local\bin;$env:PATH"
$pod = "distill"

# 1. Clear existing rows
foreach ($tbl in @('issues','releases')) {
  $ids = (lemma --json records list $tbl --pod $pod --limit 500 | ConvertFrom-Json).items.id
  foreach ($id in $ids) { lemma records delete $tbl $id --pod $pod -y | Out-Null }
}
Write-Host "cleared"

function New-Issue($obj) {
  $json = $obj | ConvertTo-Json -Compress
  return (lemma --json records create issues --data $json --pod $pod | ConvertFrom-Json).id
}

# 2. Create the CSV-export bug first so the duplicate can link to it
$csv = New-Issue @{
  source_text = "Steps: 1. Open Reports page 2. Click Export to CSV 3. File downloads but is 0 bytes / empty. Expected a populated CSV. Reproduced on Chrome and Firefox."
  source_channel = "github"; title = "CSV export produces an empty file"; type = "bug"
  confidence = 0.9; priority = "P2"; reasoning = "Clear, reproducible export bug with concrete steps and cross-browser confirmation."
  repro_steps = "1. Open the Reports page. 2. Click 'Export to CSV'. 3. Observe the downloaded file is 0 bytes."
  status = "triaged"
}
Write-Host "csv bug -> $csv"

# 3. The rest
New-Issue @{
  source_text = "Every single time I hit save the app freezes for a second then crashes, and everything I just wrote is gone. Whole team hit this in production. Urgent."
  source_channel = "email"; title = "App wipes my data on save"; type = "bug"
  confidence = 0.95; priority = "P0"; reasoning = "Reproducible crash on save causing data loss in production for the whole team — highest severity."
  repro_steps = "1. Open the app and make edits. 2. Click Save. 3. App freezes ~1s then crashes. 4. Reopen — all unsaved edits are gone."
  status = "needs_approval"
} | Out-Null

New-Issue @{
  source_text = "On the Reports page I click Export to CSV and the file downloads but it's completely empty — 0 bytes, no rows. Expected a populated CSV. Latest Chrome."
  source_channel = "email"; title = "CSV export downloads an empty file"; type = "duplicate"
  confidence = 0.85; priority = "P2"; reasoning = "Same empty-CSV export defect as an existing GitHub report."
  linked_to = $csv; status = "triaged"
} | Out-Null

New-Issue @{
  source_text = "would be amazing if we could get a dark mode at some point, the bright white background kind of kills my eyes when working late"
  source_channel = "slack"; title = "Dark mode support"; type = "feature"
  confidence = 0.9; reasoning = "Feature request for a dark theme."; status = "triaged"
} | Out-Null

New-Issue @{
  source_text = "idk, something just feels kind of off lately? like it's maybe not as snappy as it used to be, but honestly hard to say. might just be me"
  source_channel = "support"; title = "App feels less snappy lately"; type = "question"
  confidence = 0.4; reasoning = "Vague performance concern, low confidence — needs clarification before it can be actioned."; status = "triaged"
} | Out-Null

New-Issue @{
  source_text = "GET 10000 FOLLOWERS FAST!! click here >>> www.totally-not-spam.example limited time!!!"
  source_channel = "other"; title = "Follower spam"; type = "spam"
  confidence = 0.95; reasoning = "Promotional spam, not product feedback."; status = "triaged"
} | Out-Null

$n = (lemma --json records list issues --pod $pod | ConvertFrom-Json).total
Write-Host "seeded $n issues"
