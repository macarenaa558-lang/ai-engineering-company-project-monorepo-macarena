"""Configuración de pruebas: base y datos aislados, nunca los reales.

Las variables se fijan antes de importar `database`, que lee `.env` con
load_dotenv() sin sobrescribir las que ya existen en el entorno.
"""

import os
import sys
import tempfile
from pathlib import Path

# Como al arrancar uvicorn desde services/api: `services` debe ser services.py y no el paquete raíz.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_TMP = Path(tempfile.mkdtemp(prefix="brasaland-tests-"))

# TEST_DATABASE_URL permite probar contra PostgreSQL desechable (nunca Supabase real).
os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL", f"sqlite:///{_TMP / 'test.db'}"
)
os.environ["API_DATA_DIR"] = str(_TMP / "data")
os.environ["JWT_SECRET"] = "test-secret"
os.environ["RESEND_API_KEY"] = "disabled"
os.environ["FRONTEND_URL"] = "http://localhost:3001"

import pytest  # noqa: E402

_ALLOWED = ("sqlite:", "postgresql://postgres:postgres@localhost", "postgresql://postgres:postgres@127.0.0.1")

if not os.environ["DATABASE_URL"].startswith(_ALLOWED):
    raise RuntimeError(
        "Las pruebas solo pueden usar SQLite o un PostgreSQL local desechable."
    )

SAMPLE_CSV = Path(__file__).resolve().parents[3] / "scripts" / "incidents-brasaland.csv"


@pytest.fixture(scope="session")
def sample_csv() -> bytes:
    return SAMPLE_CSV.read_bytes()


# Se importa aquí, antes de que pytest cargue los paquetes padre `services`/`services.api`,
# para que `services` quede resuelto como services.py y no como el paquete raíz.
import cache  # noqa: E402
import main  # noqa: E402


@pytest.fixture()
def app_module():

    main.latest_analysis = None
    cache.invalidate_cache()
    yield main
    main.latest_analysis = None
    cache.invalidate_cache()


@pytest.fixture()
def client(app_module):
    from fastapi.testclient import TestClient

    with TestClient(app_module.app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client):
    import uuid

    email = f"user-{uuid.uuid4().hex[:8]}@example.com"
    password = "Password123"

    created = client.post(
        "/users", json={"email": email, "password": password, "name": "Test"}
    )
    assert created.status_code in (200, 201), created.text

    login = client.post(
        "/auth/login", data={"username": email, "password": password}
    )
    assert login.status_code == 200, login.text

    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.fixture()
def upload(client):
    def _upload(content: bytes, name: str = "incidents.csv"):
        return client.post(
            "/api/incidents/analyze",
            files={"file": (name, content, "text/csv")},
        )

    return _upload
