from pydantic import BaseModel, field_validator, model_validator, EmailStr, constr
from datetime import datetime, date
import re
from typing import Optional


class UserCreate(BaseModel):
    username:str
    email: EmailStr  # regex directly here
    password: str

    @field_validator("password") 
    def pass_len(cls, v:str)->str:
        if len(v) < 2:
            raise ValueError("Password must be at least 2 characters long")
        return v
    
    @field_validator("email")
    def check_email(cls, v:str)->str:
        pattern = r'^[a-zA-Z0-9]+\.?[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]+$'
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v


class UserResponse(BaseModel):
    id: int
    username:str
    email:EmailStr
    password: str
    created_at: datetime

    class config:
        from_attributes=True





class CurrencyLive(BaseModel):
    base_currency:str
    target_currency:str

    @field_validator("base_currency", "target_currency") 
    def currency_capitalize(cls, v:str)->str:
        return v.upper()
    
class CurrencyConvert(CurrencyLive):
    amount:int = 1  # default value if user doesn’t provide


class CurrencyHistoric(CurrencyConvert):
    historical_date: date | None = None

    @model_validator(mode="after") 
    def check_date(cls, value:date):
        if value.historical_date and value.historical_date > date.today():
            raise ValueError("Historical date cannot be today and in future")
        return value







class CurrencyResponse(BaseModel):
    id:int 
    checked_at:datetime 
    base_currency:str
    target_currency:str
    amount:int
    converted:float
    historical_date: date | None = None
    user_id: int
    
    class config:
        from_attributes=True



class Token(BaseModel):
    access_token:str
    token_type:str
    refresh_token: str   #for refreshing token time

class TokenData(BaseModel):
    id: Optional[int] = None    


class RefreshRequest(BaseModel):
    refresh_token:str


# for OTP 2fa
class OTPVerifyRequest(BaseModel):
    username:str
    otp:str


# for signup OTP verification
class EmailOTPVerify(BaseModel):
    email: str
    otp: str




