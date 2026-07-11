@echo off
REM Double-click this before any committee meeting or review to refresh the dashboard.
REM Close AuditTracker.xlsx first, then run this, then reopen the file.

cd /d "%~dp0"
".venv\Scripts\python.exe" build_dashboard.py
echo.
echo Done. Open AuditTracker.xlsx and go to the Dashboard tab.
pause
