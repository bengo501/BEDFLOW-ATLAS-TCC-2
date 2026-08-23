# scripts de automacao - bedflow-atlas

documentacao geral: [docs/en](../../docs/en/README.md) · [docs/pt](../../docs/pt/README.md)

o ponto de entrada no windows e `EXECUTAR_BEDFLOW-ATLAS.bat` na raiz (verifica python, pip, wizard, backend, node e instala o que faltar). os atalhos que estavam na raiz (`instalar_dependencias.bat`, `diagnostico_backend.ps1`, `monitor_pipeline.ps1`, `executar_modelo_e_visualizar.bat`) vivem agora so nesta pasta.

esta pasta contem scripts para instalacao e configuracao automatica de todos os componentes do projeto.

## indice

- [instalacao rapida](#instalacao-rapida)
- [scripts disponiveis](#scripts-disponiveis)
- [instalacao por componente](#instalacao-por-componente)
- [requisitos](#requisitos)
- [troubleshooting](#troubleshooting)

## instalacao rapida

### windows

```powershell
# executar configuracao completa
scripts\automation\setup_all.bat
```

ou diretamente:

```powershell
# configuracao completa (todos os componentes)
python scripts/automation/setup_complete.py

# configuracao sem openfoam
python scripts/automation/setup_complete.py --skip-openfoam
```

### linux / macos

```bash
# configuracao completa
python3 scripts/automation/setup_complete.py

# configuracao sem openfoam (use gerenciador de pacotes do sistema)
python3 scripts/automation/setup_complete.py --skip-openfoam
```

## scripts disponiveis

### 1. setup_complete.py (recomendado)

**script mestre** que configura todo o projeto automaticamente.

**uso:**

```bash
python scripts/automation/setup_complete.py [opcoes]
```

**opcoes:**

- `--skip-openfoam` - pula instalacao do openfoam

**componentes configurados:**

1. python (verificacao de versao)
2. java + antlr (compilador dsl)
3. blender (geracao de modelos 3d)
4. wsl2 + openfoam (simulacao cfd - windows apenas)
5. estrutura de diretorios
6. arquivo de configuracao

**tempo estimado:** 15-60 minutos (depende da conexao e componentes escolhidos)

### 2. install_antlr.py

instala **java** e **antlr** para compilar a dsl.

**uso:**

```bash
python scripts/automation/install_antlr.py [opcoes]
```

**opcoes:**

- `--antlr-version VERSION` - versao do antlr (padrao: 4.13.1)
- `--java-version VERSION` - versao do java (padrao: 17)

**o que faz:**

1. verifica se java esta instalado
2. instala java automaticamente se necessario
3. baixa antlr jar
4. gera parser python a partir da gramatica `Bed.g4`
5. testa arquivos gerados

**tempo estimado:** 5-10 minutos

### 3. install_blender.py

instala **blender** automaticamente.

**uso:**

```bash
python scripts/automation/install_blender.py [opcoes]
```

**opcoes:**

- `--version VERSION` - versao do blender (padrao: 4.0.2)
- `--no-system-package` - nao usar gerenciador de pacotes
- `--install-dir DIR` - diretorio customizado

**o que faz:**

1. detecta sistema operacional
2. tenta instalar via gerenciador de pacotes (apt/dnf/brew)
3. se falhar, baixa e instala manualmente
4. configura no path

**tempo estimado:** 5-15 minutos

### 4. install_openfoam.py

instala **wsl2** e **openfoam** no windows.

**uso:**

```bash
python scripts/automation/install_openfoam.py [opcoes]
```

**opcoes:**

- `--version VERSION` - versao do openfoam (padrao: 11)
- `--skip-wsl-install` - pula instalacao do wsl2
- `--no-extras` - nao instala paraview e tutorial

**o que faz:**

1. verifica/instala wsl2
2. instala ubuntu no wsl
3. atualiza pacotes
4. instala dependencias (gcc, cmake, openmpi, etc)
5. adiciona repositorio oficial openfoam
6. instala openfoam
7. configura bashrc
8. instala paraview
9. cria caso tutorial de exemplo

**tempo estimado:** 30-60 minutos

**atencao:** pode requerer reinicializacao do windows

### 5. setup_all.bat (windows apenas)

**arquivo batch** interativo para windows.

**uso:**

```batch
scripts\automation\setup_all.bat
```

**modos:**

1. **completo** - todos os componentes (python + java + antlr + blender + openfoam)
2. **basico** - sem openfoam (python + java + antlr + blender)
3. **minimo** - apenas dsl (python + java + antlr)

## instalacao por componente

### apenas antlr + java

```bash
python scripts/automation/install_antlr.py
```

**resultado:**

- java instalado
- antlr jar baixado
- parser python gerado
- compilador dsl funcional

### apenas blender

```bash
python scripts/automation/install_blender.py
```

**resultado:**

- blender instalado
- blender no path
- scripts python do blender funcionais

### apenas openfoam (windows)

```bash
python scripts/automation/install_openfoam.py
```

**resultado:**

- wsl2 instalado
- ubuntu instalado
- openfoam instalado
- paraview instalado
- caso tutorial criado

## requisitos

### requisitos minimos

- **python**: 3.8 ou superior
- **espaco em disco**:
  - minimo: 2 gb (python + java + antlr)
  - basico: 5 gb (+ blender)
  - completo: 15 gb (+ wsl2 + openfoam)
- **internet**: necessaria para downloads
- **sistema operacional**: windows 10/11, linux, macos

### requisitos recomendados

- **ram**: 8 gb minimo, 16 gb recomendado
- **processador**: 4 cores ou mais
- **gpu**: qualquer (blender funciona sem gpu dedicada)
- **windows**: versao 2004+ (para wsl2)

---

## troubleshooting

### erro: "python nao encontrado"

**solucao:**

1. instale python de [python.org](https://python.org)
2. marque "add python to path" durante instalacao
3. reinicie o terminal

### erro: "java nao encontrado apos instalacao"

**solucao:**

1. reinicie o terminal
2. verifique: `java -version`
3. se ainda falhar, adicione manualmente ao path:
   - windows: `C:\Program Files\Microsoft\jdk-17.0.16.8-hotspot\bin`
   - linux: `/usr/lib/jvm/java-17-openjdk/bin`

### erro: "wsl nao encontrado"

**solucao:**

1. verifique versao do windows: `winver` (requer 2004+)
2. habilite wsl nas features do windows:
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```
3. reinicie o computador
4. execute novamente

### erro: "antlr falhou ao gerar parser"

**solucao:**

1. verifique se `Bed.g4` existe em `dsl/grammar/`
2. verifique erros de sintaxe na gramatica
3. tente manualmente:
   ```bash
   java -jar dsl/antlr-4.13.1-complete.jar -Dlanguage=Python3 -o dsl/generated dsl/grammar/Bed.g4
   ```

### erro: "blender nao abre modelo"

**solucao:**

1. verifique se arquivo `.blend` existe
2. teste blender manualmente: `blender --version`
3. verifique logs em `output/` ou `temp/`

### erro: "openfoam command not found no wsl"

**solucao:**

1. abra wsl: `wsl`
2. carregue openfoam:
   ```bash
   source /opt/openfoam11/etc/bashrc
   ```
3. adicione ao `~/.bashrc` para carregar automaticamente:
   ```bash
   echo "source /opt/openfoam11/etc/bashrc" >> ~/.bashrc
   ```

### downloads muito lentos

**solucao:**

1. use cabo ethernet ao inves de wifi
2. pause outros downloads
3. tente em horario diferente
4. considere instalacao manual de componentes grandes (blender, openfoam)

## instalacao manual alternativa

se os scripts automaticos falharem, instale manualmente:

### 1. python

- download: [python.org](https://python.org)
- versao minima: 3.8

### 2. java

- download: [adoptium.net](https://adoptium.net/)
- versao minima: 17

### 3. antlr

- download jar: [antlr.org](https://www.antlr.org/download.html)
- salve em: `dsl/antlr-4.13.1-complete.jar`
- gere parser:
  ```bash
  java -jar dsl/antlr-4.13.1-complete.jar -Dlanguage=Python3 -o dsl/generated dsl/grammar/Bed.g4
  ```

### 4. blender

- download: [blender.org](https://www.blender.org/download/)
- versao minima: 4.0

### 5. openfoam (windows)

- siga: [docs/OPENFOAM_WINDOWS_GUIA.md](../../docs/OPENFOAM_WINDOWS_GUIA.md)

## estrutura de arquivos gerados

apos instalacao completa:

```
BEDFLOW-ATLAS/
├── .config/
│   └── config.ini                    # configuracao do projeto
│
├── dsl/
│   ├── antlr-4.13.1-complete.jar     # antlr runtime
│   ├── generated/                    # parser python gerado
│   │   ├── BedLexer.py
│   │   ├── BedParser.py
│   │   └── BedListener.py
│   └── antlr.bat / antlr.sh          # alias antlr
│
├── generated/
│   ├── 3d/
│   │   ├── blender/                  # arquivos .blend fonte
│   │   ├── exports/                  # glb/gltf/obj/stl exportados
│   │   └── output/                   # modelos 3d finais por execucao
│   ├── cfd/                          # casos openfoam
│   ├── configs/                      # arquivos .bed e .bed.json
│   └── batch/                        # execucoes em lote
│
├── logs/                             # logs de execucao
└── ...
```

## proximos passos apos instalacao

1. **testar wizard:**

   ```bash
   python dsl/bed_wizard.py
   ```
2. **criar primeiro leito:**

   - escolher modo blender
   - definir parametros
   - gerar modelo 3d
3. **executar simulacao cfd:**

   ```bash
   python scripts/openfoam_scripts/setup_openfoam_case.py \
     dsl/leito.bed.json \
     generated/3d/output/leito.blend \
     --output-dir generated/cfd
   ```
4. **ler documentacao:**

   - `docs/UML_COMPLETO.md` - arquitetura
   - `docs/OPENFOAM_WINDOWS_GUIA.md` - guia openfoam
   - `dsl/documentacao.html` - documentacao web

## suporte

se encontrar problemas:

1. verifique os logs em `logs/`
2. leia a documentacao em `docs/`
3. verifique issues no github
4. contate o desenvolvedor

## referencias

- [python](https://python.org)
- [java/openjdk](https://adoptium.net/)
- [antlr](https://www.antlr.org/)
- [blender](https://www.blender.org/)
- [openfoam](https://www.openfoam.com/)
- [wsl2](https://docs.microsoft.com/en-us/windows/wsl/)
