@echo off
title PiyushSocial AI - Autonomous Facebook Manager
cd /d "%~dp0"
echo ========================================================
echo  Starting PiyushSocial AI Master Hub...
echo ========================================================
start "" http://localhost:8000
.\.venv\Scripts\python.exe run_server.py
pause
