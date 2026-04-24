from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from database import get_db
from database_models import User
from utils import verify_pass
from jose import jwt, JWTError
from oauth import PRIVATE_KEY, ALGORITHM, create_access_tokens, create_refresh_tokens
from models import RefreshRequest

router = APIRouter(tags=["Login"], prefix="/login")


@router.post("/")
def login(uc: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Simple login: email/username + password.
    Returns JWT tokens directly.
    """
    db_user = db.query(User).filter((User.email == uc.username) | (User.username == uc.username)).first()
 
    if not db_user or not verify_pass(uc.password, db_user.password): 
        raise HTTPException(status_code=401, detail="Invalid email/username or password")
    
    # Create tokens
    payload = {"user_id": db_user.id}
    access_token = create_access_tokens(payload)
    refresh_token = create_refresh_tokens(payload)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }


@router.post("/refresh")
def refresh_the_token(ref: RefreshRequest):
    """
    Refresh access token using refresh token.
    """
    try:
        decode = jwt.decode(ref.refresh_token, key=PRIVATE_KEY, algorithms=ALGORITHM)
        us_id = decode.get("user_id")
        if not us_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        payload = {"user_id": us_id}
        new_access_token = create_access_tokens(payload)
        return {"access_token": new_access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
 





