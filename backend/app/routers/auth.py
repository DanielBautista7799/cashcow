from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserRead
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

#figure out who you are using username/password
@router.post("/token", response_model=Token)
# OAuth2PasswordRequestForm = read the OAuth2 login form from this request and give it to me.
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)) -> Token:

                result = await db.execute(
                        select(User).where(User.username == form_data.username)
                )
                user = result.scalar_one_or_none()
                if user is None or not verify_password(form_data.password, user.hashed_password):
                        raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail= "Incorrect Username or Password",
                                headers={"WWW-Authenticate":"Bearer"}
                        )
                access_token = create_access_token(
                        {
                                "sub": user.username,
                                "role": user.role.value
                        }
                )
                return Token(access_token=access_token)



@router.post("/register", response_model=UserRead, status_code=201)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
        ),
    )-> User:
        

        result = await db.execute(select(User).where(func.lower(User.username) == user_data.username.lower()))
        existing_user = result.scalar_one_or_none()

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        
        new_user = User(
                username = user_data.username,
                hashed_password = hash_password(user_data.password),
                role= user_data.role,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user