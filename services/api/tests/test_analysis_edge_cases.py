"""Casos límite del análisis de incidencias (CSV truncados, estados, cero válidos)."""

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


def test_truncated_row_is_rejected_with_controlled_error(upload):
    response = upload(csv_bytes(GOOD, "BRS-000002,2024-01-15,COL-01,SUPPLY,Sin carb"))

    assert response.status_code == 400
    assert "Record 2 is truncated" in response.json()["detail"]


def test_row_with_extra_columns_is_rejected(upload):
    response = upload(csv_bytes(GOOD.rstrip("\n") + ",extra\n"))

    assert response.status_code == 400
    assert "more columns" in response.json()["detail"]


def test_file_cut_mid_record_is_rejected(upload, sample_csv):
    response = upload(sample_csv[: len(sample_csv) // 2])

    assert response.status_code == 400
    assert "truncated" in response.json()["detail"]


def test_unterminated_quote_is_rejected(upload):
    response = upload(csv_bytes(GOOD, 'BRS-000002,2024-01-15,COL-01,SUPPLY,"sin cierre'))

    assert response.status_code == 400


def test_failed_upload_keeps_previous_analysis(client, upload, auth_headers, sample_csv):
    assert upload(sample_csv).status_code == 200
    before = client.get("/api/incidents/results/summary", headers=auth_headers).json()

    for bad in (csv_bytes(GOOD, "BRS-2,2024"), HEADER.encode(), b"a,b\n1,2\n"):
        assert upload(bad).status_code == 400

    after = client.get("/api/incidents/results/summary", headers=auth_headers).json()
    assert after == before
    exported = client.get("/api/incidents/results/export", headers=auth_headers)
    assert exported.status_code == 200
    assert "total_records,100" in exported.text


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


def test_zero_valid_records_export(client, upload, auth_headers, all_invalid_csv):
    upload(all_invalid_csv)

    response = client.get("/api/incidents/results/export", headers=auth_headers)

    assert response.status_code == 200
    assert "valid_records,0" in response.text
    assert "category_EQUIPMENT,0,0.0" in response.text


def test_zero_valid_records_cached_endpoints(client, upload, auth_headers, all_invalid_csv):
    upload(all_invalid_csv)

    summary = client.get("/api/incidents/results/summary", headers=auth_headers)
    categories = client.get("/api/incidents/results/categories", headers=auth_headers)

    assert summary.status_code == 200 and summary.json()["valid_records"] == 0
    assert categories.status_code == 200
    assert all(item["percentage"] == 0 for item in categories.json())
