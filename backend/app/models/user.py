# backend/app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..db import Base
import uuid


# Ova linija osigurava da je model UUID tipa stringa za kompatibilnost s PostgreSQL-om
# i lakšim rukovanjem u API-ju.

class User(Base):
    """
    SQLAlchemy Model za korisnike (PostgreSQL).
    Sadrži polja potrebna za JWT autentifikaciju i RBAC (Role-Based Access Control).
    """
    __tablename__ = "users"

    # Koristimo UUID kao primarni ključ
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    # Hash lozinke
    hashed_password = Column(String, nullable=False)

    # Role-Based Access Control (RBAC) - Modul B1
    role = Column(String, default="user", nullable=False)  # 'user' ili 'admin'

    # Status i praćenje (Soft Delete)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User username={self.username} role={self.role}>"