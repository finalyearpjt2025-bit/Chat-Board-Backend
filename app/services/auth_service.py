from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_access_token, hash_password, verify_password
from app.repositories.users import create_user, get_user_by_email
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest


async def register_user(
    session: AsyncSession,
    payload: UserRegisterRequest,
) -> TokenResponse:
    existing_user = await get_user_by_email(session, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    user = await create_user(
        session,
        name=payload.name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
    )
    access_token = create_access_token(user["id"])

    return TokenResponse(access_token=access_token, user=user)


async def login_user(
    session: AsyncSession,
    payload: UserLoginRequest,
) -> TokenResponse:
    user = await get_user_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(user["id"])

    return TokenResponse(access_token=access_token, user=user)

