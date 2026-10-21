"""Caché de resultados: coherencia, aciertos, invalidación, TTL y concurrencia."""

import csv
import io
from concurrent.futures import ThreadPoolExecutor

import pytest

import cache


@pytest.fixture()
def spy(app_module, monkeypatch):
    stats = {"hit": 0, "miss": 0, "set": 0}
    real_get, real_set = app_module.get_cached, app_module.set_cached

    def get(key):
        value = real_get(key)
        stats["hit" if value is not None else "miss"] += 1
        return value

    def set_(key, value):
        stats["set"] += 1
        return real_set(key, value)

    monkeypatch.setattr(app_module, "get_cached", get)
    monkeypatch.setattr(app_module, "set_cached", set_)
    return stats


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


def test_no_analysis_returns_404_and_caches_nothing(client, spy):
    assert client.get("/api/incidents/results/summary").status_code == 404
    assert client.get("/api/incidents/results/categories").status_code == 404
    assert spy["set"] == 0


def test_cached_values_match_analysis(client, upload, sample_csv):
    analysis = upload(sample_csv).json()

    summary = client.get("/api/incidents/results/summary").json()
    assert summary["total_records"] == analysis["total_records"]
    assert summary["valid_records"] == analysis["valid_records"]
    assert summary["average_score"] == analysis["average_score"]

    categories = client.get("/api/incidents/results/categories").json()
    assert {c["category"]: c["count"] for c in categories} == analysis["category_counts"]
    assert sum(c["count"] for c in categories) == analysis["valid_records"]
    assert sum(c["percentage"] for c in categories) == pytest.approx(100, abs=0.5)


def test_second_read_is_a_hit_with_same_payload(client, upload, sample_csv, spy):
    upload(sample_csv)
    first = client.get("/api/incidents/results/summary").json()
    assert (spy["hit"], spy["miss"], spy["set"]) == (0, 1, 1)

    second = client.get("/api/incidents/results/summary").json()
    assert second == first
    assert (spy["hit"], spy["miss"], spy["set"]) == (1, 1, 1)


def test_new_analysis_invalidates_cache(client, upload, sample_csv):
    upload(sample_csv)
    old = client.get("/api/incidents/results/summary").json()

    upload(subset(sample_csv, 30))
    new = client.get("/api/incidents/results/summary").json()

    assert old["total_records"] == 100
    assert new["total_records"] == 30


def test_rejected_upload_keeps_results_and_cache(client, upload, sample_csv, spy):
    upload(sample_csv)
    client.get("/api/incidents/results/summary")

    assert upload(b"a,b\n1,2\n").status_code == 400

    again = client.get("/api/incidents/results/summary").json()
    assert again["total_records"] == 100
    assert spy["hit"] == 1


def test_mutating_returned_value_does_not_poison_cache():
    cache.set_cached("k", {"a": [1]})
    value = cache.get_cached("k")
    value["a"].append(2)
    assert cache.get_cached("k") == {"a": [1]}


def test_ttl_expiry(monkeypatch):
    now = [1000.0]
    monkeypatch.setattr(cache, "monotonic", lambda: now[0])

    cache.set_cached("k", 1)
    now[0] += cache.CACHE_TTL_SECONDS - 1
    assert cache.get_cached("k") == 1

    now[0] += 2
    assert cache.get_cached("k") is None


def test_concurrent_reads_are_consistent(client, upload, sample_csv):
    upload(sample_csv)

    def read(_):
        response = client.get("/api/incidents/results/categories")
        return response.status_code, response.text

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(read, range(40)))

    assert {code for code, _ in results} == {200}
    assert len({body for _, body in results}) == 1


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Lectura-cálculo-escritura sin atomicidad: un análisis nuevo que invalida "
        "entre el cálculo y set_cached deja datos obsoletos durante el TTL."
    ),
)
def test_invalidation_during_computation_does_not_leave_stale_cache(
    client, upload, sample_csv, app_module, monkeypatch
):
    upload(sample_csv)
    real_set = app_module.set_cached
    reader = csv.DictReader(io.StringIO(subset(sample_csv, 30).decode()))
    newer = app_module.analyze_records(list(reader))

    def interleaved_set(key, value):
        # Equivale a un POST /analyze que termina justo antes de guardar.
        app_module.latest_analysis = newer
        cache.invalidate_cache()
        real_set(key, value)

    monkeypatch.setattr(app_module, "set_cached", interleaved_set)
    client.get("/api/incidents/results/summary")
    monkeypatch.setattr(app_module, "set_cached", real_set)

    assert client.get("/api/incidents/results/summary").json()["total_records"] == 30
