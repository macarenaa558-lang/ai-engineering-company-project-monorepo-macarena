"""Los resultados del análisis exigen autenticación y están separados por usuario."""

import csv
import io

import pytest

RESULT_ROUTES = [
    ("GET", "/api/incidents/results/summary"),
    ("GET", "/api/incidents/results/categories"),
    ("GET", "/api/incidents/results/export"),
]


def subset(sample_csv: bytes, rows: int) -> bytes:
    reader = csv.DictReader(io.StringIO(sample_csv.decode()))
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
    writer.writeheader()
    for index, row in enumerate(reader):
        if index >= rows:
            break
        writer.writerow(row)
    return out.getvalue().encode()


@pytest.mark.parametrize("method,path", RESULT_ROUTES)
def test_results_require_authentication(client, method, path):
    assert client.request(method, path).status_code == 401
    bad = {"Authorization": "Bearer token-invalido"}
    assert client.request(method, path, headers=bad).status_code == 401


def test_analyze_requires_authentication(client, sample_csv):
    response = client.post(
        "/api/incidents/analyze",
        files={"file": ("i.csv", sample_csv, "text/csv")},
    )
    assert response.status_code == 401


def test_user_without_analysis_gets_404(client, auth_headers):
    for _, path in RESULT_ROUTES:
        assert client.get(path, headers=auth_headers).status_code == 404


def test_user_cannot_read_or_export_other_users_results(
    client, upload, make_user, sample_csv
):
    alice, bob = make_user(), make_user()
    assert upload(sample_csv, headers=alice).status_code == 200

    for _, path in RESULT_ROUTES:
        assert client.get(path, headers=bob).status_code == 404
        assert client.get(path, headers=alice).status_code == 200


def test_each_user_gets_own_results_from_summary_categories_and_export(
    client, upload, make_user, sample_csv
):
    alice, bob = make_user(), make_user()
    upload(sample_csv, headers=alice)
    upload(subset(sample_csv, 30), headers=bob)

    for headers, total in ((alice, 100), (bob, 30)):
        summary = client.get("/api/incidents/results/summary", headers=headers).json()
        categories = client.get("/api/incidents/results/categories", headers=headers).json()
        exported = client.get("/api/incidents/results/export", headers=headers).text

        assert summary["total_records"] == total
        assert f"total_records,{total}," in exported.replace("\r\n", "\n")
        assert sum(c["count"] for c in categories) == summary["valid_records"]


def test_other_users_upload_does_not_invalidate_or_replace_my_cache(
    client, upload, make_user, sample_csv
):
    alice, bob = make_user(), make_user()
    upload(sample_csv, headers=alice)
    client.get("/api/incidents/results/summary", headers=alice)

    upload(subset(sample_csv, 30), headers=bob)

    assert client.get("/api/incidents/results/summary", headers=alice).json()[
        "total_records"
    ] == 100
    assert client.get("/api/incidents/results/summary", headers=bob).json()[
        "total_records"
    ] == 30


def test_failed_upload_of_other_user_does_not_touch_mine(
    client, upload, make_user, sample_csv
):
    alice, bob = make_user(), make_user()
    upload(sample_csv, headers=alice)

    assert upload(b"a,b\n1,2\n", headers=bob).status_code == 400

    assert client.get("/api/incidents/results/summary", headers=alice).json()[
        "total_records"
    ] == 100
    assert client.get("/api/incidents/results/summary", headers=bob).status_code == 404
