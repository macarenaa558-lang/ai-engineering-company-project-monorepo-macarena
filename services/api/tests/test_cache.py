"""Caché de resultados: coherencia, aciertos, invalidación, TTL, versión y concurrencia."""

import csv
import io
from concurrent.futures import ThreadPoolExecutor

import pytest

import cache

SUMMARY = "/api/incidents/results/summary"
CATEGORIES = "/api/incidents/results/categories"


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


def test_no_analysis_returns_404_and_caches_nothing(client, auth_headers, spy):
    assert client.get(SUMMARY, headers=auth_headers).status_code == 404
    assert client.get(CATEGORIES, headers=auth_headers).status_code == 404
    assert spy["set"] == 0


def test_cached_values_match_analysis(client, upload, auth_headers, sample_csv):
    analysis = upload(sample_csv).json()

    summary = client.get(SUMMARY, headers=auth_headers).json()
    assert summary["total_records"] == analysis["total_records"]
    assert summary["valid_records"] == analysis["valid_records"]
    assert summary["average_score"] == analysis["average_score"]

    categories = client.get(CATEGORIES, headers=auth_headers).json()
    assert {c["category"]: c["count"] for c in categories} == analysis["category_counts"]
    assert sum(c["count"] for c in categories) == analysis["valid_records"]
    assert sum(c["percentage"] for c in categories) == pytest.approx(100, abs=0.5)


def test_second_read_is_a_hit_with_same_payload(client, upload, auth_headers, sample_csv, spy):
    upload(sample_csv)
    first = client.get(SUMMARY, headers=auth_headers).json()
    assert (spy["hit"], spy["miss"], spy["set"]) == (0, 1, 1)

    second = client.get(SUMMARY, headers=auth_headers).json()
    assert second == first
    assert (spy["hit"], spy["miss"], spy["set"]) == (1, 1, 1)


def test_new_analysis_invalidates_cache(client, upload, auth_headers, sample_csv):
    upload(sample_csv)
    old = client.get(SUMMARY, headers=auth_headers).json()

    upload(subset(sample_csv, 30))
    new = client.get(SUMMARY, headers=auth_headers).json()

    assert old["total_records"] == 100
    assert new["total_records"] == 30


def test_rejected_upload_keeps_results_and_cache(client, upload, auth_headers, sample_csv, spy):
    upload(sample_csv)
    client.get(SUMMARY, headers=auth_headers)

    assert upload(b"a,b\n1,2\n").status_code == 400

    again = client.get(SUMMARY, headers=auth_headers).json()
    assert again["total_records"] == 100
    assert spy["hit"] == 1


def test_mutating_returned_value_does_not_poison_cache():
    cache.set_cached("k", {"a": [1]})
    value = cache.get_cached("k")
    value["a"].append(2)
    assert cache.get_cached("k") == {"a": [1]}


def test_ttl_expiry_and_purge(monkeypatch):
    now = [1000.0]
    monkeypatch.setattr(cache, "monotonic", lambda: now[0])

    cache.set_cached("k", 1)
    now[0] += cache.CACHE_TTL_SECONDS - 1
    assert cache.get_cached("k") == 1

    now[0] += 2
    assert cache.get_cached("k") is None

    cache.set_cached("old", 1)
    now[0] += cache.CACHE_TTL_SECONDS + 1
    cache.set_cached("new", 2)
    assert "old" not in cache._cache


def test_invalidate_prefix_only_removes_matching_keys():
    cache.set_cached("u1:1:summary", 1)
    cache.set_cached("u2:1:summary", 2)

    cache.invalidate_prefix("u1:")

    assert cache.get_cached("u1:1:summary") is None
    assert cache.get_cached("u2:1:summary") == 2


def test_concurrent_reads_are_consistent(client, upload, auth_headers, sample_csv):
    upload(sample_csv)

    def read(_):
        response = client.get(CATEGORIES, headers=auth_headers)
        return response.status_code, response.text

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(read, range(40)))

    assert {code for code, _ in results} == {200}
    assert len({body for _, body in results}) == 1


def test_new_analysis_during_computation_does_not_publish_stale_cache(
    client, upload, auth_headers, sample_csv, app_module, monkeypatch
):
    upload(sample_csv)
    real_set = app_module.set_cached
    newer = subset(sample_csv, 30)

    def interleaved_set(key, value):
        # Equivale a un POST /analyze del mismo usuario que termina antes de guardar.
        assert upload(newer).status_code == 200
        real_set(key, value)

    monkeypatch.setattr(app_module, "set_cached", interleaved_set)
    stale_response = client.get(SUMMARY, headers=auth_headers)
    monkeypatch.setattr(app_module, "set_cached", real_set)

    assert stale_response.json()["total_records"] == 100  # cálculo hecho sobre el snapshot previo
    assert client.get(SUMMARY, headers=auth_headers).json()["total_records"] == 30


def test_concurrent_uploads_and_reads_never_mix_versions(
    client, upload, auth_headers, sample_csv
):
    small = subset(sample_csv, 30)
    full_valid = upload(sample_csv).json()["valid_records"]
    small_valid = upload(small).json()["valid_records"]
    upload(sample_csv)

    def work(index):
        if index % 4 == 0:
            upload(small if index % 8 == 0 else sample_csv)
            return None
        body = client.get(CATEGORIES, headers=auth_headers).json()
        return sum(item["count"] for item in body)

    with ThreadPoolExecutor(max_workers=8) as pool:
        counts = [c for c in pool.map(work, range(60)) if c is not None]

    assert counts and set(counts) <= {full_valid, small_valid}

    # Tras quedar en reposo, la caché coincide con el último análisis guardado.
    stored = client.get(SUMMARY, headers=auth_headers).json()
    categories = client.get(CATEGORIES, headers=auth_headers).json()
    assert sum(item["count"] for item in categories) == stored["valid_records"]
