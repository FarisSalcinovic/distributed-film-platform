from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from ...db import get_db
from ...schemas.user import UserCreate, UserResponse, UserLogin
from ...schemas.token import Token
from ...models.user import User
from ...services.auth import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    """
    # Check if user exists - ASYNC verzija
    stmt = select(User).where(
        or_(User.username == user_data.username, User.email == user_data.email)
    )
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role="user"
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
async def login(form_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Login user and return JWT tokens.
    """
    # ASYNC query
    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Create tokens
    access_token = create_access_token(data={
        "sub": user.username,
        "user_id": str(user.id),
        "role": user.role
    })

    refresh_token = create_refresh_token(data={
        "sub": user.username,
        "user_id": str(user.id)
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # u sekundama
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.
    """
    payload = verify_token(refresh_token, is_refresh=True)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    username = payload.get("sub")
    user_id = payload.get("user_id")

    if username is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload"
        )

    # Create new access token
    access_token = create_access_token(data={
        "sub": username,
        "user_id": user_id,
        "role": payload.get("role", "user")
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # Možete rotirati refresh token ako želite
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/logout")
async def logout():
    """
    Logout user (client should delete tokens).
    """
    return {"message": "Successfully logged out. Please delete your tokens."}