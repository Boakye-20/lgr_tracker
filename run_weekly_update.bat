@echo off
REM Double-click this every Monday to refresh the intelligence feed.
REM It runs the scraper using the virtual environment in this folder.

cd /d "%~dp0"
".venv\Scripts\python.exe" update_intelligence.py
echo.
echo Done. Open AuditTracker.xlsx to review new items.
pause
