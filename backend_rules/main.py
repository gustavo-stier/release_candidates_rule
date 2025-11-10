import os
from hashlib import sha256

import bcrypt
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
ALGORITHM = os.getenv("ALGORITHM", "HS256")

app = FastAPI()

MAX_BCRYPT_BYTES = 72

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login-form")  # type: ignore
oauth2_refresh_scheme = HTTPBearer(auto_error=True)


def _normalize_secret(secret: str) -> bytes:
    secret_bytes = secret.encode("utf-8")
    if len(secret_bytes) <= MAX_BCRYPT_BYTES:
        return secret_bytes
    # Reduce long inputs deterministically so bcrypt never raises
    digest = sha256(secret_bytes).hexdigest()
    return digest.encode("ascii")


def hash_password(secret: str) -> str:
    normalized = _normalize_secret(secret)
    return bcrypt.hashpw(normalized, bcrypt.gensalt()).decode("utf-8")


def verify_password(secret: str, hashed: str) -> bool:
    normalized = _normalize_secret(secret)
    return bcrypt.checkpw(normalized, hashed.encode("utf-8"))


from auth_routes import auth_router  # noqa: E402
from rules_routes import rules_router  # noqa: E402

# uvicorn main:app --reload

app.include_router(auth_router)
app.include_router(rules_router)
