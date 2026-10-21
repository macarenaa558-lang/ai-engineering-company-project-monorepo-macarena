"""Casos límite del análisis de incidencias.

Las pruebas marcadas xfail documentan defectos confirmados que quedan
pendientes de corrección; si se corrigen, strict=True obliga a retirar la marca.
"""

import pytest

HEADER = (
    "incident_id,date,location_id,category,description,status,"
    "customer_id,satisfaction_score,reporter_id\n"
)
GOOD = "BRS-000001,2024-01-14,COL-07,EQUIPMENT,Horno sin temperatura,OPEN,CLI-1,,MGR-01\n"


def csv_bytes(*rows: str) -> bytes:
    return (HEADER + "".join(rows)).encode()


def test_header_only_csv_is_rejected(upload):
    assert upload(HEADER.encode()).status_code == 400


def test_non_utf8_csv_is_rejected(upload):
    assert upload(b"\xff\xfe\x00bad").status_code == 400


@pytest.mark.xfail(
    strict=True,
    reason="Fila truncada: DictReader devuelve None y validate_record falla con 500.",
)
def test_truncated_row_does_not_return_500(upload):
    truncated = csv_bytes(GOOD, "BRS-000002,2024-01-15,COL-01,SUPPLY,Sin carb")
    response = upload(truncated)
    assert response.status_code in (200, 400)


@pytest.mark.xfail(
    strict=True,
    reason="CSV cortado a mitad del último registro provoca 500.",
)
def test_file_cut_mid_record_does_not_return_500(upload, sample_csv):
    response = upload(sample_csv[: len(sample_csv) // 2])
    assert response.status_code in (200, 400)


@pytest.mark.parametrize("status", ["PENDING", "closed", ""])
def test_invalid_status_is_counted_and_excluded(upload, status):
    row = GOOD.replace(",OPEN,", f",{status},")
    body = upload(csv_bytes(GOOD, row)).json()

    assert body["valid_records"] == 1
    assert body["invalid_records"] == 1
    assert body["error_counts"]["invalid_status"] == 1
    assert sum(body["status_counts"].values()) == 1


@pytest.fixture()
def all_invalid_csv():
    bad = "BRS-000009,2024-01-14,XXX-99,UNKNOWN,x,PENDING,CLI-1,9,\n"
    return csv_bytes(bad, bad)


def test_zero_valid_records_analysis(upload, all_invalid_csv):
    response = upload(all_invalid_csv)
    assert response.status_code == 200
    body = response.json()
    assert body["valid_records"] == 0
    assert body["average_score"] == 0


@pytest.mark.xfail(
    strict=True,
    reason="Con 0 registros válidos el export divide entre cero (500).",
)
def test_zero_valid_records_export(client, upload, all_invalid_csv):
    upload(all_invalid_csv)
    assert client.get("/api/incidents/results/export").status_code == 200


def test_zero_valid_records_cached_endpoints(client, upload, all_invalid_csv):
    upload(all_invalid_csv)

    summary = client.get("/api/incidents/results/summary")
    categories = client.get("/api/incidents/results/categories")

    assert summary.status_code == 200 and summary.json()["valid_records"] == 0
    assert categories.status_code == 200
    assert all(item["percentage"] == 0 for item in categories.json())


@pytest.mark.xfail(
    strict=True,
    reason="latest_analysis es global: el export de un usuario devuelve el análisis de otro.",
)
def test_results_are_not_shared_between_users(client, upload, sample_csv):
    first = csv_bytes(GOOD)
    upload(first)
    assert upload(sample_csv).status_code == 200  # otro usuario sube otro archivo

    exported = client.get("/api/incidents/results/export").text
    assert "total_records,1\n" in exported.replace("\r\n", "\n")
