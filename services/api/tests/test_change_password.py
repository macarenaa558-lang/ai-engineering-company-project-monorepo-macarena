import pytest
from fastapi import HTTPException
from passlib.hash import bcrypt

import auth


def make_request(
    current_password="Password123",
    new_password="NuevaPassword123",
):
    return auth.ChangePasswordRequest(
        current_password=current_password,
        new_password=new_password,
    )


def make_user():
    return {
        "id": "user-1",
        "email": "macarena@example.com",
        "role": "user",
        "hashed_password": bcrypt.hash("Password123"),
    }


def test_change_password_success(monkeypatch):
    """La contraseña actual correcta permite cambiarla."""
    user = make_user()
    updates = []
    invalidated_users = []

    monkeypatch.setattr(
        auth,
        "update_user",
        lambda user_id, changes: updates.append(
            (user_id, changes)
        ),
    )
    monkeypatch.setattr(
        auth,
        "invalidate_password_reset_tokens_for_user",
        lambda user_id: invalidated_users.append(user_id),
    )

    result = auth.change_password(
        make_request(),
        user,
    )

    assert (
        result["message"]
        == "Contraseña actualizada correctamente"
    )
    assert len(updates) == 1
    assert updates[0][0] == "user-1"

    new_hash = updates[0][1]["hashed_password"]
    assert bcrypt.verify(
        "NuevaPassword123",
        new_hash,
    )

    assert invalidated_users == ["user-1"]


def test_change_password_invalidates_reset_tokens(
    monkeypatch,
):
    """El cambio invalida tokens de recuperación anteriores."""
    user = make_user()
    invalidated_users = []

    monkeypatch.setattr(
        auth,
        "update_user",
        lambda user_id, changes: None,
    )
    monkeypatch.setattr(
        auth,
        "invalidate_password_reset_tokens_for_user",
        lambda user_id: invalidated_users.append(user_id),
    )

    auth.change_password(
        make_request(),
        user,
    )

    assert invalidated_users == ["user-1"]


def test_change_password_wrong_current_password(
    monkeypatch,
):
    """Una contraseña actual incorrecta impide el cambio."""
    user = make_user()
    updates = []

    monkeypatch.setattr(
        auth,
        "update_user",
        lambda user_id, changes: updates.append(
            (user_id, changes)
        ),
    )

    with pytest.raises(HTTPException) as exc:
        auth.change_password(
            make_request(
                current_password="Incorrecta123"
            ),
            user,
        )

    assert exc.value.status_code == 400
    assert (
        exc.value.detail
        == "La contraseña actual es incorrecta"
    )
    assert updates == []
