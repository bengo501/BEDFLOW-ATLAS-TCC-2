@echo off
rem encaminha para o executavel principal (verifica requisitos e inicia o wizard)
cd /d "%~dp0"
call "%~dp0EXECUTAR_BEDFLOW-ATLAS.bat" %*
