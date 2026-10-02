import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import resend
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.hash import bcrypt
from pydantic import BaseModel

from services import (
    create_password_reset_token,
    get_password_reset_token,
    get_profile_by_user_id,
    get_user_by_email,
    get_user_by_id,
    invalidate_password_reset_tokens_for_user,
    mark_password_reset_token_as_used,
    update_user,
)


load_dotenv()


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

RESET_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "30")
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173",
)

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

RESET_FROM_EMAIL = os.getenv(
    "RESET_FROM_EMAIL",
    "onboarding@resend.dev",
)

resend.api_key = RESEND_API_KEY


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


def create_access_token(user_id: str):
    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "exp": expiration,
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=ALGORITHM,
    )


def hash_reset_token(token: str):
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        user = get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Usuario no válido",
            )

        return user

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado",
        )


@router.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
):
    user = get_user_by_email(form.username)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos",
        )

    if not bcrypt.verify(
        form.password,
        user["hashed_password"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos",
        )

    token = create_access_token(
        user["id"]
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user),
):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "role": current_user["role"],
        "profile": get_profile_by_user_id(
            current_user["id"]
        ),
    }


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
):
    user = get_user_by_email(data.email)

    if user:
        invalidate_password_reset_tokens_for_user(
            user["id"]
        )

        raw_token = secrets.token_urlsafe(32)
        token_hash = hash_reset_token(raw_token)

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=RESET_TOKEN_EXPIRE_MINUTES
            )
        )

        create_password_reset_token(
            {
                "token_hash": token_hash,
                "user_id": user["id"],
                "expires_at": expires_at.isoformat(),
                "used": False,
            }
        )

        reset_link = (
            f"{FRONTEND_URL}/reset-password"
            f"?token={raw_token}"
        )

        try:
            resend.Emails.send(
                {
                    "from": RESET_FROM_EMAIL,
                    "to": user["email"],
                    "subject": "Restablece tu contraseña",
                    "html": f"""
                    <div
                        style="
                            font-family: Arial, sans-serif;
                            max-width: 600px;
                            margin: auto;
                            padding: 20px;
                        "
                    >
                        <h2>Restablecimiento de contraseña</h2>

                        <p>
                            Recibimos una solicitud para restablecer
                            tu contraseña.
                        </p>

                        <p>
                            Haz clic en el siguiente botón para crear
                            una nueva contraseña:
                        </p>

                        <p style="margin: 30px 0;">
                            <a
                                href="{reset_link}"
                                style="
                                    display: inline-block;
                                    padding: 12px 20px;
                                    background-color: #111827;
                                    color: white;
                                    text-decoration: none;
                                    border-radius: 6px;
                                "
                            >
                                Restablecer contraseña
                            </a>
                        </p>

                        <p>
                            Este enlace vencerá en
                            {RESET_TOKEN_EXPIRE_MINUTES} minutos.
                        </p>

                        <p>
                            Si no solicitaste este cambio,
                            puedes ignorar este correo.
                        </p>
                    </div>
                    """,
                }
            )
        except Exception:
            invalidate_password_reset_tokens_for_user(
                user["id"]
            )
            raise HTTPException(
                status_code=503,
                detail=(
                    "El servicio de correo no está disponible "
                    "temporalmente. Intenta nuevamente más tarde."
                ),
            )


    return {
        "message": (
            "Si esa dirección está registrada, "
            "recibirás un enlace en breve."
        )
    }


@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
):
    token_hash = hash_reset_token(
        data.token
    )

    reset_token = get_password_reset_token(
        token_hash
    )

    if not reset_token:
        raise HTTPException(
            status_code=400,
            detail="Token inválido o expirado",
        )

    if reset_token.get("used"):
        raise HTTPException(
            status_code=400,
            detail="Token inválido o ya utilizado",
        )

    expires_at = datetime.fromisoformat(
        reset_token["expires_at"]
    )

    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(
            status_code=400,
            detail="Token inválido o expirado",
        )

    user = get_user_by_id(
        reset_token["user_id"]
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Token inválido",
        )

    new_hashed_password = bcrypt.hash(
        data.new_password
    )

    update_user(
        user["id"],
        {
            "hashed_password": new_hashed_password
        },
    )

    mark_password_reset_token_as_used(
        token_hash
    )

    return {
        "message": (
            "Contraseña actualizada correctamente"
        )
    }


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: dict = Depends(
        get_current_user
    ),
):
    if not bcrypt.verify(
        data.current_password,
        current_user["hashed_password"],
    ):
        raise HTTPException(
            status_code=400,
            detail="La contraseña actual es incorrecta",
        )

    new_hashed_password = bcrypt.hash(
        data.new_password
    )

    update_user(
        current_user["id"],
        {
            "hashed_password": new_hashed_password
        },
    )

    invalidate_password_reset_tokens_for_user(
        current_user["id"]
    )

    return {
        "message": (
            "Contraseña actualizada correctamente"
        )
    }