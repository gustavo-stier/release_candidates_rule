from typing import ClassVar, Optional

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, field_validator


class UserSchema(BaseModel):
    username: str
    email: str
    hashed_password: str
    admin: Optional[bool] = False

    ALLOWED_DOMAINS: ClassVar[set[str]] = {
        "eroninternational.com",
        "directa24.com",
        "d24.com",
    }

    class Config:
        from_attributes = True

    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, v: EmailStr) -> EmailStr:
        domain = v.split("@", 1)[1].lower()
        if not any(
            domain == d or domain.endswith("." + d) for d in cls.ALLOWED_DOMAINS
        ):
            allowed_list = ", ".join(sorted(cls.ALLOWED_DOMAINS))
            raise HTTPException(
                status_code=400,
                detail=f"Company domain not allowed: ({domain}). Allowed domains: ({allowed_list})",
            )
        return v


class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True
