# PowerShell script for PostgreSQL backup

$BACKUP_DIR = ".\backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_FILE = "$BACKUP_DIR\agent_db_$TIMESTAMP.sql"

Write-Host "Creating database backup..." -ForegroundColor Yellow

# Create backup
docker exec agent-postgres pg_dump -U postgres agent_db | Out-File -FilePath $BACKUP_FILE -Encoding UTF8

if ($LASTEXITCODE -eq 0) {
    Write-Host "[SUCCESS] Backup created: $BACKUP_FILE" -ForegroundColor Green
    
    # Remove old backups (older than 7 days)
    $OldBackups = Get-ChildItem -Path $BACKUP_DIR -Filter "agent_db_*.sql" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) }
    
    if ($OldBackups) {
        $OldBackups | Remove-Item -Force
        Write-Host "[INFO] Old backups removed: $($OldBackups.Count) files" -ForegroundColor Cyan
    }
} else {
    Write-Host "[ERROR] Failed to create backup" -ForegroundColor Red
    exit 1
}
