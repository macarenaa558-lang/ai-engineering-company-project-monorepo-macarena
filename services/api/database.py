import os
from pathlib import Path
from threading import RLock

from dotenv import load_dotenv
from sqlmodel import Session, create_engine
from tinydb import TinyDB


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
# API_DATA_DIR permite aislar el almacén TinyDB (pruebas).
DATA_DIR = Path(os.getenv("API_DATA_DIR") or BASE_DIR / "data")

DATA_DIR.mkdir(exist_ok=True)

# TinyDB: usuarios, autenticación y datos anteriores
db = TinyDB(DATA_DIR / "db.json")

_tinydb_lock = RLock()


class _LockedTable:
    """TinyDB comparte el archivo entre hilos: serializa cada operación de tabla."""

    def __init__(self, table):
        self._table = table

    def __getattr__(self, name):
        attribute = getattr(self._table, name)

        if not callable(attribute):
            return attribute

        def locked(*args, **kwargs):
            with _tinydb_lock:
                return attribute(*args, **kwargs)

        return locked


users_table = _LockedTable(db.table("users"))
profiles_table = _LockedTable(db.table("profiles"))
suppliers_table = _LockedTable(db.table("suppliers"))
password_reset_tokens_table = _LockedTable(db.table("password_reset_tokens"))
incidents_table = _LockedTable(db.table("incidents"))

# Supabase/PostgreSQL: inventario
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL no está configurada")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


def get_db():
    with Session(engine) as session:
        yield session