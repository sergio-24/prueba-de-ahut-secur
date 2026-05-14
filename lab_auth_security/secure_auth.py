# secure_auth.py
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

USERS = {
    "alice@example.com": {"password": hash_password("password123"), "role": "user"},
    "admin@example.com": {"password": hash_password("adminpass"), "role": "admin"},
}

with open("private.pem", "rb") as f:
    PRIVATE_KEY = f.read()
with open("public.pem", "rb") as f:
    PUBLIC_KEY = f.read()

ISS = "mi-curso-ucc"
AUD = "ucc-client"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
BLACKLIST = set()

class LoginIn(BaseModel):
    email: str
    password: str

def create_access_token(data: dict):
    now = datetime.utcnow()
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        **data,
        "exp": expire,
        "iat": now,
        "iss": ISS,
        "aud": AUD
    }
    return jwt.encode(to_encode, PRIVATE_KEY, algorithm="RS256")

@app.post("/login")
def login(data: LoginIn):
    user = USERS.get(data.email)
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    payload = {"sub": data.email, "role": user["role"]}
    token = create_access_token(payload)
    return {"access_token": token}

def verify_token(token: str):
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"], audience=AUD, issuer=ISS)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    if token in BLACKLIST:
        raise HTTPException(status_code=401, detail="Token revocado")

    return payload

@app.get("/admin")
def admin(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing token")
    token = authorization.split(" ")[1]
    payload = verify_token(token)

    if payload["role"] != "admin":
        raise HTTPException(403, "Forbidden")

    return {"msg": "Acceso seguro - solo administradores"}

@app.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing token")
    token = authorization.split(" ")[1]
    BLACKLIST.add(token)
    return {"msg": "logout exitoso"}
