from datetime import timedelta
import datetime
from app.models import user
from app.models.user import  RefreshToken, User
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.crud.user import  create_user, get_user_by_username, verify_password
from app.auth.jwt import create_access_token, create_refresh_token
from app.schemas.user import UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=timedelta(days=7))
    db_refresh_token = RefreshToken(user_id=user.id,
                                     token=refresh_token,
                                     expires_at=datetime.utcnow() + timedelta(days=7))
    db.delete
    db.add(db_refresh_token)b
    db.commit()
    db.refresh(db_refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already registered")
    new_user = create_user(db, user)
    return {"username": new_user.username, "email": new_user.email} 

@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token, RefreshToken.is_active == True).first()
    if not db_token or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired refresh token")
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not found")
    new_access_token = create_access_token(data={"sub": user.username})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token, RefreshToken.is_active == True).first()
    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid refresh token")
    db_token.is_active = False
    db.commit()
    return {"detail": "Logged out successfully"}

