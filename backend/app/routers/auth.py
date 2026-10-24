from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.schemas import TokenResponse, UserLogin, UserRegister, UserResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: UserRegister,
    db: Session = Depends(get_db),
) -> User:
    username = payload.username.strip()
    email = str(payload.email).strip().lower()

    existing_user = db.scalar(
        select(User).where(
            or_(
                User.username == username,
                User.email == email,
            )
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(payload.password),
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        ) from None

    return user


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: UserLogin,
    db: Session = Depends(get_db),
) -> TokenResponse:
    email = str(payload.email).strip().lower()

    user = db.scalar(select(User).where(User.email == email))

    if (
        user is None
        or not verify_password(payload.password, user.password_hash)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.id))

    return TokenResponse(access_token=token)
