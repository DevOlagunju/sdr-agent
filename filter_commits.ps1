# Script to remove co-author lines from git commits
cd C:\Users\thedo\SDR

# Get all commit hashes
$commits = git log --format='%H' --reverse

foreach ($commit in $commits) {
    $msg = git log -1 --format='%B' $commit
    $cleanMsg = ($msg -split "`n" | Where-Object { $_ -notmatch 'Co-authored-by:' -and $_ -ne '' }) -join "`n"
    
    Write-Host "Processing: $commit"
    Write-Host "Original message:"
    Write-Host $msg
    Write-Host "`nCleaned message:"
    Write-Host $cleanMsg
    Write-Host "---"
}
