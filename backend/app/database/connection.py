# configura sqlalchemy engine session factory e helpers de arranque
# tambem expoe get db como dependencia fastapi
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from pathlib import Path
from dotenv import load_dotenv

# carrega variaveis de um ficheiro env ao lado do projeto se existir
load_dotenv()

try:
    from bedflow_local_paths import ensure_local_data_layout
except ImportError:
    def ensure_local_data_layout() -> None:
        pass

# raiz do repositorio (backend/app/database -> quatro niveis acima)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_LOCAL_DATA = _PROJECT_ROOT / "local_data"
_LOCAL_SQLITE = _LOCAL_DATA / "cfd_pipeline.db"

# ficheiro sqlite dentro de local_data para nao misturar com cwd e facilitar gitignore
_DEFAULT_SQLITE_URL = f"sqlite:///{_LOCAL_SQLITE.as_posix()}"

# string de ligacao completa prioriza env senao sqlite local em local_data
DATABASE_URL = os.getenv("DATABASE_URL", _DEFAULT_SQLITE_URL)

# engine mantem pool de ligacoes e traduz orm para sql
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

# session local fabrica objetos session ligados ao engine acima
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# base e a classe mae declarative usada em database models
Base = declarative_base()


class DatabaseConnection:
    # agrupa operacoes estaticas para nao precisar de estado de instancia
    @staticmethod
    def get_session() -> Session:
        # quem recebe deve fechar ou usar with em codigo novo
        return SessionLocal()

    @staticmethod
    def create_tables():
        # pasta local_data guarda sqlite e outros artefactos ignorados pelo git
        try:
            _LOCAL_DATA.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        ensure_local_data_layout()
        # create all varre metadata registrada nas classes que herdam base
        Base.metadata.create_all(bind=engine)
        # migracao manual leve para bases sqlite antigas
        DatabaseConnection._ensure_sqlite_app_settings_options()
        DatabaseConnection._ensure_sqlite_user_scope_columns()
        print("[OK] tabelas criadas no banco de dados")

    @staticmethod
    def _ensure_sqlite_app_settings_options():
        # so executa em sqlite e so se faltar coluna options json
        url = str(DATABASE_URL or "")
        if not url.startswith("sqlite"):
            return
        from sqlalchemy import inspect, text

        insp = inspect(engine)
        if "app_settings" not in insp.get_table_names():
            return
        cols = {c["name"] for c in insp.get_columns("app_settings")}
        if "options_json" in cols:
            return
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE app_settings ADD COLUMN options_json TEXT"))
        print("[OK] coluna app_settings.options_json adicionada (sqlite)")

    @staticmethod
    def _ensure_sqlite_user_scope_columns():
        # migracao leve para projetos que ja tinham base antes da coluna user id
        # nao usamos alembic aqui para manter arranque simples em sqlite
        # so corre em sqlite porque outros motores podem ter migracao propria
        url = str(DATABASE_URL or "")
        if not url.startswith("sqlite"):
            return
        from sqlalchemy import inspect

        # inspect lista colunas existentes sem precisar de sql manual por tabela
        insp = inspect(engine)
        # mapa nome logico da tabela para nome da nova coluna
        tables = {
            "beds": "user_id",
            "simulations": "user_id",
            "reports": "user_id",
            "bed_templates": "user_id",
        }
        for tname, col in tables.items():
            # se a tabela ainda nao existir neste ficheiro saltamos
            if tname not in insp.get_table_names():
                continue
            cols = {c["name"] for c in insp.get_columns(tname)}
            # se a coluna ja existir nada a fazer
            if col in cols:
                continue
            # default 1 associa dados antigos ao primeiro utilizador
            with engine.begin() as conn:
                conn.execute(
                    text(f"ALTER TABLE {tname} ADD COLUMN {col} INTEGER NOT NULL DEFAULT 1")
                )
            print(f"[OK] coluna {tname}.{col} adicionada (sqlite)")
        # depois de existir user id em simulations copiamos do leito pai
        # isto evita linhas orfas com user id errado apos migracao
        try:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        """
                        UPDATE simulations
                        SET user_id = (
                            SELECT beds.user_id FROM beds WHERE beds.id = simulations.bed_id
                        )
                        WHERE EXISTS (
                            SELECT 1 FROM beds WHERE beds.id = simulations.bed_id
                        )
                        """
                    )
                )
        except Exception:
            # se falhar nao impedimos o arranque da api
            pass

    @staticmethod
    def drop_tables():
        # destrutivo util apenas em testes locais
        Base.metadata.drop_all(bind=engine)
        print("[OK] tabelas removidas do banco de dados")

    @staticmethod
    def check_connection() -> bool:
        # select 1 e o menor comando para validar sessao e permissoes
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"[ERRO] falha na conexao: {e}")
            return False


def get_db() -> Generator[Session, None, None]:
    # padrao yield garante fecho mesmo se endpoint lancar excecao
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
