"""Configuración de pruebas: base y datos aislados, nunca los reales.

Las variables se fijan antes de importar `database`, que lee `.env` con
load_dotenv() sin sobrescribir las que ya existen en el entorno.
"""

import os
import tempfile
from pathlib import Path

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


@pytest.fixture()
def app_module():
    import cache
    import main
    import results_store

    results_store.clear()
    cache.invalidate_cache()
    yield main
    results_store.clear()
    cache.invalidate_cache()


@pytest.fixture()
def client(app_module):
    from fastapi.testclient import TestClient

    with TestClient(app_module.app) as test_client:
        yield test_client


@pytest.fixture()
def make_user(client):
    """Crea un usuario nuevo y devuelve sus cabeceras de autenticación."""
    import uuid

    def _make():
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

    return _make


@pytest.fixture()
def auth_headers(make_user):
    return make_user()


@pytest.fixture()
def upload(client, auth_headers):
    def _upload(content: bytes, name: str = "incidents.csv", headers=None):
        return client.post(
            "/api/incidents/analyze",
            files={"file": (name, content, "text/csv")},
            headers=auth_headers if headers is None else headers,
        )

    return _upload
