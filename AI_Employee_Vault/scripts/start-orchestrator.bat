@echo off
REM Start Orchestrator for AI Employee (Bronze Tier)
REM This script starts the orchestrator that processes items and triggers Claude Code

cd /d "%~dp0"

echo ========================================
echo AI Employee - Orchestrator
echo ========================================
echo.
echo Vault: ..
echo Monitoring: Needs_Action and Approved folders
echo.
echo The orchestrator will:
echo   - Detect new items in Needs_Action
echo   - Trigger Claude Code processing
echo   - Execute approved actions
echo   - Update Dashboard.md
echo.
echo Press Ctrl+C to stop.
echo.

python orchestrator.py ..

pause
