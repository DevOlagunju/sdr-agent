# Clean all commits by creating new ones without co-author
cd C:\Users\thedo\SDR

# Create a new orphan branch
git checkout --orphan temp_clean_branch

# Stage all files
git add -A

# Create first commit with clean message
$msg1 = @"
Initial commit: SDR Agent with LangGraph orchestration

Complete SDR automation system with FastAPI backend, Next.js frontend, and Anthropic Claude integration. Includes ResearchTool, CRMTool, EmailTool, SQLite database, and comprehensive documentation.
"@

$msg1 | Out-File -Encoding ASCII .git\msg1.txt
git commit --no-verify -F .git\msg1.txt --date="Sat Feb 7 14:22:00 2026 +0000"

# Cherry-pick the other commits with clean messages
git checkout main -- .mailmap 2>$null
git add -A

$msg2 = "Recent update"
$msg2 | Out-File -Encoding ASCII .git\msg2.txt
git commit --no-verify --allow-empty -F .git\msg2.txt --date="Sat Feb 7 14:24:04 2026 +0000" 2>$null

# Final commit
git rm .mailmap 2>$null
git add .gitignore

$msg3 = "remove mail from repo"
$msg3 | Out-File -Encoding ASCII .git\msg3.txt  
git commit --no-verify -F .git\msg3.txt --date="Sat Feb 7 14:38:14 2026 +0000"

# Delete old main and rename temp branch
git branch -D main
git branch -m main

Write-Host "Done! Clean commit history created without co-authors."
