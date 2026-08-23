@echo off
rem ============================================================
rem  bedflow-atlas  -  executavel principal (clique duplo)
rem  1) verifica requisitos
rem  2) instala o que faltar, passo a passo
rem  3) inicia o wizard de leitos (.bed)
rem ============================================================
chcp 65001 >nul
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title bedflow-atlas - setup e wizard

echo ============================================================
echo   bedflow-atlas
echo   verificacao de requisitos e inicializacao
echo ============================================================
echo.
echo  pasta: %cd%
echo.

set "PY_CMD="
where py >nul 2>&1 && set "PY_CMD=py"
if not defined PY_CMD (
    where python >nul 2>&1 && set "PY_CMD=python"
)

if /i "%~1"=="--skip-checks" goto :run_wizard

rem ---------- passo 1: python ----------
echo [1/6] python 3.8+
if not defined PY_CMD (
    echo        python nao encontrado no path.
    echo.
    set /p "_INST_PY=instalar python agora com winget? [S/n] "
    if /i not "!_INST_PY!"=="n" (
        where winget >nul 2>&1
        if errorlevel 1 (
            echo        winget nao disponivel. abra https://www.python.org/downloads/
            echo        marque "add python.exe to path" no instalador.
            start "" "https://www.python.org/downloads/"
            echo.
            pause
            echo        depois de instalar, execute este .bat de novo.
            exit /b 1
        )
        echo        instalando python 3.12 via winget...
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        echo        feche e abra este launcher de novo para o path atualizar.
        pause
        exit /b 1
    )
    echo        sem python o wizard nao inicia.
    pause
    exit /b 1
)

%PY_CMD% -c "import sys; raise SystemExit(0 if sys.version_info>=(3,8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo        [erro] python 3.8+ e obrigatorio. atualize em https://www.python.org/downloads/
    pause
    exit /b 1
)
for /f "delims=" %%v in ('%PY_CMD% -c "import sys; print(sys.version.split()[0])"') do set "PY_VER=%%v"
echo        ok  %PY_CMD%  (!PY_VER!)
echo.

rem ---------- passo 2: pip ----------
echo [2/6] pip
%PY_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo        pip nao encontrado. tentando garantir via python -m ensurepip...
    %PY_CMD% -m ensurepip --upgrade
    %PY_CMD% -m pip install --upgrade pip
)
%PY_CMD% -m pip --version >nul 2>&1
if errorlevel 1 (
    echo        [erro] nao foi possivel usar pip.
    pause
    exit /b 1
)
echo        ok
echo.

rem ---------- passo 3: dependencias do wizard (terminal) ----------
echo [3/6] dependencias do wizard (rich, prompt_toolkit, typer, antlr)
%PY_CMD% -c "import rich, prompt_toolkit, typer, antlr4" >nul 2>&1
if errorlevel 1 (
    echo        faltam pacotes do terminal.
    set /p "_INST_TERM=instalar agora com pip? [S/n] "
    if /i not "!_INST_TERM!"=="n" (
        echo        instalando dsl\requirements-terminal.txt ...
        %PY_CMD% -m pip install -r "dsl\requirements-terminal.txt"
        if errorlevel 1 (
            echo        [aviso] falha ao instalar dependencias do terminal.
            pause
        )
    )
) else (
    echo        ok
)
echo.

rem ---------- passo 4: dependencias do backend ----------
echo [4/6] dependencias do backend (fastapi, uvicorn)
%PY_CMD% -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo        faltam pacotes do backend.
    set /p "_INST_BE=instalar agora com pip? [S/n] "
    if /i not "!_INST_BE!"=="n" (
        echo        instalando backend\requirements.txt ...
        %PY_CMD% -m pip install -r "backend\requirements.txt"
        if errorlevel 1 (
            echo        [aviso] falha ao instalar dependencias do backend.
            pause
        )
    )
) else (
    echo        ok
)
echo.

rem ---------- passo 5: node.js / npm (frontend) ----------
echo [5/6] node.js e npm (interface web)
set "HAS_NODE=0"
where node >nul 2>&1 && set "HAS_NODE=1"
if "!HAS_NODE!"=="0" (
    echo        node.js nao encontrado. a interface web precisa dele.
    set /p "_INST_NODE=instalar node.js lts agora com winget? [S/n] "
    if /i not "!_INST_NODE!"=="n" (
        where winget >nul 2>&1
        if errorlevel 1 (
            echo        winget nao disponivel. abra https://nodejs.org/
            start "" "https://nodejs.org/"
            echo        depois de instalar, execute este .bat de novo para o npm install.
        ) else (
            echo        instalando node.js lts via winget...
            winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements
            echo        feche e abra este launcher de novo para o path atualizar.
            pause
            exit /b 1
        )
    )
) else (
    for /f "delims=" %%v in ('node -v') do echo        ok  node %%v
    if exist "frontend\node_modules\" (
        echo        frontend\node_modules ja existe
    ) else (
        echo        pasta frontend\node_modules nao encontrada.
        set /p "_INST_NPM=rodar npm install no frontend agora? [S/n] "
        if /i not "!_INST_NPM!"=="n" (
            pushd frontend
            call npm install
            popd
        )
    )
)
echo.

rem ---------- passo 6: visualizacao 3d desktop (opcional) ----------
echo [6/6] visualizacao 3d desktop (open3d) - opcional
%PY_CMD% -c "import open3d" >nul 2>&1
if errorlevel 1 (
    echo        open3d nao instalado. so e preciso para o viewer desktop.
    set /p "_INST_VIS=instalar requirements-visualizacao.txt agora? [n/S] "
    if /i "!_INST_VIS!"=="s" (
        echo        instalando requirements-visualizacao.txt ...
        %PY_CMD% -m pip install -r "requirements-visualizacao.txt"
        if errorlevel 1 (
            echo        [aviso] a instalacao do open3d pode falhar no windows
            echo        se os caminhos forem muito longos. veja o comentario
            echo        em requirements-visualizacao.txt
        )
    ) else (
        echo        pulado
    )
) else (
    echo        ok
)
echo.

echo requisitos verificados.
echo.

:run_wizard
if not defined PY_CMD (
    echo [erro] python nao encontrado no path.
    pause
    exit /b 1
)
echo iniciando o wizard... (use o menu; escolha "sair" para fechar)
echo dica: no menu, opcao 2 sobe a aplicacao web (backend + frontend).
echo.
%PY_CMD% bed_wizard.py
set "_RC=%errorlevel%"

echo.
if not "%_RC%"=="0" (
    echo [o wizard terminou com codigo %_RC%]
    pause
)
endlocal
exit /b %_RC%
