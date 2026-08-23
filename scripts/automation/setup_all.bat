@echo off
REM configuracao automatica completa do projeto bedflow-atlas
REM este script instala todas as dependencias necessarias

echo ====================================================================
echo   CONFIGURADOR AUTOMATICO COMPLETO - BEDFLOW-ATLAS
echo ====================================================================
echo.
echo este script ira configurar:
echo   - python (verificacao)
echo   - java + antlr (compilador dsl)
echo   - blender (geracao 3d)
echo   - wsl2 + openfoam (simulacao cfd - opcional)
echo.
echo tempo estimado: 15-60 minutos (dependendo da conexao e componentes)
echo.

pause

echo.
echo ====================================================================
echo [1/3] verificando python...
echo ====================================================================
python --version >nul 2>&1
if errorlevel 1 (
    echo [erro] python nao encontrado!
    echo.
    echo baixe e instale python 3.8+ de: https://python.org
    echo marque a opcao "add python to PATH" durante a instalacao
    echo.
    pause
    exit /b 1
)

python --version
echo [ok] python encontrado

echo.
echo ====================================================================
echo [2/3] navegando para diretorio do projeto...
echo ====================================================================
cd %~dp0\..\..
echo diretorio atual: %CD%
echo [ok] diretorio configurado

echo.
echo ====================================================================
echo [3/3] executando configuracao completa...
echo ====================================================================
echo.
echo escolha o modo de instalacao:
echo   1. completa (python + java + antlr + blender + openfoam)
echo   2. basica (python + java + antlr + blender, sem openfoam)
echo   3. minima (python + java + antlr, sem blender e openfoam)
echo.

set /p MODE="digite sua escolha (1/2/3) [2]: "
if "%MODE%"=="" set MODE=2

if "%MODE%"=="1" (
    echo.
    echo [modo: completo] instalando todos os componentes...
    python scripts\automation\setup_complete.py
) else if "%MODE%"=="2" (
    echo.
    echo [modo: basico] instalando sem openfoam...
    python scripts\automation\setup_complete.py --skip-openfoam
) else if "%MODE%"=="3" (
    echo.
    echo [modo: minimo] instalando apenas essenciais...
    python scripts\automation\install_antlr.py
) else (
    echo.
    echo [erro] opcao invalida: %MODE%
    pause
    exit /b 1
)

if errorlevel 1 (
    echo.
    echo ====================================================================
    echo [erro] configuracao falhou!
    echo ====================================================================
    echo verifique os erros acima
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo [sucesso] configuracao concluida!
echo ====================================================================
echo.
echo proximos passos:
echo   1. teste o wizard: python dsl\bed_wizard.py
echo   2. leia a documentacao: docs\UML_COMPLETO.md
echo   3. veja exemplos em: dsl\examples\
echo.
echo pressione qualquer tecla para sair...
pause >nul

