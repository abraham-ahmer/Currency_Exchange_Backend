# for jwt tokens

from jose import jwt, JWTError
from datetime import datetime, timedelta
from models import TokenData
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from database_models import User
import os
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_EXPIRATION_MINUTES = int(os.getenv("ACCESS_EXPIRATION_MINUTES", 30))
ACCESS_EXPIRATION_DAYS = int(os.getenv("ACCESS_EXPIRATION_DAYS", 7))


#creating token
def create_access_tokens(data:dict):
    to_encode = data.copy()
    expiry = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRATION_MINUTES)
    to_encode.update({"exp": expiry})
    jwt_token = jwt.encode(claims=to_encode, key=PRIVATE_KEY, algorithm=ALGORITHM)
    return jwt_token



#refreshing token
def create_refresh_tokens(data:dict):
    to_encode = data.copy()
    expiry = datetime.utcnow() + timedelta(days=ACCESS_EXPIRATION_DAYS)
    to_encode.update({"exp":expiry})
    jwt_refresh = jwt.encode(claims=to_encode, key=PRIVATE_KEY, algorithm=ALGORITHM)
    return jwt_refresh

"""now i can issue both tokens. for short time and refreshed one for longer period """


#verifying token
def verify_token(token:str, credential_exception):
    try:
        decode = jwt.decode(token, key=PRIVATE_KEY, algorithms=ALGORITHM)
        us_id = decode.get("user_id")

        if not us_id:
            raise credential_exception
        return TokenData(id=us_id)
    except JWTError:
        raise credential_exception


scheme = OAuth2PasswordBearer(tokenUrl="login")

#creating access via verifyin token
def create_access(tok:str = Depends(scheme), db:Session = Depends(get_db)):
    credential_exception= HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail= "User deleted or does not exist",
        headers= {"WWW-Authenticate": "bearer"}
    )

    new_token= verify_token(tok, credential_exception)
    user_query = db.query(User).filter(User.id == new_token.id).first()

    if not user_query:
        raise credential_exception
    return user_query
