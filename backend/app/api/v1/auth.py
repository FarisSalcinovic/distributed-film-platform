from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.app.db import get_db
from backend.app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from backend.app.models.user import User
from backend.app.services.auth import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token, verify_token
)
from backend.app.dependencies.auth import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

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
        role="user"  # Default role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/login", response_model=Token)
async def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Create tokens
    access_token = create_access_token(data={"sub": user.username, "user_id": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": user.username, "user_id": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token, is_refresh=True)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Create new access token
    access_token = create_access_token(data={"sub": username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # Return same refresh token (or rotate if needed)
        "token_type": "bearer",
        "expires_in": 3600
    }


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    # In production, you might want to blacklist the token
    # For now, just acknowledge logout
    return {"message": "Successfully logged out"}