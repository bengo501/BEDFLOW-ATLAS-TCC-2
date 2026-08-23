# bedflow-atlas

<p align="center">
  <img src="docs/assets/cfdPipelineLight.png" alt="bedflow-atlas" width="220">
</p>

<p align="center">
  pipeline automatizado de cfd para leitos empacotados — dsl, blender / motor python e openfoam.
</p>

<p align="center">
  <a href="README.md">english readme</a>
  ·
  <a href="docs/pt/README.md">documentação completa (pt)</a>
  ·
  <a href="docs/en/README.md">full documentation (en)</a>
</p>

[![python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![blender](https://img.shields.io/badge/blender-4.0+-orange.svg)](https://blender.org)
[![openfoam](https://img.shields.io/badge/openfoam-11-green.svg)](https://openfoam.org)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

https://github.com/bengo501/BEDFLOW-ATLAS/issues

https://github.com/bengo501/BEDFLOW-ATLAS/milestones

## o que é

o bedflow-atlas gera geometrias de leitos empacotados a partir de uma descrição `.bed`, compila para json normalizado, constrói modelos 3d (python puro ou packing rigid-body no blender) e pode montar casos openfoam. um dashboard em react fala com um backend fastapi (wizard, jobs, resultados, templates e relatórios).

pipeline:

1. **dsl** — linguagem declarativa `.bed` (gramática antlr)
2. **compilador** — `.bed` → `.bed.json` (unidades si)
3. **geração 3d** — blender ou o motor python
4. **cfd** — openfoam (`blockmesh`, `snappyhexmesh`, `simplefoam`)
5. **interface web** — dashboard, wizard, viewer 3d, histórico, configurações

## início rápido (windows)

clique duplo em **`EXECUTAR_BEDFLOW-ATLAS.bat`** na raiz do repositório.

o launcher verifica python, pip, pacotes do wizard, pacotes do backend, node/npm e, se quiser, open3d. se faltar algo, pergunta e instala passo a passo (`winget` quando existir).

no menu do wizard, escolha **2** para subir a aplicação web (uvicorn na porta **8000** + vite na **5173**).

comandos manuais (a partir da raiz):

```bash
# wizard (use a raiz, nao a pasta dsl/)
python bed_wizard.py

# backend
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# frontend (outro terminal)
cd frontend
npm install
npm run dev
```

- interface: http://127.0.0.1:5173
- api: http://127.0.0.1:8000
- swagger: http://127.0.0.1:8000/docs

pular a verificação: `EXECUTAR_BEDFLOW-ATLAS.bat --skip-checks`

## docker local

```bash
cd docker
copy .env.example .env
docker compose up --build
```

a imagem do backend é construída a partir da **raiz do repo**. `WITH_BLENDER=0` é o perfil python; `1` inclui blender. `MODELING_PROFILE=blender` (padrão) ou `python`.

## estrutura

```
BEDFLOW-ATLAS/
├── EXECUTAR_BEDFLOW-ATLAS.bat   # launcher principal (checagens + wizard)
├── bed_wizard.py                # atalho da raiz → dsl/bed_wizard.py
├── bedflow_*.py                 # caminhos, malhas e registro compartilhados
├── backend/                     # api fastapi
├── frontend/                    # interface react + vite
├── dsl/                         # gramática, compilador, wizard terminal
├── scripts/                     # automação, blender, openfoam, testes
├── docker/                      # compose + dockerfiles
├── docs/                        # documentação (en + pt)
├── tutorial/                    # tutoriais mínimos de openfoam
├── cases/                       # casos .bed de exemplo
├── local_data/                  # artefactos de runtime (não versionados)
└── generated/                   # saídas antigas do pipeline
```

os módulos `bedflow_*.py` ficam na raiz de propósito: backend, wizard e docker importam-nos como pacotes de topo.

os atalhos finos que estavam na raiz passaram para `scripts/automation/`.

## documentação

| idioma | entrada |
|--------|---------|
| português (este ficheiro) | [docs/pt/README.md](docs/pt/README.md) |
| english | [README.md](README.md) · [docs/en/README.md](docs/en/README.md) |
| html (wizard) | [dsl/documentacao.html](dsl/documentacao.html) · [dsl/documentacao_en.html](dsl/documentacao_en.html) |

tópicos: [início](docs/pt/inicio.md) · [arquitetura](docs/pt/arquitetura.md) · [dsl e wizard](docs/pt/dsl-e-wizard.md) · [frontend](docs/pt/frontend.md) · [backend](docs/pt/backend.md) · [pipeline e cfd](docs/pt/pipeline-e-cfd.md) · [docker](docs/pt/docker.md) · [dados e caminhos](docs/pt/dados-e-caminhos.md)

## autor

**bengo501** — [github](https://github.com/bengo501)
