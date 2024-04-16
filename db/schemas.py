from __future__ import annotations

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, EmailStr, field_validator


class TraderBase(BaseModel):
    email: EmailStr | None = None
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        try:
            validate_email(v)
            return v
        except EmailNotValidError as e:
            raise ValueError(str(e)) from e


class TraderCreate(TraderBase):
    api_key: str
    api_secret: str


class Trader(TraderBase):
    id: int

    class Config:
        from_attributes = True


class TraderDict(TraderBase):
    email: int
    is_active: bool
    api_key: str
    api_secret: str
    id: int


class FollowerBase(TraderBase):
    email: str


class FollowerCreate(TraderCreate):
    api_key: str
    api_secret: str


class FollowerDict(TraderBase):
    email: int
    is_active: bool
    api_key: str
    api_secret: str
    trader_id: int


class Follower(TraderBase):
    id: int

    class Config:
        from_attributes = True
