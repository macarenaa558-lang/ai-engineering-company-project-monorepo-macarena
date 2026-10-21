"""El empaquetado y los imports no dependen del nombre `services`."""

import tomllib
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]


def test_every_declared_py_module_exists():
    config = tomllib.loads((API_DIR / "pyproject.toml").read_text())
    modules = config["tool"]["setuptools"]["py-modules"]

    missing = [name for name in modules if not (API_DIR / f"{name}.py").exists()]
    assert missing == []


def test_every_top_level_module_is_declared():
    config = tomllib.loads((API_DIR / "pyproject.toml").read_text())
    declared = set(config["tool"]["setuptools"]["py-modules"])
    on_disk = {p.stem for p in API_DIR.glob("*.py") if p.stem != "__init__"}

    assert on_disk <= declared


def test_no_module_shadows_the_root_services_package():
    assert not (API_DIR / "services.py").exists()


def test_data_access_module_imports():
    import repository

    assert hasattr(repository, "get_user_by_id")
