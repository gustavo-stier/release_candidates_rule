from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy import func
from sqlalchemy.orm import Session  # noqa: F401

from dependecy import create_session, token_verify
from main import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    hash_password,
    verify_password,
)
from models import User, db_engine  # noqa: F401
from schema import LoginSchema, UserSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])


def create_token(
    email: str,
    duration_time: timedelta | int = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
) -> str:
    expire_datetime = datetime.now(timezone.utc) + duration_time  # type: ignore

    dic_info = {"sub_email": email, "exp": expire_datetime}
    encoded_jwt = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)  # type: ignore
    return encoded_jwt


def user_authenticate(email: str, password: str, session: Session) -> User | bool:
    email_normalized = email.strip().lower()
    user = (
        session.query(User).filter(func.lower(User.email) == email_normalized).first()
    )  # type: ignore
    if not user:
        return False
    if not verify_password(password, user.hashed_password):  # type: ignore
        return False
    return user  # type: ignore


def decode_refresh(token: str) -> dict:
    # igual ao decode acima, mas exigindo token_type="refresh"
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
    except ExpiredSignatureError:
        raise HTTPException(
            401, "Refresh token expired", headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise HTTPException(
            401, "Invalid refresh token", headers={"WWW-Authenticate": "Bearer"}
        )
    if payload.get("token_type") != "refresh":
        raise HTTPException(
            401, "Wrong token type", headers={"WWW-Authenticate": "Bearer"}
        )
    return payload


@auth_router.post("/register")
async def register_user(
    user_in: UserSchema,
    current_user: UserSchema = Depends(token_verify),
    session: Session = Depends(create_session),
):
    if not current_user.admin:  # type: ignore
        raise HTTPException(status_code=403, detail="Admin access required")
    email_normalized = user_in.email.strip().lower()
    user = (
        session.query(User).filter(func.lower(User.email) == email_normalized).first()
    )  # type: ignore
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    crypted_password = hash_password(user_in.hashed_password)
    user_in = User(
        username=user_in.username,
        email=email_normalized,
        hashed_password=crypted_password,
        admin=user_in.admin,  # type: ignore
    )
    session.add(user_in)
    session.commit()
    return {"message": f"User '{email_normalized}' registered successfully "}


@auth_router.post("/login")
async def login_user(
    login_schema: LoginSchema, session: Session = Depends(create_session)
):
    user = user_authenticate(login_schema.email, login_schema.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_token(user.email)  # type: ignore
    refresh_token = create_token(user.email, duration_time=timedelta(days=7))  # type: ignore
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }


@auth_router.post("/refresh-token")
async def refresh_token(user: User = Depends(token_verify)):
    access_token = create_token(user.email)  # type: ignore
    return {
        "access_token": access_token,
        "token_type": "Bearer",
    }


# FASTAPI ACCESS
@auth_router.post("/login-form")
async def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(create_session),
):
    user = user_authenticate(form.username, form.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_token(user.email)  # type: ignore
    return {
        "access_token": access_token,
        "token_type": "Bearer",
    }
