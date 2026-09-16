from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

import auth


def test_get_me_success(monkeypatch):
    """Un usuario autenticado obtiene sus datos y perfil."""
    user = {
        "id": "user-1",
        "email": "macarena@example.com",
        "role": "user",
    }

    profile = {
        "user_id": "user-1",
        "first_name": "Macarena",
    }

    monkeypatch.setattr(
        auth,
        "get_profile_by_user_id",
        lambda user_id: profile,
    )

    result = auth.get_me(user)

    assert result["id"] == "user-1"
    assert result["email"] == "macarena@example.com"
    assert result["role"] == "user"
    assert result["profile"] == profile


def test_get_me_without_profile(monkeypatch):
    """Un usuario autenticado puede no tener perfil asociado."""
    user = {
        "id": "user-1",
        "email": "macarena@example.com",
        "role": "user",
    }

    monkeypatch.setattr(
        auth,
        "get_profile_by_user_id",
        lambda user_id: None,
    )

    result = auth.get_me(user)

    assert result["id"] == "user-1"
    assert result["profile"] is None


def test_get_current_user_with_expired_token(monkeypatch):
    """Un token expirado debe ser rechazado."""
    expired_payload = {
        "sub": "user-1",
        "exp": datetime.now(timezone.utc)
        - timedelta(minutes=1),
    }

    expired_token = jwt.encode(
        expired_payload,
        auth.JWT_SECRET,
        algorithm=auth.ALGORITHM,
    )

    monkeypatch.setattr(
        auth,
        "get_user_by_id",
        lambda user_id: {
            "id": user_id,
            "email": "macarena@example.com",
            "role": "user",
        },
    )

    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(expired_token)

    assert exc.value.status_code == 401
    assert (
        exc.value.detail
        == "Token inválido o expirado"
    )
