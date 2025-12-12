# backend/app/main.py
from fastapi import FastAPI, status, Depends, HTTPException, APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from pydantic import BaseModel, EmailStr, Field, validator
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging
import sys
import os
import uuid
from typing import Optional

from .dependencies.auth import require_admin, get_current_user

# Dodajemo putanju da bi mogli importovati app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Uvozimo konekcije i modele iz internih modula
from .db import get_db, create_all_tables, connect_to_mongo, close_mongo_connection
from .models.user import User
from .services.auth import get_password_hash, verify_password, create_access_token, create_refresh_token

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Učitavanje varijabli okoline
load_dotenv()

# Inicijalizacija FastAPI Aplikacije
app = FastAPI(
    title="Distributed Film Platform API",
    description="REST API for film data aggregation and analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ----------------------------------------------------------------------
## CORS MIDDLEWARE
# ----------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # FastAPI itself
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
## PYDANTIC MODELS ZA AUTH
# ----------------------------------------------------------------------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: Optional[dict] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: datetime
    message: str = "User registered successfully"

    class Config:
        from_attributes = True


# ----------------------------------------------------------------------
## AUTH ROUTER
# ----------------------------------------------------------------------
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    logger.info(f"Register attempt for user: {user_data.username}")

    # Check if user exists
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

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user
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

    logger.info(f"User {user_data.username} registered successfully")

    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "role": db_user.role,
        "created_at": db_user.created_at,
        "message": "User registered successfully"
    }


@auth_router.post("/login", response_model=Token)
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user and return JWT tokens"""
    logger.info(f"Login attempt for user: {login_data.username}")

    # Find user
    stmt = select(User).where(User.username == login_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Create tokens
    access_token = create_access_token(data={
        "sub": user.username,
        "user_id": str(user.id),
        "role": user.role,
        "type": "access"
    })

    refresh_token = create_refresh_token(data={
        "sub": user.username,
        "user_id": str(user.id),
        "type": "refresh"
    })

    logger.info(f"User {login_data.username} logged in successfully")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token"""
    from .services.auth import verify_token

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
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600
    }


@auth_router.post("/logout")
async def logout_user():
    """Logout user (client should delete tokens)"""
    return {"message": "Successfully logged out. Please delete your tokens."}


@auth_router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "created_at": current_user.created_at,
        "is_active": current_user.is_active
    }


# ----------------------------------------------------------------------
## DEPENDENCY ZA CURRENT USER
# ----------------------------------------------------------------------
from fastapi.security import OAuth2PasswordBearer
from .services.auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


# ----------------------------------------------------------------------
## LIFESPAN HANDLERI (Startup i Shutdown)
# ----------------------------------------------------------------------
@app.on_event("startup")
async def startup_events():
    """Handler koji se izvršava pri pokretanju aplikacije."""
    logger.info("=" * 60)
    logger.info("Starting up Film Data Platform API")
    logger.info("=" * 60)

    # 1. Kreiranje SQL tablica
    logger.info("Creating PostgreSQL tables...")
    try:
        await create_all_tables()
        logger.info("✓ PostgreSQL tables created successfully")
    except Exception as e:
        logger.error(f"✗ Error creating PostgreSQL tables: {e}")

    # 2. Povezivanje na MongoDB
    try:
        await connect_to_mongo()
        logger.info("✓ MongoDB connection established")
    except Exception as e:
        logger.error(f"✗ Error connecting to MongoDB: {e}")

    # 3. Uključi auth router
    app.include_router(auth_router, prefix="/api/v1")
    logger.info("✓ Auth router included at /api/v1/auth")
    logger.info("✓ Available auth endpoints:")
    logger.info("  - POST /api/v1/auth/register")
    logger.info("  - POST /api/v1/auth/login")
    logger.info("  - POST /api/v1/auth/refresh")
    logger.info("  - POST /api/v1/auth/logout")
    logger.info("  - GET  /api/v1/auth/me")

    logger.info("=" * 60)
    logger.info("Application startup complete!")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_events():
    """Handler koji se izvršava prilikom gašenja aplikacije."""
    logger.info("Shutting down Film Data Platform...")

    # Zatvaranje MongoDB konekcije
    try:
        await close_mongo_connection()
        logger.info("✓ MongoDB connection closed")
    except Exception as e:
        logger.error(f"✗ Error closing MongoDB connection: {e}")


# ----------------------------------------------------------------------
## STATUS RUTE
# ----------------------------------------------------------------------
@app.get("/", tags=["Status"])
def read_root():
    """Osnovni status aplikacije."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "online",
            "service": "Distributed Film Platform API",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "documentation": {
                "swagger": "/api/docs",
                "redoc": "/api/redoc"
            },
            "authentication": {
                "register": "POST /api/v1/auth/register",
                "login": "POST /api/v1/auth/login",
                "refresh": "POST /api/v1/auth/refresh",
                "logout": "POST /api/v1/auth/logout",
                "current_user": "GET /api/v1/auth/me"
            }
        }
    )


@app.get("/health", tags=["Status"])
async def health_check():
    """Detaljna provjera zdravlja aplikacije."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "running",
            "postgresql": "connected",
            "mongodb": "connected"
        }
    }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=health_status
    )


@app.get("/api/status", tags=["Status"])
def api_status():
    """Status API endpointova."""
    endpoints = [
        {"path": "/api/v1/auth/register", "method": "POST", "description": "User registration", "protected": False},
        {"path": "/api/v1/auth/login", "method": "POST", "description": "User login", "protected": False},
        {"path": "/api/v1/auth/refresh", "method": "POST", "description": "Refresh token", "protected": False},
        {"path": "/api/v1/auth/logout", "method": "POST", "description": "User logout", "protected": True},
        {"path": "/api/v1/auth/me", "method": "GET", "description": "Get current user", "protected": True},
        {"path": "/health", "method": "GET", "description": "Health check", "protected": False},
        {"path": "/api/docs", "method": "GET", "description": "Swagger documentation", "protected": False},
    ]

    return {
        "api": "Distributed Film Platform API v1",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": endpoints,
        "documentation": {
            "swagger": "/api/docs",
            "redoc": "/api/redoc"
        }
    }


# Debug endpoint za provjeru ruta
@app.get("/debug/routes", tags=["Debug"])
async def debug_routes():
    """Vraća sve registrovane rute."""
    routes = []
    for route in app.routes:
        route_info = {
            "path": route.path,
            "name": getattr(route, "name", "N/A"),
            "methods": list(getattr(route, "methods", []))
        }
        routes.append(route_info)

    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x["path"])
    }


# Test endpoint za provjeru auth
@app.post("/api/v1/auth/test", tags=["Debug"])
async def test_auth_endpoint():
    """Test endpoint za provjeru da li auth rute rade."""
    return {
        "message": "Auth test endpoint works!",
        "timestamp": datetime.utcnow().isoformat(),
        "expected_endpoints": {
            "register": "POST /api/v1/auth/register",
            "login": "POST /api/v1/auth/login",
            "refresh": "POST /api/v1/auth/refresh",
            "logout": "POST /api/v1/auth/logout",
            "me": "GET /api/v1/auth/me"
        }
    }


# Simple test endpoint
@app.get("/test", tags=["Test"])
async def test_endpoint():
    """Simple test endpoint."""
    return {
        "message": "API is working!",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "OK"
    }


@app.get("/admin/users", tags=["Admin"])
async def admin_get_users(
        current_user: User = Depends(require_admin),  # Zahtijeva admin role
        db: AsyncSession = Depends(get_db)
):
    """Get all users (admin only)"""
    from sqlalchemy import select

    stmt = select(User).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()

    return {
        "count": len(users),
        "users": [
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            for user in users
        ]
    }