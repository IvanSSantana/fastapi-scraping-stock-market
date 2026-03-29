from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt # type: ignore
from passlib.context import CryptContext # type: ignore
from repository.user_model import UserRegistration
import uuid
from env import AUTH_KEY, HASHING_ALGORITHM
from datetime import datetime, timedelta

app = FastAPI()

password_encrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str):
    return password_encrypt_context.hash(password)

def verify_password(password: str, hashed: str):
    return password_encrypt_context.verify(password, hashed)

def create_token(username: str, is_admin: bool = False):

    payload = {
        "sub": str(uuid.uuid4()), # Unique identifier for the token
        "username": username,
        "admin": is_admin, 
        "iat": datetime.now(), # Issued at
        "exp": datetime.now() + timedelta(weeks=2) # Expires
    }

    return jwt.encode(payload, AUTH_KEY, algorithm=HASHING_ALGORITHM)

@app.post("/api/v1/register")
def register(user: UserRegistration):
    if user.username in ["fake_db_users"]: 
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return {"message": "User registered successfully"}

@app.post("/api/v1/login")
def login(username: str, password: str):

    if username != "admin" or password != "123": # TODO: Implementar com verificação de credenciais real em um banco de dados, hashing de senhas etc.
        raise HTTPException(status_code=401)

    token = create_token(username)

    return {
        "access_token": token, 
        "token_type": "bearer"
        }

def verify_token(token: str = Depends(oauth2_scheme)):

    try:
        payload = jwt.decode(token, AUTH_KEY, algorithms=[HASHING_ALGORITHM])
        return payload["sub"]
    except:
        raise HTTPException(status_code=401)


@app.get("/secure-data")
def secure_route_example(user_token: str = Depends(verify_token)):
    return {"user": user_token}