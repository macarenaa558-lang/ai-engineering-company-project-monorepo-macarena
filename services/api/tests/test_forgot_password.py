import pytest
from fastapi import HTTPException

import auth


GENERIC_MESSAGE = (
    "Si esa dirección está registrada, "
    "recibirás un enlace en breve."
)


def test_forgot_password_success(monkeypatch):
    """Un usuario existente genera un token y un correo de recuperación."""
    user = {
        "id": "user-1",
        "email": "macarena@example.com",
    }

    created_tokens = []
    invalidated_users = []
    sent_emails = []

    monkeypatch.setattr(
        auth,
        "get_user_by_email",
        lambda email: user,
    )
    monkeypatch.setattr(
        auth,
        "invalidate_password_reset_tokens_for_user",
        lambda user_id: invalidated_users.append(user_id),
    )
    monkeypatch.setattr(
        auth,
        "create_password_reset_token",
        lambda token_data: created_tokens.append(token_data),
    )
    monkeypatch.setattr(
        auth.resend.Emails,
        "send",
        lambda email_data: sent_emails.append(email_data),
    )

    result = auth.forgot_password(
        auth.ForgotPasswordRequest(
            email="macarena@example.com"
        )
    )

    assert result["message"] == GENERIC_MESSAGE
    assert invalidated_users == ["user-1"]
    assert len(created_tokens) == 1
    assert created_tokens[0]["user_id"] == "user-1"
    assert created_tokens[0]["used"] is False
    assert created_tokens[0]["token_hash"]
    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == "macarena@example.com"


def test_forgot_password_unknown_email(monkeypatch):
    """Un email inexistente recibe la misma respuesta genérica."""
    monkeypatch.setattr(
        auth,
        "get_user_by_email",
        lambda email: None,
    )

    result = auth.forgot_password(
        auth.ForgotPasswordRequest(
            email="noexiste@example.com"
        )
    )

    assert result["message"] == GENERIC_MESSAGE


def test_forgot_password_email_service_failure(monkeypatch):
    """Si falla el correo, el token generado se invalida."""
    user = {
        "id": "user-1",
        "email": "macarena@example.com",
    }

    invalidated_users = []

    monkeypatch.setattr(
        auth,
        "get_user_by_email",
        lambda email: user,
    )
    monkeypatch.setattr(
        auth,
        "invalidate_password_reset_tokens_for_user",
        lambda user_id: invalidated_users.append(user_id),
    )
    monkeypatch.setattr(
        auth,
        "create_password_reset_token",
        lambda token_data: token_data,
    )

    def fail_to_send(email_data):
        raise RuntimeError("Servicio de correo no disponible")

    monkeypatch.setattr(
        auth.resend.Emails,
        "send",
        fail_to_send,
    )

    with pytest.raises(HTTPException) as exc:
        auth.forgot_password(
            auth.ForgotPasswordRequest(
                email="macarena@example.com"
            )
        )

    assert exc.value.status_code == 503
    assert invalidated_users == ["user-1", "user-1"]
    assert (
        exc.value.detail
        == "El servicio de correo no está disponible "
        "temporalmente. Intenta nuevamente más tarde."
    )
