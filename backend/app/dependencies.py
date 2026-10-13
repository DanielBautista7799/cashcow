

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
import jwt

from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.enums import UserRole
from app.security import decode_access_token


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        #just bascially a comment for readability
        headers={"WWW-Authenticate":"Bearer"}
    )
    try: 
        payload=decode_access_token(token)
        username= payload.get("sub")

        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    result = await db.execute(
        select(User).where(User.username == username)
    )

    user =  result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    
    return user
    

def require_role(*allowed_roles: UserRole):
    #role checker checks current role must be nested to check against allowed roles
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' is not permitted to perform this action"
            )
        return current_user
    return role_checker #returns function with parameters of allowed roles



# Permission-based authorization.
# Permissions are resolved from the user's current database role on every request.
from app.permissions import Permission, permissions_for_role


def require_permission(permission: Permission):
    async def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        permissions = permissions_for_role(current_user.role)

        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission.value}",
            )

        return current_user

    return permission_checker
