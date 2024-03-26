from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Trader(Base):
    __tablename__ = "traders"
    id = Column(Integer, primary_key=True)
    api_key = Column(String)
    api_secret = Column(String)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    followers = relationship(
        "Follower", back_populates="trader", cascade="all, delete-orphan"
    )

    def dict(self):
        return {
            "email": self.email,
            "is_active": self.is_active,
            "api_key": self.api_key,
            "api_secret": self.api_secret,
            "id": self.id,
        }


class Follower(Base):
    __tablename__ = "followers"
    id = Column(Integer, primary_key=True)
    api_key = Column(String)
    api_secret = Column(String)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    trader_id = Column(Integer, ForeignKey("traders.id"))
    trader = relationship("Trader", back_populates="followers")
