from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

import auth


def make_request(token="reset-token", password="NuevaPassword123"):
    return auth.ResetPasswordRequest(
        token=token,
        new_password=password,
    )


def test_reset_password_success(monkeypatch):
    """Un token válido permite cambiar la contraseña."""
    token_hash = auth.hash_reset_token("reset-token")

    reset_token = {
        "token_hash": token_hash,
        "user_id": "user-1",
        "expires_at": (
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ).isoformat(),
        "used": False,
    }

    user = {
        "id": "user-1",
        "email": "macarena@example.com",
    }

    updates = []
    used_tokens = []

    monkeypatch.setattr(
        auth,
        "get_password_reset_token",
        lambda received_hash: reset_token,
    )
    monkeypatch.setattr(
        auth,
        "get_user_by_id",
        lambda user_id: user,
    )
    monkeypatch.setattr(
        auth,
        "update_user",
        lambda user_id, changes: updates.append(
            (user_id, changes)
        ),
    )
    monkeypatch.setattr(
        auth,
        "mark_password_reset_token_as_used",
        lambda received_hash: used_tokens.append(
            received_hash
        ),
    )

    result = auth.reset_password(make_request())

    assert (
        result["message"]
        == "Contraseña actualizada correctamente"
    )
    assert len(updates) == 1
    assert updates[0][0] == "user-1"

    new_hash = updates[0][1]["hashed_password"]
    assert auth.bcrypt.verify(
        "NuevaPassword123",
        new_hash,
    )

    assert used_tokens == [token_hash]


def test_reset_password_used_token(monkeypatch):
    """Un token ya utilizado no puede reutilizarse."""
    reset_token = {
        "user_id": "user-1",
        "expires_at": (
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        ).isoformat(),
        "used": True,
    }

    monkeypatch.setattr(
        auth,
        "get_password_reset_token",
        lambda token_hash: reset_token,
    )

    with pytest.raises(HTTPException) as exc:
        auth.reset_password(make_request())

    assert exc.value.status_code == 400
    assert (
        exc.value.detail
        == "Token inválido o ya utilizado"
    )


def test_reset_password_unknown_token(monkeypatch):
    """Un token inexistente debe ser rechazado."""
    monkeypatch.setattr(
        auth,
        "get_password_reset_token",
        lambda token_hash: None,
    )

    with pytest.raises(HTTPException) as exc:
        auth.reset_password(
            make_request(token="token-inexistente")
        )

    assert exc.value.status_code == 400
    assert (
        exc.value.detail
        == "Token inválido o expirado"
    )


def test_reset_password_expired_token(monkeypatch):
    """Un token vencido no permite cambiar la contraseña."""
    reset_token = {
        "user_id": "user-1",
        "expires_at": (
            datetime.now(timezone.utc)
            - timedelta(minutes=1)
        ).isoformat(),
        "used": False,
    }

    monkeypatch.setattr(
        auth,
        "get_password_reset_token",
        lambda token_hash: reset_token,
    )

    with pytest.raises(HTTPException) as exc:
        auth.reset_password(make_request())

    assert exc.value.status_code == 400
    assert (
        exc.value.detail
        == "Token inválido o expirado"
    )
