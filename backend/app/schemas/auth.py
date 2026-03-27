from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from datetime import datetime


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    password: str = Field(..., min_length=8)
    role: Literal["hybrid", "radiologist", "sonographer"] = "hybrid"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OTPSendRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")


class OTPVerifyRequest(BaseModel):
    phone: str
    code: str = Field(..., min_length=4, max_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    role: str
    otp_verified: bool
    created_at: datetime


TokenResponse.model_rebuild()
