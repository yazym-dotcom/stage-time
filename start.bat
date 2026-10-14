@echo off
rem Stage Time: double-click to start. Keeps the window open if something fails.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
pause
