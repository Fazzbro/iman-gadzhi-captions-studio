@echo off
title Iman Gadzhi Studio Captions Pro (Windows Edition)
cd /d "%~dp0"
echo [Iman Gadzhi Studio] Launching Studio Captions Pro...
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" tiny.py
) else (
    python tiny.py
)
pause
