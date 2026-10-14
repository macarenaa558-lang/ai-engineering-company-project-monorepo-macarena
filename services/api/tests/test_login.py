from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from jose import jwt
from passlib.hash import bcrypt

import auth


def make_login_form(
    email="macarena@example.com",
    password="Password123",
):
    return SimpleNamespace(
        username=email,
        password=password,
    )


def test_login_success(monkeypatch):
    """Un usuario válido recibe un access token."""
    user = {
        "id": "user-1",
        "email": "macarena@example.com",
        "hashed_password": bcrypt.hash("Password123"),
    }

    monkeypatch.setattr(
        auth,
        "get_user_by_email",
        lambda email: user,
    )

    form = make_login_form()

    result = auth.login(form)

    assert result["token_type"] == "bearer"
    assert result["access_token"]

    payload = jwt.decode(
        result["access_token"],
        auth.JWT_SECRET,
        algorithms=[auth.ALGORITHM],
    )

    assert payload["sub"] == "user-1"
    assert "exp" in payload


def test_login_user_not_found(monkeypatch):
    """Un email no registrado no puede iniciar sesión."""
    monkeypatch.setattr(
        auth,
        "get_user_by_email",
        lambda email: None,
    )

    form = make_login_form(
        email="noexiste@example.com",
    )

    with pytest.raises(HTTPException) as exc:
        auth.login(form)

    assert exc.value.status_code == 401
    assert (
        exc.value.detail
        == "Email o contraseña incorrectos"
    )


def test_login_wrong_password(monkeypatch):
    """Una contraseña incorrecta no permite iniciar sesión."""
    user = {
        "id": "user-1",
        "email": "macarena@example.com",
        "hashed_password": bcrypt.hash("Password123"),
    }

    monkeypatch.setattr(
        auth,
        "get_user_by_email",
        lambda email: user,
    )

    form = make_login_form(
        password="Incorrecta123",
    )

    with pytest.raises(HTTPException) as exc:
        auth.login(form)

    assert exc.value.status_code == 401
    assert (
        exc.value.detail
        == "Email o contraseña incorrectos"
    )


def test_login_empty_email(monkeypatch):
    """Un email vacío se maneja como un caso límite de credenciales inválidas."""
    monkeypatch.setattr(
        auth,
        "get_user_by_email",
        lambda email: None,
    )

    form = make_login_form(
        email="",
    )

    with pytest.raises(HTTPException) as exc:
        auth.login(form)

    assert exc.value.status_code == 401
    assert (
        exc.value.detail
        == "Email o contraseña incorrectos"
    )
