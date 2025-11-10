# noqa: F401

from fastapi import Depends, HTTPException
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker

from main import ALGORITHM, SECRET_KEY, oauth2_scheme
from models import User, db_engine


def create_session():
    try:
        Session = sessionmaker(bind=db_engine)
        session = Session()
        yield session
    finally:
        session.close()


def token_verify(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(create_session),
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,  # type: ignore
            algorithms=[ALGORITHM],
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={
                "WWW-Authenticate": "Bearer error='invalid_token', error_description='token expired'"
            },
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # aceita 'sub_email' (seu padrão) ou 'sub' (padrão comum)
    user_email = (payload.get("sub_email") or payload.get("sub") or "").strip()
    if not user_email:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = (
        session.query(User).filter(func.lower(User.email) == user_email.lower()).first()
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
