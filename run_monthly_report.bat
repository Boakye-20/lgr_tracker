@echo off
REM Double-click this once a month to produce the Word report for committee.

cd /d "%~dp0"
".venv\Scripts\python.exe" build_report.py
echo.
echo Done. Look for the new NCC_Obligations_Report file in this folder.
pause
