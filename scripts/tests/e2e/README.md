# testes end-to-end (e2e) - bedflow-atlas

testes automatizados completos do pipeline, desde geracao de leitos ate simulacao openfoam.

## estrutura

```
scripts/tests/e2e/
├── test_full_pipeline.py       # suite principal de testes
├── test_blender_only.py        # testes focados em blender
├── test_openfoam_only.py       # testes focados em openfoam
├── test_performance.py         # testes de performance
├── outputs/                    # arquivos gerados pelos testes
│   ├── *.bed                  # arquivos de entrada
│   ├── *.bed.json             # parametros compilados
│   ├── *.blend                # modelos 3d
│   └── *_cfd/                 # casos openfoam
├── results/                    # resultados dos testes
│   └── report_*.json          # relatorios em json
├── logs/                       # logs de execucao
│   ├── test_*.log            # logs gerais
│   ├── *_blender.log         # logs blender
│   └── *_openfoam_*.log      # logs openfoam
└── README.md                   # este arquivo
```

## testes disponiveis

### suite principal: test_full_pipeline.py

**6 testes end-to-end:**

1. **test_basic_generation** - geracao basica

   - cria arquivo .bed
   - compila para .bed.json
   - valida sintaxe
2. **test_3d_generation** - geracao 3d completa

   - gera arquivo .bed
   - compila para json
   - gera modelo 3d no blender
   - valida arquivo .blend
3. **test_3d_and_open_blender** - gerar e visualizar

   - gera modelo 3d
   - abre no blender gui
   - teste interativo (requer confirmacao manual)
4. **test_openfoam_setup** - configuracao cfd

   - gera modelo 3d
   - exporta stl
   - cria caso openfoam
   - valida estrutura de arquivos
5. **test_full_simulation_quick** - simulacao rapida

   - pipeline completo
   - executa apenas blockmesh (rapido)
   - valida malha gerada
6. **test_parametric_study** - estudo parametrico

   - gera multiplos leitos
   - varia diametro e numero de particulas
   - valida todos os arquivos

## como usar

### executar todos os testes

```bash
cd scripts/tests/e2e
python test_full_pipeline.py
```

**saida esperada:**

```
======================================================================
INICIANDO SUITE DE TESTES E2E
======================================================================

======================================================================
TESTE 1: geracao basica de leito
======================================================================
[info] arquivo .bed criado: test01_basic_generation.bed
[info] compilando test01_basic_generation.bed...
[ok] compilacao bem-sucedida: test01_basic_generation.bed.json

======================================================================
TESTE 2: geracao 3d completa
======================================================================
[info] arquivo .bed criado: test02_3d_generation.bed
[ok] compilacao bem-sucedida: test02_3d_generation.bed.json
[info] gerando modelo 3d para test02_3d_generation...
[ok] modelo 3d gerado: test02_3d_generation.blend (12.34 mb)

...

======================================================================
RELATORIO FINAL DOS TESTES E2E
======================================================================
total de testes: 6
[ok] passou: 6
[erro] falhou: 0

taxa de sucesso: 100.0%
```

### pular testes interativos

```bash
python test_full_pipeline.py --skip-interactive
```

isso pula o teste que abre o blender gui.

### executar teste especifico

```bash
# apenas geracao 3d
python test_full_pipeline.py --test test_3d_generation

# apenas configuracao openfoam
python test_full_pipeline.py --test test_openfoam_setup

# apenas estudo parametrico
python test_full_pipeline.py --test test_parametric_study
```

## relatorios

### relatorio json

apos cada execucao, um relatorio json e gerado em `results/`:

```json
{
  "timestamp": "2025-10-07T19:30:00",
  "tests": [
    {
      "name": "test01_basic_generation",
      "type": "basic_generation",
      "success": true,
      "duration": 2.5,
      "details": {
        "params": {
          "diameter": 0.05,
          "height": 0.1,
          "particle_count": 20
        },
        "files_created": true
      }
    },
    ...
  ],
  "summary": {
    "total": 6,
    "passed": 6,
    "failed": 0,
    "skipped": 0
  }
}
```

### logs detalhados

cada teste gera logs especificos:

- `logs/test_20251007.log` - log geral
- `logs/test02_blender.log` - log do blender
- `logs/test04_openfoam_setup.log` - log setup openfoam
- `logs/test05_openfoam_run.log` - log simulacao

## cenarios de teste

### cenario 1: validacao basica

**objetivo:** validar compilador dsl

**testes:**

- test_basic_generation

**tempo:** ~5 segundos

### cenario 2: geracao 3d

**objetivo:** validar pipeline blender

**testes:**

- test_basic_generation
- test_3d_generation

**tempo:** ~2 minutos

### cenario 3: visualizacao

**objetivo:** verificar modelo visualmente

**testes:**

- test_3d_and_open_blender

**tempo:** ~3 minutos + tempo manual

### cenario 4: cfd completo

**objetivo:** validar pipeline openfoam

**testes:**

- test_openfoam_setup
- test_full_simulation_quick

**tempo:** ~10 minutos

**requisitos:** wsl2 + openfoam (windows)

### cenario 5: estudo parametrico

**objetivo:** testar multiplas configuracoes

**testes:**

- test_parametric_study

**tempo:** ~30 segundos

**saida:** 4 leitos com variacoes

## configuracao

### requisitos

**minimos:**

- python 3.8+
- java 17+
- antlr 4.13.1
- compilador dsl funcional

**para testes 3d:**

+ blender 4.0+

**para testes cfd:**

+ wsl2 (windows)
+ openfoam 11
+ paraview (opcional)

### verificar ambiente

antes de executar os testes, verifique o ambiente:

```bash
# testar instalacao
python scripts/automation/run_tests.py

# deve mostrar:
# [ok] python
# [ok] java
# [ok] antlr
# [ok] blender
# [ok] wsl2 (se windows)
```

## parametros dos testes

cada teste usa parametros diferentes:

| teste  | diametro | altura | particulas | objetivo                 |
| ------ | -------- | ------ | ---------- | ------------------------ |
| test01 | 0.05m    | 0.1m   | 20         | rapido, validacao basica |
| test02 | 0.05m    | 0.1m   | 30         | tamanho medio            |
| test03 | 0.08m    | 0.15m  | 50         | maior, visualizacao      |
| test04 | 0.05m    | 0.1m   | 20         | rapido, cfd              |
| test05 | 0.05m    | 0.1m   | 15         | muito rapido, simulacao  |
| test06 | varia    | 0.1m   | varia      | multiplas configuracoes  |

## troubleshooting

### erro: "blender nao encontrado"

**solucao:**

```bash
# instalar blender
python scripts/automation/install_blender.py

# ou adicionar ao path manualmente
```

### erro: "wsl nao disponivel"

**solucao:**

```bash
# instalar wsl + openfoam
python scripts/automation/install_openfoam.py

# ou pular testes de simulacao:
python test_full_pipeline.py --skip-interactive
```

### erro: "compilacao falhou"

**solucao:**

```bash
# verificar antlr
python scripts/automation/install_antlr.py

# testar compilador manualmente
python dsl/compiler/bed_compiler_antlr_standalone.py scripts/tests/e2e/outputs/test01.bed
```

### testes muito lentos

**causas:**

- muitas particulas
- iteracoes de empacotamento altas
- simulacao openfoam completa

**solucao:**

- reduzir `particle_count` (20 e rapido)
- reduzir `packing_iterations` (30 e suficiente)
- usar `quick=True` nas simulacoes (apenas blockmesh)

## metricas de performance

tempos esperados (computador medio):

| teste           | tempo            | gargalo               |
| --------------- | ---------------- | --------------------- |
| test01          | 5s               | compilacao            |
| test02          | 2min             | blender physics       |
| test03          | 3min             | blender + manual      |
| test04          | 5min             | exportacao stl        |
| test05          | 10min            | blockmesh             |
| test06          | 30s              | multiplas compilacoes |
| **total** | **~20min** | fisica + cfd          |

## integracao ci/cd

para usar em ci/cd (github actions, gitlab ci):

```yaml
name: testes e2e

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
    
      - name: instalar dependencias
        run: |
          python scripts/automation/setup_complete.py --skip-openfoam
    
      - name: executar testes e2e
        run: |
          cd scripts/tests/e2e
          python test_full_pipeline.py --skip-interactive
    
      - name: upload resultados
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: scripts/tests/e2e/results/
```

## referencias

- [suite de testes](test_full_pipeline.py)
- [automacoes](../../scripts/automation/)
- [documentacao projeto](../../README.md)
- [guia openfoam](../../docs/OPENFOAM_WINDOWS_GUIA.md)

## proximos passos

1. **executar testes**

   ```bash
   python test_full_pipeline.py
   ```
2. **analisar resultados**

   ```bash
   cat results/report_*.json
   ```
3. **verificar logs se houver falhas**

   ```bash
   cat logs/*.log
   ```
4. **visualizar modelos gerados**

   ```bash
   blender outputs/*.blend
   ```
5. **verificar casos openfoam**

   ```bash
   ls -la outputs/*_cfd/
   ```
