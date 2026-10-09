from app.config import settings
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import hashlib
import secrets

SECRET_KEY = settings.secret_key

ALGORITHM = "HS256"


def hash_password(plain_password:str) -> str:
    #hashed = hashed (plain password in bytes "encode" + sale "or an additonal string for protection"
    #this is python .encode not to be confused with jwt.encode
    hashed = bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt()
    )
    #sqlalch takes String(255) and since currently in bytes we need to turn back
    return hashed.decode("utf-8")

def verify_password(plain_password:str, hashed_password:str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(data:dict,
                        expires_delta: timedelta | None = None
                        ) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
    expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
)
    to_encode["exp"] = expire
# jwt.encode() creates and signs the JWT using the token data, secret key, and algorithm.
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token:str) -> dict:
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

def create_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()