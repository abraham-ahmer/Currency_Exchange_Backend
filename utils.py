from passlib.context import CryptContext

pwd = CryptContext(schemes="bcrypt", deprecated="auto")

def hash_pass(plain_password:str)->str:
    return pwd.hash(plain_password)

def verify_pass(plain_password:str, hashed_password:str)->bool:
    return pwd.verify(plain_password, hashed_password)




