@echo off
setlocal
powershell -ExecutionPolicy Bypass -File "%~dp0start_project.ps1" %*
if errorlevel 1 (
    echo.
    echo Start projektu nie powiodl sie.
    pause
)
