"""TinyDB no es seguro entre hilos por sí solo: las lecturas autenticadas concurrentes deben funcionar."""

from concurrent.futures import ThreadPoolExecutor


def test_concurrent_authenticated_requests_do_not_fail(client, auth_headers):
    def read(_):
        return client.get("/auth/me", headers=auth_headers).status_code

    with ThreadPoolExecutor(max_workers=8) as pool:
        codes = list(pool.map(read, range(80)))

    assert set(codes) == {200}
