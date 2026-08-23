@echo off
REM Script de Automação para Windows
REM Configuração automática do projeto BEDFLOW-ATLAS

echo ========================================
echo    CONFIGURADOR AUTOMATICO - BEDFLOW-ATLAS
echo ========================================
echo.

echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale o Python 3.6+ de: https://python.org
    pause
    exit /b 1
)
echo OK: Python encontrado

echo.
echo [2/5] Verificando Blender...
blender --version >nul 2>&1
if errorlevel 1 (
    echo Blender nao encontrado no PATH
    echo.
    echo [2.1/5] Configurando Blender automaticamente...
    python scripts\setup_blender_path.py
    if errorlevel 1 (
        echo ERRO: Falha na configuracao do Blender
        echo Instale o Blender manualmente e tente novamente
        pause
        exit /b 1
    )
) else (
    echo OK: Blender encontrado
)

echo.
echo [3/5] Criando diretorios...
if not exist "models" mkdir models
if not exist "exports" mkdir exports
if not exist "temp" mkdir temp
echo OK: Diretorios criados

echo.
echo [4/5] Executando setup do projeto...
python scripts\setup_project.py --no-auto-install
if errorlevel 1 (
    echo ERRO: Falha no setup do projeto
    pause
    exit /b 1
)

echo.
echo [5/5] Testando instalacao...
python scripts\teste_blender.py
if errorlevel 1 (
    echo AVISO: Alguns testes falharam
) else (
    echo OK: Todos os testes passaram
)

echo.
echo ======================================
echo =======CONFIGURACAO CONCLUIDA=========
echo ======================================
echo.
echo Proximos passos:
echo 1. Teste: blender --version
echo 2. Gere um leito: python scripts\leito_standalone.py
echo 3. Veja exemplos: python scripts\exemplo_uso_standalone.py
echo.
echo Pressione qualquer tecla para sair...
pause >nul
