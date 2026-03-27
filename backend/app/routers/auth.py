from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends

from app.core.database import users_col
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    OTPSendRequest,
    OTPVerifyRequest,
    TokenResponse,
    UserOut,
)
from app.services.otp_service import send_otp, verify_otp

router = APIRouter(prefix="/auth", tags=["Auth"])


def _serialize_user(doc: dict) -> UserOut:
    return UserOut(
        id=str(doc["_id"]),
        full_name=doc["full_name"],
        email=doc["email"],
        phone=doc["phone"],
        role=doc["role"],
        otp_verified=doc.get("otp_verified", False),
        created_at=doc["created_at"],
    )


# ── POST /auth/register ───────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest):
    # Check duplicate email
    if await users_col().find_one({"email": body.email}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    now = datetime.now(timezone.utc)
    doc = {
        "full_name": body.full_name,
        "email": body.email,
        "phone": body.phone,
        "password_hash": hash_password(body.password),
        "role": body.role,
        "otp_verified": False,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    result = await users_col().insert_one(doc)
    doc["_id"] = result.inserted_id

    # Auto-send OTP to phone after registration
    await send_otp(body.phone)

    token = create_access_token({"sub": str(result.inserted_id), "role": body.role})
    return TokenResponse(access_token=token, user=_serialize_user(doc))


# ── POST /auth/login ──────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    user = await users_col().find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token({"sub": str(user["_id"]), "role": user["role"]})
    return TokenResponse(access_token=token, user=_serialize_user(user))


# ── GET /auth/me ─────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
async def get_me(current_user: dict = Depends(get_current_user)):
    return _serialize_user(current_user)


# ── POST /auth/logout ─────────────────────────────────────────────────────────
# JWT is stateless — client drops the token.
# Optionally maintain a server-side blocklist here later.

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    return {"message": "Logged out successfully"}


# ── POST /auth/otp/send ───────────────────────────────────────────────────────

@router.post("/otp/send")
async def otp_send(body: OTPSendRequest):
    result = await send_otp(body.phone)
    if not result["sent"]:
        raise HTTPException(status_code=503, detail=result["message"])
    return {"message": result["message"]}


# ── POST /auth/otp/verify ─────────────────────────────────────────────────────

@router.post("/otp/verify")
async def otp_verify(
    body: OTPVerifyRequest,
    current_user: dict = Depends(get_current_user),
):
    # Only verify OTP if the phone matches the current user's phone
    if current_user["phone"] != body.phone:
        raise HTTPException(
            status_code=400,
            detail="Phone number does not match your account",
        )

    success, message = await verify_otp(body.phone, body.code)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    # Mark user as OTP-verified
    await users_col().update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": {"otp_verified": True}},
    )

    return {"message": message, "otp_verified": True}
