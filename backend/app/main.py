# arranca a aplicacao fastapi registra middlewares monta estaticos e inclui routers
# tambem corre migracao leve e seed opcional no evento startup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys

# calcula raiz do repo subindo tres niveis a partir deste ficheiro app main py
project_root = Path(__file__).parent.parent.parent
# insere raiz no sys path para imports absolutos estilo backend app
sys.path.insert(0, str(project_root))

from bedflow_local_paths import ensure_local_data_layout, legacy_generated_root, local_data_root

from backend.app.api import routes
from backend.app.database.connection import DatabaseConnection
from backend.app.database.seed_demo import seed_demo_data_if_needed

# objeto app exposto ao asgi uvicorn
# docs e redoc gerados a partir dos tipos pydantic dos endpoints
app = FastAPI(
    title="CFD Pipeline API",
    description="api rest para gerenciar pipeline de simulações cfd de leitos empacotados",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# cors liberta chamadas do frontend vite ou create react app em portas locais
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# local_data e o sitio canonico; generated mantido para ficheiros antigos
ensure_local_data_layout()
_local = local_data_root()
_legacy_gen = legacy_generated_root()

# /files -> local_data (ex.: /files/beds/foo.bed.json)
app.mount("/files", StaticFiles(directory=str(_local)), name="files")
# /generated -> pasta legada ainda referenciada por caminhos antigos
app.mount("/generated", StaticFiles(directory=str(_legacy_gen)), name="generated_static")

# router principal cobre bed compile modelo jobs e listagens
app.include_router(routes.router, prefix="/api")

# router sql expoe crud beds simulations results e resumos
from backend.app.api import routes_database
app.include_router(routes_database.router, prefix="/api")

# router integrado orquestra pipeline longo
from backend.app.api import routes_integrated
app.include_router(routes_integrated.router, prefix="/api")

# routers auxiliares wizard cfd casos templates relatorios perfil settings admin
from backend.app.api import routes_wizard, routes_cfd, routes_casos, routes_templates
app.include_router(routes_wizard.router, prefix="/api")
app.include_router(routes_cfd.router, prefix="/api")
app.include_router(routes_casos.router, prefix="/api")
app.include_router(routes_templates.router, prefix="/api")

from backend.app.api import routes_reports
app.include_router(routes_reports.router, prefix="/api")

from backend.app.api import routes_profile
app.include_router(routes_profile.router, prefix="/api")

from backend.app.api import routes_settings
app.include_router(routes_settings.router, prefix="/api")

from backend.app.api import routes_admin
app.include_router(routes_admin.router, prefix="/api")

from backend.app.api import routes_viewer
app.include_router(routes_viewer.router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    # garante ddl aplicada antes de aceitar trafego
    DatabaseConnection.create_tables()
    # dados demo so se env e base permitirem
    seed_demo_data_if_needed()


@app.get("/")
async def root():
    # health humano com links uteis
    return {
        "message": "cfd pipeline api",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health():
    # health de infraestrutura inclui ping ao sql
    db_status = DatabaseConnection.check_connection()

    return {
        "status": "healthy" if db_status else "degraded",
        "services": {
            "bed_compiler": "available",
            "blender": "available",
            "openfoam": "available",
            "database": "connected" if db_status else "disconnected"
        }
    }

if __name__ == "__main__":
    import uvicorn
    # bloco main permite python backend app main py em dev
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
