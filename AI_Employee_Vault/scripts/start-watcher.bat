@echo off
REM Start Filesystem Watcher for AI Employee (Bronze Tier)
REM This script starts the watcher that monitors the Inbox folder

cd /d "%~dp0"

echo ========================================
echo AI Employee - Filesystem Watcher
echo ========================================
echo.
echo Watching folder: ..\Inbox
echo Vault: ..
echo.
echo Drop files into the Inbox folder to trigger processing.
echo Press Ctrl+C to stop.
echo.

python filesystem_watcher.py ..

pause
