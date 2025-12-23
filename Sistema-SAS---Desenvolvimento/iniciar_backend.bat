@echo off
echo Iniciando o servidor backend do SAS...
cd /d "%~dp0"
python -m backend.app
pause
