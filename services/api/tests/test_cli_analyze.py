"""El CLI de análisis comparte validación y no divide entre cero."""

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "analyze.py"

HEADER = (
    "incident_id,date,location_id,category,description,status,"
    "customer_id,satisfaction_score,reporter_id\n"
)
INVALID = "BRS-9,2024-01-14,XXX-99,UNKNOWN,x,PENDING,CLI-1,9,\n"


@pytest.fixture()
def cli():
    spec = importlib.util.spec_from_file_location("analyze_cli", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["analyze_cli"] = module
    spec.loader.exec_module(module)
    yield module
    sys.modules.pop("analyze_cli", None)


def write(tmp_path, content):
    path = tmp_path / "incidents.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_zero_valid_records_prints_and_exports(cli, tmp_path, capsys):
    path = write(tmp_path, HEADER + INVALID + INVALID)
    analysis = cli.analyze_records(cli.load_csv(path))

    cli.print_analysis(path, analysis)
    out = tmp_path / "out.csv"
    cli.export_results(out, analysis)

    assert "Valid records ................ 0" in capsys.readouterr().out
    assert "category_EQUIPMENT,0,0.0" in out.read_text()


def test_truncated_csv_exits_with_controlled_error(cli, tmp_path, capsys):
    path = write(tmp_path, HEADER + "BRS-1,2024-01-14,COL-01,SUPPLY,Sin carb")

    with pytest.raises(SystemExit) as exit_info:
        cli.load_csv(path)

    assert exit_info.value.code == 1
    assert "truncated" in capsys.readouterr().err


def test_header_only_csv_exits_with_controlled_error(cli, tmp_path, capsys):
    with pytest.raises(SystemExit):
        cli.load_csv(write(tmp_path, HEADER))

    assert "does not contain any records" in capsys.readouterr().err
