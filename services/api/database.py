import os
from pathlib import Path

from dotenv import load_dotenv
from sqlmodel import Session, create_engine
from tinydb import TinyDB


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

# TinyDB: usuarios, autenticación y datos anteriores
db = TinyDB(DATA_DIR / "db.json")

users_table = db.table("users")
profiles_table = db.table("profiles")
suppliers_table = db.table("suppliers")
password_reset_tokens_table = db.table("password_reset_tokens")
incidents_table = db.table("incidents")

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