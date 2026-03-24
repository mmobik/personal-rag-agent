# migrate_to_user_types.ps1
Write-Host "Starting migration..." -ForegroundColor Yellow

Get-Content migrate.sql | docker exec -i agent-postgres psql -U postgres -d agent_db

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration completed!" -ForegroundColor Green
} else {
    Write-Host "Migration failed!" -ForegroundColor Red
}