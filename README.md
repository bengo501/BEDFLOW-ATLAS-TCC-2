# bedflow-atlas

<p align="center">
  <img src="docs/assets/cfdPipelineLight.png" alt="bedflow-atlas" width="220">
</p>

<p align="center">
  automated cfd pipeline for packed beds — dsl, blender / python modeling, and openfoam.
</p>

<p align="center">
  <a href="README.pt.md">documentação em português</a>
  ·
  <a href="docs/en/README.md">full documentation (en)</a>
  ·
  <a href="docs/pt/README.md">documentação completa (pt)</a>
</p>

[![python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![blender](https://img.shields.io/badge/blender-4.0+-orange.svg)](https://blender.org)
[![openfoam](https://img.shields.io/badge/openfoam-11-green.svg)](https://openfoam.org)
[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

https://github.com/bengo501/BEDFLOW-ATLAS/issues

https://github.com/bengo501/BEDFLOW-ATLAS/milestones

## what it is

bedflow-atlas generates packed-bed geometries from a `.bed` description, compiles them to normalized json, builds 3d models (pure python or blender rigid-body packing), and can drive openfoam cases. a react dashboard talks to a fastapi backend for wizard runs, jobs, results, templates, and reports.

pipeline:

1. **dsl** — declarative `.bed` language (antlr grammar)
2. **compiler** — `.bed` → `.bed.json` (si units)
3. **3d generation** — blender or the python modeling engine
4. **cfd** — openfoam (`blockmesh`, `snappyhexmesh`, `simplefoam`)
5. **web ui** — dashboard, wizard, 3d viewer, history, settings

## quick start (windows)

double-click **`EXECUTAR_BEDFLOW-ATLAS.bat`** at the repo root.

the launcher checks python, pip, wizard packages, backend packages, node/npm, and optionally open3d. if something is missing it asks and installs step by step (`winget` when available).

then, in the wizard menu, pick **2** to start the web app (uvicorn on port **8000** + vite on **5173**).

manual commands (from the repo root):

```bash
# wizard (recommended from the root, not from dsl/)
python bed_wizard.py

# backend
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# frontend (another terminal)
cd frontend
npm install
npm run dev
```

- ui: http://127.0.0.1:5173
- api: http://127.0.0.1:8000
- swagger: http://127.0.0.1:8000/docs

skip the installer checks: `EXECUTAR_BEDFLOW-ATLAS.bat --skip-checks`

## local docker

```bash
cd docker
copy .env.example .env
docker compose up --build
```

backend image is built from the **repo root** (`docker build -f docker/Dockerfile ..`). `WITH_BLENDER=0` is the python-modeling profile; `1` includes blender. `MODELING_PROFILE=blender` (default) or `python`.

## project layout

```
BEDFLOW-ATLAS/
├── EXECUTAR_BEDFLOW-ATLAS.bat   # main launcher (checks + wizard)
├── bed_wizard.py                # root shim → dsl/bed_wizard.py
├── bedflow_*.py                 # shared path / mesh / registry modules
├── backend/                     # fastapi api
├── frontend/                    # react + vite ui
├── dsl/                         # grammar, compiler, terminal wizard
├── scripts/                     # automation, blender, openfoam, tests
├── docker/                      # compose + dockerfiles
├── docs/                        # documentation (en + pt)
├── tutorial/                    # minimal openfoam tutorials
├── cases/                       # sample .bed cases
├── local_data/                  # runtime artifacts (gitignored)
└── generated/                   # legacy pipeline outputs
```

root python modules (`bedflow_local_paths.py`, `bedflow_bed_registry.py`, …) stay at the root on purpose: backend, wizard, and docker import them as top-level modules.

thin wrappers that used to sit in the root now live under `scripts/automation/`.

## documentation

| language | entry |
|----------|--------|
| english (this file) | [docs/en/README.md](docs/en/README.md) |
| português | [README.pt.md](README.pt.md) · [docs/pt/README.md](docs/pt/README.md) |
| html (wizard) | [dsl/documentacao.html](dsl/documentacao.html) · [dsl/documentacao_en.html](dsl/documentacao_en.html) |

topics: [getting started](docs/en/getting-started.md) · [architecture](docs/en/architecture.md) · [dsl and wizard](docs/en/dsl-and-wizard.md) · [frontend](docs/en/frontend.md) · [backend](docs/en/backend.md) · [pipeline and cfd](docs/en/pipeline-and-cfd.md) · [docker](docs/en/docker.md) · [data and paths](docs/en/data-and-paths.md)

## dsl example

```
bed {
    diameter = 5cm
    height = 10cm
    wall_thickness = 2mm
    shape = "cylinder"
}

particles {
    count = 100
    kind = "sphere"
    diameter = 5mm
    mass = 0.1kg
}

packing {
    method = "rigid_body"
    gravity = (0, 0, -9.81) m/s2
}

cfd {
    regime = "laminar"
    inlet_velocity = 0.1 m/s
    fluid_density = 1000 kg/m3
}
```

compile:

```bash
python dsl/compiler/bed_compiler_antlr_standalone.py leito.bed
```

## openfoam tutorials

versioned minimal cases (no packed-bed pipeline):

| folder | content |
|--------|---------|
| [`tutorial/cavity-icoFoam/`](tutorial/cavity-icoFoam/) | lid-driven cavity — `icoFoam` |
| [`tutorial/channel-simpleFoam/`](tutorial/channel-simpleFoam/) | 2d laminar channel — `simpleFoam` |
| [`tutorial/sphere-snappyHexMesh/`](tutorial/sphere-snappyHexMesh/) | `blockMesh` + `snappyHexMesh` |

see [tutorial/README.md](tutorial/README.md).

## author

**bengo501** — [github](https://github.com/bengo501)
