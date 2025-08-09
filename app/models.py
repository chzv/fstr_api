from sqlalchemy import (
    Column, BigInteger, Integer, Text, ForeignKey, DateTime, LargeBinary, Numeric
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base
import enum

class ModerationStatus(enum.Enum):
    new = "new"
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    full_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    phone = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    perevals = relationship("Pereval", back_populates="user")

class Coords(Base):
    __tablename__ = "coords"
    id = Column(BigInteger, primary_key=True)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    height = Column(Integer, nullable=False)
    perevals = relationship("Pereval", back_populates="coords")

class Levels(Base):
    __tablename__ = "levels"
    id = Column(BigInteger, primary_key=True)
    winter = Column(Text, nullable=False, default="")
    summer = Column(Text, nullable=False, default="")
    autumn = Column(Text, nullable=False, default="")
    spring = Column(Text, nullable=False, default="")
    perevals = relationship("Pereval", back_populates="levels")

class Pereval(Base):
    __tablename__ = "pereval"
    id = Column(BigInteger, primary_key=True)
    beauty_title = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    other_titles = Column(Text, nullable=False, default="")
    connect = Column(Text, nullable=False, default="")
    add_time = Column(DateTime(timezone=True), nullable=False)

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    coords_id = Column(BigInteger, ForeignKey("coords.id", ondelete="RESTRICT"), nullable=False)
    levels_id = Column(BigInteger, ForeignKey("levels.id", ondelete="RESTRICT"), nullable=False)

    from sqlalchemy.dialects.postgresql import ENUM as PGEnum
    status = Column(PGEnum(ModerationStatus, name="moderation_status"), nullable=False, default=ModerationStatus.new)
    moderator_note = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="perevals")
    coords = relationship("Coords", back_populates="perevals")
    levels = relationship("Levels", back_populates="perevals")
    images = relationship("Image", back_populates="pereval", cascade="all, delete-orphan")

class Image(Base):
    __tablename__ = "images"
    id = Column(BigInteger, primary_key=True)
    pereval_id = Column(BigInteger, ForeignKey("pereval.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    pereval = relationship("Pereval", back_populates="images")
