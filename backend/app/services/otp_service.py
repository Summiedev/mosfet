
import base64
import hashlib
import random
import string
import uuid
from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings
from app.core.database import otps_col


# ── Helpers ───────────────────────────────────────────────────────────────────

def _generate_code(length: int = 6) -> str:
    """Generate a numeric OTP code."""
    return "".join(random.choices(string.digits, k=length))


def _hash_code(code: str) -> str:
    """Store only a hash — never store plaintext OTP codes."""
    return hashlib.sha256(code.encode()).hexdigest()


def _basic_auth_header() -> str:
    """
    Interswitch OAuth requires Basic auth:
    base64(CLIENT_ID:CLIENT_SECRET)
    """
    raw = f"{settings.INTERSWITCH_CLIENT_ID}:{settings.INTERSWITCH_CLIENT_SECRET}"
    encoded = base64.b64encode(raw.encode()).decode()
    return f"Basic {encoded}"


def _is_dev_mode() -> bool:
    return (
        not settings.INTERSWITCH_CLIENT_ID
        or settings.APP_ENV == "development"
    )



async def _get_bearer_token() -> str | None:
 
    token_url = f"{settings.INTERSWITCH_BASE_URL}/passport/oauth/token"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                token_url,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": _basic_auth_header(),
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": "profile",
                },
            )
            resp.raise_for_status()
            token = resp.json().get("access_token")
            if not token:
                print(f"[OTP ERROR] No access_token in Interswitch response: {resp.text}")
            return token
    except httpx.HTTPStatusError as exc:
        print(f"[OTP ERROR] Token fetch HTTP {exc.response.status_code}: {exc.response.text}")
        return None
    except httpx.HTTPError as exc:
        print(f"[OTP ERROR] Token fetch failed: {exc}")
        return None



async def _whatsapp_send(phone: str, code: str, bearer_token: str) -> bool:
 
    if phone.startswith("0"):
        normalised = "+234" + phone[1:]
    elif not phone.startswith("+"):
        normalised = "+" + phone
    else:
        normalised = phone

    payload = {
        "phoneNumber": normalised,
        "code": code,
        "action": "verifying your RadFlow account",
        "service": "RadFlow",
        "channel": "phone",
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                settings.INTERSWITCH_WHATSAPP_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {bearer_token}",
                },
            )
            # Interswitch returns 200/201 on success
            if resp.status_code in (200, 201):
                print(f"[OTP] WhatsApp OTP sent to {normalised}")
                return True
            else:
                print(f"[OTP ERROR] WhatsApp send {resp.status_code}: {resp.text}")
                return False
    except httpx.HTTPError as exc:
        print(f"[OTP ERROR] WhatsApp send failed: {exc}")
        return False


# ── Public API ────────────────────────────────────────────────────────────────

async def send_otp(phone: str) -> dict:
    """
    Generate OTP code, store hash in MongoDB, send via Interswitch WhatsApp.

    Returns:
      { "sent": bool, "message": str, "expires_in_seconds": int }

    Enforces:
      - 60-second resend cooldown
      - Code stored as SHA-256 hash (never plaintext in prod)
    """
    now = datetime.now(timezone.utc)

    # ── Resend cooldown ───────────────────────────────────────────────────────
    existing = await otps_col().find_one({"phone": phone})
    if existing:
        last_sent = existing.get("sent_at")
        if last_sent:
            if last_sent.tzinfo is None:
                last_sent = last_sent.replace(tzinfo=timezone.utc)
            elapsed = (now - last_sent).total_seconds()
            if elapsed < 60:
                wait = int(60 - elapsed)
                return {
                    "sent": False,
                    "message": f"Please wait {wait}s before requesting a new OTP.",
                    "expires_in_seconds": 0,
                }

    # ── Generate code ─────────────────────────────────────────────────────────
    code = _generate_code(settings.OTP_LENGTH)
    expires_at = now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    expires_in = settings.OTP_EXPIRE_MINUTES * 60

    # ── Dev mode — print to console, skip API ─────────────────────────────────
    if _is_dev_mode():
        await otps_col().update_one(
            {"phone": phone},
            {
                "$set": {
                    "phone": phone,
                    "code_hash": _hash_code(code),
                    # Store plaintext ONLY in dev mode for e2e test retrieval
                    "_dev_plain": code,
                    "expires_at": expires_at,
                    "verified": False,
                    "attempts": 0,
                    "sent_at": now,
                    "verified_at": None,
                    "provider": "dev",
                }
            },
            upsert=True,
        )
        print("─" * 54)
        print(f"  [OTP DEV]  WhatsApp OTP (console fallback)")
        print(f"  [OTP DEV]  Phone   : {phone}")
        print(f"  [OTP DEV]  Code    : {code}   ← enter this")
        print(f"  [OTP DEV]  Expires : {expires_at.strftime('%H:%M:%S UTC')}")
        print("─" * 54)
        return {
            "sent": True,
            "message": "OTP sent (dev mode — check server console)",
            "expires_in_seconds": expires_in,
        }

    # ── Production — Interswitch WhatsApp OTP ─────────────────────────────────

    # Step A: get Bearer token
    bearer = await _get_bearer_token()
    if not bearer:
        return {
            "sent": False,
            "message": "Authentication with OTP provider failed. Please try again.",
            "expires_in_seconds": 0,
        }

    # Step B: send via WhatsApp
    sent = await _whatsapp_send(phone, code, bearer)
    if not sent:
        return {
            "sent": False,
            "message": "Failed to deliver OTP via WhatsApp. Please try again.",
            "expires_in_seconds": 0,
        }

    # ── Persist (hash only — never plaintext in production) ───────────────────
    await otps_col().update_one(
        {"phone": phone},
        {
            "$set": {
                "phone": phone,
                "code_hash": _hash_code(code),
                "expires_at": expires_at,
                "verified": False,
                "attempts": 0,
                "sent_at": now,
                "verified_at": None,
                "provider": "interswitch_whatsapp",
            }
        },
        upsert=True,
    )

    return {
        "sent": True,
        "message": "Verification code sent to your WhatsApp",
        "expires_in_seconds": expires_in,
    }


async def verify_otp(phone: str, code: str) -> tuple[bool, str]:
    """
    Verify an OTP code the user entered.

    RadFlow owns the code (we generated it), so verification is always
    a local hash comparison — no second Interswitch call needed.

    Returns (success: bool, message: str)
    """
    record = await otps_col().find_one({"phone": phone})

    if not record:
        return False, "No verification code found. Please request a new one."

    if record.get("verified"):
        return False, "This code was already used. Please request a new one."

    attempts = record.get("attempts", 0)
    if attempts >= 5:
        return False, "Too many failed attempts. Please request a new code."

    # Increment attempts before checking (prevents timing attacks)
    await otps_col().update_one({"phone": phone}, {"$inc": {"attempts": 1}})

    # Check expiry
    now = datetime.now(timezone.utc)
    expires_at = record["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now > expires_at:
        return False, "Code has expired. Please request a new one."

    # Verify hash
    if record.get("code_hash") != _hash_code(code):
        remaining = max(0, 4 - attempts)
        if remaining > 0:
            return False, f"Incorrect code. {remaining} attempt(s) remaining."
        return False, "Incorrect code. No attempts remaining — please request a new one."

    # Mark verified
    await otps_col().update_one(
        {"phone": phone},
        {"$set": {"verified": True, "verified_at": now}},
    )
    return True, "Phone number verified successfully."


async def get_otp_status(phone: str) -> dict:
    """
    Returns OTP metadata for frontend countdown timers.
    Never exposes the code or hash.
    """
    record = await otps_col().find_one({"phone": phone})
    if not record:
        return {"exists": False}

    now = datetime.now(timezone.utc)
    expires_at = record["expires_at"]
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    sent_at = record.get("sent_at", expires_at)
    if sent_at.tzinfo is None:
        sent_at = sent_at.replace(tzinfo=timezone.utc)

    return {
        "exists": True,
        "verified": record.get("verified", False),
        "attempts_remaining": max(0, 5 - record.get("attempts", 0)),
        "expired": now > expires_at,
        "time_remaining_seconds": max(0, int((expires_at - now).total_seconds())),
        "resend_wait_seconds": max(0, int(60 - (now - sent_at).total_seconds())),
        "provider": record.get("provider", "interswitch_whatsapp"),
        "channel": "WhatsApp",
    }
