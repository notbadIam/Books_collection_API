from bcrypt import hashpw, checkpw, gensalt
from fastapi import Depends
from jose import jwt, JWTError
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


from config import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from datetime import datetime, timedelta, timezone


def create_token(data:dict):
    copy_of_data = data.copy()
    expiring_time = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    copy_of_data.update({"new_version": 1})
    copy_of_data.update({"exp":expiring_time})
    token = jwt.encode(copy_of_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return token



def verify_token(token:str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("user")
    except  JWTError:
        raise HTTPException(status_code=404, detail="Token is invalid")



def verify_admin(token:str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('role') == 'admin':
            return True
        else:
            return False
    except  JWTError:
        raise HTTPException(status_code=404, detail="Token is invalid")


def hashing_p(password: str):
    hashed = hashpw(password.encode("utf-8)"),gensalt())
    return hashed.decode("utf-8")


def check_pwd(hashed: str, password: str):
    return checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

