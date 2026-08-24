@echo off
title Sistema de Controle Financeiro Pessoal
echo =========================================================
echo  Iniciando Sistema de Controle Financeiro Pessoal...
echo =========================================================

if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" "%~dp0bolso.py"
) else (
    python "%~dp0bolso.py"
)

pause

