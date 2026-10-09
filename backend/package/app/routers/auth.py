from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db, require_role
from app.models.enums import UserRole
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.user import RefreshRequest, Token, UserCreate, UserRead
from app.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:

    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )

    user = result.scalar_one_or_none()

    if user is None or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Username or Password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        {
            "sub": user.username,
            "role": user.role.value,
        }
    )

    refresh_token = create_refresh_token()

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            chain_id=str(uuid4()),
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(days=settings.refresh_token_expire_days)
            ),
        )
    )

    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Token)
async def refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:

    token_hash = hash_refresh_token(request.refresh_token)

    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .with_for_update()
    )

    refresh_record = result.scalar_one_or_none()

    if refresh_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if refresh_record.revoked:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.chain_id == refresh_record.chain_id)
            .values(revoked=True)
        )
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if refresh_record.expires_at <= datetime.now(timezone.utc):
        refresh_record.revoked = True
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    result = await db.execute(
        select(User).where(User.id == refresh_record.user_id)
    )

    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user",
        )

    refresh_record.revoked = True

    access_token = create_access_token(
        {
            "sub": user.username,
            "role": user.role.value,
        }
    )

    new_refresh_token = create_refresh_token()

    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(new_refresh_token),
            chain_id=refresh_record.chain_id,
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(days=settings.refresh_token_expire_days)
            ),
        )
    )

    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.post("/logout")
async def logout(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):

    token_hash = hash_refresh_token(request.refresh_token)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )

    refresh_record = result.scalar_one_or_none()

    if refresh_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.chain_id == refresh_record.chain_id)
        .values(revoked=True)
    )

    await db.commit()

    return {"message": "Logged out"}


@router.post("/register", response_model=UserRead, status_code=201)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    ),
) -> User:

    result = await db.execute(
        select(User).where(
            func.lower(User.username) == user_data.username.lower()
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user