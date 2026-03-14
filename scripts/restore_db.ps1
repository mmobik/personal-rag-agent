# PowerShell script for database restore from backup

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile
)

if (-not (Test-Path $BackupFile)) {
    Write-Host "[ERROR] File not found: $BackupFile" -ForegroundColor Red
    Write-Host "Usage: .\restore_db.ps1 <path_to_backup_file>" -ForegroundColor Yellow
    Write-Host "Example: .\restore_db.ps1 .\backups\agent_db_20260314_151000.sql" -ForegroundColor Yellow
    exit 1
}

Write-Host "Restoring database from $BackupFile..." -ForegroundColor Yellow

# Restore database
Get-Content $BackupFile | docker exec -i agent-postgres psql -U postgres -d agent_db

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Database restored successfully!" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Failed to restore database" -ForegroundColor Red
    exit 1
}
