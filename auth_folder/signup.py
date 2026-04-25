from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from email_validator import validate_email, EmailNotValidError
from random import randint
from time import time

from models import UserCreate, UserResponse, EmailOTPVerify
from database import get_db
from database_models import User
from utils import hash_pass
from email_service import send_otp_email

router = APIRouter(tags=["Signup"])

# OTP storage: {email: {"otp": "123456", "expiry": timestamp, "user_data": UserCreate}}
otp_store = {}

@router.post("/signup")
def signup(uc: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Step 1: User submits email and password. Validates email format, generates OTP, sends to inbox. """
    # Validate email format
    try:
        valid = validate_email(uc.email)
        uc.email = valid.email  # normalized email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=f"Invalid email: {str(e)}")
    
    # Check if email already registered
    db_user = db.query(User).filter(User.email == uc.email).first()
    if db_user:
        raise HTTPException(status_code=401, detail="Email already registered")
    
    # Generate OTP
    otp = str(randint(100000, 999999))

    # Schedule OTP email as background task
    background_tasks.add_task(send_otp_email, uc.email, otp)
    
    
    # Store OTP and user data temporarily (5 minutes expiry)
    otp_store[uc.email] = {
        "otp": otp,
        "expiry": time() + 300,
        "user_data": uc
    }
    
    return {
        "message": "OTP sent to your email. Check your inbox",
    }


@router.post("/signup/verify_otp", response_model=UserResponse)
def verify_otp(req: EmailOTPVerify, db: Session = Depends(get_db)):
    """
    Step 2: User submits email and OTP.
    Verifies OTP, creates user account, marks email as verified.
    """
    record = otp_store.get(req.email)
    
    # Check if OTP exists, matches, and hasn't expired
    if not record:
        raise HTTPException(status_code=400, detail="OTP request not found. Please sign up again.")
    
    if record["otp"] != req.otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")
    
    if time() > record["expiry"]:
        del otp_store[req.email]
        raise HTTPException(status_code=401, detail="OTP expired. Please sign up again.")
    
    # OTP verified! Now create the user
    uc = record["user_data"]
    hashed_password = hash_pass(uc.password)
    
    new_user = User(
        username=uc.username,
        email=uc.email,
        password=hashed_password,
        email_verified=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Clean up OTP
    del otp_store[req.email]
    
    return new_user

















